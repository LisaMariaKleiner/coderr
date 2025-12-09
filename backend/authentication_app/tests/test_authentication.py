from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        User = get_user_model()
        User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        url = reverse('login')
        data = {'username': self.username, 'password': self.password}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], self.username)

    def test_login_failure(self):
        url = reverse('login')
        data = {'username': self.username, 'password': 'wrongpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Unable to log in with provided credentials.', str(response.data))
