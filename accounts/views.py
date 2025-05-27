from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )

    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def profile_view(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
