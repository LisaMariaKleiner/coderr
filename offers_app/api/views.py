from django_filters import rest_framework as filters

from ..models import Offer, OfferDetail


from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Offer, OfferDetail
from .serializers import (
    OfferSerializer, OfferCompactSerializer, OfferListSerializer, OfferUpdateSerializer,
    OfferRetrieveFullSerializer, OfferDetailSerializer
)
from .permissions import IsBusinessUserOrReadOnly


class OfferFilterSet(filters.FilterSet):
    creator_id = filters.NumberFilter(field_name='business_user__id')
    min_price = filters.NumberFilter(method='filter_min_price')
    def filter_min_price(self, queryset, name, value):
            return queryset.filter(min_price__gte=value)
    max_delivery_time = filters.NumberFilter(field_name='details__delivery_time_in_days', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time', 'business_user']


class OfferDetailRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny] 


class OfferViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        """List offers with pagination support"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """get a single offer with full details"""
        offer = self.get_object()
        serializer = OfferRetrieveFullSerializer(offer, context={'request': request})
        return Response(serializer.data)

    # ViewSet for Offers
    def get_queryset(self):
        from django.db.models import Min
        qs = Offer.objects.filter(is_active=True)
        qs = qs.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        ).filter(min_price__isnull=False, min_delivery_time__isnull=False)
        qs = qs.order_by('-updated_at', 'id')
        return qs
    permission_classes = [permissions.AllowAny]
    filterset_class = OfferFilterSet
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'min_price', 'min_delivery_time']

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
        """Patch an offer and return full offer with all details (wie POST)"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        offer = instance
        details = offer.details.all()
        def price_as_int_or_float(val):
            return int(val) if float(val).is_integer() else float(val)
        details_list = [
            {
                'id': d.id,
                'title': d.title,
                'revisions': d.revisions,
                'delivery_time_in_days': d.delivery_time_in_days,
                'price': price_as_int_or_float(d.price),
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
        def price_as_int_or_float(val):
            return int(val) if float(val).is_integer() else float(val)
        details_list = [
            {
                'id': d.id,
                'title': d.title,
                'revisions': d.revisions,
                'delivery_time_in_days': d.delivery_time_in_days,
                'price': price_as_int_or_float(d.price),
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
        def price_as_int_or_float(val):
            return int(val) if float(val).is_integer() else float(val)
        details_list = [
            {
                'id': d.id,
                'title': d.title,
                'revisions': d.revisions,
                'delivery_time_in_days': d.delivery_time_in_days,
                'price': price_as_int_or_float(d.price),
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
