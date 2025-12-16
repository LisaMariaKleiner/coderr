from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

class BaseInfoTests(APITestCase):
    def test_base_info_success(self):
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)
        self.assertIn('detail', response.data)

    def test_base_info_internal_error(self):
        with patch('reviews_app.models.Review.objects.count', side_effect=Exception()):
            url = reverse('base-info')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('detail', response.data)
            self.assertEqual(response.data['detail'], 'Interner Serverfehler.')
