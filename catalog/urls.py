from django.urls import path, re_path
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('promos/', views.promos, name='promos'),
    path('faq/', views.faq, name='faq'),

    # News
    path('news/', views.news_list, name='news_list'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),

    # Cars — CRUD
    path('cars/', views.car_list, name='car_list'),
    re_path(r'^cars/(?P<pk>\d+)/$', views.car_detail, name='car_detail'),
    path('cars/new/', views.car_create, name='car_create'),
    re_path(r'^cars/(?P<pk>\d+)/edit/$', views.car_update, name='car_update'),
    re_path(r'^cars/(?P<pk>\d+)/delete/$', views.car_delete, name='car_delete'),

    # Orders — клиент создаёт, менеджер подтверждает
    # car_pk передаётся при создании заказа клиентом
    re_path(r'^cars/(?P<car_pk>\d+)/order/$', views.client_order_create, name='client_order_create'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    re_path(r'^orders/(?P<pk>\d+)/$', views.order_detail, name='order_detail'),
    re_path(r'^orders/(?P<pk>\d+)/confirm/$', views.order_confirm, name='order_confirm'),
    re_path(r'^orders/(?P<pk>\d+)/edit/$', views.order_update, name='order_update'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Clients (staff)
    path('clients/', views.client_list, name='client_list'),
    path('clients/new/', views.client_create, name='client_create'),
    re_path(r'^clients/(?P<pk>\d+)/$', views.client_detail, name='client_detail'),
    re_path(r'^clients/(?P<pk>\d+)/edit/$', views.client_update, name='client_update'),

    # Reviews
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/add/', views.review_create, name='review_create'),

    # Analytics (superuser) / Statistics (staff)
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('statistics/', views.statistics_view, name='statistics'),

    # Cart / Checkout
    path('cart/', views.cart_detail, name='cart_detail'),
    re_path(r'^cart/add/(?P<pk>\d+)/$', views.cart_add, name='cart_add'),
    re_path(r'^cart/remove/(?P<pk>\d+)/$', views.cart_remove, name='cart_remove'),
    re_path(r'^cart/update/(?P<pk>\d+)/$', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),

    # JSON API
    path('api/cars/', views.api_cars, name='api_cars'),
    path('api/stats/', views.api_stats, name='api_stats'),
]

