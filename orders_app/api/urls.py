from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import OrderCountView, CompletedOrderCountView

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('', include(router.urls)),
]
