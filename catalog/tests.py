"""
Tests for the CarShop catalog app.
Run: pytest --cov=catalog --cov=users --cov-report=term-missing
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from catalog.models import (
    Car, CarType, Client, CompanyInfo, Contact, Employee,
    FAQ, Feature, Manufacturer, Order, Promo, Review, Vacancy, Article
)
from catalog.models import validate_phone, validate_adult


# ─────────────────────────────────────
# Fixtures helpers
# ─────────────────────────────────────

def make_manufacturer(name='Toyota', country='Япония'):
    return Manufacturer.objects.create(name=name, country=country)


def make_car_type(name='Седан'):
    return CarType.objects.get_or_create(name=name)[0]


def make_car(manufacturer=None, car_type=None, **kwargs):
    if not manufacturer:
        manufacturer = make_manufacturer()
    if not car_type:
        car_type = make_car_type()
    defaults = dict(
        vin='TEST00000000000001',
        name='Camry',
        manufacturer=manufacturer,
        car_type=car_type,
        year=2022,
        price=Decimal('89000'),
        mileage=0,
        color='Белый',
        transmission='AT',
        fuel='petrol',
        engine_volume=Decimal('2.5'),
        horsepower=181,
        status='available',
    )
    defaults.update(kwargs)
    return Car.objects.create(**defaults)


def make_user(username='testuser', password='pass1234!'):
    return User.objects.create_user(username=username, password=password, first_name='Test', last_name='User')


def make_client(user=None, **kwargs):
    if not user:
        user = make_user()
    defaults = dict(
        phone='+375 (29) 111-11-11',
        birth_date=date(1990, 1, 1),
        city='Минск',
        email='test@test.com',
    )
    defaults.update(kwargs)
    return Client.objects.create(user=user, **defaults)


# ─────────────────────────────────────
# Validator tests
# ─────────────────────────────────────

class ValidatorTests(TestCase):

    def test_phone_valid(self):
        # Should not raise
        validate_phone('+375 (29) 123-45-67')
        validate_phone('+375 (44) 987-65-43')

    def test_phone_invalid_format(self):
        with self.assertRaises(ValidationError):
            validate_phone('89001234567')

    def test_phone_invalid_missing_code(self):
        with self.assertRaises(ValidationError):
            validate_phone('+375 29 1234567')

    def test_adult_valid(self):
        adult_dob = date.today() - timedelta(days=365 * 20)
        validate_adult(adult_dob)  # Should not raise

    def test_adult_minor_raises(self):
        minor_dob = date.today() - timedelta(days=365 * 16)
        with self.assertRaises(ValidationError):
            validate_adult(minor_dob)

    def test_adult_exactly_18(self):
        dob_18 = date.today() - timedelta(days=365 * 18 + 1)
        validate_adult(dob_18)  # Should not raise


# ─────────────────────────────────────
# Model tests
# ─────────────────────────────────────

class ManufacturerModelTests(TestCase):

    def test_str(self):
        m = make_manufacturer('Toyota', 'Япония')
        self.assertIn('Toyota', str(m))
        self.assertIn('Япония', str(m))

    def test_ordering(self):
        make_manufacturer('Volkswagen', 'Германия')
        make_manufacturer('Audi', 'Германия')
        names = list(Manufacturer.objects.values_list('name', flat=True))
        self.assertEqual(names, sorted(names))


class CarModelTests(TestCase):

    def test_str(self):
        car = make_car()
        self.assertIn('Toyota', str(car))
        self.assertIn('Camry', str(car))

    def test_status_choices(self):
        car = make_car()
        self.assertEqual(car.status, 'available')

    def test_unique_vin(self):
        make_car(vin='UNIQUEVIN00000001')
        with self.assertRaises(Exception):
            make_car(vin='UNIQUEVIN00000001')

    def test_many_to_many_features(self):
        car = make_car(vin='FEATURETEST00001')
        f1, _ = Feature.objects.get_or_create(name='Климат-контроль')
        f2, _ = Feature.objects.get_or_create(name='Навигация')
        car.features.add(f1, f2)
        self.assertEqual(car.features.count(), 2)


class ClientModelTests(TestCase):

    def test_str(self):
        user = make_user('client_str', 'pass1234!')
        c = make_client(user=user)
        self.assertIn('Минск', str(c))

    def test_one_to_one_user(self):
        user = make_user('client_one', 'pass1234!')
        c = make_client(user=user)
        self.assertEqual(user.client_profile, c)


class OrderModelTests(TestCase):

    def setUp(self):
        self.car = make_car(vin='ORDERTEST000001A')
        self.user = make_user('order_client', 'pass1234!')
        self.client_obj = make_client(user=self.user)

    def test_create_order(self):
        order = Order.objects.create(
            client=self.client_obj,
            car=self.car,
            status='pending',
            sale_price=self.car.price,
        )
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.sale_price, self.car.price)

    def test_str(self):
        order = Order.objects.create(
            client=self.client_obj,
            car=self.car,
            status='pending',
            sale_price=self.car.price,
        )
        self.assertIn('Заказ', str(order))

    def test_fk_car(self):
        order = Order.objects.create(
            client=self.client_obj,
            car=self.car,
            status='approved',
            sale_price=self.car.price,
        )
        self.assertEqual(order.car, self.car)


class PromoModelTests(TestCase):

    def test_create_promo(self):
        promo = Promo.objects.create(code='TEST10', discount_percent=10, status='active')
        self.assertEqual(str(promo), 'TEST10 (-10%)')

    def test_unique_code(self):
        Promo.objects.create(code='UNIQUE', discount_percent=5, status='active')
        with self.assertRaises(Exception):
            Promo.objects.create(code='UNIQUE', discount_percent=10, status='active')


# ─────────────────────────────────────
# View tests
# ─────────────────────────────────────

class PublicViewTests(TestCase):

    def setUp(self):
        self.car = make_car(vin='VIEWTEST00000001')

    def test_index_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_car_list_200(self):
        response = self.client.get(reverse('car_list'))
        self.assertEqual(response.status_code, 200)

    def test_car_detail_200(self):
        response = self.client.get(reverse('car_detail', args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)

    def test_car_detail_404(self):
        response = self.client.get(reverse('car_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_news_list_200(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)

    def test_about_200(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_faq_200(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_200(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_200(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)

    def test_vacancies_200(self):
        response = self.client.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)

    def test_promos_200(self):
        response = self.client.get(reverse('promos'))
        self.assertEqual(response.status_code, 200)

    def test_reviews_200(self):
        response = self.client.get(reverse('reviews_list'))
        self.assertEqual(response.status_code, 200)

    def test_car_list_search(self):
        response = self.client.get(reverse('car_list') + '?q=Camry')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Camry')

    def test_car_list_filter_fuel(self):
        response = self.client.get(reverse('car_list') + '?fuel=petrol')
        self.assertEqual(response.status_code, 200)

    def test_car_list_filter_price(self):
        response = self.client.get(reverse('car_list') + '?price_min=50000&price_max=100000')
        self.assertEqual(response.status_code, 200)


class AuthViewTests(TestCase):

    def setUp(self):
        self.user = make_user('auth_test', 'pass1234!')
        self.client_profile = make_client(user=self.user)
        self.car = make_car(vin='AUTHTEST00000001')

    def test_login_page_200(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_200(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response['Location'])

    def test_my_orders_requires_login(self):
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 302)

    def test_profile_authenticated(self):
        self.client.login(username='auth_test', password='pass1234!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_register_new_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser123',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'email': 'new@test.com',
            'password1': 'SecurePass456!',
            'password2': 'SecurePass456!',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_api_cars_requires_auth(self):
        response = self.client.get(reverse('api_cars'))
        self.assertEqual(response.status_code, 401)

    def test_api_cars_authenticated(self):
        self.client.login(username='auth_test', password='pass1234!')
        response = self.client.get(reverse('api_cars'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('cars', data)

    def test_api_stats_authenticated(self):
        self.client.login(username='auth_test', password='pass1234!')
        response = self.client.get(reverse('api_stats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_cars', data)

    def test_statistics_requires_staff(self):
        self.client.login(username='auth_test', password='pass1234!')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 302)

    def test_statistics_staff_access(self):
        staff_user = User.objects.create_user('staff', 'staff@test.com', 'pass1234!', is_staff=True)
        self.client.login(username='staff', password='pass1234!')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)

    def test_car_create_requires_staff(self):
        self.client.login(username='auth_test', password='pass1234!')
        response = self.client.get(reverse('car_create'))
        self.assertEqual(response.status_code, 302)

    def test_order_create_redirects_unauthenticated(self):
        response = self.client.get(reverse('order_create', args=[self.car.pk]))
        self.assertEqual(response.status_code, 302)


class OrderCreateViewTests(TestCase):

    def setUp(self):
        self.user = make_user('order_user', 'pass1234!')
        self.client_profile = make_client(user=self.user)
        self.car = make_car(vin='ORDERVIEW000001A')
        self.client.login(username='order_user', password='pass1234!')

    def test_order_create_get(self):
        response = self.client.get(reverse('order_create', args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)

    def test_order_create_post(self):
        response = self.client.post(reverse('order_create', args=[self.car.pk]), {
            'car': self.car.pk,
            'comment': 'Хочу купить этот автомобиль',
        })
        self.assertIn(response.status_code, [200, 302])


# ─────────────────────────────────────
# FAQ / Article / Review tests
# ─────────────────────────────────────

class ContentTests(TestCase):

    def test_article_str(self):
        a = Article.objects.create(title='Тест', summary='..', content='Полный текст')
        self.assertEqual(str(a), 'Тест')

    def test_faq_creation(self):
        faq = FAQ.objects.create(question='Вопрос?', answer='Ответ.')
        self.assertEqual(str(faq), 'Вопрос?')

    def test_vacancy_creation(self):
        v = Vacancy.objects.create(title='Менеджер', description='...', is_active=True)
        self.assertEqual(str(v), 'Менеджер')

    def test_review_requires_client(self):
        user = make_user('review_user', 'pass1234!')
        c = make_client(user=user)
        car = make_car(vin='REVIEWTEST000001')
        review = Review.objects.create(client=c, rating=5, text='Отличный автосалон!')
        self.assertEqual(review.rating, 5)

    def test_news_detail_view(self):
        article = Article.objects.create(
            title='Тестовая новость', summary='Краткое', content='Полный текст...'
        )
        response = self.client.get(reverse('news_detail', args=[article.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая новость')


# ─────────────────────────────────────
# Parametrized-style tests
# ─────────────────────────────────────

class CarFilterTests(TestCase):
    """Test search and filtering from car_list view"""

    def setUp(self):
        mfr_toyota = make_manufacturer('FilterToyota', 'Япония')
        mfr_bmw = make_manufacturer('FilterBMW', 'Германия')
        ct = make_car_type('Седан')
        make_car(vin='FILTER00000000001', manufacturer=mfr_toyota, price=Decimal('50000'), fuel='petrol')
        make_car(vin='FILTER00000000002', manufacturer=mfr_bmw, price=Decimal('150000'), fuel='diesel')

    def test_filter_by_manufacturer(self):
        mfr = Manufacturer.objects.get(name='FilterToyota')
        response = self.client.get(f"{reverse('car_list')}?manufacturer={mfr.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FilterToyota')

    def test_filter_by_price_range(self):
        response = self.client.get(f"{reverse('car_list')}?price_min=40000&price_max=60000")
        self.assertEqual(response.status_code, 200)

    def test_sort_by_price_asc(self):
        response = self.client.get(f"{reverse('car_list')}?sort=price")
        self.assertEqual(response.status_code, 200)

    def test_sort_by_price_desc(self):
        response = self.client.get(f"{reverse('car_list')}?sort=-price")
        self.assertEqual(response.status_code, 200)
