
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from profiles_app.models import User, BusinessProfile, CustomerProfile
from rest_framework import status

class UserProfileTests(APITestCase):

    def test_get_customer_profiles_list_success(self):
        url = reverse('customer-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        for profile in response.data:
            expected_fields = {
                'user', 'username', 'first_name', 'last_name', 'file', 'type',
                'location', 'tel', 'description', 'working_hours'
            }
            self.assertEqual(set(profile.keys()), expected_fields)
            self.assertEqual(profile['type'], 'customer')
            self.assert_no_null_strings(
                profile,
                ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
            )

    def test_get_customer_profiles_list_unauthenticated(self):
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assert_no_null_strings(self, data, fields):
        for field in fields:
            self.assertIn(field, data)
            self.assertIsInstance(data[field], str)
            self.assertIsNotNone(data[field])

    def test_get_business_profiles_list_success(self):
        url = reverse('business-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        for profile in response.data:
            expected_fields = {
                'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type'
            }
            self.assertEqual(set(profile.keys()), expected_fields)
            self.assertEqual(profile['type'], 'business')
            self.assert_no_null_strings(
                profile,
                ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
            )

    def test_get_business_profiles_list_unauthenticated(self):
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def setUp(self):
        self.customer_user = User.objects.create_user(username='customer1', password='test123', user_type='customer')
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user, first_name='Max', last_name='Mustermann')
        self.customer_token = Token.objects.create(user=self.customer_user)

        self.business_user = User.objects.create_user(username='business1', password='test123', user_type='business')
        self.business_profile = BusinessProfile.objects.create(user=self.business_user, location='Berlin', phone='123456789', description='Test business', working_hours='9-17')
        self.business_token = Token.objects.create(user=self.business_user)

        self.other_user = User.objects.create_user(username='otheruser', password='test123', user_type='customer')
        self.other_token = Token.objects.create(user=self.other_user)

    def test_get_own_customer_profile_success(self):
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer1')

    def test_get_own_business_profile_success(self):
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'business1')

    def test_get_profile_unauthenticated(self):
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_other_user_profile_authenticated(self):
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_not_found(self):
        url = reverse('profile-detail', kwargs={'pk': 99999})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_customer_profile_success(self):
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.first_name, 'Updated')
        self.assertEqual(self.customer_user.last_name, 'Name')

    def test_patch_own_business_profile_success(self):
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        data = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'location': 'Munich',
            'tel': '987654321',
            'description': 'Updated description',
            'working_hours': '10-18'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['location'], 'Munich')
        self.assertEqual(response.data['tel'], '987654321')
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(response.data['working_hours'], '10-18')
        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.location, 'Munich')
        self.assertEqual(self.business_profile.phone, '987654321')

    def test_patch_profile_unauthenticated(self):
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_other_user_profile_forbidden(self):
        url = reverse('profile-detail', kwargs={'pk': self.other_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission', response.data['detail'].lower())

    def test_patch_profile_not_found(self):
        url = reverse('profile-detail', kwargs={'pk': 99999})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'first_name': 'Test'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_partial_update(self):
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        data = {'location': 'Hamburg'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Hamburg')
        self.assertEqual(response.data['tel'], '123456789')
        self.assertEqual(response.data['description'], 'Test business')

    def test_customer_response_has_correct_structure(self):
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get(url)
        expected_fields = {'user', 'username', 'first_name', 'last_name', 'file', 'type'}
        actual_fields = set(response.data.keys())
        self.assertEqual(expected_fields, actual_fields)

    def test_business_response_has_correct_structure(self):
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        response = self.client.get(url)
        expected_fields = {
            'user', 'username', 'first_name', 'last_name', 'file', 'type',
            'location', 'tel', 'description', 'working_hours', 'email', 'created_at'
        }
        actual_fields = set(response.data.keys())
        self.assertEqual(expected_fields, actual_fields)

    def test_empty_strings_for_missing_business_fields(self):
        user = User.objects.create_user(
            username='minimal_business',
            password='test123',
            user_type='business'
        )
        BusinessProfile.objects.create(user=user)
        token = Token.objects.create(user=user)
        url = reverse('profile-detail', kwargs={'pk': user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')
