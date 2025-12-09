from django.db import models
from profiles_app.models import User


class Offer(models.Model):
    """Offer/Service model for businesses"""
    business_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='offers',
        limit_choices_to={'user_type': 'business'}
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.business_user.username}"

    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    class Meta:
        db_table = "offer_details"
        ordering = ["offer", "price"]

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"
