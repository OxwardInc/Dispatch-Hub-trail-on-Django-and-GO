import ctypes
from pathlib import Path
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# 1. DEFINE DIRECTORY & PATH
MODULE_DIR = Path(__file__).resolve().parent
lib_path = str(MODULE_DIR / "login" / "distance_engine.so")

# 2. DEFINE CONTRACT (The Go Struct)
class DistanceResult(ctypes.Structure):
    _fields_ = [
        ("Value", ctypes.c_double),
        ("ErrorMessage", ctypes.c_char_p)
    ]

# 3. LOAD LIBRARY (Initialize once on startup)
try:
    lib = ctypes.CDLL(lib_path)
    lib.CalculateDistance.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.CalculateDistance.restype = DistanceResult
except OSError as e:
    lib = None

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # The Gatekeeper
def calculate_view(request):
    """
    API: /api/calculate/?lat1=X&lon1=Y&lat2=A&lon2=B
    """
    if lib is None:
        return JsonResponse({"status": "error", "message": "Go Engine unavailable"}, status=500)

    # 4. INPUT VALIDATION
    # We check if keys exist before converting them
    params = ['lat1', 'lon1', 'lat2', 'lon2']
    try:
        data = {p: float(request.GET.get(p)) for p in params}
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error", 
            "message": f"Missing or invalid parameters. Expected: {params}"
        }, status=400)

    # 5. EXECUTE GO LOGIC
    go_response = lib.CalculateDistance(
        data['lat1'], data['lon1'], data['lat2'], data['lon2']
    )

    # 6. ERROR HANDLING
    if go_response.ErrorMessage:
        error_msg = go_response.ErrorMessage.decode('utf-8')
        return JsonResponse({"status": "error", "message": error_msg}, status=400)

    # 7. SUCCESS RESPONSE
    return JsonResponse({
        "status": "success",
        "data": {
            "lat1": data['lat1'],
            "lon1": data['lon1'],
            "distance_km": round(go_response.Value, 2)
        }
    })