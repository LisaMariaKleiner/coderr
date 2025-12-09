
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer, RegistrationSerializer

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """Login endpoint that returns user token and basic info"""
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type,
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {'detail': 'Internal server error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        """Creates a new user (customer or business)"""
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token = Token.objects.create(user=user)
                return Response({
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.id,
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {'detail': 'Internal server error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout endpoint that deletes the user's token"""
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)
