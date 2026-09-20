import io
import base64
import logging
import calendar
import statistics
from datetime import date, timedelta
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count, Max, Min, Sum, Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    CarSearchForm, OrderForm, OrderItemFormSet,
    OrderConfirmForm, ClientOrderForm, ClientQuickForm, ReviewForm
)
from .models import (
    Article, Car, CarType, Client, CompanyInfo,
    Contact, FAQ, Feature, Manufacturer,
    Order, OrderItem, Promo, Review, Vacancy, Partner
)

logger = logging.getLogger('catalog')


# ─────────────────────────────────────
# Matplotlib helper
# ─────────────────────────────────────

def _fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight',
                facecolor='#141414', edgecolor='none')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_b64


def _matplotlib_charts(year):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np

    GOLD    = '#c9a84c'
    BG      = '#141414'
    GRID    = '#2a2a2a'
    TEXT    = '#cccccc'
    PALETTE = ['#c9a84c', '#5b8dd9', '#e05a5a', '#5dc87c', '#b07ae0',
               '#e0a05a', '#5ad4e0', '#e05ab0', '#90e05a']

    plt.rcParams.update({
        'figure.facecolor': BG, 'axes.facecolor': BG,
        'axes.edgecolor': GRID, 'axes.labelcolor': TEXT,
        'xtick.color': TEXT, 'ytick.color': TEXT,
        'text.color': TEXT, 'grid.color': GRID, 'grid.alpha': 0.5,
        'legend.facecolor': '#1e1e1e', 'legend.edgecolor': GRID,
        'font.size': 10,
    })

    charts = {}
    months_labels = [calendar.month_abbr[m] for m in range(1, 13)]

    # Ежемесячная выручка
    monthly_totals = []
    monthly_counts = []
    for m in range(1, 13):
        qs = Order.objects.filter(
            status='completed', sale_date__year=year, sale_date__month=m
        ).aggregate(s=Sum('total_amount'), c=Count('id'))
        monthly_totals.append(float(qs['s'] or 0))
        monthly_counts.append(int(qs['c'] or 0))

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(months_labels, monthly_totals, color=GOLD, alpha=0.85)
    ax.set_title(f'Ежемесячная выручка {year} (BYN)', color=GOLD, pad=10)
    ax.set_ylabel('Сумма (BYN)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    for bar, val in zip(bars, monthly_totals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(monthly_totals, default=1) * 0.01,
                    f'{int(val):,}', ha='center', va='bottom', fontsize=8, color=GOLD)
    plt.tight_layout()
    charts['monthly_revenue'] = _fig_to_b64(fig)
    plt.close(fig)

    # Линейный тренд
    x = np.arange(12)
    non_zero = [(i, v) for i, v in enumerate(monthly_totals) if v > 0]
    coeffs = None
    if len(non_zero) >= 2:
        xs = np.array([i for i, _ in non_zero])
        ys = np.array([v for _, v in non_zero])
        coeffs = np.polyfit(xs, ys, 1)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(months_labels, monthly_totals, 'o-', color=GOLD, linewidth=2, label='Факт')
    if coeffs is not None:
        trend_y = np.polyval(coeffs, x)
        ax.plot(months_labels, trend_y, '--', color='#5b8dd9', linewidth=1.5, label='Линейный тренд')
    ax.set_title(f'Тренд продаж {year}', color=GOLD, pad=10)
    ax.set_ylabel('Сумма (BYN)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(linestyle='--', alpha=0.4)
    ax.legend()
    plt.tight_layout()
    charts['trend'] = _fig_to_b64(fig)
    plt.close(fig)

    # Прогноз
    fig, ax = plt.subplots(figsize=(9, 4))
    full_x      = np.arange(15)
    full_labels = months_labels + ['М+1', 'М+2', 'М+3']
    ax.plot(months_labels, monthly_totals, 'o-', color=GOLD, linewidth=2, label='Факт')
    if coeffs is not None:
        trend_full = np.polyval(coeffs, full_x)
        ax.plot(full_labels[12:], trend_full[12:], 's--', color='#5dc87c',
                linewidth=2, markersize=8, label='Прогноз')
        ax.plot(full_labels, trend_full, ':', color='#5b8dd9',
                linewidth=1, alpha=0.5, label='Тренд')
    else:
        ax.text(0.5, 0.5, 'Недостаточно данных для прогноза',
                transform=ax.transAxes, ha='center', va='center', color=TEXT)
    ax.set_title(f'Прогноз продаж (тренд от {year})', color=GOLD, pad=10)
    ax.set_ylabel('Сумма (BYN)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(linestyle='--', alpha=0.4)
    ax.legend()
    plt.tight_layout()
    charts['forecast'] = _fig_to_b64(fig)
    plt.close(fig)

    # По типам кузова
    by_type = list(
        OrderItem.objects.filter(order__status='completed', order__sale_date__year=year)
        .values('car__car_type__name')
        .annotate(total=Sum(F('quantity') * F('unit_price')), cnt=Sum('quantity'))
        .order_by('-total')
    )
    if by_type:
        labels_t = [r['car__car_type__name'] for r in by_type]
        vals_t   = [float(r['total']) for r in by_type]
        fig, ax  = plt.subplots(figsize=(8, max(3, len(labels_t) * 0.7 + 1)))
        bars = ax.barh(labels_t, vals_t,
                       color=[PALETTE[i % len(PALETTE)] for i in range(len(labels_t))],
                       alpha=0.85)
        ax.set_title('Объём продаж по типу кузова (BYN)', color=GOLD, pad=10)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
        ax.grid(axis='x', linestyle='--', alpha=0.4)
        for bar, val in zip(bars, vals_t):
            ax.text(bar.get_width() + max(vals_t, default=1) * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val):,}', va='center', fontsize=8, color=TEXT)
        plt.tight_layout()
        charts['by_type'] = _fig_to_b64(fig)
        plt.close(fig)

    # По производителям
    by_mfr = list(
        OrderItem.objects.filter(order__status='completed', order__sale_date__year=year)
        .values('car__manufacturer__name')
        .annotate(total=Sum(F('quantity') * F('unit_price')))
        .order_by('-total')[:8]
    )
    if by_mfr:
        labels_m = [r['car__manufacturer__name'] for r in by_mfr]
        vals_m   = [float(r['total']) for r in by_mfr]
        fig, ax  = plt.subplots(figsize=(7, 5))
        wedges, texts, autotexts = ax.pie(
            vals_m, labels=labels_m, autopct='%1.1f%%',
            colors=PALETTE[:len(vals_m)], startangle=140,
            wedgeprops={'edgecolor': BG, 'linewidth': 1.5}
        )
        for t in texts + autotexts:
            t.set_color(TEXT)
        ax.set_title('Доля выручки по производителям', color=GOLD, pad=10)
        plt.tight_layout()
        charts['by_manufacturer'] = _fig_to_b64(fig)
        plt.close(fig)

    # Клиенты по городам
    by_city = list(
        Client.objects.values('city')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:10]
    )
    if by_city:
        labels_c = [r['city'] or '—' for r in by_city]
        vals_c   = [r['cnt'] for r in by_city]
        fig, ax  = plt.subplots(figsize=(8, 4))
        ax.bar(labels_c, vals_c, color=PALETTE[1], alpha=0.85)
        ax.set_title('Клиенты по городам', color=GOLD, pad=10)
        ax.set_ylabel('Количество клиентов')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        charts['by_city'] = _fig_to_b64(fig)
        plt.close(fig)

    # Сводная по кварталам
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    q_counts, q_totals = [], []
    for months in [(1,2,3),(4,5,6),(7,8,9),(10,11,12)]:
        qs = Order.objects.filter(
            status='completed', sale_date__year=year, sale_date__month__in=months
        ).aggregate(s=Sum('total_amount'), c=Count('id'))
        q_counts.append(int(qs['c'] or 0))
        q_totals.append(float(qs['s'] or 0))

    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax2  = ax1.twinx()
    xpos = np.arange(4)
    w    = 0.35
    ax1.bar(xpos - w/2, q_totals, w, color=GOLD,       alpha=0.85, label='Выручка (BYN)')
    ax2.bar(xpos + w/2, q_counts, w, color=PALETTE[1], alpha=0.75, label='Кол-во заказов')
    ax1.set_xticks(xpos)
    ax1.set_xticklabels(quarters)
    ax1.set_ylabel('Выручка (BYN)', color=GOLD)
    ax2.set_ylabel('Заказов', color=PALETTE[1])
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax1.set_title(f'Сводная диаграмма по кварталам {year}', color=GOLD, pad=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    plt.tight_layout()
    charts['quarterly'] = _fig_to_b64(fig)
    plt.close(fig)

    # Топ моделей
    top_cars = list(
        OrderItem.objects.filter(order__status='completed')
        .values('car__manufacturer__name', 'car__name')
        .annotate(total_qty=Sum('quantity'), total_rev=Sum(F('quantity') * F('unit_price')))
        .order_by('-total_qty')[:10]
    )
    if top_cars:
        labels_tc = [f"{r['car__manufacturer__name']} {r['car__name']}" for r in top_cars]
        vals_tc   = [int(r['total_qty']) for r in top_cars]
        fig, ax   = plt.subplots(figsize=(9, max(4, len(labels_tc) * 0.55 + 1)))
        bars = ax.barh(labels_tc[::-1], vals_tc[::-1],
                       color=[PALETTE[i % len(PALETTE)] for i in range(len(labels_tc))],
                       alpha=0.85)
        ax.set_title('Топ моделей по количеству продаж', color=GOLD, pad=10)
        ax.set_xlabel('Количество')
        ax.grid(axis='x', linestyle='--', alpha=0.4)
        for bar, val in zip(bars, vals_tc[::-1]):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                    str(val), va='center', fontsize=9, color=TEXT)
        plt.tight_layout()
        charts['top_cars'] = _fig_to_b64(fig)
        plt.close(fig)

    return charts


