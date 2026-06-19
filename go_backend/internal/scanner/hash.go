package scanner

import (
    "crypto/sha256"
    "encoding/hex"
    "io"
    "os"
)

// HashVideoFile computes a stable content hash for a video file.
// Reads three 64 KB chunks (start, middle, end) and feeds them into a single SHA-256 instance.
// See _ref/VIDEO_HASHING.md for the full specification.
func HashVideoFile(path string) (string, error) {
    f, err := os.Open(path)
    if err != nil {
        return "", err
    }
    defer f.Close()

    size, err := f.Seek(0, io.SeekEnd)
    if err != nil {
        return "", err
    }

    const chunk = 64 * 1024
    buf := make([]byte, chunk)
    h := sha256.New()

    for _, off := range []int64{0, size / 2, size - chunk} {
        if off < 0 {
            off = 0
        }
        if _, err := f.Seek(off, io.SeekStart); err != nil {
            return "", err
        }
        n, _ := f.Read(buf)
        h.Write(buf[:n])
    }

    return hex.EncodeToString(h.Sum(nil)), nil
}
