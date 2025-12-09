from django.urls import reverse
from rest_framework.test import APITestCase
from users_app.models import User
from offers_app.models import Offer
from reviews_app.models import Review
from rest_framework import status
from users_app.models import CustomerProfile

class ReviewTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer1', password='test123', user_type='customer')
        CustomerProfile.objects.create(user=self.customer)
        self.business = User.objects.create_user(username='business1', password='test123', user_type='business')
        self.offer = Offer.objects.create(business_user=self.business, title='Testangebot', description='desc')
        self.list_url = reverse('review-list')

    def create_review(self, reviewer=None):
        if reviewer is None:
            reviewer = self.customer
        offer = Offer.objects.create(business_user=self.business, title='Testangebot2', description='desc2')
        review = Review.objects.create(offer=offer, reviewer=reviewer, rating=4, comment='Gut!')
        return review

    def test_review_list(self):
        Review.objects.create(offer=self.offer, reviewer=self.customer, rating=4, comment='Gut!')
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], 4)

    def test_review_create_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        new_offer = Offer.objects.create(business_user=self.business, title='Neues Angebot', description='desc')
        data = {'business_user': self.business.id, 'rating': 5, 'description': 'Super!'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['reviewer'], self.customer.id)

    def test_review_create_unauthenticated(self):
        data = {'offer': self.offer.id, 'rating': 5, 'description': 'Super!'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_delete_by_owner(self):
        review = self.create_review()
        url = reverse('review-detail', args=[review.id])
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_review_delete_unauthenticated(self):
        review = self.create_review()
        url = reverse('review-detail', args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_delete_by_other_user(self):
        review = self.create_review()
        url = reverse('review-detail', args=[review.id])
        self.client.force_authenticate(user=self.business)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_update_by_owner(self):
        review = self.create_review()
        url = reverse('review-detail', args=[review.id])
        self.client.force_authenticate(user=self.customer)
        data = {'rating': 3, 'description': 'Geändert!'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 3)
        self.assertEqual(response.data['description'], 'Geändert!')

    def test_review_update_unauthenticated(self):
        review = self.create_review()
        url = reverse('review-detail', args=[review.id])
        data = {'rating': 2, 'description': 'Nicht erlaubt!'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update_by_other_user(self):
        review = self.create_review()
        url = reverse('review-detail', args=[review.id])
        self.client.force_authenticate(user=self.business)
        data = {'rating': 1, 'description': 'Nicht berechtigt!'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_update_not_found(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('review-detail', args=[9999])
        data = {'rating': 5, 'description': 'Nicht gefunden!'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_delete_not_found(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('review-detail', args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
