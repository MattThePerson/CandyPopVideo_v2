package query

import (
    "strings"

    "cpv_backend/internal/config"
    "cpv_backend/internal/schemas"
)

// ApplyGlobalFilter narrows vids to those matching the active content filter.
// Returns vids unchanged (fast path) when all filter arrays are empty.
func ApplyGlobalFilter(vids []schemas.VideoData, f config.GlobalFilter) []schemas.VideoData {
    if len(f.CollectionsInclude) == 0 && len(f.CollectionsExclude) == 0 &&
        len(f.StudiosInclude) == 0 && len(f.StudiosExclude) == 0 &&
        len(f.ActorsInclude) == 0 && len(f.ActorsExclude) == 0 {
        return vids
    }

    // Treat empty mode string as "include" (backward-compat with old state.json)
    collMode   := f.CollectionsMode; if collMode == ""   { collMode = "include" }
    studioMode := f.StudiosMode;     if studioMode == "" { studioMode = "include" }

    return filterSliceFunc(vids, func(vd schemas.VideoData) bool {
        // Collections: OR across include list, or AND-NOT across exclude list
        if collMode == "include" && len(f.CollectionsInclude) > 0 {
            if !anyEqualFold(vd.Collection, f.CollectionsInclude) {
                return false
            }
        }
        if collMode == "exclude" && len(f.CollectionsExclude) > 0 {
            if anyEqualFold(vd.Collection, f.CollectionsExclude) {
                return false
            }
        }

        // Studios: match Studio field OR Line field
        if studioMode == "include" && len(f.StudiosInclude) > 0 {
            if !anyEqualFold(vd.Studio, f.StudiosInclude) && !anyEqualFold(vd.Line, f.StudiosInclude) {
                return false
            }
        }
        if studioMode == "exclude" && len(f.StudiosExclude) > 0 {
            if anyEqualFold(vd.Studio, f.StudiosExclude) || anyEqualFold(vd.Line, f.StudiosExclude) {
                return false
            }
        }

        // Actors include: AND — video must have every required actor
        for _, req := range f.ActorsInclude {
            if !actorInVideo(req, vd.Actors) {
                return false
            }
        }

        // Actors exclude: AND-NOT — video must have none of the excluded actors
        for _, excl := range f.ActorsExclude {
            if actorInVideo(excl, vd.Actors) {
                return false
            }
        }

        return true
    })
}

func anyEqualFold(val string, list []string) bool {
    for _, s := range list {
        if strings.EqualFold(val, s) {
            return true
        }
    }
    return false
}

func actorInVideo(actor string, actors []string) bool {
    for _, a := range actors {
        if strings.EqualFold(a, actor) {
            return true
        }
    }
    return false
}
