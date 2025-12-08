from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Order
from .serializers import OrderCountResponseSerializer

class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        User = get_user_model()
        try:
            business_user = User.objects.get(id=business_user_id, user_type='business')
        except User.DoesNotExist:
            return Response({'detail': 'Kein Geschäftsnutzer mit dieser ID gefunden.'}, status=404)
        count = Order.objects.filter(business=business_user, status='in_progress').count()
        serializer = OrderCountResponseSerializer({'order_count': count})
        return Response(serializer.data, status=200)
