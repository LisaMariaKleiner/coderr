from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from profiles_app.models import User, BusinessProfile, CustomerProfile


class ProfileAPITestCase(TestCase):

    def test_patch_business_profile_full_fields(self):
        """Test PATCH mit allen Feldern und exakter Response-Prüfung"""
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "new_email@business.de"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Exakte Response-Struktur und Werte prüfen
        expected = {
            "user": self.business_user.id,
            "username": "business_test",
            "first_name": "Max",
            "last_name": "Mustermann",
            "file": None,
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "type": "business",
            "email": "new_email@business.de",
            "created_at": response.data["created_at"]  # Zeitformat wird separat geprüft
        }
        self.assertEqual(set(response.data.keys()), set(expected.keys()))
        for key in expected:
            if key == "created_at":
                self.assertIsInstance(response.data[key], str)
                self.assertRegex(response.data[key], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*")
            else:
                self.assertEqual(response.data[key], expected[key])
        # Alle relevanten Felder dürfen nicht null sein
        self.assert_no_null_strings(
            response.data,
            ["first_name", "last_name", "location", "tel", "description", "working_hours"]
        )

    def assert_no_null_strings(self, data, fields):
        for field in fields:
            self.assertIn(field, data)
            self.assertIsInstance(data[field], str)
            self.assertIsNotNone(data[field])

    """
    Test suite for Profile API endpoints
    Tests GET and PATCH /api/profile/{pk}/ with various scenarios
    """

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.customer_user = User.objects.create_user(
            username='customer_test',
            email='customer@test.com',
            password='testpass123',
            user_type='customer'
        )
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user,
            first_name='Jane',
            last_name='Doe'
        )
        self.customer_token = Token.objects.create(user=self.customer_user)

        # Create business user
        self.business_user = User.objects.create_user(
            username='business_test',
            email='business@test.com',
            password='testpass123',
            user_type='business'
        )
        self.business_profile = BusinessProfile.objects.create(
            user=self.business_user,
            location='Berlin',
            phone='123456789',
            description='Test business',
            working_hours='9-17'
        )
        self.business_token = Token.objects.create(user=self.business_user)

        # Create another user for permission tests
        self.other_user = User.objects.create_user(
            username='other_test',
            email='other@test.com',
            password='testpass123',
            user_type='customer'
        )
        CustomerProfile.objects.create(user=self.other_user)
        self.other_token = Token.objects.create(user=self.other_user)

    def test_get_customer_profile_success(self):
        """Test GET customer profile returns correct fields (200)"""
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.customer_user.id)
        self.assertEqual(response.data['username'], 'customer_test')
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertEqual(response.data['type'], 'customer')
        
        # Customer should NOT have these fields
        self.assertNotIn('email', response.data)
        self.assertNotIn('created_at', response.data)
        self.assertNotIn('tel', response.data)
        self.assertNotIn('location', response.data)
        self.assertNotIn('description', response.data)
        self.assertNotIn('working_hours', response.data)

    def test_get_business_profile_success(self):
        """Test GET business profile returns correct fields (200)"""
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.business_user.id)
        self.assertEqual(response.data['username'], 'business_test')
        self.assertEqual(response.data['type'], 'business')
        
        # Business should have these additional fields
        self.assertEqual(response.data['location'], 'Berlin')
        self.assertEqual(response.data['tel'], '123456789')
        self.assertEqual(response.data['description'], 'Test business')
        self.assertEqual(response.data['working_hours'], '9-17')

        self.assert_no_null_strings(
            response.data,
            ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        )

    def test_get_profile_unauthenticated(self):
        """Test GET profile without authentication (401)"""
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        """Test GET profile with non-existent user (404)"""
        url = reverse('profile-detail', kwargs={'pk': 99999})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_customer_profile_success(self):
        """Test PATCH own customer profile (200)"""
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
        
        # Verify database was updated
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.first_name, 'Updated')
        self.assertEqual(self.customer_user.last_name, 'Name')

    def test_patch_own_business_profile_success(self):
        """Test PATCH own business profile (200)"""
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
        
        # Verify database was updated
        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.location, 'Munich')
        self.assertEqual(self.business_profile.phone, '987654321')

        # Nach PATCH: Felder dürfen nicht null sein
        self.assert_no_null_strings(
            response.data,
            ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        )

    def test_patch_profile_unauthenticated(self):
        """Test PATCH profile without authentication (401)"""
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_other_user_profile_forbidden(self):
        """Test PATCH another user's profile (403)"""
        url = reverse('profile-detail', kwargs={'pk': self.other_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission', response.data['detail'].lower())

    def test_patch_profile_not_found(self):
        """Test PATCH non-existent profile (404)"""
        url = reverse('profile-detail', kwargs={'pk': 99999})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        
        data = {'first_name': 'Test'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_partial_update(self):
        """Test PATCH with partial data updates only provided fields"""
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        
        # Only update location
        data = {'location': 'Hamburg'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Hamburg')
        
        # Other fields should remain unchanged
        self.assertEqual(response.data['tel'], '123456789')
        self.assertEqual(response.data['description'], 'Test business')

        # Nach PATCH: Felder dürfen nicht null sein
        self.assert_no_null_strings(
            response.data,
            ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        )

    def test_customer_response_has_correct_structure(self):
        """Test customer response has exactly the required fields"""
        url = reverse('profile-detail', kwargs={'pk': self.customer_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        
        response = self.client.get(url)
        
        expected_fields = {'user', 'username', 'first_name', 'last_name', 'file', 'type'}
        actual_fields = set(response.data.keys())
        
        self.assertEqual(expected_fields, actual_fields)

    def test_business_response_has_correct_structure(self):
        """Test business response has exactly the required fields"""
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
        """Test business profile returns empty strings for missing optional fields"""
        # Create business without optional fields
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

        # Alle relevanten Felder dürfen nicht null sein
        self.assert_no_null_strings(
            response.data,
            ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        )
