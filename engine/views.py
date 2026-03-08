import ctypes
import os
from pathlib import Path
from django.http import JsonResponse

# 1. DEFINE THE DIRECTORY
# This finds the directory where views.py lives (the 'engine' folder)
MODULE_DIR = Path(__file__).resolve().parent

# 2. BUILD THE PATH TO THE GO LIBRARY
# We point specifically to the 'login' folder shown in your file structure
lib_path = str(MODULE_DIR / "login" / "distance_engine.so")

# 3. DEFINE THE GO "CONTRACT" (The Result Struct)
# Since Go cannot return an 'error' type to C, we use this structure
class DistanceResult(ctypes.Structure):
    _fields_ = [
        ("Value", ctypes.c_double),
        ("ErrorMessage", ctypes.c_char_p)  # maps to Go's *C.char
    ]

try:
    # 4. LOAD THE LIBRARY
    lib = ctypes.CDLL(lib_path)

    # 5. DEFINE FUNCTION SIGNATURES
    lib.CalculateDistance.argtypes = [
        ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double
    ]
    lib.CalculateDistance.restype = DistanceResult

except OSError as e:
    # This will catch issues like missing .so files or architecture mismatches
    print(f"CRITICAL ERROR: Could not find Go library at {lib_path}")
    lib = None

def calculate_view(request):
    """
    API Endpoint: /api/calculate/?lat1=10&lon1=20&lat2=30&lon2=40
    Calculates distance using the Go-compiled shared library.
    """
    if not lib:
        return JsonResponse({"status": "error", "message": "Go Engine not loaded"}, status=500)

    try:
        # Get coordinates from the URL parameters
        lat1 = float(request.GET.get('lat1', 0))
        lon1 = float(request.GET.get('lon1', 0))
        lat2 = float(request.GET.get('lat2', 0))
        lon2 = float(request.GET.get('lon2', 0))

        # 6. CALL THE GO FUNCTION
        # This returns the struct containing both the value and any error message
        go_response = lib.CalculateDistance(lat1, lon1, lat2, lon2)

        # 7. CHECK FOR ERRORS RETURNED BY GO
        if go_response.ErrorMessage:
            error_msg = go_response.ErrorMessage.decode('utf-8')
            return JsonResponse({"status": "error", "message": error_msg}, status=400)

        return JsonResponse({
            "status": "success",
            "runtime": "Polyglot (Python + Go)",
            "distance": go_response.Value
        })

    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid coordinate format"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)