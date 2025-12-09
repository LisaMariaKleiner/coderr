from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('profile', views.ProfileViewSet, basename='profile')
router.register('profiles/business', views.BusinessProfileViewSet, basename='business-profile')
router.register('profiles/customer', views.CustomerProfileViewSet, basename='customer-profile')

urlpatterns = [
    path('', include(router.urls)),
]