# ─────────────────────────────────────
# External API helpers
# ─────────────────────────────────────

def get_weather(city='Minsk'):
    key = settings.OPENWEATHER_API_KEY
    if not key:
        return None
    try:
        url = (f'https://api.openweathermap.org/data/2.5/weather'
               f'?q={city}&appid={key}&units=metric&lang=ru')
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


# ─────────────────────────────────────
# Public pages
# ─────────────────────────────────────

def index(request):
    logger.info('Home page accessed')
    latest_article = Article.objects.filter(is_published=True).first()
    featured_cars  = Car.objects.filter(status='available').select_related('manufacturer', 'car_type')[:6]
    weather   = get_weather()
    rates     = get_exchange_rates()
    now_utc   = timezone.now()
    now_local = timezone.localtime(now_utc)
    cal_text  = calendar.month(now_local.year, now_local.month)

    return render(request, 'catalog/index.html', {
        'latest_article': latest_article,
        'featured_cars': featured_cars,
        'weather': weather,
        'rates': rates,
        'now_utc_str': now_utc.strftime('%d.%m.%Y %H:%M'),
        'now_local_str': now_local.strftime('%d.%m.%Y %H:%M'),
        'now_utc': now_utc,
        'now_local': now_local,
        'calendar': cal_text,
        'company': CompanyInfo.objects.first(),
        'partners': Partner.objects.all(),
    })


