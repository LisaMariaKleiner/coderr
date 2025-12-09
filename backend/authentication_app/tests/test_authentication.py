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
        # Erwartete Keys im Response
        expected_keys = {'token', 'username', 'email', 'user_id'}
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertIsInstance(response.data['token'], str)
        self.assertEqual(response.data['username'], self.username)
        self.assertIsInstance(response.data['email'], str)
        self.assertIsInstance(response.data['user_id'], int)

    def test_login_failure(self):
        url = reverse('login')
        data = {'username': self.username, 'password': 'wrongpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Unable to log in with provided credentials.', str(response.data))

    def test_registration_response_structure(self):
        url = reverse('registration')
        data = {
            'username': 'exampleUsername',
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword',
            'type': 'customer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Erwartete Keys im Response
        expected_keys = {'token', 'username', 'email', 'user_id'}
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertIsInstance(response.data['token'], str)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertIsInstance(response.data['user_id'], int)
