package db

import (
	"cpv_backend/internal/schemas"
	"fmt"
	"sync"
	"time"
)

var (
	cachedVideos map[string]schemas.VideoData
	cacheTime time.Time
	cacheMutex sync.Mutex
)

func GetCachedVideos(db_path string, cache_timeout int) (map[string]schemas.VideoData, error) {

	mpfil := map[string]schemas.VideoData{}
	
	// Get from cache
	cacheMutex.Lock()
	defer cacheMutex.Unlock()

	if time.Since(cacheTime) < time.Duration(cache_timeout)*time.Second && cachedVideos != nil {
		fmt.Println("Using cache!!!")
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
	
	return mpfil, nil

}
