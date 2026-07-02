package main

import (
    "fmt"
    "os"

    "cpv_backend/internal/scanner"
)

func main() {
    if len(os.Args) < 2 {
        fmt.Fprintln(os.Stderr, "usage: vidhash <file>")
        os.Exit(1)
    }

    hash, err := scanner.HashVideoFile(os.Args[1])
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }

    fmt.Println(hash)
}
