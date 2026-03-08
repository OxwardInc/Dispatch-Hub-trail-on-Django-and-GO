package main

import "C"
import "fmt"

//export CalculateDistance
func CalculateDistance(lat1, lon1, lat2, lon2 float64) float64 {
	// A dummy calculation for example purposes
	fmt.Printf("Go Module: Calculating distance between %f and %f\n", lat1, lat2)
	return (lat1 + lon1) - (lat2 + lon2) 
}

func main() {} // Required for compilation 