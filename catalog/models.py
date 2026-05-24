from django.db import models
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone

def validate_phone(value):
    """Телефон в формате +375 (XX) XXX-XX-XX"""
    pattern = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Телефон должен быть в формате +375 (XX) XXX-XX-XX'
        )
    
def validate_adult(value):
    """Возрастное ограничение """
    if value:
        today = timezone.now().date()
        age = (today - value).days // 365
        if age < 18:
            raise ValidationError('Возраст должен быть 18+')

class Manufacturer(models.Model):
    """Изготовитель / Производитель автомобиля"""
    name = models.CharField('Название', max_length=100)
    country = models.CharField('Страна', max_length=100)
    website = models.URLField('Сайт', blank=True)
    logo = models.ImageField('Логотип', upload_to='manufacturers/', blank=True, null=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.country})'
    
class CarType(models.Model):
    """Тип товара / Класс автомобиля"""
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Тип кузова'
        verbose_name_plural = 'Типы кузова'
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Feature(models.Model):
    """Опция/характеристика (M2M с автомобилем)"""
    name = models.CharField('Опция', max_length=100)

    class Meta:
        verbose_name = 'Опция'
        verbose_name_plural = 'Опции'

    def __str__(self):
        return self.name
    
class Car(models.Model):
    """Автомобиль — основной товар автосалона"""
    TRANSMISSION_CHOICES = [
        ('MT', 'Механика'),
        ('AT', 'Автомат'),
        ('CVT', 'Вариатор'),
        ('DCT', 'Робот'),
    ]
    FUEL_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('electric', 'Электро'),
        ('hybrid', 'Гибрид'),
    ]
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('reserved', 'Зарезервирован'),
        ('sold', 'Продан'),
    ]

    vin = models.CharField('VIN', max_length=17, unique=True)
    name = models.CharField('Модель', max_length=200)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT,
        related_name='cars', verbose_name='Производитель'
    )
    car_type = models.ForeignKey(
        CarType, on_delete=models.PROTECT,
        related_name='cars', verbose_name='Тип кузова'
    )
    year = models.PositiveSmallIntegerField('Год выпуска')
    price = models.DecimalField('Цена (BYN)', max_digits=12, decimal_places=2)
    mileage = models.PositiveIntegerField('Пробег (км)', default=0)
    color = models.CharField('Цвет', max_length=50)
    transmission = models.CharField('Трансмиссия', max_length=3, choices=TRANSMISSION_CHOICES)
    fuel = models.CharField('Тип топлива', max_length=10, choices=FUEL_CHOICES)
    engine_volume = models.DecimalField('Объём двигателя (л)', max_digits=4, decimal_places=1)
    horsepower = models.PositiveSmallIntegerField('Мощность (л.с.)')
    description = models.TextField('Описание', blank=True)
    photo = models.ImageField('Фото', upload_to='cars/', blank=True, null=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='available')
    features = models.ManyToManyField(
        Feature, blank=True,
        related_name='cars', verbose_name='Опции'
    )
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.manufacturer.name} {self.name} ({self.year})'
    
class Employee(models.Model):
    """Сотрудник автосалона"""
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('director', 'Директор'),
        ('mechanic', 'Механик'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='employee_profile', verbose_name='Пользователь'
    )
    role = models.CharField('Должность', max_length=20, choices=ROLE_CHOICES, default='manager')
    phone = models.CharField('Телефон', max_length=20, validators=[validate_phone])
    birth_date = models.DateField('Дата рождения', validators=[validate_adult])
    photo = models.ImageField('Фото', upload_to='employees/', blank=True, null=True)
    hired_at = models.DateField('Дата найма', default=timezone.now)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.get_role_display()})'
    
class Client(models.Model):
    """Клиент автосалона"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='client_profile', verbose_name='Пользователь'
    )
    phone = models.CharField('Телефон', max_length=20, validators=[validate_phone])
    address = models.CharField('Адрес', max_length=255, blank=True)
    birth_date = models.DateField('Дата рождения', validators=[validate_adult])
    city = models.CharField('Город', max_length=100, blank=True)
    email = models.EmailField('Email', blank=True)
    created_at = models.DateTimeField('Зарегистрирован', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.city}'
    
class Order(models.Model):
    """Заказ / Продажа"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT,
        related_name='orders', verbose_name='Клиент'
    )
    car = models.ForeignKey(
        Car, on_delete=models.PROTECT,
        related_name='orders', verbose_name='Автомобиль'
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Менеджер'
    )
    status = models.CharField('Статус', max_length=15, choices=STATUS_CHOICES, default='pending')
    sale_price = models.DecimalField('Цена продажи (BYN)', max_digits=12, decimal_places=2)
    sale_date = models.DateField('Дата продажи', null=True, blank=True)
    delivery_date = models.DateField('Дата доставки', null=True, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.car} ({self.get_status_display()})'
    
class Article(models.Model):
    """Новости"""
    title = models.CharField('Заголовок', max_length=255)
    summary = models.CharField('Краткое содержание', max_length=500)
    content = models.TextField('Полный текст')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

class FAQ(models.Model):
    """Словарь терминов / FAQ"""
    question = models.CharField('Вопрос', max_length=255)
    answer = models.TextField('Ответ')
    added_at = models.DateField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['-added_at']

    def __str__(self):
        return self.question

class Review(models.Model):
    """Отзыв"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Клиент'
    )
    car = models.ForeignKey(
        Car, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviews', verbose_name='Автомобиль'
    )
    rating = models.PositiveSmallIntegerField('Оценка', choices=RATING_CHOICES)
    text = models.TextField('Текст отзыва')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.client} ({self.rating}★)'
    
class Vacancy(models.Model):
    """Вакансии"""
    title = models.CharField('Должность', max_length=200)
    description = models.TextField('Описание')
    salary_from = models.DecimalField('Зарплата от', max_digits=10, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField('Зарплата до', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateField('Добавлена', auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class Promo(models.Model):
    """Промокоды и купоны"""
    STATUS_CHOICES = [('active', 'Активен'), ('archived', 'Архив')]
    code = models.CharField('Код', max_length=50, unique=True)
    discount_percent = models.PositiveSmallIntegerField('Скидка (%)')
    description = models.CharField('Описание', max_length=255, blank=True)
    valid_until = models.DateField('Действует до', null=True, blank=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

    def __str__(self):
        return f'{self.code} (-{self.discount_percent}%)'
    
class CompanyInfo(models.Model):
    """О компании"""
    name = models.CharField('Название компании', max_length=200)
    description = models.TextField('Описание')
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20, validators=[validate_phone])
    email = models.EmailField('Email')
    founded_year = models.PositiveSmallIntegerField('Год основания', null=True, blank=True)
    logo = models.ImageField('Логотип', upload_to='company/', blank=True, null=True)

    class Meta:
        verbose_name = 'О компании'
        verbose_name_plural = 'О компании'

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    """Контакты сотрудников (отдельно от Employee — для публичной страницы)"""
    name = models.CharField('ФИО', max_length=200)
    position = models.CharField('Должность', max_length=200)
    phone = models.CharField('Телефон', max_length=20, validators=[validate_phone])
    email = models.EmailField('Email')
    photo = models.ImageField('Фото', upload_to='contacts/', blank=True, null=True)
    description = models.TextField('Описание работ', blank=True)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return self.name