package db

import (
	"cpv_backend/internal/schemas"
	"fmt"
	"sync"
	"time"
)

var (
	cachedVideos map[string]schemas.VideoData
	cacheTime time.Time // time when cache was created
	cacheLastAccess time.Time
	cacheMutex sync.Mutex
)

func GetCachedVideos(db_path string, cache_base_timeout int, cache_access_timeout int) (map[string]schemas.VideoData, error) {

	mpfil := map[string]schemas.VideoData{}
	
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
	
	// Get from db
	mp, err := ReadSerializedMapFromTable[schemas.VideoData](db_path, "videos")
	if err != nil {
		return mp, err
	}

	for hsh, vd := range mp {
		if vd.IsLinked {
			mpfil[hsh] = vd
		}
	}

	cachedVideos = mp
    cacheTime = time.Now()
	cacheLastAccess = time.Now()
	
	return mpfil, nil

}
