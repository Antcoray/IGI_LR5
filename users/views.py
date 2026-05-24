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
            user = form.save()
            login(request, user)
            logger.info(f'New user registered: {user.username}')
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('profile')
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

    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)

    if request.method == 'POST':
        if client:
            form = ClientProfileForm(request.POST, instance=client)
        else:
            form = ClientProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = ClientProfileForm(instance=client) if client else ClientProfileForm()

    orders = []
    if client:
        orders = client.orders.select_related('car__manufacturer').order_by('-created_at')[:5]

    return render(request, 'users/profile.html', {
        'form': form,
        'client': client,
        'employee': employee,
        'orders': orders,
        'now_utc': now_utc,
        'now_local': now_local,
    })