# ─────────────────────────────────────
# Cart (session-based)
# ─────────────────────────────────────

def _get_cart(request):
    return request.session.setdefault('cart', {})


def cart_detail(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0')
    if cart:
        cars = Car.objects.filter(pk__in=[int(k) for k in cart.keys()]).select_related('manufacturer')
        cars_by_id = {c.pk: c for c in cars}
        for car_id, qty in cart.items():
            car = cars_by_id.get(int(car_id))
            if not car:
                continue
            subtotal = car.price * qty
            total += subtotal
            items.append({'car': car, 'quantity': qty, 'subtotal': subtotal})
    return render(request, 'catalog/cart_detail.html', {'items': items, 'total': total})


@require_POST
def cart_add(request, pk):
    car = get_object_or_404(Car, pk=pk)
    cart = _get_cart(request)
    key = str(pk)
    cart[key] = cart.get(key, 0) + 1
    request.session.modified = True
    messages.success(request, f'«{car}» добавлен в корзину.')
    return redirect(request.POST.get('next') or 'cart_detail')


@require_POST
def cart_remove(request, pk):
    cart = _get_cart(request)
    cart.pop(str(pk), None)
    request.session.modified = True
    return redirect('cart_detail')


@require_POST
def cart_update(request, pk):
    cart = _get_cart(request)
    key = str(pk)
    action = request.POST.get('action')
    if key in cart:
        if action == 'inc':
            cart[key] += 1
        elif action == 'dec':
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]
    request.session.modified = True
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Корзина пуста.')
        return redirect('cart_detail')
    if not hasattr(request.user, 'client_profile'):
        messages.warning(request, 'Заполните профиль клиента перед оплатой.')
        return redirect('profile')

    cars = Car.objects.filter(pk__in=[int(k) for k in cart.keys()])
    cars_by_id = {c.pk: c for c in cars}
    items = [{'car': cars_by_id[int(cid)], 'quantity': qty}
              for cid, qty in cart.items() if int(cid) in cars_by_id]
    total = sum(i['car'].price * i['quantity'] for i in items)

    if request.method == 'POST':
        client = request.user.client_profile
        order = Order.objects.create(client=client, status='pending', total_amount=total)
        for i in items:
            OrderItem.objects.create(order=order, car=i['car'], quantity=i['quantity'], unit_price=i['car'].price)
            i['car'].status = 'reserved'
            i['car'].save(update_fields=['status'])
        request.session['cart'] = {}
        request.session.modified = True
        logger.info(f'Checkout: order #{order.pk} created by {request.user}')
        messages.success(request, f'Оплата прошла успешно! Заказ #{order.pk} оформлен.')
        return redirect('order_detail', pk=order.pk)

    return render(request, 'catalog/checkout.html', {'items': items, 'total': total})


