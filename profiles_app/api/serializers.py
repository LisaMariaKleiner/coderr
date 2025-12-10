from rest_framework import serializers
from ..models import User, BusinessProfile, CustomerProfile

class ProfileDetailSerializer(serializers.Serializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    tel = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    working_hours = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(source='user.created_at', read_only=True)

    def get_first_name(self, obj):
        return getattr(obj, 'first_name', '')

    def get_last_name(self, obj):
        return getattr(obj, 'last_name', '')
    
    def get_location(self, obj):
        return getattr(obj, 'location', '')

    def get_file(self, obj):
        return getattr(obj, 'profile_image', None).name if getattr(obj, 'profile_image', None) else None

    def get_tel(self, obj):
        return getattr(obj, 'phone', '')

    def get_description(self, obj):
        return getattr(obj, 'description', '')

    def get_working_hours(self, obj):
        return getattr(obj, 'working_hours', '')

    def get_type(self, obj):
        if hasattr(obj, 'company_name'):
            return 'business'
        return 'customer'

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
    """Business Profile List Serializer for GET /api/profiles/business/"""
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
        data['first_name'] = getattr(instance.user, 'first_name', '') or ''
        data['last_name'] = getattr(instance.user, 'last_name', '') or ''
        data['location'] = getattr(instance, 'location', '') or ''
        data['tel'] = getattr(instance, 'phone', '') or ''
        data['description'] = getattr(instance, 'description', '') or ''
        data['working_hours'] = getattr(instance, 'working_hours', '') or ''
        data['file'] = self.get_file(instance)
        data['type'] = self.get_type(instance)
        return data


class CustomerProfileListSerializer(serializers.Serializer):
    """Customer Profile List Serializer for GET /api/profiles/customer/"""
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    file = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_file(self, obj):
        return obj.profile_image.name if obj.profile_image else None

    def get_uploaded_at(self, obj):
        if obj.profile_image and hasattr(obj.profile_image, 'field'):
            return obj.updated_at.strftime('%Y-%m-%dT%H:%M:%S') if obj.updated_at else ''
        return ''

    def get_type(self, obj):
        return 'customer'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['first_name'] = getattr(instance, 'first_name', '') or ''
        data['last_name'] = getattr(instance, 'last_name', '') or ''
        data['file'] = self.get_file(instance)
        data['uploaded_at'] = self.get_uploaded_at(instance)
        data['type'] = self.get_type(instance)
        return {
            'user': data['user'],
            'username': data['username'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'file': data['file'],
            'uploaded_at': data['uploaded_at'],
            'type': data['type'],
        }


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
    created_at = serializers.SerializerMethodField()

    def get_file(self, obj):
        """Get profile image URL"""
        if hasattr(obj, 'profile_image'):
            return obj.profile_image.url if obj.profile_image else None
        return None

    def get_created_at(self, obj):
        import pytz
        from django.utils import timezone
        dt = getattr(obj, 'date_joined', None) or getattr(obj, 'created_at', None)
        if dt:
            dt = dt.astimezone(pytz.UTC).replace(microsecond=0)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        return ''

    def to_representation(self, instance):
        """
        Gibt für Business-Profile alle Felder, für Customer-Profile nur die erlaubten Felder zurück.
        Alle Felder sind nie null, sondern immer mindestens ein leerer String.
        """
        if hasattr(instance, 'user') and getattr(instance.user, 'user_type', None) == 'business':
            profile = getattr(instance, 'business_profile', None)
            def safe_str(val):
                return val if val is not None else ''
            data = {
                'user': instance.id,
                'username': safe_str(getattr(instance, 'username', '')),
                'first_name': safe_str(getattr(instance, 'first_name', '')),
                'last_name': safe_str(getattr(instance, 'last_name', '')),
                'file': getattr(profile, 'profile_image', None).url if profile and getattr(profile, 'profile_image', None) else None,
                'location': safe_str(getattr(profile, 'location', '')),
                'tel': safe_str(getattr(profile, 'phone', '')),
                'description': safe_str(getattr(profile, 'description', '')),
                'working_hours': safe_str(getattr(profile, 'working_hours', '')),
                'type': safe_str(getattr(instance, 'user_type', '')),
                'email': safe_str(getattr(instance, 'email', '')),
                'created_at': self.get_created_at(instance),
            }
            return data
        else:
            profile = getattr(instance, 'customer_profile', None)
            def safe_str(val):
                return val if val is not None else ''
            data = {
                'user': instance.id,
                'username': safe_str(getattr(instance, 'username', '')),
                'first_name': safe_str(getattr(profile, 'first_name', '')),
                'last_name': safe_str(getattr(profile, 'last_name', '')),
                'file': getattr(profile, 'profile_image', None).url if profile and getattr(profile, 'profile_image', None) else None,
                'location': safe_str(getattr(profile, 'location', '')),
                'tel': safe_str(getattr(profile, 'phone', '')),
                'description': safe_str(getattr(profile, 'description', '')),
                'working_hours': safe_str(getattr(profile, 'working_hours', '')),
                'type': safe_str(getattr(instance, 'user_type', '')),
                'email': safe_str(getattr(instance, 'email', '')),
                'created_at': self.get_created_at(instance),
            }
            return data


class ProfileUpdateSerializer(serializers.Serializer):
    """
    Unified Profile Update Serializer for PATCH /api/profile/{pk}/
    Handles both customer and business profiles with unified field names
    """
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    location = serializers.CharField(required=False, allow_blank=True)
    tel = serializers.CharField(required=False, allow_blank=True)
    file = serializers.ImageField(required=False, allow_null=True)

    description = serializers.CharField(required=False, allow_blank=True)
    working_hours = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        """
        Update User and Profile data
        Leere Felder (empty string) werden ignoriert und nicht überschrieben.
        instance = User object
        """
        user = instance
        # User-Felder
        if 'first_name' in validated_data and validated_data['first_name'] != '':
            user.first_name = validated_data['first_name']
        if 'last_name' in validated_data and validated_data['last_name'] != '':
            user.last_name = validated_data['last_name']
        if 'email' in validated_data and validated_data['email'] != '':
            user.email = validated_data['email']
        user.save()

        profile = None
        if user.user_type == 'business':
            profile = getattr(user, 'business_profile', None)
            if not profile:
                raise ValueError('Business profile does not exist')
        elif user.user_type == 'customer':
            profile = getattr(user, 'customer_profile', None)
            if not profile:
                raise ValueError('Customer profile does not exist')

        if profile:
            if user.user_type == 'business':
                if 'tel' in validated_data and validated_data['tel'] != '':
                    profile.phone = validated_data['tel']
                if 'location' in validated_data and validated_data['location'] != '':
                    profile.location = validated_data['location']
                if 'description' in validated_data and validated_data['description'] != '':
                    profile.description = validated_data['description']
                if 'working_hours' in validated_data and validated_data['working_hours'] != '':
                    profile.working_hours = validated_data['working_hours']
            elif user.user_type == 'customer':
                if 'first_name' in validated_data and validated_data['first_name'] != '':
                    profile.first_name = validated_data['first_name']
                if 'last_name' in validated_data and validated_data['last_name'] != '':
                    profile.last_name = validated_data['last_name']
                if 'tel' in validated_data and validated_data['tel'] != '':
                    profile.phone = validated_data['tel']
                if 'location' in validated_data and validated_data['location'] != '':
                    profile.location = validated_data['location']
                if 'description' in validated_data and validated_data['description'] != '':
                    profile.description = validated_data['description']
                if 'working_hours' in validated_data and validated_data['working_hours'] != '':
                    profile.working_hours = validated_data['working_hours']
            if 'file' in validated_data and validated_data['file']:
                profile.profile_image = validated_data['file']
            profile.save()
        return user

    def to_representation(self, instance):
        """
        PATCH-Response: Alle Felder sind nie null, sondern immer mindestens ein leerer String.
        Robust gegen fehlende Attribute.
        """
        user = instance
        def safe_str(val):
            return val if val is not None else ''
        if user.user_type == 'business':
            profile = getattr(user, 'business_profile', None)
            data = {
                'user': safe_str(getattr(user, 'id', '')),
                'username': safe_str(getattr(user, 'username', '')),
                'first_name': safe_str(getattr(profile, 'first_name', '')) if profile else '',
                'last_name': safe_str(getattr(profile, 'last_name', '')) if profile else '',
                'file': getattr(profile, 'profile_image', None).url if profile and getattr(profile, 'profile_image', None) else None,
                'location': safe_str(getattr(profile, 'location', '')) if profile else '',
                'tel': safe_str(getattr(profile, 'phone', '')) if profile else '',
                'description': safe_str(getattr(profile, 'description', '')) if profile else '',
                'working_hours': safe_str(getattr(profile, 'working_hours', '')) if profile else '',
                'type': safe_str(getattr(user, 'user_type', '')),
                'email': safe_str(getattr(user, 'email', '')),
                'created_at': '',
            }
            dt = getattr(user, 'date_joined', None) or getattr(user, 'created_at', None)
            if dt:
                import pytz
                dt = dt.astimezone(pytz.UTC).replace(microsecond=0)
                data['created_at'] = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            return data
        else:
            profile = getattr(user, 'customer_profile', None)
            data = {
                'user': safe_str(getattr(user, 'id', '')),
                'username': safe_str(getattr(user, 'username', '')),
                'first_name': safe_str(getattr(profile, 'first_name', '')) if profile else '',
                'last_name': safe_str(getattr(profile, 'last_name', '')) if profile else '',
                'file': getattr(profile, 'profile_image', None).url if profile and getattr(profile, 'profile_image', None) else None,
                'type': safe_str(getattr(user, 'user_type', '')),
            }
            return data


class ProfileSerializer(serializers.Serializer):
    """Read-only Profile Serializer for GET /api/profile/{pk}/"""
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
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        import pytz
        dt = getattr(obj, 'created_at', None)
        if dt:
            dt = dt.astimezone(pytz.UTC).replace(microsecond=0)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        return ''

    def get_updated_at(self, obj):
        import pytz
        dt = getattr(obj, 'updated_at', None)
        if dt:
            dt = dt.astimezone(pytz.UTC).replace(microsecond=0)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        return ''
    def to_representation(self, instance):
        """Format output based on profile type"""
        import pytz
        data = {
            'id': instance.id,
            'user': instance.user.id,
            'username': instance.user.username,
            'email': instance.user.email,
            'user_type': instance.user.user_type,
            'phone': instance.phone if hasattr(instance, 'phone') else '',
            'profile_image': instance.profile_image.url if instance.profile_image else None,
            'created_at': self.get_created_at(instance),
            'updated_at': self.get_updated_at(instance),
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
