from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Manufacturer, CarType, Feature, Car,
    Employee, Client, Order, OrderItem,
    Article, FAQ, Review, Vacancy, Promo, CompanyInfo, Contact
)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'website']
    search_fields = ['name', 'country']


@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['car', 'quantity', 'unit_price', 'subtotal_display']
    readonly_fields = ['subtotal_display']

    def subtotal_display(self, obj):
        if obj.pk:
            return format_html('<strong>{}</strong> BYN', obj.subtotal)
        return '—'
    subtotal_display.short_description = 'Сумма'


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display  = ['name', 'manufacturer', 'car_type', 'year', 'price', 'status', 'mileage']
    list_filter   = ['status', 'car_type', 'manufacturer', 'fuel', 'transmission', 'year']
    search_fields = ['name', 'vin', 'manufacturer__name']
    list_editable = ['price', 'status']
    filter_horizontal = ['features']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'role', 'phone', 'hired_at']
    list_filter   = ['role']
    search_fields = ['user__first_name', 'user__last_name', 'phone']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'phone', 'email', 'city', 'created_at']
    list_filter   = ['city']
    search_fields = ['last_name', 'first_name', 'phone', 'city', 'email']

    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = 'ФИО'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'client', 'employee', 'status', 'total_amount', 'sale_date', 'delivery_date']
    list_filter   = ['status', 'sale_date', 'employee']
    search_fields = ['client__last_name', 'client__phone']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    inlines       = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ['order', 'car', 'quantity', 'unit_price']
    search_fields = ['car__name', 'car__manufacturer__name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display  = ['title', 'published_at', 'is_published']
    list_editable = ['is_published']
    search_fields = ['title']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ['question', 'added_at']
    search_fields = ['question']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client', 'car', 'rating', 'created_at']
    list_filter  = ['rating']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display  = ['title', 'salary_from', 'salary_to', 'is_active']
    list_editable = ['is_active']


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display  = ['code', 'discount_percent', 'valid_until', 'status']
    list_editable = ['status']


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display  = ['name', 'position', 'phone', 'email']
    search_fields = ['name', 'position']
