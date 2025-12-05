from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.offers.models import Offer, OfferDetail
from apps.orders.models import Order

class CreateOrderFromOfferDetailTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer1', password='test123', user_type='customer')
        self.business = User.objects.create_user(username='business1', password='test123', user_type='business')
        self.offer = Offer.objects.create(business_user=self.business, title='Logo Design', description='desc')
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Logo Design',
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Visitenkarten"],
            offer_type='basic',
        )
        self.url = reverse('order-create-from-offer-detail')

    def test_create_order_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['title'], self.offer_detail.title)
        self.assertEqual(response.data['price'], float(self.offer_detail.price))
        self.assertEqual(response.data['status'], 'in_progress')

    def test_create_order_unauthenticated(self):
        response = self.client.post(self.url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_wrong_user_type(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post(self.url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_missing_offer_detail_id(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_offer_detail_id(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {'offer_detail_id': 9999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