def car_list(request):
    form = CarSearchForm(request.GET)
    cars = Car.objects.select_related('manufacturer', 'car_type').all()
    form.fields['car_type'].widget.choices = (
        [('', 'Все типы')] + list(CarType.objects.values_list('id', 'name'))
    )
    form.fields['manufacturer'].widget.choices = (
        [('', 'Все марки')] + list(Manufacturer.objects.values_list('id', 'name'))
    )
    if form.is_valid():
        q         = form.cleaned_data.get('q')
        ct        = form.cleaned_data.get('car_type')
        mfr       = form.cleaned_data.get('manufacturer')
        fuel      = form.cleaned_data.get('fuel')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        only_available = form.cleaned_data.get('only_available')
        sort      = form.cleaned_data.get('sort')
        if q:
            cars = cars.filter(
                Q(name__icontains=q) | Q(manufacturer__name__icontains=q) | Q(vin__icontains=q)
            )
        if ct:             cars = cars.filter(car_type_id=ct)
        if mfr:            cars = cars.filter(manufacturer_id=mfr)
        if fuel:           cars = cars.filter(fuel=fuel)
        if price_min:      cars = cars.filter(price__gte=price_min)
        if price_max:      cars = cars.filter(price__lte=price_max)
        if only_available: cars = cars.filter(status='available')
        if sort:           cars = cars.order_by(sort)
    return render(request, 'catalog/car_list.html', {'form': form, 'cars': cars})


def car_detail(request, pk):
    car     = get_object_or_404(Car, pk=pk)
    reviews = car.reviews.select_related('client').all()
    review_form = ReviewForm(initial={'car': car})
    return render(request, 'catalog/car_detail.html', {
        'car': car,
        'reviews': reviews,
        'review_form': review_form,
    })


