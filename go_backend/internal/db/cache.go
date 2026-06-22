package db

import (
	"cpv_backend/internal/schemas"
	"fmt"
	"sync"
	"time"
)

var (
	cachedVideos    map[string]schemas.VideoData
	cacheTime       time.Time
	cacheLastAccess time.Time
	cacheMutex      sync.Mutex
)

var (
	cachedInteractions    map[string]schemas.VideoInteractions
	cacheITime            time.Time
	cacheILastAccess      time.Time
	cacheMutexInteractions sync.Mutex
)

// GetCachedVideos returns a map of all linked videos, deserializing from SQLite
// on cache miss. Only linked videos (is_linked=1) are ever stored or returned.
func GetCachedVideos(db_path string, cache_base_timeout int, cache_access_timeout int) (map[string]schemas.VideoData, error) {

	// Get from cache
	cacheMutex.Lock()
	defer cacheMutex.Unlock()

	baseTimeout :=   time.Since(cacheTime)       > time.Duration(cache_base_timeout)*time.Second
	accessTimeout := time.Since(cacheLastAccess) > time.Duration(cache_access_timeout)*time.Second
	if !(baseTimeout && accessTimeout) && cachedVideos != nil {
		cacheLastAccess = time.Now()
		fmt.Printf("___USING CACHE___ cacheTime: %.2fs  lastAccess: %.2fs\n", time.Since(cacheTime).Seconds(), time.Since(cacheLastAccess).Seconds())
		return cachedVideos, nil
	}

	// Get from db (linked only)
	mp, err := ReadLinkedVideosMap(db_path)
	if err != nil {
		return mp, err
	}

	cachedVideos = mp
	cacheTime = time.Now()
	cacheLastAccess = time.Now()

	return mp, nil

}


// InvalidateCache forces the next GetCachedVideos call to re-read from DB.
func InvalidateCache() {
    cacheMutex.Lock()
    defer cacheMutex.Unlock()
    cachedVideos = nil
    cacheTime = time.Time{}
    cacheLastAccess = time.Time{}
}

// GetCachedInteractions returns all VideoInteractions, deserializing from SQLite
// on cache miss. Uses the same TTL semantics as GetCachedVideos.
func GetCachedInteractions(db_path string, cache_base_timeout int, cache_access_timeout int) (map[string]schemas.VideoInteractions, error) {
    cacheMutexInteractions.Lock()
    defer cacheMutexInteractions.Unlock()

    baseTimeout   := time.Since(cacheITime)        > time.Duration(cache_base_timeout)*time.Second
    accessTimeout := time.Since(cacheILastAccess)  > time.Duration(cache_access_timeout)*time.Second
    if !(baseTimeout && accessTimeout) && cachedInteractions != nil {
        cacheILastAccess = time.Now()
        return cachedInteractions, nil
    }

    mp, err := ReadSerializedMapFromTable[schemas.VideoInteractions](db_path, "interactions")
    if err != nil {
        return mp, err
    }

    cachedInteractions = mp
    cacheITime = time.Now()
    cacheILastAccess = time.Now()

    return mp, nil
}

// InvalidateInteractionsCache forces the next GetCachedInteractions call to re-read from DB.
func InvalidateInteractionsCache() {
    cacheMutexInteractions.Lock()
    defer cacheMutexInteractions.Unlock()
    cachedInteractions = nil
    cacheITime = time.Time{}
    cacheILastAccess = time.Time{}
}

// func GetCachedInteractions(db_path string, cache_base_timeout int, cache_access_timeout int) (map[string]schemas.VideoInteractions, error) {

// 	mpfil := map[string]schemas.VideoInteractions{}

// 	// Get from cache
// 	cacheMutex.Lock()
// 	defer cacheMutex.Unlock()

// 	baseTimeout :=   time.Since(cacheTime)       > time.Duration(cache_base_timeout)*time.Second
// 	accessTimeout := time.Since(cacheLastAccess) > time.Duration(cache_access_timeout)*time.Second
// 	if !(baseTimeout && accessTimeout) && cachedVideos != nil {
// 		cacheLastAccess = time.Now()
// 		fmt.Printf("___USING CACHE___ cacheTime: %.2fs  lastAccess: %.2fs\n", time.Since(cacheTime).Seconds(), time.Since(cacheLastAccess).Seconds())
// 		return cachedVideos, nil
// 	}

// 	// Get from db
// 	mp, err := ReadSerializedMapFromTable[schemas.VideoInteractions](db_path, "videos")
// 	if err != nil {
// 		return mp, err
// 	}

// 	cachedVideos = mp
//     cacheTime = time.Now()
// 	cacheLastAccess = time.Now()

// 	return mpfil, nil

// }
