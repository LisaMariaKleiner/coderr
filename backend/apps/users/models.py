from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
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
