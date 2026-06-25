package scanner

import (
	"fmt"
	"path/filepath"
	"regexp"
	"strings"

	string_parser "github.com/MattThePerson/string_parser"

	"cpv_backend/internal/schemas"
)

var purelyNumeric = regexp.MustCompile(`^[0-9]+$`)

// ExtractTags scans a filename stem or path from right to left, consuming
// trailing space-delimited tokens from the last path component that look like
// "#Word" where Word is not purely numeric. Returns the tags in left-to-right
// order and the input with those tokens stripped from the final component.
func ExtractTags(stemOrPath string) (tags []string, cleaned string) {
    dir, base := "", stemOrPath
    if idx := strings.LastIndex(stemOrPath, "/"); idx >= 0 {
        dir, base = stemOrPath[:idx+1], stemOrPath[idx+1:]
    }
    tokens := strings.Fields(base)
    cutAt := len(tokens)
    for i := len(tokens) - 1; i >= 0; i-- {
        tok := tokens[i]
        if !strings.HasPrefix(tok, "#") {
            break
        }
        rest := tok[1:]
        if rest == "" || purelyNumeric.MatchString(rest) {
            break
        }
        cutAt = i
    }
    tags = make([]string, 0, len(tokens)-cutAt)
    for _, tok := range tokens[cutAt:] {
        tags = append(tags, tok[1:])
    }
    return tags, dir + strings.Join(tokens[:cutAt], " ")
}

// ParseFilename tries to extract structured metadata from the path string
// (relative parent dirs + cleaned filename stem, no extension, no tags).
// Returns an empty map if no format matched — that is not an error.
func ParseFilename(relPathStem string, parser *string_parser.StringParser) map[string]any {
    if relPathStem == "" {
        return map[string]any{}
    }
    result, err := parser.Parse(relPathStem)
    if err != nil {
        return map[string]any{}
    }
    return result
}

// clearFilenameFields zeros all VideoData fields that PopulateFromParseResult
// can set. Call this before reparsing an existing record so stale values from a
// previous (possibly incorrect) parse don't survive when the new parse omits them.
func clearFilenameFields(vd *schemas.VideoData) {
    vd.Title = ""
    vd.SceneTitle = ""
    vd.SceneNumber = 0
    vd.MovieTitle = ""
    vd.MovieSeries = ""
    vd.Studio = ""
    vd.Line = ""
    vd.DateReleased = ""
    vd.SourceID = ""
    vd.DVDCode = ""
    vd.Actors = nil
    vd.PrimaryActors = nil
}

// PopulateFromParseResult maps string_parser field names onto VideoData fields.
func PopulateFromParseResult(vd *schemas.VideoData, parsed map[string]any) {
    str := func(key string) string {
        v, ok := parsed[key]
        if !ok {
            return ""
        }
        s, _ := v.(string)
        return strings.TrimSpace(s)
    }
    splitActors := func(s string) []string {
        var out []string
        for part := range strings.SplitSeq(s, ",") {
            if t := strings.TrimSpace(part); t != "" {
                out = append(out, t)
            }
        }
        return out
    }

    if v := str("primary_actors"); v != "" {
        vd.PrimaryActors = splitActors(v)
        vd.Actors = append(vd.Actors, vd.PrimaryActors...)
    }
    if v := str("secondary_actors"); v != "" {
        vd.SecondaryActors = splitActors(v)
        vd.Actors = append(vd.Actors, vd.SecondaryActors...)
    }
    if v := str("actors"); v != "" {
        extra := splitActors(v)
        vd.Actors = append(vd.Actors, extra...)
    }
    if v := str("studio"); v != "" {
        vd.Studio = v
    }
    if v := str("line"); v != "" {
        vd.Line = v
    }
    if v := str("title"); v != "" {
        vd.Title = v
    }
    if v := str("scene_title"); v != "" {
        vd.SceneTitle = v
    }
    if v := str("movie_title"); v != "" {
        vd.MovieTitle = v
    }
    if v := str("movie_series"); v != "" {
        vd.MovieSeries = v
    }
    if v := str("date_released"); v != "" {
        vd.DateReleased = v
    }
    if v := str("source_id"); v != "" {
        vd.SourceID = v
    }
    if v := str("dvd_code"); v != "" {
        vd.DVDCode = v
    }

    // year (int) → DateReleased if date_released not already set
    if vd.DateReleased == "" {
        if y, ok := parsed["year"]; ok {
            switch yv := y.(type) {
            case int:
                vd.DateReleased = fmt.Sprintf("%d", yv)
            case string:
                vd.DateReleased = yv
            }
        }
    }

    if sn, ok := parsed["scene_number"]; ok {
        switch snv := sn.(type) {
        case int:
            vd.SceneNumber = snv
        }
    }

    // Deduplicate Actors
    seen := map[string]bool{}
    unique := vd.Actors[:0]
    for _, a := range vd.Actors {
        if !seen[a] {
            seen[a] = true
            unique = append(unique, a)
        }
    }
    vd.Actors = unique
}

