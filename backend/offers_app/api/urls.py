from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('offers', views.OfferViewSet, basename='offer')
router.register('offerdetails', views.OfferDetailRetrieveViewSet, basename='offerdetail')

urlpatterns = [
    path('', include(router.urls)),
]
