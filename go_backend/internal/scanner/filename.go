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

// ExtractTags scans the filename stem from right to left, consuming trailing
// space-delimited tokens that look like "#Word" where Word is not purely numeric.
// Returns the tags in their original left-to-right order, and the stem with
// those tokens stripped from the right.
func ExtractTags(stem string) (tags []string, cleanedStem string) {
    tokens := strings.Fields(stem)
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
        tags = append(tags, tok[1:]) // strip leading '#'
    }
    cleanedStem = strings.Join(tokens[:cutAt], " ")
    return tags, cleanedStem
}

// ParseFilename tries to extract structured metadata from the path string
// (relative parent dirs + cleaned filename stem, no extension, no tags).
// Returns an empty map if no format matched — that is not an error.
func ParseFilename(relPathStem string, formats []string) map[string]any {
    if len(formats) == 0 || relPathStem == "" {
        return map[string]any{}
    }
    parser := string_parser.NewStringParserFromList(formats)
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
        for _, part := range regexp.MustCompile(`[,/]`).Split(s, -1) {
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
    for _, part := range strings.Split(dir, "/") {
        part = strings.TrimSpace(part)
        if part == "" {
            continue
        }
        if !ignore[strings.ToLower(part)] {
            tags = append(tags, part)
        }
    }
    return tags
}
