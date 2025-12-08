from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import User, BusinessProfile, CustomerProfile
from .serializers import (
    UserSerializer, 
    BusinessProfileSerializer, 
    CustomerProfileSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ProfileDetailSerializer,
    BusinessProfileListSerializer,
    CustomerProfileListSerializer
)


class ProfileViewSet(viewsets.ViewSet):
    """
    Combined Profile ViewSet for GET and PATCH operations
    Handles both Business and Customer profiles with unified API
    """
    permission_classes = [IsAuthenticated]
    
    # Explicitly allow GET and PATCH methods
    http_method_names = ['get', 'patch', 'options', 'head']

    def retrieve(self, request, pk=None):
        """
        GET /api/profile/{pk}/
        Returns detailed profile information for a user
        """
        try:
            user = User.objects.get(pk=pk)
            serializer = ProfileDetailSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'detail': 'User profile not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': 'Internal server error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, pk=None):
        """
        PATCH /api/profile/{pk}/
        Updates profile - User can ONLY edit their own profile
        """
        try:
            user = User.objects.get(pk=pk)
            
            # Check if user is updating their own profile
            if request.user.id != user.id:
                return Response(
                    {'detail': 'You do not have permission to edit this profile.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response(
                {'detail': 'User profile not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': 'Internal server error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BusinessProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Business Profiles
    GET /api/profiles/business/
    Returns list of all business users
    """
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all business profiles with user data"""
        return BusinessProfile.objects.select_related('user').all()

    def list(self, request, *args, **kwargs):
        """GET /api/profiles/business/"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': 'Internal server error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's business profile"""
        try:
            profile = BusinessProfile.objects.get(user=request.user)
            serializer = BusinessProfileListSerializer(profile)
            return Response(serializer.data)
        except BusinessProfile.DoesNotExist:
            return Response(
                {'detail': 'Business profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class CustomerProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Customer Profiles
    GET /api/profiles/customer/
    Returns list of all customer users
    """
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all customer profiles with user data"""
        return CustomerProfile.objects.select_related('user').all()

    def list(self, request, *args, **kwargs):
        """GET /api/profiles/customer/"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': 'Internal server error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's customer profile"""
        try:
            profile = CustomerProfile.objects.get(user=request.user)
            serializer = CustomerProfileListSerializer(profile)
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