# ─────────────────────────────────────
# Car CRUD (staff only)
# ─────────────────────────────────────

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
            form.save()
            messages.success(request, 'Автомобиль обновлён.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm(instance=car)
    return render(request, 'catalog/car_form.html', {
        'form': form, 'title': 'Редактировать автомобиль', 'car': car
    })


@staff_member_required
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Автомобиль удалён.')
        return redirect('car_list')
    return render(request, 'catalog/car_confirm_delete.html', {'car': car})


# ─────────────────────────────────────
# Orders — КЛИЕНТ создаёт заявку
# ─────────────────────────────────────

@login_required
def client_order_create(request, car_pk):
    """
    Клиент нажимает «Заказать» на карточке авто.
    Создаётся заявка со статусом 'pending'.
    Менеджер затем подтверждает её.
    """
    car = get_object_or_404(Car, pk=car_pk)

    if car.status != 'available':
        messages.warning(request, 'Этот автомобиль уже недоступен.')
        return redirect('car_detail', pk=car.pk)

    # Создаём профиль клиента автоматически, если его нет
    if not hasattr(request.user, 'client_profile'):
        messages.warning(request, 'Заполните профиль клиента перед оформлением заказа.')
        return redirect('profile')

    client = request.user.client_profile

    if request.method == 'POST':
        form = ClientOrderForm(request.POST)
        if form.is_valid():
            # Создаём заказ со статусом pending
            order = Order.objects.create(
                client=client,
                status='pending',
                total_amount=car.price,
                comment=form.cleaned_data.get('comment', ''),
            )
            OrderItem.objects.create(
                order=order,
                car=car,
                quantity=1,
                unit_price=car.price,
            )
            # Резервируем авто
            car.status = 'reserved'
            car.save(update_fields=['status'])

            logger.info(f'Client order #{order.pk} created by {request.user} for car {car}')
            messages.success(request, f'Заявка #{order.pk} принята! Менеджер свяжется с вами.')
            return redirect('my_orders')
    else:
        form = ClientOrderForm()

    return render(request, 'catalog/client_order_create.html', {
        'form': form,
        'car': car,
    })


# ─────────────────────────────────────
# Orders — МЕНЕДЖЕР подтверждает заявку
# ─────────────────────────────────────

@login_required
def order_confirm(request, pk):
    """
    Менеджер открывает заявку клиента, проверяет данные клиента,
    добавляет/корректирует позиции, устанавливает даты и подтверждает.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Доступ запрещён.')
        return redirect('index')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        confirm_form = OrderConfirmForm(request.POST, instance=order)
        item_formset = OrderItemFormSet(request.POST, instance=order)
        client_form  = ClientQuickForm(request.POST, instance=order.client)

        if confirm_form.is_valid() and item_formset.is_valid() and client_form.is_valid():
            # Сохраняем актуальные данные клиента
            client_form.save()

            # Назначаем менеджера автоматически
            order = confirm_form.save(commit=False)
            if hasattr(request.user, 'employee_profile') and not order.employee:
                order.employee = request.user.employee_profile
            order.save()

            # Сохраняем позиции
            item_formset.save()
            order.recalculate_total()

            # Обновляем статус авто
            for item in order.items.all():
                if order.status == 'completed':
                    item.car.status = 'sold'
                    item.car.save(update_fields=['status'])
                elif order.status in ('approved', 'pending'):
                    item.car.status = 'reserved'
                    item.car.save(update_fields=['status'])
                elif order.status == 'cancelled':
                    item.car.status = 'available'
                    item.car.save(update_fields=['status'])

            logger.info(f'Order #{order.pk} confirmed by {request.user}, status={order.status}')
            messages.success(request, f'Заказ #{order.pk} обновлён: {order.get_status_display()}')
            return redirect('order_detail', pk=order.pk)
    else:
        confirm_form = OrderConfirmForm(instance=order)
        item_formset = OrderItemFormSet(instance=order)
        client_form  = ClientQuickForm(instance=order.client)

    return render(request, 'catalog/order_confirm.html', {
        'order':        order,
        'confirm_form': confirm_form,
        'item_formset': item_formset,
        'client_form':  client_form,
    })


@login_required
def order_list(request):
    """Список заказов с разным доступом"""
    if request.user.is_superuser:
        orders = Order.objects.select_related('client', 'employee').prefetch_related('items__car__manufacturer')
    elif hasattr(request.user, 'employee_profile'):
        # Менеджер видит ВСЕ заказы (не только свои) — чтобы подтверждать новые
        orders = Order.objects.select_related('client', 'employee').prefetch_related('items__car')
    else:
        return redirect('my_orders')

    status = request.GET.get('status', '')
    q      = request.GET.get('q', '')
    if status:
        orders = orders.filter(status=status)
    if q:
        orders = orders.filter(
            Q(client__last_name__icontains=q) |
            Q(client__first_name__icontains=q) |
            Q(client__phone__icontains=q)
        )
    return render(request, 'catalog/order_list.html', {
        'orders':          orders.order_by('-created_at'),
        'status_choices':  Order.STATUS_CHOICES,
        'current_status':  status,
        'q':               q,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    # Клиент может видеть только свои заказы
    if not request.user.is_staff and not request.user.is_superuser:
        if not hasattr(request.user, 'client_profile') or \
                order.client != request.user.client_profile:
            messages.error(request, 'Нет доступа.')
            return redirect('my_orders')
    return render(request, 'catalog/order_detail.html', {'order': order})


@login_required
def order_create(request):
    """Ручное создание заказа менеджером/суперюзером (без авто из карточки)"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Доступ запрещён.')
        return redirect('index')

    if request.method == 'POST':
        order_form   = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)
        if order_form.is_valid() and item_formset.is_valid():
            order = order_form.save(commit=False)
            if not order.employee and hasattr(request.user, 'employee_profile'):
                order.employee = request.user.employee_profile
            order.save()
            item_formset.instance = order
            item_formset.save()
            order.recalculate_total()
            for item in order.items.all():
                if order.status == 'completed':
                    item.car.status = 'sold'
                    item.car.save(update_fields=['status'])
                elif order.status in ('approved', 'pending'):
                    item.car.status = 'reserved'
                    item.car.save(update_fields=['status'])
            logger.info(f'Order #{order.pk} manually created by {request.user}')
            messages.success(request, f'Заказ #{order.pk} создан.')
            return redirect('order_detail', pk=order.pk)
    else:
        order_form   = OrderForm()
        item_formset = OrderItemFormSet()

    return render(request, 'catalog/order_create.html', {
        'order_form': order_form,
        'item_formset': item_formset,
    })