// GetFileMetadata parses filename metadata and optionally loads the sidecar
// JSON for a video file. It sets vd.Path, vd.Filename, vd.TagsFromFilename,
// and all fields that ParseFilename/ApplySidecarToVideoData can populate.
// The caller is responsible for setting vd.PathRelative and calling
// ExtractPathTags + RebuildTags afterwards.
func GetFileMetadata(fullPath string, vd *schemas.VideoData, parser *string_parser.StringParser, readJSON bool) {
    vd.Path = fullPath
    vd.Filename = filepath.Base(fullPath)
    ext := filepath.Ext(fullPath)
    pathNoExt := strings.TrimSuffix(filepath.ToSlash(fullPath), ext)
    tags, cleanPath := ExtractTags(pathNoExt)
    vd.TagsFromFilename = tags
    clearFilenameFields(vd)
    PopulateFromParseResult(vd, ParseFilename(cleanPath, parser))
    if readJSON {
        sidecarID := vd.SourceID
        if sidecarID == "" {
            sidecarID = vd.DVDCode
        }
        if files := FindSidecarFiles(fullPath, sidecarID); len(files) > 0 {
            vd.TagsFromJSON, vd.Views, vd.Likes, vd.Metadata = nil, 0, 0, nil
            ApplySidecarToVideoData(vd, MergeSidecarFiles(files))
        }
    }
}

// RebuildTags sets vd.Tags to the deduplicated union of TagsFromFilename,
// TagsFromPath, and TagsFromJSON (in that priority order).
func RebuildTags(vd *schemas.VideoData) {
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

// ExtractPathTags derives tags from intermediate directory names in the
// relative path (everything between collection root and the filename).
// Excludes names that are already known as actors, studio, or line.
func ExtractPathTags(vd *schemas.VideoData) []string {
    rel := filepath.ToSlash(vd.PathRelative)
    // strip filename from relative path
    dir := rel
    if idx := strings.LastIndex(rel, "/"); idx >= 0 {
        dir = rel[:idx]
    } else {
        return nil
    }

    ignore := map[string]bool{}
    for _, a := range vd.Actors {
        ignore[strings.ToLower(a)] = true
    }
    for _, a := range vd.PrimaryActors {
        ignore[strings.ToLower(a)] = true
    }
    if vd.Studio != "" {
        ignore[strings.ToLower(vd.Studio)] = true
    }
    if vd.Line != "" {
        ignore[strings.ToLower(vd.Line)] = true
    }

    var tags []string
    for part := range strings.SplitSeq(dir, "/") {
        part = strings.TrimSpace(part)
        if part == "" {
            continue
        }
        partTags, partClean := ExtractTags(part)
        tags = append(tags, partTags...)
        partClean = strings.TrimSpace(partClean)
        if partClean != "" && !ignore[strings.ToLower(partClean)] {
            tags = append(tags, partClean)
        }
    }
    return tags
}
