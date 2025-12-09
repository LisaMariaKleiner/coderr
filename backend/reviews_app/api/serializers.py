from rest_framework import serializers
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Review Serializer"""

    business_user = serializers.SerializerMethodField()
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    description = serializers.CharField(source='comment')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        # Ausgabe im Format YYYY-MM-DDTHH:MM:SSZ (UTC, ohne Mikrosekunden)
        from django.utils.timezone import is_naive, make_aware
        import datetime
        dt = obj.created_at
        if is_naive(dt):
            dt = make_aware(dt, datetime.timezone.utc)
        dt = dt.astimezone(datetime.timezone.utc)
        return dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    def get_updated_at(self, obj):
        from django.utils.timezone import is_naive, make_aware
        import datetime
        dt = obj.updated_at
        if is_naive(dt):
            dt = make_aware(dt, datetime.timezone.utc)
        dt = dt.astimezone(datetime.timezone.utc)
        return dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def get_business_user(self, obj):
        return getattr(obj.offer, 'business_user_id', None)

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
