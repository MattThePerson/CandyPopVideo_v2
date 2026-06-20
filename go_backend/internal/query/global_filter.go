package query

import (
    "strings"

    "cpv_backend/internal/config"
    "cpv_backend/internal/schemas"
)

// ApplyGlobalFilter narrows vids to those matching the active content filter.
// Empty fields are "all". Returns vids unchanged when no filter is active.
func ApplyGlobalFilter(vids []schemas.VideoData, f config.GlobalFilter) []schemas.VideoData {
    if f.Collection == "" && f.Studio == "" && len(f.Actors) == 0 {
        return vids
    }
    return filterSliceFunc(vids, func(vd schemas.VideoData) bool {
        if f.Collection != "" && !strings.EqualFold(vd.Collection, f.Collection) {
            return false
        }
        if f.Studio != "" && !strings.EqualFold(vd.Studio, f.Studio) && !strings.EqualFold(vd.Line, f.Studio) {
            return false
        }
        for _, actor := range f.Actors {
            found := false
            for _, va := range vd.Actors {
                if strings.EqualFold(va, actor) {
                    found = true
                    break
                }
            }
            if !found {
                return false
            }
        }
        return true
    })
}
