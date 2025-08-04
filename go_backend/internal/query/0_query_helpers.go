package query

import (
	"math/rand"
	"strings"
)

// filterSliceFunc
func filterSliceFunc[S any](list []S, rule func(S) bool) []S {
	filt := []S{}
	for _, x := range list {
		if rule(x) {
			filt = append(filt, x)
		}
	}
	return filt
}

// getSubSliceSafe slices a slice safely
func getSubSliceSafe[S any](slic []S, start int, end int) []S {
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


// seededShuffle_Perm uses rand.Perm() to shuffle a list
func seededShuffle_Perm[T any](list []T, seed int64) []T {
	r := rand.New(rand.NewSource(seed))
	shuffled := make([]T, len(list))
	perm := r.Perm(len(list))
	for i1, i2 := range perm {
		shuffled[i1] = list[i2]
	}
	return shuffled
}


