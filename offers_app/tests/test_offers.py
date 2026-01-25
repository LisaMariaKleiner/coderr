from django.urls import reverse
from rest_framework.test import APITestCase


from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offer
from rest_framework import status


class OfferTests(APITestCase):
    def test_offer_list_page_size_one(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'page_size': 1})
        print("[TEST-DEBUG] Response data:", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertLessEqual(len(response.data['results']), 1)
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user1 = User.objects.create_user(username='user1', password='testpass', user_type='business')
        cls.user2 = User.objects.create_user(username='user2', password='testpass', user_type='business')
        offer1 = Offer.objects.create(business_user=cls.user1, title='Webdesign', description='Webseiten', is_active=True)
        offer1.details.create(title='Basic', revisions=1, delivery_time_in_days=5, price=250, features=["A"], offer_type='basic')
        offer1.details.create(title='Premium', revisions=2, delivery_time_in_days=10, price=300, features=["B"], offer_type='premium')
        offer2 = Offer.objects.create(business_user=cls.user2, title='Logo', description='Logo Design', is_active=True)
        offer2.details.create(title='Basic', revisions=1, delivery_time_in_days=3, price=300, features=["C"], offer_type='basic')

    def test_offer_list_page_size(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'page_size': 2})
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.data['results']), 2)

    def test_offer_list_response_structure(self):
        import decimal
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = {'count', 'next', 'previous', 'results'}
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertIsInstance(response.data['count'], int)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
        results = response.data['results']
        for offer in results:
            offer_expected_keys = {
                'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
                'details', 'min_price', 'min_delivery_time'
            }
            # user_details ist optional, je nach Serializer
            self.assertTrue(offer_expected_keys.issubset(set(offer.keys())))
            self.assertIsInstance(offer['min_price'], (int, float, decimal.Decimal))
            self.assertIsInstance(offer['min_delivery_time'], (int, float, decimal.Decimal))

    def test_offer_list_filter_creator_id(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'creator_id': self.user2.id})
        self.assertEqual(response.status_code, 200)
        for offer in response.data['results']:
            self.assertEqual(offer['user'], self.user2.id)

    def test_offer_list_filter_min_price(self):
        import decimal
        url = reverse('offer-list')
        response = self.client.get(url, {'min_price': 200})
        self.assertEqual(response.status_code, 200)
        for offer in response.data['results']:
            self.assertGreaterEqual(offer['min_price'], decimal.Decimal('200'))

    def test_offer_list_filter_max_delivery_time(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'max_delivery_time': 3})
        self.assertEqual(response.status_code, 200)
        for offer in response.data['results']:
            self.assertLessEqual(offer['min_delivery_time'], 3)

    def test_offer_list_ordering(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'ordering': 'min_price'})
        self.assertEqual(response.status_code, 200)
        prices = [offer['min_price'] for offer in response.data['results']]
        from decimal import Decimal
        self.assertEqual(prices, sorted(prices, key=lambda x: float(x) if isinstance(x, Decimal) else x))

    def test_offer_list_search(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'search': 'Web'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('Web' in offer['title'] or 'Web' in offer['description'] for offer in response.data['results']))

