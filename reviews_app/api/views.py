from rest_framework import status, viewsets, permissions
from rest_framework.response import Response

from ..models import Review
from .serializers import ReviewSerializer
from offers_app.models import Offer
from .permissions import IsReviewerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Reviews"""
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response({'detail': 'Nicht gefunden. Es wurde keine Bewertung mit der angegebenen ID gefunden.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Unauthorized. Der Benutzer muss authentifiziert sein.'}, status=status.HTTP_401_UNAUTHORIZED)

        if instance.reviewer != user:
            return Response({'detail': 'Forbidden. Der Benutzer ist nicht berechtigt, diese Bewertung zu löschen.'}, status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        """Allows only the creator to edit rating and description (comment)"""
        try:
            instance = self.get_object()
        except Exception:
            return Response({'detail': 'Nicht gefunden. Es wurde keine Bewertung mit der angegebenen ID gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        if not user.is_authenticated:
            return Response({'detail': 'Unauthorized. Der Benutzer muss authentifiziert sein.'}, status=status.HTTP_401_UNAUTHORIZED)

        if instance.reviewer != user:
            return Response({'detail': 'Forbidden. Der Benutzer ist nicht berechtigt, diese Bewertung zu bearbeiten.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        allowed_fields = {'rating', 'description'}
        update_data = {}
        errors = {}

        for field in allowed_fields:
            if field in data:
                if field == 'rating':
                    try:
                        rating = int(data['rating'])
                        if rating < 1 or rating > 5:
                            errors['rating'] = 'Rating muss zwischen 1 und 5 liegen.'
                        else:
                            update_data['rating'] = rating
                    except (ValueError, TypeError):
                        errors['rating'] = 'Rating muss eine Zahl sein.'
                elif field == 'description':
                    update_data['comment'] = data['description']

        if errors:
            return Response({'detail': 'Bad Request. Der Anfrage-Body enthält ungültige Daten.'}, status=status.HTTP_400_BAD_REQUEST)

        if not update_data:
            return Response({'detail': 'Es muss mindestens rating oder description gesetzt werden.'}, status=status.HTTP_400_BAD_REQUEST)

        for attr, value in update_data.items():
            setattr(instance, attr, value)
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
    filterset_fields = ['offer__business_user', 'reviewer', 'rating']
    ordering_fields = ['rating', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        if business_user_id:
            queryset = queryset.filter(offer__business_user=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer=reviewer_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Override create to handle duplicate reviews and permissions"""
        user = request.user

        if not user.is_authenticated:
            return Response({'detail': 'Der Benutzer muss authentifiziert sein und ein Kundenprofil besitzen.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not hasattr(user, 'customer_profile'):
            return Response({'detail': 'Der Benutzer muss authentifiziert sein und ein Kundenprofil besitzen.'}, status=status.HTTP_401_UNAUTHORIZED)

        if hasattr(user, 'businessprofile'):
            return Response({'detail': 'Mit einem Geschäftsprofil dürfen keine Bewertungen abgegeben werden.'}, status=status.HTTP_403_FORBIDDEN)

        business_user_id = request.data.get('business_user')
        rating = request.data.get('rating')
        description = request.data.get('description')
        if not business_user_id or not rating or not description:
            return Response({'detail': 'business_user, rating und description sind erforderlich.'}, status=status.HTTP_400_BAD_REQUEST)

        offer = Offer.objects.filter(business_user_id=business_user_id).first()
        if not offer:
            return Response({'detail': 'Kein Angebot für diesen Geschäftsbenutzer gefunden.'}, status=status.HTTP_400_BAD_REQUEST)

        if Review.objects.filter(offer__business_user_id=business_user_id, reviewer=user).exists():
            return Response({'detail': 'Der Benutzer hat möglicherweise bereits eine Bewertung für das gleiche Geschäftsprofil abgegeben.'}, status=status.HTTP_400_BAD_REQUEST)

        review = Review.objects.create(
            offer=offer,
            reviewer=user,
            rating=rating,
            comment=description
        )
        serializer = self.get_serializer(review)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
