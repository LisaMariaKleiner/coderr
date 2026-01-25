from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from profiles_app.models import User, BusinessProfile

class ProfileResponseAkzeptanzTests(APITestCase):
    def test_patch_business_profile_updates_user_names(self):
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        data = {"first_name": "Dwighn", "last_name": "Schrute"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business_user.refresh_from_db()
        self.assertEqual(self.business_user.first_name, "Dwighn")
        self.assertEqual(self.business_user.last_name, "Schrute")
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='max_mustermann',
            password='test123',
            user_type='business',
            email='old_email@business.de'
        )
        self.business_profile = BusinessProfile.objects.create(
            user=self.business_user,
            company_name='Testfirma',
            description='Beschreibung',
            location='Berlin',
            phone='123456789',
            working_hours='9-17',
        )
        self.business_user.set_password('test123')
        self.business_user.save()
        self.client.login(username='max_mustermann', password='test123')


    def test_patch_business_profile_permission(self):
        other_user = User.objects.create_user(
            username='other', password='test123', user_type='business'
        )
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        self.client.logout()
        self.client.login(username='other', password='test123')
        data = {"first_name": "Hacker"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)

    def test_patch_business_profile_unauthenticated(self):
        self.client.logout()
        url = reverse('profile-detail', kwargs={'pk': self.business_user.id})
        data = {"first_name": "Hacker"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_patch_business_profile_not_found(self):
        url = reverse('profile-detail', kwargs={'pk': 9999})
        data = {"first_name": "Nobody"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
