import logging
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from catalog.models import Client, Order
from .forms import ClientProfileForm, LoginForm, RegisterForm
from django.http import HttpRequest

logger = logging.getLogger('users')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Создаём пользователя
            user = form.save()
            
            # Создаём профиль клиента с данными из формы
            client = Client.objects.create(
                user=user,
                last_name=form.cleaned_data['last_name'],
                first_name=form.cleaned_data['first_name'],
                patronymic=form.cleaned_data.get('patronymic', ''),
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data.get('address', ''),
                city=form.cleaned_data.get('city', ''),
                birth_date=form.cleaned_data['birth_date'],
                passport_series=form.cleaned_data.get('passport_series', ''),
                passport_number=form.cleaned_data.get('passport_number', '')
            )
            
            # Автоматически логиним пользователя
            login(request, user)
            
            logger.info(f'New user registered: {user.username} with client profile')
            messages.success(request, f'Добро пожаловать, {user.first_name}! Регистрация успешно завершена.')
            
            return redirect('index')  # или 'profile'
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User logged in: {user.username}')
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logger.info(f'User logged out: {request.user.username}')
        logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    user = request.user
    client = getattr(user, 'client_profile', None)
    employee = getattr(user, 'employee_profile', None)

    # Если нет профиля клиента (старый пользователь), перенаправляем на заполнение
    if not client and not employee:
        messages.warning(request, 'Пожалуйста, заполните профиль.')
        # Можно показать форму или перенаправить на специальную страницу
    
    if request.method == 'POST' and client:
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = ClientProfileForm(instance=client) if client else ClientProfileForm()

    orders = []
    if client:
        orders = client.orders.prefetch_related('items__car__manufacturer').order_by('-created_at')[:5]

    return render(request, 'users/profile.html', {
        'form': form,
        'client': client,
        'employee': employee,
        'orders': orders,
        'now_utc': timezone.now(),
        'now_local': timezone.localtime(timezone.now()),
    })