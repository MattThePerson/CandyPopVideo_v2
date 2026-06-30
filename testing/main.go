package main

import (
    "fmt"
    "math"
)

// getLogAdjustedPoints returns the value of the function a * ln(b * x + 1)
func getLogAdjustedPoints(x float64, a float64, b float64) float64 {
    return a * math.Log(b * x + 1)
}

func main() {

    // points += getLogAdjustedPoints( i.Viewtime, 7.0, 0.129 )
    // vt :=
}
