import ctypes
import os
from pathlib import Path
from django.http import JsonResponse

# 1. DEFINE THE DIRECTORY (Fixes the NameError)
# This finds the 'engine' folder where this views.py file lives
MODULE_DIR = Path(__file__).resolve().parent

# 2. LOCATE THE SHARED LIBRARY
# This points to the .so file inside your 'login' sub-folder
lib_path = str(MODULE_DIR / "login" / "distance_engine.so")

# 3. DEFINE THE "CONTRACT" STRUCT
# This must match the Go struct exactly to handle results and errors safely
class DistanceResult(ctypes.Structure):
    _fields_ = [
        ("Value", ctypes.c_double),
        ("ErrorMessage", ctypes.c_char_p) # Maps to Go's *C.char
    ]

# 4. LOAD THE LIBRARY
try:
    lib = ctypes.CDLL(lib_path)
    
    # Define the Go function's input and output types
    lib.CalculateDistance.argtypes = [
        ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double
    ]
    lib.CalculateDistance.restype = DistanceResult

except OSError as e:
    # This prevents the server from crashing if the .so is missing, 
    # instead it logs the error to your console.
    print(f"\n--- CRITICAL ENGINE ERROR ---")
    print(f"Could not find Go library at: {lib_path}")
    print(f"Check if the file is in engine/login/distance_engine.so")
    print(f"-----------------------------\n")
    lib = None

def calculate_view(request):
    """
    API Endpoint: /api/calculate/?lat1=6.5&lon1=3.3&lat2=9.0&lon2=8.6
    """
    if lib is None:
        return JsonResponse({
            "status": "error", 
            "message": "Go Engine not loaded. Check server logs."
        }, status=500)

    try:
        # Get coordinates from the URL parameters
        lat1 = float(request.GET.get('lat1', 0))
        lon1 = float(request.GET.get('lon1', 0))
        lat2 = float(request.GET.get('lat2', 0))
        lon2 = float(request.GET.get('lon2', 0))

        # 5. CALL THE GO ENGINE
        # This calls the high-performance Go logic
        go_response = lib.CalculateDistance(lat1, lon1, lat2, lon2)

        # 6. HANDLE ERRORS FROM GO
        if go_response.ErrorMessage:
            error_msg = go_response.ErrorMessage.decode('utf-8')
            return JsonResponse({"status": "error", "message": error_msg}, status=400)

        # 7. RETURN THE RESULT
        return JsonResponse({
            "status": "success",
            "runtime": "Polyglot (Django + Go Shared Library)",
            "distance_km": round(go_response.Value, 2)
        })

    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid coordinates"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)