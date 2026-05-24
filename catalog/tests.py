"""
Tests for CarShop.  Run:
  pytest --cov=catalog --cov=users --cov-report=term-missing
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client as TestClient
from django.urls import reverse

from catalog.models import (
    Car, CarType, Client, Employee, Feature,
    Manufacturer, Order, OrderItem, Promo, Review, Vacancy, Article, FAQ
)
from catalog.models import validate_phone, validate_adult


# ── helpers ──────────────────────────────────────

def make_mfr(name='Toyota'):
    return Manufacturer.objects.create(name=name, country='Япония')

def make_ct(name='Седан'):
    return CarType.objects.get_or_create(name=name)[0]

def make_car(vin='TSTVIN00000000001', **kw):
    defaults = dict(
        name='Camry', manufacturer=make_mfr(), car_type=make_ct(),
        year=2022, price=Decimal('89000'), mileage=0,
        color='Белый', transmission='AT', fuel='petrol',
        engine_volume=Decimal('2.5'), horsepower=181, status='available',
    )
    defaults.update(kw)
    return Car.objects.create(vin=vin, **defaults)

def make_user(username='user1', password='pass1234!'):
    return User.objects.create_user(username, password=password, first_name='T', last_name='U')

def make_client(user=None, **kw):
    if not user:
        user = make_user()
    defaults = dict(phone='+375 (29) 111-11-11', birth_date=date(1990,1,1),
                    city='Минск', email='t@t.com',
                    last_name='Тест', first_name='Клиент')
    defaults.update(kw)
    return Client.objects.create(user=user, **defaults)

def make_employee(user=None):
    if not user:
        user = make_user('emp1')
    return Employee.objects.create(
        user=user, role='manager',
        phone='+375 (29) 999-99-99',
        birth_date=date(1988, 6, 15),
    )

def make_order(client=None, employee=None, status='pending'):
    if not client:
        client = make_client(make_user('ocli'))
    return Order.objects.create(
        client=client, employee=employee,
        status=status, total_amount=Decimal('0'),
    )


# ── Validators ───────────────────────────────────

class ValidatorTests(TestCase):

    def test_phone_valid(self):
        validate_phone('+375 (29) 123-45-67')
        validate_phone('+375 (44) 987-65-43')

    def test_phone_invalid(self):
        with self.assertRaises(ValidationError):
            validate_phone('89001234567')
        with self.assertRaises(ValidationError):
            validate_phone('+375 29 1234567')

    def test_adult_valid(self):
        validate_adult(date.today() - timedelta(days=365*20))

    def test_adult_minor_raises(self):
        with self.assertRaises(ValidationError):
            validate_adult(date.today() - timedelta(days=365*16))

    def test_adult_exactly_18(self):
        validate_adult(date.today() - timedelta(days=365*18+1))


# ── Model tests ───────────────────────────────────

class ManufacturerTests(TestCase):
    def test_str(self):
        m = make_mfr('BMW')
        self.assertIn('BMW', str(m))

    def test_ordering(self):
        Manufacturer.objects.create(name='Zonda', country='X')
        Manufacturer.objects.create(name='Aston', country='Y')
        names = list(Manufacturer.objects.values_list('name', flat=True))
        self.assertEqual(names, sorted(names))


class CarModelTests(TestCase):
    def test_str(self):
        car = make_car()
        self.assertIn('Camry', str(car))

    def test_unique_vin(self):
        make_car(vin='UNIQUE00000000001')
        with self.assertRaises(Exception):
            make_car(vin='UNIQUE00000000001')

    def test_m2m_features(self):
        car = make_car(vin='FEAT000000000001')
        f1, _ = Feature.objects.get_or_create(name='Навигация')
        f2, _ = Feature.objects.get_or_create(name='Климат')
        car.features.add(f1, f2)
        self.assertEqual(car.features.count(), 2)


class ClientModelTests(TestCase):
    def test_full_name(self):
        u = make_user('cn1')
        c = Client.objects.create(
            user=u, last_name='Иванов', first_name='Алексей',
            patronymic='Сергеевич', phone='+375 (29) 111-11-11',
            birth_date=date(1990,1,1), email='a@b.com'
        )
        self.assertIn('Иванов', c.full_name())
        self.assertIn('Алексей', c.full_name())

    def test_one_to_one(self):
        u = make_user('cn2')
        c = make_client(user=u)
        self.assertEqual(u.client_profile, c)


class OrderItemTests(TestCase):
    def test_subtotal(self):
        car = make_car(vin='OITEM00000000001')
        client = make_client(make_user('oi_cli'))
        order = Order.objects.create(client=client, status='pending', total_amount=0)
        item = OrderItem.objects.create(order=order, car=car, quantity=2, unit_price=Decimal('50000'))
        self.assertEqual(item.subtotal, Decimal('100000'))

    def test_recalculate_total(self):
        car = make_car(vin='RCALC00000000001')
        client = make_client(make_user('rc_cli'))
        order = Order.objects.create(client=client, status='pending', total_amount=0)
        OrderItem.objects.create(order=order, car=car, quantity=1, unit_price=Decimal('89000'))
        order.recalculate_total()
        order.refresh_from_db()
        self.assertEqual(order.total_amount, Decimal('89000'))

    def test_order_str(self):
        client = make_client(make_user('ord_str'))
        order = Order.objects.create(client=client, status='pending', total_amount=0)
        self.assertIn('Заказ', str(order))

    def test_multiple_items(self):
        car1 = make_car(vin='MULTI0000000001A')
        car2 = make_car(vin='MULTI0000000002B', manufacturer=make_mfr('BMW'))
        client = make_client(make_user('multi_cli'))
        order = Order.objects.create(client=client, status='pending', total_amount=0)
        OrderItem.objects.create(order=order, car=car1, quantity=1, unit_price=Decimal('89000'))
        OrderItem.objects.create(order=order, car=car2, quantity=1, unit_price=Decimal('145000'))
        order.recalculate_total()
        order.refresh_from_db()
        self.assertEqual(order.total_amount, Decimal('234000'))


class PromoTests(TestCase):
    def test_str(self):
        p = Promo.objects.create(code='TEST10', discount_percent=10, status='active')
        self.assertEqual(str(p), 'TEST10 (-10%)')

    def test_unique_code(self):
        Promo.objects.create(code='UNIQ', discount_percent=5, status='active')
        with self.assertRaises(Exception):
            Promo.objects.create(code='UNIQ', discount_percent=10, status='active')


# ── Public view tests ─────────────────────────────

class PublicViewTests(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.car = make_car(vin='PUB000000000001A')

    def test_index(self):
        self.assertEqual(self.c.get(reverse('index')).status_code, 200)

    def test_car_list(self):
        self.assertEqual(self.c.get(reverse('car_list')).status_code, 200)

    def test_car_detail(self):
        self.assertEqual(self.c.get(reverse('car_detail', args=[self.car.pk])).status_code, 200)

    def test_car_detail_404(self):
        self.assertEqual(self.c.get(reverse('car_detail', args=[99999])).status_code, 404)

    def test_news_list(self):
        self.assertEqual(self.c.get(reverse('news_list')).status_code, 200)

    def test_about(self):
        self.assertEqual(self.c.get(reverse('about')).status_code, 200)

    def test_faq(self):
        self.assertEqual(self.c.get(reverse('faq')).status_code, 200)

    def test_contacts(self):
        self.assertEqual(self.c.get(reverse('contacts')).status_code, 200)

    def test_privacy(self):
        self.assertEqual(self.c.get(reverse('privacy')).status_code, 200)

    def test_vacancies(self):
        self.assertEqual(self.c.get(reverse('vacancies')).status_code, 200)

    def test_promos(self):
        self.assertEqual(self.c.get(reverse('promos')).status_code, 200)

    def test_reviews(self):
        self.assertEqual(self.c.get(reverse('reviews_list')).status_code, 200)

    def test_car_search(self):
        r = self.c.get(reverse('car_list') + '?q=Camry')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Camry')

    def test_car_filter_fuel(self):
        self.assertEqual(self.c.get(reverse('car_list') + '?fuel=petrol').status_code, 200)

    def test_car_filter_price(self):
        self.assertEqual(self.c.get(reverse('car_list') + '?price_min=50000&price_max=100000').status_code, 200)

    def test_car_sort_price(self):
        self.assertEqual(self.c.get(reverse('car_list') + '?sort=price').status_code, 200)


# ── Auth & access tests ───────────────────────────

class AuthAccessTests(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.user = make_user('auth_u', 'pass1234!')
        self.client_profile = make_client(self.user)
        self.car = make_car(vin='AUTH000000000001')

    def test_login_page(self):
        self.assertEqual(self.c.get(reverse('login')).status_code, 200)

    def test_register_page(self):
        self.assertEqual(self.c.get(reverse('register')).status_code, 200)

    def test_profile_requires_login(self):
        r = self.c.get(reverse('profile'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r['Location'])

    def test_my_orders_requires_login(self):
        self.assertEqual(self.c.get(reverse('my_orders')).status_code, 302)

    def test_order_create_requires_staff(self):
        self.c.login(username='auth_u', password='pass1234!')
        r = self.c.get(reverse('order_create'))
        self.assertEqual(r.status_code, 302)

    def test_client_list_requires_staff(self):
        self.c.login(username='auth_u', password='pass1234!')
        r = self.c.get(reverse('client_list'))
        self.assertEqual(r.status_code, 302)

    def test_analytics_requires_superuser(self):
        # Regular staff should be redirected
        staff = User.objects.create_user('stf', 'stf@t.com', 'pass1234!', is_staff=True)
        self.c.login(username='stf', password='pass1234!')
        r = self.c.get(reverse('analytics'))
        self.assertEqual(r.status_code, 302)

    def test_analytics_superuser_access(self):
        su = User.objects.create_superuser('su2', 'su2@t.com', 'pass1234!')
        self.c.login(username='su2', password='pass1234!')
        r = self.c.get(reverse('analytics'))
        self.assertEqual(r.status_code, 200)

    def test_statistics_staff_access(self):
        staff = User.objects.create_user('stf2', 'stf2@t.com', 'pass1234!', is_staff=True)
        self.c.login(username='stf2', password='pass1234!')
        r = self.c.get(reverse('statistics'))
        self.assertEqual(r.status_code, 200)

    def test_api_cars_unauthenticated(self):
        self.assertEqual(self.c.get(reverse('api_cars')).status_code, 401)

    def test_api_cars_authenticated(self):
        self.c.login(username='auth_u', password='pass1234!')
        r = self.c.get(reverse('api_cars'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('cars', r.json())

    def test_api_stats_authenticated(self):
        self.c.login(username='auth_u', password='pass1234!')
        r = self.c.get(reverse('api_stats'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('total_cars', r.json())

    def test_profile_authenticated(self):
        self.c.login(username='auth_u', password='pass1234!')
        self.assertEqual(self.c.get(reverse('profile')).status_code, 200)


# ── Staff views ───────────────────────────────────

class StaffViewTests(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.staff = User.objects.create_user('staff3', 'stf3@t.com', 'pass1234!', is_staff=True)
        self.emp = make_employee(self.staff)
        self.c.login(username='staff3', password='pass1234!')

    def test_order_list(self):
        self.assertEqual(self.c.get(reverse('order_list')).status_code, 200)

    def test_order_create_get(self):
        self.assertEqual(self.c.get(reverse('order_create')).status_code, 200)

    def test_client_list(self):
        self.assertEqual(self.c.get(reverse('client_list')).status_code, 200)

    def test_client_create_get(self):
        self.assertEqual(self.c.get(reverse('client_create')).status_code, 200)

    def test_car_create_get(self):
        self.assertEqual(self.c.get(reverse('car_create')).status_code, 200)

    def test_client_create_post(self):
        r = self.c.post(reverse('client_create'), {
            'last_name': 'Тестов', 'first_name': 'Тест', 'patronymic': '',
            'phone': '+375 (29) 000-00-01', 'email': 'newclient@t.com',
            'address': 'ул. Тест, 1', 'city': 'Минск',
            'birth_date': '1990-01-01',
            'passport_series': 'HB', 'passport_number': '0000001',
        })
        self.assertIn(r.status_code, [200, 302])

    def test_client_search(self):
        u = make_user('cli_s')
        make_client(u, last_name='Петров')
        r = self.c.get(reverse('client_list') + '?q=Петров')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Петров')


# ── Content model tests ───────────────────────────

class ContentTests(TestCase):
    def test_article(self):
        a = Article.objects.create(title='Тест', summary='..', content='Текст')
        self.assertEqual(str(a), 'Тест')
        tc = TestClient()
        r = tc.get(reverse('news_detail', args=[a.pk]))
        self.assertEqual(r.status_code, 200)

    def test_faq(self):
        f = FAQ.objects.create(question='Вопрос?', answer='Ответ.')
        self.assertEqual(str(f), 'Вопрос?')

    def test_vacancy(self):
        v = Vacancy.objects.create(title='Менеджер', description='...', is_active=True)
        self.assertEqual(str(v), 'Менеджер')

    def test_review(self):
        u = make_user('rev_u')
        c = make_client(u)
        car = make_car(vin='REV000000000001A')
        rev = Review.objects.create(client=c, rating=5, text='Отлично!')
        self.assertEqual(rev.rating, 5)


# ── Filter / sort parametrized ────────────────────

class CarFilterTests(TestCase):
    def setUp(self):
        self.c = TestClient()
        m1 = Manufacturer.objects.create(name='FilterA', country='X')
        m2 = Manufacturer.objects.create(name='FilterB', country='Y')
        ct = make_ct()
        Car.objects.create(vin='FLT000000000001A', name='ModelA',
            manufacturer=m1, car_type=ct, year=2020, price=50000, mileage=0,
            color='W', transmission='AT', fuel='petrol',
            engine_volume=2, horsepower=150, status='available')
        Car.objects.create(vin='FLT000000000002B', name='ModelB',
            manufacturer=m2, car_type=ct, year=2021, price=150000, mileage=0,
            color='B', transmission='AT', fuel='diesel',
            engine_volume=2, horsepower=200, status='available')

    def test_search_name(self):
        r = self.c.get(reverse('car_list') + '?q=ModelA')
        self.assertContains(r, 'ModelA')
        self.assertNotContains(r, 'ModelB')

    def test_filter_manufacturer(self):
        mfr = Manufacturer.objects.get(name='FilterA')
        r = self.c.get(reverse('car_list') + f'?manufacturer={mfr.pk}')
        self.assertContains(r, 'FilterA')

    def test_filter_price_range(self):
        r = self.c.get(reverse('car_list') + '?price_min=40000&price_max=80000')
        self.assertEqual(r.status_code, 200)

    def test_sort_price_asc(self):
        self.assertEqual(self.c.get(reverse('car_list') + '?sort=price').status_code, 200)

    def test_sort_price_desc(self):
        self.assertEqual(self.c.get(reverse('car_list') + '?sort=-price').status_code, 200)

    def test_filter_fuel(self):
        r = self.c.get(reverse('car_list') + '?fuel=diesel')
        self.assertContains(r, 'ModelB')
