from rest_framework import serializers
from ..models import Offer, OfferDetail

"""Serializers for Offer and OfferDetail models"""
class OfferRetrieveReferenceDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/offerdetails/{obj.id}/')
        return f'/api/offerdetails/{obj.id}/'

"""Serializer for detailed offer retrieval including min price and delivery time"""
class OfferRetrieveFullSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='business_user', read_only=True)
    details = OfferRetrieveReferenceDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time'
        ]

    def get_min_price(self, obj):
        if not obj.details.exists():
            return None
        min_price = min([d.price for d in obj.details.all()])
        return int(min_price) if float(min_price).is_integer() else float(min_price)

    def get_min_delivery_time(self, obj):
        return min([d.delivery_time_in_days for d in obj.details.all()]) if obj.details.exists() else None

"""Serializer for detailed offer retrieval including all detail fields"""
class OfferRetrieveDetailSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

    def get_price(self, obj):
        if obj.price == int(obj.price):
            return int(obj.price)
        return float(obj.price)


"""Serializer for updating OfferDetail"""
class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

"""Serializer for updating Offer along with its details"""
class OfferUpdateSerializer(serializers.ModelSerializer):
    def validate_details(self, value):
        for detail in value:
            if 'offer_type' not in detail or not detail['offer_type']:
                raise serializers.ValidationError("Jedes Angebots-Detail muss ein offer_type enthalten.")
        return value
    details = OfferDetailUpdateSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            # Erst nach ID, dann nach offer_type matchen
            existing_details_by_id = {str(d.id): d for d in instance.details.all()}
            existing_details_by_type = {d.offer_type: d for d in instance.details.all()}
            for detail in details_data:
                detail_id = str(detail.get('id')) if detail.get('id') is not None else None
                offer_type = detail.get('offer_type')
                if detail_id and detail_id in existing_details_by_id:
                    detail_instance = existing_details_by_id[detail_id]
                elif offer_type and offer_type in existing_details_by_type:
                    detail_instance = existing_details_by_type[offer_type]
                else:
                    detail_instance = None

                if detail_instance:
                    for attr, value in detail.items():
                        if attr not in ['id', 'offer']:
                            setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail)
        return instance


"""Serializer for referencing OfferDetail with URL"""
class OfferDetailReferenceSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


"""Serializer for listing Offers with minimal detail info"""
class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='business_user', read_only=True)
    details = OfferDetailReferenceSerializer(many=True, read_only=True)
    user_details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField(read_only=True)
    min_delivery_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        user = obj.business_user
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        } if user else None

    def get_min_price(self, obj):
        prices = obj.details.values_list('price', flat=True)
        if not prices:
            return None
        min_price = min(prices)
        return int(min_price) if float(min_price).is_integer() else float(min_price)

    def get_min_delivery_time(self, obj):
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None


"""Serializer for compact OfferDetail representation"""
class OfferDetailCompactSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

    def get_price(self, obj):
        if obj.price == int(obj.price):
            return int(obj.price)
        return float(obj.price)


"""Serializer for compact Offer representation"""
class OfferDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    def validate_price(self, value):
        if value is None:
            raise serializers.ValidationError("Preis darf nicht leer sein.")
        if float(value) <= 0:
            raise serializers.ValidationError("Preis muss größer als 0 sein.")
        return value
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

    def get_price(self, obj):
        if obj.price == int(obj.price):
            return int(obj.price)
        return float(obj.price)


"""Serializer for compact Offer representation"""
class OfferCompactSerializer(serializers.ModelSerializer):
    details = OfferDetailCompactSerializer(many=True)
    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id', 'details']


"""Serializer for creating and updating Offers along with their details"""
class OfferSerializer(serializers.ModelSerializer):
    def validate_details(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Ein Angebot muss mindestens 3 Details enthalten.")
        for detail in value:
            price = detail.get('price')
            try:
                price_val = float(price)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"Preis ist ungültig: {price!r}.")
            if price_val <= 0:
                raise serializers.ValidationError("Jedes Angebots-Detail muss einen Preis > 0 haben.")
        return value
    user = serializers.PrimaryKeyRelatedField(source='business_user', read_only=True)
    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField(read_only=True)
    min_delivery_time = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['business_user'] = request.user
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def get_min_price(self, obj):
        prices = obj.details.values_list('price', flat=True)
        if not prices:
            return None
        min_price = min(prices)
        return int(min_price) if float(min_price).is_integer() else float(min_price)

    def get_min_delivery_time(self, obj):
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {d.id: d for d in instance.details.all()}
            sent_ids = set()
            for detail in details_data:
                detail_id = detail.get('id', None)
                if detail_id and detail_id in existing_details:
                    detail_instance = existing_details[detail_id]
                    for attr, value in detail.items():
                        if attr != 'id':
                            setattr(detail_instance, attr, value)
                    detail_instance.save()
                    sent_ids.add(detail_id)
                else:
                    OfferDetail.objects.create(offer=instance, **detail)
            for detail_id, detail_instance in existing_details.items():
                if detail_id not in sent_ids:
                    detail_instance.delete()

        return instance
