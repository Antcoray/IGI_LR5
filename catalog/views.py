import logging
import calendar
import statistics
from datetime import date, datetime
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import (
    Avg, Count, Max, Min, Sum, Q
)
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CarSearchForm, OrderForm, ReviewForm
from .models import (
    Article, Car, CarType, Client, CompanyInfo,
    Contact, FAQ, Feature, Manufacturer,
    Order, Promo, Review, Vacancy
)

logger = logging.getLogger('catalog')

def get_weather(city='Minsk'):
    """Погода через OpenWeatherMap API"""
    key = settings.OPENWEATHER_API_KEY
    if not key:
        return None
    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric&lang=ru'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'].capitalize(),
                'city': data['name'],
            }
    except Exception as e:
        logger.warning(f'Weather API error: {e}')
    return None

def get_exchange_rates():
    """Курсы валют через ExchangeRate-API"""
    key = settings.EXCHANGERATE_API_KEY
    if not key:
        # Fallback: NBRB
        try:
            rates = {}
            for code, abbr in [(431, 'USD'), (451, 'EUR'), (298, 'RUB')]:
                url = f'https://www.nbrb.by/api/exrates/rates/{code}?parammode=1'
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    d = r.json()
                    rates[abbr] = round(d['Cur_OfficialRate'] / d['Cur_Scale'], 4)
            return rates
        except Exception as e:
            logger.warning(f'NBRB API error: {e}')
        return None
    try:
        url = f'https://v6.exchangerate-api.com/v6/{key}/latest/BYN'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            rates = data.get('conversion_rates', {})
            return {k: rates[k] for k in ['USD', 'EUR', 'RUB'] if k in rates}
    except Exception as e:
        logger.warning(f'Exchange rate API error: {e}')
    return None

def index(request):
    """Главная страница"""
    logger.info('Home page accessed')
    latest_article = Article.objects.filter(is_published=True).first()
    featured_cars = Car.objects.filter(status='available').select_related('manufacturer', 'car_type')[:6]
    weather = get_weather()
    rates = get_exchange_rates()
    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)
    cal_text = calendar.month(now_local.year, now_local.month)
    return render(request, 'catalog/index.html', {
        'latest_article': latest_article,
        'featured_cars': featured_cars,
        'weather': weather,
        'rates': rates,
        'now_utc': now_utc,
        'now_local': now_local,
        'calendar': cal_text,
    })


def car_list(request):
    """Список автомобилей с поиском и фильтрацией"""
    form = CarSearchForm(request.GET)
    cars = Car.objects.select_related('manufacturer', 'car_type').all()

    # Populate dynamic choices
    form.fields['car_type'].widget.choices = [('', 'Все типы')] + list(CarType.objects.values_list('id', 'name'))
    form.fields['manufacturer'].widget.choices = [('', 'Все марки')] + list(Manufacturer.objects.values_list('id', 'name'))

    if form.is_valid():
        q = form.cleaned_data.get('q')
        ct = form.cleaned_data.get('car_type')
        mfr = form.cleaned_data.get('manufacturer')
        fuel = form.cleaned_data.get('fuel')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        sort = form.cleaned_data.get('sort')

        if q:
            cars = cars.filter(
                Q(name__icontains=q) | Q(manufacturer__name__icontains=q) | Q(vin__icontains=q)
            )
        if ct:
            cars = cars.filter(car_type_id=ct)
        if mfr:
            cars = cars.filter(manufacturer_id=mfr)
        if fuel:
            cars = cars.filter(fuel=fuel)
        if price_min:
            cars = cars.filter(price__gte=price_min)
        if price_max:
            cars = cars.filter(price__lte=price_max)
        if sort:
            cars = cars.order_by(sort)

    return render(request, 'catalog/car_list.html', {'form': form, 'cars': cars})


def car_detail(request, pk):
    """Детальная страница автомобиля"""
    car = get_object_or_404(Car, pk=pk)
    reviews = car.reviews.select_related('client__user').all()
    review_form = ReviewForm(initial={'car': car})
    order_form = OrderForm(initial={'car': car})
    return render(request, 'catalog/car_detail.html', {
        'car': car,
        'reviews': reviews,
        'review_form': review_form,
        'order_form': order_form,
    })

