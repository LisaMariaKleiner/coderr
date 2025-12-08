from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users_app.models import User
from offers_app.models import Offer


class Review(models.Model):
    """Review model for offers"""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        limit_choices_to={'user_type': 'customer'}
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5'
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['offer', 'reviewer']  # One review per user per offer

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.offer.title} - {self.rating}★"
