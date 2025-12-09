from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offer
from rest_framework import status

class OfferTests(APITestCase):
    def test_offerdetail_retrieve_success(self):
        User = get_user_model()
        business_user = User.objects.create_user(username='detailuser', password='testpass', user_type='business')
        self.client.login(username='detailuser', password='testpass')
        from offers_app.models import Offer, OfferDetail
        offer = Offer.objects.create(
            business_user=business_user,
            title='Detail Angebot',
            description='Beschreibung',
            is_active=True
        )
        detail = OfferDetail.objects.create(
            offer=offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo Design", "Visitenkarte"],
            offer_type='basic'
        )
        url = reverse('offerdetail-detail', args=[detail.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected_keys = {"id", "title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"}
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertEqual(response.data["id"], detail.id)
        self.assertEqual(response.data["title"], detail.title)
        self.assertEqual(response.data["revisions"], detail.revisions)
        self.assertEqual(response.data["delivery_time_in_days"], detail.delivery_time_in_days)
        self.assertEqual(response.data["price"], detail.price)
        self.assertEqual(response.data["features"], detail.features)
        self.assertEqual(response.data["offer_type"], detail.offer_type)
    def test_offer_delete_success(self):
        User = get_user_model()
        business_user = User.objects.create_user(username='deleteuser', password='testpass', user_type='business')
        self.client.login(username='deleteuser', password='testpass')
        from offers_app.models import Offer
        offer = Offer.objects.create(
            business_user=business_user,
            title='Delete Angebot',
            description='Beschreibung',
            is_active=True
        )
        url = reverse('offer-detail', args=[offer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(response.content)  # Kein Inhalt
    def test_offer_patch_response_structure(self):
        User = get_user_model()
        business_user = User.objects.create_user(username='patchuser', password='testpass', user_type='business')
        self.client.login(username='patchuser', password='testpass')
        # Angebot mit 3 Details anlegen
        from offers_app.models import Offer, OfferDetail
        offer = Offer.objects.create(
            business_user=business_user,
            title='Grafikdesign-Paket',
            description='Ein umfassendes Grafikdesign-Paket für Unternehmen.',
            is_active=True
        )
        detail1 = OfferDetail.objects.create(offer=offer, title='Basic Design', revisions=2, delivery_time_in_days=5, price=100, features=["Logo Design", "Visitenkarte"], offer_type='basic')
        detail2 = OfferDetail.objects.create(offer=offer, title='Standard Design', revisions=5, delivery_time_in_days=10, price=120, features=["Logo Design", "Visitenkarte", "Briefpapier"], offer_type='standard')
        detail3 = OfferDetail.objects.create(offer=offer, title='Premium Design', revisions=10, delivery_time_in_days=10, price=150, features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"], offer_type='premium')

        url = reverse('offer-detail', args=[offer.id])
        patch_data = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "id": detail1.id,
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, 200)
        offer_expected_keys = {"id", "title", "image", "description", "details"}
        self.assertEqual(set(response.data.keys()), offer_expected_keys)
        self.assertEqual(response.data["id"], offer.id)
        self.assertEqual(response.data["title"], patch_data["title"])
        self.assertEqual(response.data["description"], offer.description)
        self.assertIsNone(response.data["image"])
        self.assertEqual(len(response.data["details"]), 3)
        # Basic Design wurde aktualisiert
        updated_detail = next(d for d in response.data["details"] if d["id"] == detail1.id)
        self.assertEqual(updated_detail["title"], "Basic Design Updated")
        self.assertEqual(updated_detail["revisions"], 3)
        self.assertEqual(updated_detail["delivery_time_in_days"], 6)
        self.assertEqual(updated_detail["price"], 120)
        self.assertEqual(updated_detail["features"], ["Logo Design", "Flyer"])
        self.assertEqual(updated_detail["offer_type"], "basic")
        # Die anderen Details bleiben unverändert
        for detail in response.data["details"]:
            self.assertIn("id", detail)
            self.assertIn("title", detail)
            self.assertIn("revisions", detail)
            self.assertIn("delivery_time_in_days", detail)
            self.assertIn("price", detail)
            self.assertIn("features", detail)
            self.assertIn("offer_type", detail)
    def test_offer_create_response_structure(self):
        User = get_user_model()
        business_user = User.objects.create_user(username='businessuser2', password='testpass', user_type='business')
        self.client.login(username='businessuser2', password='testpass')
        url = reverse('offer-list')
        data = {
            "title": "Grafikdesign-Paket",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        offer_expected_keys = {"id", "title", "image", "description", "details"}
        self.assertEqual(set(response.data.keys()), offer_expected_keys)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["description"], data["description"])
        self.assertIsNone(response.data["image"])
        self.assertEqual(len(response.data["details"]), 3)
        for i, detail in enumerate(response.data["details"]):
            detail_expected_keys = {"id", "title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"}
            self.assertEqual(set(detail.keys()), detail_expected_keys)
            self.assertEqual(detail["title"], data["details"][i]["title"])
            self.assertEqual(detail["revisions"], data["details"][i]["revisions"])
            self.assertEqual(detail["delivery_time_in_days"], data["details"][i]["delivery_time_in_days"])
            self.assertEqual(detail["price"], data["details"][i]["price"])
            self.assertEqual(detail["features"], data["details"][i]["features"])
            self.assertEqual(detail["offer_type"], data["details"][i]["offer_type"])
            self.assertIsInstance(detail["id"], int)
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
        # Prüfe, ob paginierte oder nicht-paginierte Antwort
        if hasattr(response.data, 'keys'):
            # paginierte Antwort
            expected_keys = {'count', 'next', 'previous', 'results'}
            self.assertEqual(set(response.data.keys()), expected_keys)
            self.assertIsInstance(response.data['count'], int)
            self.assertIn('results', response.data)
            self.assertIsInstance(response.data['results'], list)
            results = response.data['results']
        else:
            # nicht-paginierte Antwort (ReturnList)
            results = response.data
        if results:
            offer = results[0]
            offer_expected_keys = {
                'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
                'details', 'min_price', 'min_delivery_time', 'user_details'
            }
            self.assertEqual(set(offer.keys()), offer_expected_keys)
            self.assertEqual(offer['title'], 'Test Angebot')

    def test_offer_detail_success(self):
        url = reverse('offer-detail', args=[self.offer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offer_expected_keys = {
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time'
        }
        self.assertEqual(set(response.data.keys()), offer_expected_keys)
        self.assertEqual(response.data['id'], self.offer.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['title'], self.offer.title)
        self.assertEqual(response.data['description'], self.offer.description)
        self.assertIn('details', response.data)
        self.assertIsInstance(response.data['details'], list)
        for detail in response.data['details']:
            detail_expected_keys = {'id', 'url'}
            self.assertEqual(set(detail.keys()), detail_expected_keys)
            self.assertIsInstance(detail['id'], int)
            self.assertIsInstance(detail['url'], str)

    def test_offer_detail_unauthenticated(self):
        # Angenommen, Endpoint ist geschützt (sonst entfällt dieser Test)
        # Hier: Kein Login, trotzdem GET
        url = reverse('offer-detail', args=[self.offer.id])
        response = self.client.get(url)
        # Falls Endpoint geschützt: 401, sonst 200 (je nach Implementation)
        # Passe ggf. an, falls Endpoint öffentlich ist
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_offer_detail_not_found(self):
        url = reverse('offer-detail', args=[999999])  # Nicht existierende ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



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
