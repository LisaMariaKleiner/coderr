from rest_framework import serializers
from .models import User, BusinessProfile, CustomerProfile


class UserSerializer(serializers.ModelSerializer):
    """Basic User Serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Business Profile Serializer"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'user', 'username', 'email', 'company_name', 'description',
            'location', 'profile_image', 'working_hours', 'phone', 'website',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Customer Profile Serializer"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'user', 'username', 'email', 'first_name', 'last_name',
            'profile_image', 'phone', 'location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class BusinessProfileListSerializer(serializers.Serializer):
    """
    Business Profile List Serializer for GET /api/profiles/business/
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    file = serializers.SerializerMethodField()
    location = serializers.CharField(read_only=True)
    tel = serializers.CharField(source='phone', read_only=True)
    description = serializers.CharField(read_only=True)
    working_hours = serializers.CharField(read_only=True)
    type = serializers.SerializerMethodField()

    def get_file(self, obj):
        return obj.profile_image.url if obj.profile_image else None

    def get_type(self, obj):
        return 'business'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['first_name'] = data.get('first_name') or ''
        data['last_name'] = data.get('last_name') or ''
        data['location'] = data.get('location') or ''
        data['tel'] = data.get('tel') or ''
        data['description'] = data.get('description') or ''
        data['working_hours'] = data.get('working_hours') or ''
        return data


class CustomerProfileListSerializer(serializers.Serializer):
    """
    Customer Profile List Serializer for GET /api/profiles/customer/
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    file = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_file(self, obj):
        return obj.profile_image.url if obj.profile_image else None

    def get_type(self, obj):
        return 'customer'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['first_name'] = data.get('first_name') or ''
        data['last_name'] = data.get('last_name') or ''
        return data


class ProfileDetailSerializer(serializers.Serializer):
    """
    Profile Detail Serializer for GET /api/profile/{pk}/
    Unified response for both customer and business profiles
    """
    user = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    file = serializers.SerializerMethodField()
    location = serializers.CharField(read_only=True)
    tel = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    working_hours = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_file(self, obj):
        """Get profile image URL"""
        if hasattr(obj, 'profile_image'):
            return obj.profile_image.url if obj.profile_image else None
        return None

    def to_representation(self, instance):
        """
        Custom representation based on User object
        instance = User object
        """
        profile = None
        if instance.user_type == 'business':
            profile = getattr(instance, 'business_profile', None)
        else:
            profile = getattr(instance, 'customer_profile', None)

        data = {
            'user': instance.id,
            'username': instance.username,
        }

        if instance.user_type == 'customer' and profile:
            data['first_name'] = profile.first_name or ''
            data['last_name'] = profile.last_name or ''
        else:
            data['first_name'] = instance.first_name or ''
            data['last_name'] = instance.last_name or ''

        if profile:
            data['file'] = profile.profile_image.url if profile.profile_image else None
        else:
            data['file'] = None

        if instance.user_type == 'business':
            if profile:
                data['location'] = profile.location or ''
                data['tel'] = profile.phone or ''
                data['description'] = profile.description or ''
                data['working_hours'] = profile.working_hours or ''
            else:
                data['location'] = ''
                data['tel'] = ''
                data['description'] = ''
                data['working_hours'] = ''
            
            data['type'] = instance.user_type
            data['email'] = instance.email
            data['created_at'] = instance.date_joined.isoformat() if hasattr(instance, 'date_joined') else instance.created_at.isoformat()
        else:
            data['type'] = instance.user_type

        return data


class ProfileUpdateSerializer(serializers.Serializer):
    """
    Unified Profile Update Serializer for PATCH /api/profile/{pk}/
    Handles both customer and business profiles with unified field names
    """
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    
    location = serializers.CharField(required=False, allow_blank=True)
    tel = serializers.CharField(required=False, allow_blank=True)
    file = serializers.ImageField(required=False, allow_null=True)
    
    description = serializers.CharField(required=False, allow_blank=True)
    working_hours = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        """
        Update User and Profile data
        instance = User object
        """
        user = instance
        
        if 'first_name' in validated_data:
            user.first_name = validated_data['first_name'] or ''
        if 'last_name' in validated_data:
            user.last_name = validated_data['last_name'] or ''
        if 'email' in validated_data:
            user.email = validated_data['email']
        user.save()
        
        profile = None
        if user.user_type == 'business':
            profile = getattr(user, 'business_profile', None)
            if not profile:
                profile = BusinessProfile.objects.create(user=user)
        elif user.user_type == 'customer':
            profile = getattr(user, 'customer_profile', None)
            if not profile:
                profile = CustomerProfile.objects.create(user=user)
        
        if profile:
            if 'tel' in validated_data and user.user_type == 'business':
                profile.phone = validated_data['tel'] or ''
            
            if user.user_type == 'business':
                if 'location' in validated_data:
                    profile.location = validated_data['location'] or ''
                if 'description' in validated_data:
                    profile.description = validated_data['description'] or ''
                if 'working_hours' in validated_data:
                    profile.working_hours = validated_data['working_hours'] or ''
            else:
                if 'first_name' in validated_data:
                    profile.first_name = validated_data['first_name'] or ''
                if 'last_name' in validated_data:
                    profile.last_name = validated_data['last_name'] or ''
            
            if 'file' in validated_data:
                profile.profile_image = validated_data['file']
            
            profile.save()
        
        return user

    def to_representation(self, instance):
        """
        Format output with unified field names and empty strings instead of null
        instance = User object
        """
        user = instance
        profile = None
        
        if user.user_type == 'business':
            profile = getattr(user, 'business_profile', None)
        elif user.user_type == 'customer':
            profile = getattr(user, 'customer_profile', None)
        
        data = {
            'user': user.id,
            'username': user.username,
        }
        
        if user.user_type == 'customer' and profile:
            data['first_name'] = profile.first_name or ''
            data['last_name'] = profile.last_name or ''
        else:
            data['first_name'] = user.first_name or ''
            data['last_name'] = user.last_name or ''
        
        if profile:
            data['file'] = profile.profile_image.url if profile.profile_image else None
        else:
            data['file'] = None
        
        if user.user_type == 'business':
            if profile:
                data['location'] = profile.location or ''
                data['tel'] = profile.phone or ''
                data['description'] = profile.description or ''
                data['working_hours'] = profile.working_hours or ''
            else:
                data['location'] = ''
                data['tel'] = ''
                data['description'] = ''
                data['working_hours'] = ''
            
            data['type'] = user.user_type
            data['email'] = user.email
            data['created_at'] = user.date_joined.isoformat() if hasattr(user, 'date_joined') else user.created_at.isoformat()
        else:
            data['type'] = user.user_type
        
        return data


class ProfileSerializer(serializers.Serializer):
    """
    Read-only Profile Serializer for GET /api/profile/{pk}/
    """
    id = serializers.IntegerField(read_only=True)
    user = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    user_type = serializers.CharField(read_only=True)
    
    company_name = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    working_hours = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    
    phone = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        """Format output based on profile type"""
        data = {
            'id': instance.id,
            'user': instance.user.id,
            'username': instance.user.username,
            'email': instance.user.email,
            'user_type': instance.user.user_type,
            'phone': instance.phone if hasattr(instance, 'phone') else '',
            'profile_image': instance.profile_image.url if instance.profile_image else None,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

        if isinstance(instance, BusinessProfile):
            data.update({
                'company_name': instance.company_name,
                'description': instance.description,
                'location': instance.location,
                'working_hours': instance.working_hours,
                'website': instance.website,
            })
        elif isinstance(instance, CustomerProfile):
            data.update({
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'location': instance.location,
            })

        return data
