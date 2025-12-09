from django.urls import reverse
from rest_framework.test import APITestCase
from profiles_app.models import User
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from rest_framework import status

class OrderTests(APITestCase):
    def test_order_patch_status_response_structure(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('order-update-status', args=[self.order.id])
        patch_data = {"status": "completed"}
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = {
            'id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertEqual(response.data['id'], self.order.id)
        self.assertEqual(response.data['customer_user'], self.order.customer.id)
        self.assertEqual(response.data['business_user'], self.order.business.id)
        self.assertEqual(response.data['status'], 'completed')
    def test_order_list_response_structure(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            order = response.data[0]
            expected_keys = {
                'id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at'
            }
            self.assertEqual(set(order.keys()), expected_keys)
    def test_create_order_success_full_response(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.create_url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['title'], self.offer_detail.title)
        self.assertEqual(response.data['price'], float(self.offer_detail.price))
        self.assertEqual(response.data['status'], 'in_progress')
    def setUp(self):
        self.customer = User.objects.create_user(username='customer1', password='test123', user_type='customer')
        self.business = User.objects.create_user(username='business1', password='test123', user_type='business')
        self.admin = User.objects.create_user(username='admin1', password='test123', user_type='business', is_staff=True)
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
        self.order = Order.objects.create(
            customer=self.customer,
            business=self.business,
            offer=self.offer,
            status='in_progress',
            total_price=150
        )
        self.create_url = reverse('order-create-from-offer-detail')
        self.delete_url = reverse('order-detail', args=[self.order.id])
        self.count_url = reverse('order-count', args=[self.business.id])
        self.completed_count_url = reverse('completed-order-count', args=[self.business.id])

    def test_create_order_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.create_url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_order_unauthenticated(self):
        response = self.client.post(self.create_url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_wrong_user_type(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post(self.create_url, {'offer_detail_id': self.offer_detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_missing_offer_detail_id(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_offer_detail_id(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.create_url, {'offer_detail_id': 9999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_order_as_non_admin(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_unauthenticated(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_not_found(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('order-detail', args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_authenticated(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.get(self.count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('order_count', response.data)

    def test_order_count_unauthenticated(self):
        response = self.client.get(self.count_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_invalid_user(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('order-count', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_authenticated(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.get(self.completed_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completed_order_count', response.data)

    def test_completed_order_count_unauthenticated(self):
        response = self.client.get(self.completed_count_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_order_count_invalid_user(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('completed-order-count', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
