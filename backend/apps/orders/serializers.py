from rest_framework import serializers
from apps.offers.models import OfferDetail
from .models import Order

# Serializer für die Order-Count-Response
class OrderCountResponseSerializer(serializers.Serializer):
    order_count = serializers.IntegerField()

# PATCH-Request-Serializer für Status-Update
class OrderStatusUpdateRequestSerializer(serializers.Serializer):
    status = serializers.CharField(required=True)

# PATCH-Response-Serializer (eigenständig, keine Vererbung von OrderListSerializer)
class OrderStatusUpdateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer_user = serializers.IntegerField()
    business_user = serializers.IntegerField()
    title = serializers.CharField()
    revisions = serializers.IntegerField()
    delivery_time_in_days = serializers.IntegerField()
    price = serializers.FloatField()
    features = serializers.ListField(child=serializers.CharField())
    offer_type = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class OrderCreateRequestSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField(required=True)

class OrderListSerializer(serializers.ModelSerializer):
    def get_offer_detail(self, obj):
       
        if hasattr(obj, 'offer_detail_id') and obj.offer_detail_id:
            try:
                return OfferDetail.objects.get(id=obj.offer_detail_id)
            except OfferDetail.DoesNotExist:
                return None
        elif hasattr(obj, 'offer_id') and obj.offer_id:
            return OfferDetail.objects.filter(offer_id=obj.offer_id).first()
        elif hasattr(obj, 'offer') and obj.offer:
            return OfferDetail.objects.filter(offer=obj.offer).first()
        return None
    offer_type = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
    customer_user = serializers.PrimaryKeyRelatedField(source='customer', read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(source='business', read_only=True)
    title = serializers.SerializerMethodField()
    revisions = serializers.SerializerMethodField()
    delivery_time_in_days = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    def get_title(self, obj):
        offer_detail = self.get_offer_detail(obj)
        return offer_detail.title if offer_detail else None

    def get_revisions(self, obj):
        offer_detail = self.get_offer_detail(obj)
        return offer_detail.revisions if offer_detail else None

    def get_delivery_time_in_days(self, obj):
        offer_detail = self.get_offer_detail(obj)
        return offer_detail.delivery_time_in_days if offer_detail else None

    def get_price(self, obj):
        offer_detail = self.get_offer_detail(obj)
        return offer_detail.price if offer_detail else None

    def get_features(self, obj):
        offer_detail = self.get_offer_detail(obj)
        if offer_detail and hasattr(offer_detail, 'features'):
            return offer_detail.features
        return []

    def get_offer_type(self, obj):
        offer_detail = self.get_offer_detail(obj)
        return offer_detail.offer_type if offer_detail else None

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        offer_detail_id = request.data.get('offer_detail_id') if request else None

        # Set customer
        validated_data['customer'] = user

        # Wenn offer_detail_id vorhanden, hole OfferDetail und setze offer, business, total_price
        if offer_detail_id:
            from apps.offers.models import OfferDetail
            try:
                offer_detail = OfferDetail.objects.select_related('offer', 'offer__business_user').get(id=offer_detail_id)
            except OfferDetail.DoesNotExist:
                raise serializers.ValidationError({'offer_detail_id': 'Ungültige offer_detail_id.'})
            offer = offer_detail.offer
            validated_data['offer'] = offer
            validated_data['business'] = offer.business_user
            validated_data['total_price'] = offer_detail.price
        else:
            offer = validated_data.get('offer')
            if offer:
                validated_data['business'] = offer.business_user
                validated_data['total_price'] = offer.price
        return super().create(validated_data)

class OrderCreateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer_user = serializers.IntegerField()
    business_user = serializers.IntegerField()
    title = serializers.CharField()
    revisions = serializers.IntegerField()
    delivery_time_in_days = serializers.IntegerField()
    price = serializers.FloatField()
    features = serializers.ListField(child=serializers.CharField())
    offer_type = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()