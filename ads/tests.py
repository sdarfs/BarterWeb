from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Ad

class AdModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

    def test_create_ad(self):
        """Тест создания объявления."""
        ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление',
            description='Это тестовое описание объявления.',
            image_url='https://example.com/image.jpg',
            category='electronics',
            condition='new'
        )

        self.assertEqual(ad.title, 'Тестовое объявление')
        self.assertEqual(ad.description, 'Это тестовое описание объявления.')
        self.assertEqual(ad.category, 'electronics')
        self.assertEqual(ad.condition, 'new')

        self.assertIsNotNone(ad.created_at)

    def test_string_representation(self):
        """Тест строкового представления модели."""
        ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление',
            description='Описание',
            category='books',
            condition='used'
        )
        self.assertEqual(str(ad), 'Тестовое объявление')

    def test_get_absolute_url(self):
        """Тест метода get_absolute_url."""
        ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление',
            description='Описание',
            category='clothing',
            condition='new'
        )
        expected_url = reverse('product_detail', kwargs={'pk': ad.pk})  # Используем reverse для генерации URL
        self.assertEqual(ad.get_absolute_url(), expected_url)

class AddProductViewTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.login(username='testuser', password='testpassword123')

    def test_add_product_authenticated(self):
        """Тест создания объявления авторизованным пользователем."""
        url = reverse('create_ad')
        data = {
            'title': 'Новое объявление',
            'description': 'Тестовое описание',
            'image_url': 'https://example.com/test.jpg',
            'category': 'electronics',
            'condition': 'new'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='Новое объявление').exists())

    def test_add_product_unauthenticated(self):
        """Тест создания объявления неавторизованным пользователем."""
        self.client.logout()
        url = reverse('create_ad')
        data = {
            'title': 'Новое объявление',
            'description': 'Тестовое описание',
            'image_url': 'https://example.com/test.jpg',
            'category': 'electronics',
            'condition': 'new'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(title='Новое объявление').exists())

class ProductsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        Ad.objects.create(
            user=self.user,
            title='Объявление 1',
            description='Описание 1',
            category='electronics',
            condition='new'
        )
        Ad.objects.create(
            user=self.user,
            title='Объявление 2',
            description='Описание 2',
            category='books',
            condition='used'
        )

    def test_products_list(self):
        """Тест просмотра списка объявлений."""
        url = reverse('products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Объявление 1')
        self.assertContains(response, 'Объявление 2')

    def test_ordering_by_created_at(self):
        """Тест сортировки объявлений по дате публикации."""
        url = reverse('products')
        response = self.client.get(url)
        products = response.context['products']
        self.assertEqual(products[0].title, 'Объявление 2')
        self.assertEqual(products[1].title, 'Объявление 1')

class UpdateProductViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Старое название',
            description='Старое описание',
            category='electronics',
            condition='new'
        )
        self.client.login(username='testuser', password='testpassword123')

    def test_update_product_authenticated(self):
        """Тест редактирования объявления авторизованным пользователем."""
        url = reverse('edit_page', kwargs={'pk': self.ad.pk})
        data = {
            'title': 'Новое название',
            'description': 'Новое описание',
            'category': 'books',
            'condition': 'used'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        updated_ad = Ad.objects.get(pk=self.ad.pk)
        self.assertEqual(updated_ad.title, 'Новое название')
        self.assertEqual(updated_ad.description, 'Новое описание')
        self.assertEqual(updated_ad.category, 'books')
        self.assertEqual(updated_ad.condition, 'used')

    def test_update_product_unauthorized(self):
        """Тест редактирования объявления неавторизованным пользователем."""
        self.client.logout()
        url = reverse('edit_page', kwargs={'pk': self.ad.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_update_product_wrong_user(self):
        """Тест попытки редактирования объявления другого пользователя."""
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        self.client.login(username='otheruser', password='otherpassword123')
        url = reverse('edit_page', kwargs={'pk': self.ad.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Доступ запрещен

class DeleteProductViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Объявление для удаления',
            description='Описание',
            category='electronics',
            condition='new'
        )
        self.client.login(username='testuser', password='testpassword123')

    def test_delete_product_authenticated(self):
        """Тест удаления объявления авторизованным пользователем."""
        url = reverse('delete_page', kwargs={'pk': self.ad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_delete_product_unauthorized(self):
        """Тест удаления объявления неавторизованным пользователем."""
        self.client.logout()
        url = reverse('delete_page', kwargs={'pk': self.ad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_delete_product_wrong_user(self):
        """Тест попытки удаления объявления другого пользователя."""
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        self.client.login(username='otheruser', password='otherpassword123')
        url = reverse('delete_page', kwargs={'pk': self.ad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ad.objects.filter(pk=self.ad.pk).exists())

class DeleteProductViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Объявление для удаления',
            description='Описание',
            category='electronics',
            condition='new'
        )
        self.client.login(username='testuser', password='testpassword123')

    def test_delete_product_authenticated(self):
        """Тест удаления объявления авторизованным пользователем."""
        url = reverse('delete_page', kwargs={'pk': self.ad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_delete_product_unauthorized(self):
        """Тест удаления объявления неавторизованным пользователем."""
        self.client.logout()
        url = reverse('delete_page', kwargs={'pk': self.ad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_delete_product_wrong_user(self):
        """Тест попытки удаления объявления другого пользователя."""
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        self.client.login(username='otheruser', password='otherpassword123')
        url = reverse('delete_page', kwargs={'pk': self.ad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ad.objects.filter(pk=self.ad.pk).exists())

class SearchProductsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        Ad.objects.create(
            user=self.user,
            title='Laptop for sale',
            description='High-performance laptop',
            category='electronics',
            condition='new'
        )
        Ad.objects.create(
            user=self.user,
            title='Old book',
            description='Classic novel',
            category='books',
            condition='used'
        )

    def test_search_by_title(self):
        """Тест поиска объявлений по названию."""
        url = reverse('products') + '?q=Laptop'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop for sale')
        self.assertNotContains(response, 'Old book')

    def test_search_by_description(self):
        """Тест поиска объявлений по описанию."""
        url = reverse('products') + '?q=classic'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Old book')
        self.assertNotContains(response, 'Laptop for sale')

class FilterProductsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        Ad.objects.create(
            user=self.user,
            title='Laptop',
            description='High-performance laptop',
            category='electronics',
            condition='new'
        )
        Ad.objects.create(
            user=self.user,
            title='Book',
            description='Classic novel',
            category='books',
            condition='used'
        )

    def test_filter_by_category(self):
        """Тест фильтрации объявлений по категории."""
        url = reverse('products') + '?category=electronics'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')
        self.assertNotContains(response, 'Book')

    def test_filter_by_condition(self):
        """Тест фильтрации объявлений по состоянию."""
        url = reverse('products') + '?condition=new'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')
        self.assertNotContains(response, 'Book')

from .models import ExchangeProposal

class ExchangeProposalTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        self.ad_sender = Ad.objects.create(
            user=self.user1,
            title='Sender Item',
            description='Item to send',
            category='electronics',
            condition='new'
        )
        self.ad_receiver = Ad.objects.create(
            user=self.user2,
            title='Receiver Item',
            description='Item to receive',
            category='books',
            condition='used'
        )
        self.client.login(username='user1', password='password123')

    def test_create_exchange_proposal(self):
        """Тест создания предложения обмена."""
        url = reverse('create_exchange')
        data = {
            'ad_sender_id': self.ad_sender.id,
            'ad_receiver_id': self.ad_receiver.id,
            'comment': 'I want to exchange this item.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExchangeProposal.objects.filter(ad_sender=self.ad_sender, ad_receiver=self.ad_receiver).exists())

    def test_update_exchange_status(self):
        """Тест обновления статуса предложения обмена."""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver,
            comment='Test proposal',
            status='pending'
        )
        self.client.login(username='user2', password='password123')
        url = reverse('update_exchange', kwargs={'pk': proposal.id})
        data = {'action': 'accept'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        updated_proposal = ExchangeProposal.objects.get(id=proposal.id)
        self.assertEqual(updated_proposal.status, 'accepted')
        self.assertTrue(updated_proposal.ad_sender.is_archived)
        self.assertTrue(updated_proposal.ad_receiver.is_archived)