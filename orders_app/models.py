from django.db import models
from profiles_app.models import User
from offers_app.models import Offer


class Order(models.Model):
    """Order model for tracking purchases"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_customer',
        limit_choices_to={'user_type': 'customer'}
    )
    business = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_business',
        limit_choices_to={'user_type': 'business'}
    )
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} -> {self.business.username}"
