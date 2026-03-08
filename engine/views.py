import ctypes
from pathlib import Path
from django.http import JsonResponse
from django.contrib.auth.models import User

# DRF & JWT Imports
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- 1. GO ENGINE SETUP (Original Logic) ---
MODULE_DIR = Path(__file__).resolve().parent
lib_path = str(MODULE_DIR / "login" / "distance_engine.so")

class DistanceResult(ctypes.Structure):
    _fields_ = [
        ("Value", ctypes.c_double),
        ("ErrorMessage", ctypes.c_char_p)
    ]

try:
    lib = ctypes.CDLL(lib_path)
    lib.CalculateDistance.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.CalculateDistance.restype = DistanceResult
except OSError:
    lib = None


# --- 2. AUTHENTICATION VIEWS (New Logic) ---

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT payload to ensure 'username' and 'user_id' 
    are easily accessible by the Go server and Frontend.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims for the Go Signaling Server
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    """
    The Login Endpoint: Returns the Access and Refresh tokens.
    """
    serializer_class = MyTokenObtainPairSerializer

class SignupView(generics.CreateAPIView):
    """
    The Signup Endpoint: Creates a new user in the Django Database.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


# --- 3. LOGISTICS VIEWS (Original Logic) ---

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def calculate_view(request):
    """
    Existing logic to call the Go .so library for distance math.
    """
    if lib is None:
        return JsonResponse({"status": "error", "message": "Go Engine unavailable"}, status=500)

    params = ['lat1', 'lon1', 'lat2', 'lon2']
    try:
        data = {p: float(request.GET.get(p)) for p in params}
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error", 
            "message": f"Missing or invalid parameters. Expected: {params}"
        }, status=400)

    go_response = lib.CalculateDistance(
        data['lat1'], data['lon1'], data['lat2'], data['lon2']
    )

    if go_response.ErrorMessage:
        error_msg = go_response.ErrorMessage.decode('utf-8')
        return JsonResponse({"status": "error", "message": error_msg}, status=400)

    return JsonResponse({
        "status": "success",
        "data": {
            "lat1": data['lat1'],
            "lon1": data['lon1'],
            "distance_km": round(go_response.Value, 2)
        }
    })