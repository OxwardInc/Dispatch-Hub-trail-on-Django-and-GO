package main

/*
#include <stdlib.h>
// 1. Define the struct in C so Go knows exactly how to export it
typedef struct {
    double Value;
    char* ErrorMessage;
} DistanceResult;
*/
import "C"
import (
    "math" // This imports the Go math library
    "unsafe"
)

//export CalculateDistance
func CalculateDistance(lat1, lon1, lat2, lon2 float64) C.DistanceResult {
	const EarthRadiusKm = 6371.0

	// Convert degrees to radians
	toRad := func(deg float64) float64 { return deg * math.Pi / 180.0 }
	
	dLat := toRad(lat2 - lat1)
	dLon := toRad(lon2 - lon1)
	
	lat1Rad := toRad(lat1)
	lat2Rad := toRad(lat2)

	// Haversine formula
	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Cos(lat1Rad)*math.Cos(lat2Rad)*
			math.Sin(dLon/2)*math.Sin(dLon/2)
	
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	distance := EarthRadiusKm * c

	return C.DistanceResult{
		Value:        C.double(distance),
		ErrorMessage: nil,
	}
}

//export FreeString
func FreeString(s *C.char) {
	C.free(unsafe.Pointer(s))
}

func main() {}