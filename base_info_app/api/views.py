from django.db import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles_app.models import BusinessProfile
from offers_app.models import Offer
from reviews_app.models import Review

class BaseInfoView(APIView):
    """View to retrieve basic information"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            review_count = Review.objects.count()
            avg_rating = Review.objects.aggregate(models.Avg('rating'))['rating__avg']
            average_rating = round(avg_rating, 1) if avg_rating is not None else 0.0
            business_profile_count = BusinessProfile.objects.count()
            offer_count = Offer.objects.count()

            return Response({
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count,
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Interner Serverfehler."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
