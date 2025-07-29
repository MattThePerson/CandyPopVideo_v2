package query

import "strings"

func filterSliceFunc[S any](list []S, rule func(S) bool) []S {
	filt := []S{}
	for _, x := range list {
		if rule(x) {
			filt = append(filt, x)
		}
	}
	return filt
}

// sliceSliceSafe slices a slice safely
func sliceSliceSafe[S any](slic []S, start int, end int) []S {
	if end > len(slic) {
		end = len(slic)
	}
	if start >= len(slic) {
		return []S{}
	}
	return slic[start:end]
}

func standardizeString(a string) string {
	a = strings.ToLower(a)
	a = strings.ReplaceAll(a, ".", "")
	return a
}