@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Доступ запрещён.')
        return redirect('index')
    if request.method == 'POST':
        order_form   = OrderForm(request.POST, instance=order)
        item_formset = OrderItemFormSet(request.POST, instance=order)
        if order_form.is_valid() and item_formset.is_valid():
            order = order_form.save()
            item_formset.save()
            order.recalculate_total()
            messages.success(request, 'Заказ обновлён.')
            return redirect('order_detail', pk=order.pk)
    else:
        order_form   = OrderForm(instance=order)
        item_formset = OrderItemFormSet(instance=order)
    return render(request, 'catalog/order_create.html', {
        'order_form': order_form,
        'item_formset': item_formset,
        'editing': True,
        'order': order,
    })


@login_required
def my_orders(request):
    if not hasattr(request.user, 'client_profile'):
        return redirect('profile')
    orders = request.user.client_profile.orders.prefetch_related(
        'items__car__manufacturer'
    ).order_by('-created_at')
    return render(request, 'catalog/my_orders.html', {'orders': orders})


# ─────────────────────────────────────
# Clients (staff)
# ─────────────────────────────────────

@login_required
def client_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('index')

    q    = request.GET.get('q', '')
    city = request.GET.get('city', '')

    # Менеджер видит только клиентов, заказы которых он вёл
    if request.user.is_superuser:
        clients = Client.objects.all()
    elif hasattr(request.user, 'employee_profile'):
        # Клиенты, чьи заказы ведёт этот менеджер
        client_ids = Order.objects.filter(
            employee=request.user.employee_profile
        ).values_list('client_id', flat=True).distinct()
        clients = Client.objects.filter(id__in=client_ids)
    else:
        clients = Client.objects.none()

    if q:
        clients = clients.filter(
            Q(last_name__icontains=q) | Q(first_name__icontains=q) |
            Q(phone__icontains=q)     | Q(email__icontains=q)
        )
    if city:
        clients = clients.filter(city__icontains=city)

    cities = Client.objects.values_list('city', flat=True).distinct().order_by('city')

    return render(request, 'catalog/client_list.html', {
        'clients': clients.order_by('last_name', 'first_name'),
        'cities': cities,
        'q': q,
        'city': city,
    })


