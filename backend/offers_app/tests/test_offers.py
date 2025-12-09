from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offer
from rest_framework import status

class OfferTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='businessuser', password='testpass', user_type='business')
        self.offer = Offer.objects.create(
            business_user=self.user,
            title='Test Angebot',
            description='Beschreibung des Angebots',
            is_active=True
        )

    def test_offer_list(self):
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Angebot')

    def test_offer_detail(self):
        url = reverse('offer-detail', args=[self.offer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Angebot')



class OfferErrorTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.business_user = User.objects.create_user(username='businessuser', password='testpass', user_type='business')
        self.customer_user = User.objects.create_user(username='customeruser', password='testpass', user_type='customer')
        self.offer = Offer.objects.create(
            business_user=self.business_user,
            title='Test Angebot',
            description='Beschreibung des Angebots',
            is_active=True
        )

    def test_create_offer_unauthenticated(self):
        url = reverse('offer-list')
        data = {
            'business_user': self.business_user.id,
            'title': 'Neues Angebot',
            'description': 'Beschreibung',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_create_offer_as_customer(self):
        self.client.login(username='customeruser', password='testpass')
        url = reverse('offer-list')
        data = {
            'business_user': self.customer_user.id,
            'title': 'Neues Angebot',
            'description': 'Beschreibung',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)

    def test_my_offers_unauthenticated(self):
        url = reverse('offer-my-offers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication required.', response.data['detail'])
