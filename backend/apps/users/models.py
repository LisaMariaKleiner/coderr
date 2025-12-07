from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, user_type='customer', **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, user_type='customer', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, user_type, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')

    objects = UserManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class BusinessProfile(models.Model):
    """
    Business-specific profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    company_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='profiles/business/', blank=True, null=True)
    working_hours = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name or self.user.username}'s Business Profile"


class CustomerProfile(models.Model):
    """
    Customer-specific profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/customer/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Customer Profile"
