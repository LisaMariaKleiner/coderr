from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Review Serializer"""

    business_user = serializers.SerializerMethodField()
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    description = serializers.CharField(source='comment')


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
