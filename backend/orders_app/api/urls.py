from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .apiviews import OrderCountView
from .apiviews_completed import CompletedOrderCountView

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('orders/<int:business_user_id>/count/', OrderCountView.as_view(), name='order-count'),
    path('orders/<int:business_user_id>/completed-count/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('', include(router.urls)),
]