@login_required
def client_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('index')
    from django.contrib.auth.models import User as DjangoUser
    if request.method == 'POST':
        form = ClientQuickForm(request.POST)
        if form.is_valid():
            phone    = form.cleaned_data['phone']
            username = 'client_' + ''.join(c for c in phone if c.isdigit())
            user, _  = DjangoUser.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': form.cleaned_data['first_name'],
                    'last_name':  form.cleaned_data['last_name'],
                    'email':      form.cleaned_data['email'],
                }
            )
            client = form.save(commit=False)
            client.user = user
            client.save()
            messages.success(request, f'Клиент {client.full_name()} добавлен.')
            return redirect('client_list')
    else:
        form = ClientQuickForm()
    return render(request, 'catalog/client_form.html', {'form': form, 'title': 'Добавить клиента'})


@login_required
def client_update(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('index')
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientQuickForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные клиента обновлены.')
            return redirect('client_list')
    else:
        form = ClientQuickForm(instance=client)
    return render(request, 'catalog/client_form.html', {
        'form': form, 'title': 'Редактировать клиента', 'client': client
    })


@login_required
def client_detail(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('index')
    client = get_object_or_404(Client, pk=pk)
    orders = client.orders.prefetch_related('items__car').order_by('-created_at')
    return render(request, 'catalog/client_detail.html', {
        'client': client, 'orders': orders
    })


# ─────────────────────────────────────
# Reviews
# ─────────────────────────────────────

@login_required
@require_POST
def review_create(request):
    if not hasattr(request.user, 'client_profile'):
        messages.warning(request, 'Заполните профиль клиента.')
        return redirect('profile')
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.client = request.user.client_profile
        review.save()
        messages.success(request, 'Отзыв добавлен.')
    else:
        messages.error(request, 'Ошибка при добавлении отзыва.')
    return redirect(request.POST.get('next', '/'))


def reviews_list(request):
    reviews     = Review.objects.select_related('client', 'car__manufacturer').all()
    review_form = None
    if request.user.is_authenticated and hasattr(request.user, 'client_profile'):
        review_form = ReviewForm()
    return render(request, 'catalog/reviews.html', {
        'reviews': reviews, 'review_form': review_form,
    })


# ─────────────────────────────────────
# Content pages
# ─────────────────────────────────────

def about(request):
    return render(request, 'catalog/about.html', {'company': CompanyInfo.objects.first()})

def news_list(request):
    return render(request, 'catalog/news_list.html',
                  {'articles': Article.objects.filter(is_published=True)})

def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, 'catalog/news_detail.html', {'article': article})

def faq(request):
    return render(request, 'catalog/faq.html', {'faqs': FAQ.objects.all()})

def contacts(request):
    return render(request, 'catalog/contacts.html', {
        'contacts': Contact.objects.all(),
        'company':  CompanyInfo.objects.first(),
    })

def privacy(request):
    return render(request, 'catalog/privacy.html')

def vacancies(request):
    return render(request, 'catalog/vacancies.html',
                  {'jobs': Vacancy.objects.filter(is_active=True)})

def promos(request):
    return render(request, 'catalog/promos.html', {
        'active':   Promo.objects.filter(status='active'),
        'archived': Promo.objects.filter(status='archived'),
    })


# ─────────────────────────────────────
# Analytics (superuser) / Statistics (staff)
# ─────────────────────────────────────

@staff_member_required
def analytics_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Страница доступна только суперпользователю.')
        return redirect('index')

    current_year = int(request.GET.get('year', date.today().year))
    logger.info(f'Analytics by {request.user}, year={current_year}')

    price_list = (
        Car.objects.filter(status='available')
        .values('car_type__name', 'manufacturer__name', 'name', 'year',
                'price', 'fuel', 'transmission')
        .order_by('car_type__name', 'price')
    )

    city_groups = {}
    for c in Client.objects.order_by('city', 'last_name'):
        city_groups.setdefault(c.city or '—', []).append(c)

    # Топ товаров — список словарей с индексом для шаблона
    top_cars_qs = list(
        OrderItem.objects.filter(order__status='completed')
        .values('car__manufacturer__name', 'car__name', 'car__car_type__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_rev=Sum(F('quantity') * F('unit_price'))
        )
        .order_by('-total_qty')[:10]
    )
    # Добавляем порядковый номер прямо в Python
    top_cars = [{'idx': i + 1, **row} for i, row in enumerate(top_cars_qs)]
    most_popular = top_cars[0] if top_cars else None

    monthly_data = []
    for m in range(1, 13):
        qs = Order.objects.filter(
            status='completed', sale_date__year=current_year, sale_date__month=m,
        ).aggregate(revenue=Sum('total_amount'), count=Count('id'))
        by_type_month = list(
            OrderItem.objects
            .filter(order__status='completed',
                    order__sale_date__year=current_year,
                    order__sale_date__month=m)
            .values('car__car_type__name')
            .annotate(qty=Sum('quantity'), rev=Sum(F('quantity') * F('unit_price')))
            .order_by('-rev')
        )
        monthly_data.append({
            'month':   calendar.month_name[m],
            'revenue': float(qs['revenue'] or 0),
            'count':   int(qs['count'] or 0),
            'by_type': by_type_month,
        })

    annual_qs = Order.objects.filter(
        status='completed', sale_date__year=current_year
    ).aggregate(
        total_revenue=Sum('total_amount'), total_orders=Count('id'),
        avg_order=Avg('total_amount'), max_order=Max('total_amount'),
        min_order=Min('total_amount'),
    )
    annual = {k: float(v) if v is not None else 0 for k, v in annual_qs.items()}
    annual['total_orders'] = int(annual['total_orders'])

    pivot_by_type = list(
        OrderItem.objects
        .filter(order__status='completed', order__sale_date__year=current_year)
        .values('car__car_type__name')
        .annotate(qty=Sum('quantity'), revenue=Sum(F('quantity') * F('unit_price')))
        .order_by('-revenue')
    )
    pivot_by_mfr = list(
        OrderItem.objects
        .filter(order__status='completed', order__sale_date__year=current_year)
        .values('car__manufacturer__name')
        .annotate(qty=Sum('quantity'), revenue=Sum(F('quantity') * F('unit_price')))
        .order_by('-revenue')
    )
    pivot_by_client = list(
        Order.objects
        .filter(status='completed', sale_date__year=current_year)
        .values('client__last_name', 'client__first_name',
                'client__city', 'client__phone')
        .annotate(orders_count=Count('id'), total_spent=Sum('total_amount'))
        .order_by('-total_spent')[:20]
    )

    charts = _matplotlib_charts(current_year)

    years_qs = Order.objects.filter(status='completed').dates('sale_date', 'year')
    available_years = sorted({d.year for d in years_qs}, reverse=True)
    if current_year not in available_years:
        available_years.insert(0, current_year)

    return render(request, 'catalog/analytics.html', {
        'year':             current_year,
        'available_years':  available_years,
        'price_list':       price_list,
        'city_groups':      city_groups,
        'top_cars':         top_cars,
        'most_popular':     most_popular,
        'monthly_data':     monthly_data,
        'annual':           annual,
        'pivot_by_type':    pivot_by_type,
        'pivot_by_mfr':     pivot_by_mfr,
        'pivot_by_client':  pivot_by_client,
        'charts':           charts,
    })


@staff_member_required
def statistics_view(request):
    current_year = date.today().year
    orders  = Order.objects.filter(status='completed')
    prices  = [float(o.total_amount) for o in orders if o.total_amount]
    by_type = (
        Car.objects.values('car_type__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    now_utc   = timezone.now()
    now_local = timezone.localtime(now_utc)
    return render(request, 'catalog/statistics.html', {
        'total_sales':  sum(prices),
        'avg_price':    statistics.mean(prices) if prices else 0,
        'median_price': statistics.median(prices) if prices else 0,
        'orders_count': len(prices),
        'by_type':      by_type,
        'current_year': current_year,
        'now_utc':      now_utc,
        'now_local':    now_local,
    })


# ─────────────────────────────────────
# JSON API
# ─────────────────────────────────────

def _require_auth(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    return None

def api_cars(request):
    err = _require_auth(request)
    if err: return err
    cars = list(Car.objects.filter(status='available')
                .values('id', 'name', 'manufacturer__name', 'year', 'price', 'fuel', 'status'))
    return JsonResponse({'cars': cars})

def api_stats(request):
    err = _require_auth(request)
    if err: return err
    return JsonResponse({
        'total_cars':       Car.objects.count(),
        'available':        Car.objects.filter(status='available').count(),
        'total_orders':     Order.objects.count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
    })