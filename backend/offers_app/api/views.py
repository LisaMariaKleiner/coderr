from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferCompactSerializer, OfferListSerializer, OfferUpdateSerializer, OfferRetrieveFullSerializer, OfferDetailSerializer


class OfferDetailRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny] 


class IsBusinessUserOrReadOnly(permissions.BasePermission):
    """Custom permission: Only business users can create/edit offers"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.user_type == 'business'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.business_user == request.user


class OfferViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        """get a single offer with full details"""
        offer = self.get_object()
        serializer = OfferRetrieveFullSerializer(offer, context={'request': request})
        return Response(serializer.data)
    
    """ViewSet for Offers"""
    queryset = Offer.objects.filter(is_active=True)
    permission_classes = [IsBusinessUserOrReadOnly]
    filterset_fields = ['business_user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']


    def get_serializer_class(self):
        if self.action == 'list':
            return OfferListSerializer
        if self.action == 'retrieve':
            return OfferRetrieveFullSerializer
        if self.action in ['partial_update', 'update']:
            return OfferUpdateSerializer
        if self.action == 'create':
            return OfferSerializer
        return OfferSerializer

    def partial_update(self, request, *args, **kwargs):
        """Patch an offer and return compact format"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        offer = serializer.instance
        details = offer.details.all()
        details_list = [
            {
                'id': d.id,
                'title': d.title,
                'revisions': d.revisions,
                'delivery_time_in_days': d.delivery_time_in_days,
                'price': float(d.price),
                'features': d.features,
                'offer_type': d.offer_type
            }
            for d in details
        ]
        data = {
            'id': offer.id,
            'title': offer.title,
            'image': offer.image.url if offer.image else None,
            'description': offer.description,
            'details': details_list
        }
        return Response(data)

    def update(self, request, *args, **kwargs):
        """Put an offer and return compact format"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        offer = serializer.instance
        details = offer.details.all()
        details_list = [
            {
                'id': d.id,
                'title': d.title,
                'revisions': d.revisions,
                'delivery_time_in_days': d.delivery_time_in_days,
                'price': float(d.price),
                'features': d.features,
                'offer_type': d.offer_type
            }
            for d in details
        ]
        data = {
            'id': offer.id,
            'title': offer.title,
            'image': offer.image.url if offer.image else None,
            'description': offer.description,
            'details': details_list
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        """Create a new Offer along with its details"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        offer = serializer.instance
        details = offer.details.all()
        details_list = [
            {
                'id': d.id,
                'title': d.title,
                'revisions': d.revisions,
                'delivery_time_in_days': d.delivery_time_in_days,
                'price': float(d.price),
                'features': d.features,
                'offer_type': d.offer_type
            }
            for d in details
        ]
        data = {
            'id': offer.id,
            'title': offer.title,
            'image': offer.image.url if offer.image else None,
            'description': offer.description,
            'details': details_list
        }
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=201, headers=headers)

    @action(detail=False, methods=['get'])
    def my_offers(self, request):
        """Get offers created by the current user"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=401)
        offers = Offer.objects.filter(business_user=request.user)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)
