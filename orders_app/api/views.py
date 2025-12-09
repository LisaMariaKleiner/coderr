from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Order
from .serializers import (
    OrderListSerializer, OrderCreateResponseSerializer, OrderCreateRequestSerializer,
    OrderStatusUpdateRequestSerializer, OrderStatusUpdateResponseSerializer, OrderCountResponseSerializer
)
from offers_app.models import OfferDetail


class OrderViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'], url_path='order-count/(?P<business_user_id>[^/.]+)')
    def order_count(self, request, business_user_id=None):
        """Get the count of orders for a specific business user with status 'in_progress'"""
        User = get_user_model()
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=401)
        try:
            business_user = User.objects.get(id=business_user_id, user_type='business')
        except User.DoesNotExist:
            return Response({'detail': 'Kein Geschäftsnutzer mit dieser ID gefunden.'}, status=404)
        count = Order.objects.filter(business=business_user, status='in_progress').count()
        serializer = OrderCountResponseSerializer({'order_count': count})
        return Response(serializer.data, status=200)
    def destroy(self, request, *args, **kwargs):
        """DELETE an order (only for admin users)"""
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Benutzer ist nicht authentifiziert.'}, status=401)
        if not user.is_staff:
            return Response({'detail': 'Benutzer hat keine Berechtigung, die Bestellung zu löschen.'}, status=403)
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            return Response({'detail': 'Die angegebene Bestellung wurde nicht gefunden.'}, status=404)
        order.delete()
        return Response(None, status=204)
    

    """ViewSet for Orders"""
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateRequestSerializer
        return OrderListSerializer

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Admins see all orders, business users see their orders, customers see their orders"""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        if user.user_type == 'business':
            return Order.objects.filter(business=user)
        return Order.objects.filter(customer=user)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get orders for current user"""
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """PATCH /api/orders/{id}/ – State of an order update (only by business user)"""
        order = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=401)
        if user != order.business:
            return Response({'detail': 'Only the business user can update status.'}, status=403)
        serializer = OrderStatusUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_value = serializer.validated_data['status']
        if status_value not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Invalid status.'}, status=400)

        order.status = status_value
        order.save()

        offer_detail = None
        from offers_app.models import OfferDetail
        if hasattr(order, 'offer_id') and order.offer_id:
            offer_detail = OfferDetail.objects.filter(offer_id=order.offer_id).first()
        elif hasattr(order, 'offer') and order.offer:
            offer_detail = OfferDetail.objects.filter(offer=order.offer).first()

        response_data = {
            'id': order.id,
            'customer_user': order.customer.id,
            'business_user': order.business.id,
            'title': offer_detail.title if offer_detail else '',
            'revisions': offer_detail.revisions if offer_detail else None,
            'delivery_time_in_days': offer_detail.delivery_time_in_days if offer_detail else None,
            'price': float(offer_detail.price) if offer_detail else None,
            'features': offer_detail.features if offer_detail else [],
            'offer_type': offer_detail.offer_type if offer_detail else '',
            'status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        }
        response_serializer = OrderStatusUpdateResponseSerializer(response_data)
        return Response(response_serializer.data, status=200)

    def create(self, request, *args, **kwargs):
        """POST /orders/ – Create a new order (only for customer users)"""
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=401)
        if user.user_type != 'customer':
            return Response({'detail': 'Only customers can create orders.'}, status=403)

        serializer = OrderCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer_detail_id = serializer.validated_data['offer_detail_id']

        from offers_app.models import OfferDetail
        try:
            offer_detail = OfferDetail.objects.select_related('offer__business_user').get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({'detail': 'OfferDetail not found.'}, status=404)

        offer = offer_detail.offer
        business_user = offer.business_user

        """Create order"""
        order = Order.objects.create(
            customer=user,
            business=business_user,
            offer=offer,
            total_price=offer_detail.price,
            status='in_progress',
        )

        """Save optional fields as notes"""
        notes = f"Order created from OfferDetail: {offer_detail.title}\n"
        notes += f"Revisions: {offer_detail.revisions}, Delivery: {offer_detail.delivery_time_in_days} days\n"
        notes += f"Features: {', '.join(offer_detail.features) if offer_detail.features else ''}\n"
        notes += f"Offer type: {offer_detail.offer_type}"
        order.notes = notes
        order.save()

        response_data = {
            'id': order.id,
            'customer_user': order.customer.id,
            'business_user': order.business.id,
            'title': offer_detail.title,
            'revisions': offer_detail.revisions,
            'delivery_time_in_days': offer_detail.delivery_time_in_days,
            'price': float(offer_detail.price),
            'features': offer_detail.features,
            'offer_type': offer_detail.offer_type,
            'status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        }
        response_serializer = OrderCreateResponseSerializer(response_data)
        return Response(response_serializer.data, status=201)

    @action(detail=False, methods=['post'], url_path='create-from-offer-detail')
    def create_from_offer_detail(self, request):
        """Create a new order based on OfferDetail (only for customer users)"""
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=401)
        if user.user_type != 'customer':
            return Response({'detail': 'Only customers can create orders.'}, status=403)

        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({'detail': "'offer_detail_id' is required."}, status=400)

        try:
            offer_detail = OfferDetail.objects.select_related('offer__business_user').get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({'detail': 'OfferDetail not found.'}, status=404)

        offer = offer_detail.offer
        business_user = offer.business_user

        """Create order"""
        order = Order.objects.create(
            customer=user,
            business=business_user,
            offer=offer,
            total_price=offer_detail.price,
            status='in_progress',
        )

        """Save optional fields as notes"""
        notes = f"Order created from OfferDetail: {offer_detail.title}\n"
        notes += f"Revisions: {offer_detail.revisions}, Delivery: {offer_detail.delivery_time_in_days} days\n"
        notes += f"Features: {', '.join(offer_detail.features) if offer_detail.features else ''}\n"
        notes += f"Offer type: {offer_detail.offer_type}"
        order.notes = notes
        order.save()

        from .serializers import OrderCreateResponseSerializer
        response_data = {
            'id': order.id,
            'customer_user': order.customer.id,
            'business_user': order.business.id,
            'title': offer_detail.title,
            'revisions': offer_detail.revisions,
            'delivery_time_in_days': offer_detail.delivery_time_in_days,
            'price': float(offer_detail.price),
            'features': offer_detail.features,
            'offer_type': offer_detail.offer_type,
            'status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        }
        serializer = OrderCreateResponseSerializer(response_data)
        return Response(serializer.data, status=201)
