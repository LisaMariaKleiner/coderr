from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'profiles/business', views.BusinessProfileViewSet, basename='business-profile')
router.register(r'profiles/customer', views.CustomerProfileViewSet, basename='customer-profile')

urlpatterns = [
    path('', include(router.urls)),
]
