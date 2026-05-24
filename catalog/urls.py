from django.urls import path, re_path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('promos/', views.promos, name='promos'),
    path('faq/', views.faq, name='faq'),

    # News — re_path with regex
    path('news/', views.news_list, name='news_list'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),

    # Cars — CRUD
    path('cars/', views.car_list, name='car_list'),
    re_path(r'^cars/(?P<pk>\d+)/$', views.car_detail, name='car_detail'),
    path('cars/new/', views.car_create, name='car_create'),
    re_path(r'^cars/(?P<pk>\d+)/edit/$', views.car_update, name='car_update'),
    re_path(r'^cars/(?P<pk>\d+)/delete/$', views.car_delete, name='car_delete'),

    # Orders
    re_path(r'^cars/(?P<car_pk>\d+)/order/$', views.order_create, name='order_create'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('employee/orders/', views.employee_orders, name='employee_orders'),

    # Reviews
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/add/', views.review_create, name='review_create'),

    # Statistics
    path('statistics/', views.statistics_view, name='statistics'),

    # JSON API
    path('api/cars/', views.api_cars, name='api_cars'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
