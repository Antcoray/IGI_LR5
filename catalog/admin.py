from django.contrib import admin
from .models import (
    Manufacturer, CarType, Feature, Car,
    Employee, Client, Order,
    Article, FAQ, Review, Vacancy, Promo, CompanyInfo, Contact
)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'website']
    search_fields = ['name', 'country']


@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ['client', 'employee', 'status', 'sale_price', 'sale_date']
    readonly_fields = ['created_at']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'car_type', 'year', 'price', 'status', 'mileage']
    list_filter = ['status', 'car_type', 'manufacturer', 'fuel', 'transmission', 'year']
    search_fields = ['name', 'vin', 'manufacturer__name']
    list_editable = ['price', 'status']
    filter_horizontal = ['features']
    inlines = [OrderInline]
    fieldsets = (
        ('Основное', {'fields': ('vin', 'name', 'manufacturer', 'car_type', 'year', 'status', 'photo')}),
        ('Технические характеристики', {'fields': ('fuel', 'transmission', 'engine_volume', 'horsepower', 'mileage', 'color')}),
        ('Цена и описание', {'fields': ('price', 'description', 'features')}),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'role', 'phone', 'hired_at']
    list_filter = ['role']
    search_fields = ['user__first_name', 'user__last_name', 'phone']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'phone', 'city', 'email', 'created_at']
    list_filter = ['city']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'city']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'client', 'car', 'employee', 'status', 'sale_price', 'sale_date', 'created_at']
    list_filter = ['status', 'sale_date', 'employee']
    search_fields = ['client__user__last_name', 'car__name', 'car__vin']
    list_editable = ['status']
    date_hierarchy = 'created_at'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'is_published']
    list_filter = ['is_published']
    search_fields = ['title']
    list_editable = ['is_published']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'added_at']
    search_fields = ['question', 'answer']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client', 'car', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary_from', 'salary_to', 'is_active', 'created_at']
    list_filter = ['is_active']
    list_editable = ['is_active']


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_until', 'status']
    list_filter = ['status']
    list_editable = ['status']


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'phone', 'email']
    search_fields = ['name', 'position']