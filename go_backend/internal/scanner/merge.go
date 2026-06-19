package scanner

import (
    "sort"

    "cpv_backend/internal/db"
    "cpv_backend/internal/schemas"
)

// normalizeVideoDataSlices replaces nil slices with empty slices so JSON
// marshaling writes [] instead of null, keeping Python readers happy.
func normalizeVideoDataSlices(vd *schemas.VideoData) {
    if vd.Actors == nil          { vd.Actors = []string{} }
    if vd.PrimaryActors == nil   { vd.PrimaryActors = []string{} }
    if vd.SecondaryActors == nil { vd.SecondaryActors = []string{} }
    if vd.Tags == nil            { vd.Tags = []string{} }
    if vd.TagsFromFilename == nil { vd.TagsFromFilename = []string{} }
    if vd.TagsFromPath == nil    { vd.TagsFromPath = []string{} }
    if vd.TagsFromJSON == nil    { vd.TagsFromJSON = []string{} }
    if vd.Genres == nil          { vd.Genres = []string{} }
}

// SortTagsByFrequency sorts each video's tag source lists by descending
// frequency of that tag within the same collection, then re-derives Tags.
func SortTagsByFrequency(videos map[string]*schemas.VideoData) {
    // Count tag frequency per collection across all tag sources
    freq := map[string]map[string]int{} // collection → tag → count
    for _, vd := range videos {
        if _, ok := freq[vd.Collection]; !ok {
            freq[vd.Collection] = map[string]int{}
        }
        for _, t := range vd.TagsFromFilename {
            freq[vd.Collection][t]++
        }
        for _, t := range vd.TagsFromPath {
            freq[vd.Collection][t]++
        }
        for _, t := range vd.TagsFromJSON {
            freq[vd.Collection][t]++
        }
    }

    sorter := func(coll string, tags []string) []string {
        f := freq[coll]
        sorted := make([]string, len(tags))
        copy(sorted, tags)
        sort.SliceStable(sorted, func(i, j int) bool {
            return f[sorted[i]] > f[sorted[j]]
        })
        return sorted
    }

    for _, vd := range videos {
        vd.TagsFromFilename = sorter(vd.Collection, vd.TagsFromFilename)
        vd.TagsFromPath = sorter(vd.Collection, vd.TagsFromPath)
        vd.TagsFromJSON = sorter(vd.Collection, vd.TagsFromJSON)

        // Rebuild Tags as deduplicated union (filename → path → json order)
        seen := map[string]bool{}
        var merged []string
        for _, src := range [][]string{vd.TagsFromFilename, vd.TagsFromPath, vd.TagsFromJSON} {
            for _, t := range src {
                if !seen[t] {
                    seen[t] = true
                    merged = append(merged, t)
                }
            }
        }
        vd.Tags = merged
    }
}

// MergeAndSave loads the existing DB records, merges newly-scanned videos in,
// marks anything not found in the scan as is_linked=false (when !isFiltered),
// and writes everything back to the DB.
func MergeAndSave(dbPath string, loaded map[string]*schemas.VideoData, isFiltered bool) error {
    existing, err := db.ReadSerializedMapFromTable[schemas.VideoData](dbPath, "videos")
    if err != nil {
        return err
    }

    // Start from existing; mark all unlinked if this is a full scan
    merged := map[string]schemas.VideoData{}
    for hash, vd := range existing {
        if !isFiltered {
            vd.IsLinked = false
        }
        merged[hash] = vd
    }

    // Overlay newly-scanned videos, preserving fields the scan didn't touch
    for hash, scanned := range loaded {
        scanned.IsLinked = true
        if old, exists := merged[hash]; exists {
            // Preserve fields populated by other means (sidecar, manual edits)
            if scanned.Description == "" {
                scanned.Description = old.Description
            }
            if scanned.Metadata == nil {
                scanned.Metadata = old.Metadata
            }
            if scanned.DateAdded == "" {
                scanned.DateAdded = old.DateAdded
            }
        }
        merged[hash] = *scanned
    }

    // Write all records back, ensuring nil slices become [] not null in JSON
    for hash, vd := range merged {
        normalizeVideoDataSlices(&vd)
        if err := db.WriteSerializedRowToTable(dbPath, "videos", hash, vd); err != nil {
            return err
        }
    }

    db.InvalidateCache()
    return nil
}