@staff_member_required
def car_create(request):
    from django.forms import modelform_factory
    CarForm = modelform_factory(Car, exclude=['created_at', 'updated_at'])
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            logger.info(f'Car created: {car}')
            messages.success(request, 'Автомобиль добавлен.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm()
    return render(request, 'catalog/car_form.html', {'form': form, 'title': 'Добавить автомобиль'})


@staff_member_required
def car_update(request, pk):
    car = get_object_or_404(Car, pk=pk)
    from django.forms import modelform_factory
    CarForm = modelform_factory(Car, exclude=['created_at', 'updated_at'])
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            car = form.save()
            logger.info(f'Car updated: {car}')
            messages.success(request, 'Автомобиль обновлён.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm(instance=car)
    return render(request, 'catalog/car_form.html', {'form': form, 'title': 'Редактировать автомобиль', 'car': car})


@staff_member_required
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        logger.info(f'Car deleted: {car}')
        car.delete()
        messages.success(request, 'Автомобиль удалён.')
        return redirect('car_list')
    return render(request, 'catalog/car_confirm_delete.html', {'car': car})

@login_required
def order_create(request, car_pk):
    car = get_object_or_404(Car, pk=car_pk)
    if not hasattr(request.user, 'client_profile'):
        messages.warning(request, 'Для оформления заказа нужно заполнить профиль клиента.')
        return redirect('profile')
    client = request.user.client_profile
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order: Order = form.save(commit=False)
            order.client = client
            order.car = car
            order.sale_price = car.price
            order.save()
            car.status = 'reserved'
            car.save()
            logger.info(f'Order created: {order}')
            messages.success(request, f'Заказ #{order.pk} успешно оформлен!')
            return redirect('my_orders')
    else:
        form = OrderForm(initial={'car': car})
    return render(request, 'catalog/order_create.html', {'form': form, 'car': car})


@login_required
def my_orders(request: HttpRequest):
    if not hasattr(request.user, 'client_profile'):
        return redirect('profile')
    orders = request.user.client_profile.orders.select_related('car__manufacturer').order_by('-created_at')
    return render(request, 'catalog/my_orders.html', {'orders': orders})


@login_required
def employee_orders(request):
    if not hasattr(request.user, 'employee_profile'):
        return redirect('index')
    orders = request.user.employee_profile.orders.select_related('car', 'client__user').order_by('-created_at')
    return render(request, 'catalog/employee_orders.html', {'orders': orders})

@login_required
@require_POST
def review_create(request):
    if not hasattr(request.user, 'client_profile'):
        messages.warning(request, 'Заполните профиль клиента, чтобы оставлять отзывы.')
        return redirect('profile')
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.client = request.user.client_profile
        review.save()
        messages.success(request, 'Отзыв добавлен.')
    else:
        messages.error(request, 'Ошибка при добавлении отзыва. Убедитесь, что ваш отзыв содержит не менее 10 символов')
    next_url = request.POST.get('next', '/')
    return redirect(next_url)


def reviews_list(request):
    reviews = Review.objects.select_related('client__user', 'car__manufacturer').all()
    review_form = None
    if request.user.is_authenticated and hasattr(request.user, 'client_profile'):
        review_form = ReviewForm()
    return render(request, 'catalog/reviews.html', {'reviews': reviews, 'review_form': review_form})


def about(request):
    company = CompanyInfo.objects.first()
    return render(request, 'catalog/about.html', {'company': company})


def news_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, 'catalog/news_list.html', {'articles': articles})


def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, 'catalog/news_detail.html', {'article': article})


def faq(request):
    faqs = FAQ.objects.all()
    return render(request, 'catalog/faq.html', {'faqs': faqs})


def contacts(request):
    contacts = Contact.objects.all()
    company = CompanyInfo.objects.first()
    return render(request, 'catalog/contacts.html', {'contacts': contacts, 'company': company})


def privacy(request):
    return render(request, 'catalog/privacy.html')


def vacancies(request):
    jobs = Vacancy.objects.filter(is_active=True)
    return render(request, 'catalog/vacancies.html', {'jobs': jobs})


def promos(request):
    active = Promo.objects.filter(status='active')
    archived = Promo.objects.filter(status='archived')
    return render(request, 'catalog/promos.html', {'active': active, 'archived': archived})

@staff_member_required
def statistics_view(request):
    logger.info(f'Statistics accessed by {request.user}')

    # Sales stats
    orders = Order.objects.filter(status='completed')
    prices = list(orders.values_list('sale_price', flat=True))
    prices_float = [float(p) for p in prices]

    total_sales = sum(prices_float)
    avg_price = statistics.mean(prices_float) if prices_float else 0
    median_price = statistics.median(prices_float) if prices_float else 0

    # Cars by type
    by_type = (
        Car.objects.values('car_type__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Most popular manufacturers
    by_manufacturer = (
        Order.objects.filter(status='completed')
        .values('car__manufacturer__name')
        .annotate(count=Count('id'), revenue=Sum('sale_price'))
        .order_by('-count')
    )

    # Monthly sales this year
    current_year = date.today().year
    monthly = []
    for m in range(1, 13):
        total = Order.objects.filter(
            status='completed', sale_date__year=current_year, sale_date__month=m
        ).aggregate(s=Sum('sale_price'))['s'] or 0
        monthly.append({'month': calendar.month_abbr[m], 'total': float(total)})

    # Clients by city
    by_city = (
        Client.objects.values('city')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Client ages
    today = date.today()
    clients_with_age = []
    for c in Client.objects.exclude(birth_date=None):
        age = (today - c.birth_date).days // 365
        clients_with_age.append(age)
    avg_age = statistics.mean(clients_with_age) if clients_with_age else 0
    median_age = statistics.median(clients_with_age) if clients_with_age else 0

    return render(request, 'catalog/statistics.html', {
        'total_sales': total_sales,
        'avg_price': avg_price,
        'median_price': median_price,
        'orders_count': len(prices),
        'by_type': by_type,
        'by_manufacturer': by_manufacturer,
        'monthly': monthly,
        'by_city': by_city,
        'avg_age': avg_age,
        'median_age': median_age,
        'current_year': current_year,
    })

def api_check_auth(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    return None


def api_cars(request):
    auth_error = api_check_auth(request)
    if auth_error:
        return auth_error
    cars = list(
        Car.objects.filter(status='available')
        .values('id', 'name', 'manufacturer__name', 'year', 'price', 'fuel', 'status')
    )
    return JsonResponse({'cars': cars})


def api_stats(request):
    auth_error = api_check_auth(request)
    if auth_error:
        return auth_error
    data = {
        'total_cars': Car.objects.count(),
        'available': Car.objects.filter(status='available').count(),
        'total_orders': Order.objects.count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
    }
    return JsonResponse(data)
