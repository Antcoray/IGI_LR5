import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone


# ────────────────────────────────────────────────
# Validators
# ────────────────────────────────────────────────

def validate_phone(value):
    """Телефон в формате +375 (XX) XXX-XX-XX"""
    pattern = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Телефон должен быть в формате +375 (XX) XXX-XX-XX')


def validate_adult(value):
    """Возрастное ограничение 18+"""
    if value:
        today = timezone.now().date()
        age = (today - value).days // 365
        if age < 18:
            raise ValidationError('Возраст должен быть 18+')


# ────────────────────────────────────────────────
# Reference / Directory models
# ────────────────────────────────────────────────

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
    """Тип кузова автомобиля"""
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


# ────────────────────────────────────────────────
# Main product model
# ────────────────────────────────────────────────

class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('MT', 'Механика'), ('AT', 'Автомат'),
        ('CVT', 'Вариатор'), ('DCT', 'Робот'),
    ]
    FUEL_CHOICES = [
        ('petrol', 'Бензин'), ('diesel', 'Дизель'),
        ('electric', 'Электро'), ('hybrid', 'Гибрид'),
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
        Feature, blank=True, related_name='cars', verbose_name='Опции'
    )
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.manufacturer.name} {self.name} ({self.year})'


# ────────────────────────────────────────────────
# People
# ────────────────────────────────────────────────

class Employee(models.Model):
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
    """Клиент автосалона — анкетные данные"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='client_profile', verbose_name='Пользователь'
    )
    # Стандартные анкетные данные
    last_name = models.CharField('Фамилия', max_length=100, blank=True)
    first_name = models.CharField('Имя', max_length=100, blank=True)
    patronymic = models.CharField('Отчество', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20, validators=[validate_phone])
    email = models.EmailField('Email')
    address = models.CharField('Адрес', max_length=255, blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    birth_date = models.DateField('Дата рождения', validators=[validate_adult])
    passport_series = models.CharField('Серия паспорта', max_length=10, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    created_at = models.DateTimeField('Зарегистрирован', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['last_name', 'first_name']

    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(p for p in parts if p) or self.user.get_full_name() or self.user.username

    def __str__(self):
        return f'{self.full_name()} — {self.city}'


# ────────────────────────────────────────────────
# Orders / Sales
# ────────────────────────────────────────────────

class Order(models.Model):
    """Заказ / Продажа — фиксируется сотрудником"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    # Клиент — стандартные анкетные данные
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT,
        related_name='orders', verbose_name='Клиент'
    )
    # Сотрудник, фиксирующий продажу
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Сотрудник'
    )
    status = models.CharField('Статус', max_length=15, choices=STATUS_CHOICES, default='pending')

    # Даты, которые фиксирует сотрудник
    sale_date = models.DateField('Дата продажи', null=True, blank=True)
    delivery_date = models.DateField('Дата доставки', null=True, blank=True)

    # Итог
    total_amount = models.DecimalField(
        'Итоговая сумма (BYN)', max_digits=14, decimal_places=2, default=0
    )
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def recalculate_total(self):
        """Пересчитать итоговую сумму по позициям"""
        total = sum(
            item.quantity * item.unit_price
            for item in self.items.all()
        )
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def __str__(self):
        return f'Заказ #{self.pk} — {self.client} ({self.get_status_display()})'


class OrderItem(models.Model):
    """Позиция заказа: конкретный автомобиль + количество + цена"""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='Заказ'
    )
    car = models.ForeignKey(
        Car, on_delete=models.PROTECT,
        related_name='order_items', verbose_name='Автомобиль'
    )
    quantity = models.PositiveSmallIntegerField('Количество', default=1)
    unit_price = models.DecimalField(
        'Цена за единицу (BYN)', max_digits=12, decimal_places=2
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f'{self.car} × {self.quantity} = {self.subtotal} BYN'


# ────────────────────────────────────────────────
# Site content models
# ────────────────────────────────────────────────

class Article(models.Model):
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
    name = models.CharField('Название компании', max_length=200)
    description = models.TextField('Описание')
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20, validators=[validate_phone])
    email = models.EmailField('Email')
    founded_year = models.PositiveSmallIntegerField('Год основания', null=True, blank=True)
    logo = models.ImageField('Логотип', upload_to='company/', blank=True, null=True)
    video_url = models.URLField('Видео о компании (ссылка)', blank=True)
    requisites = models.TextField('Реквизиты', blank=True)
    certificate_text = models.TextField('Текст сертификата', blank=True)

    class Meta:
        verbose_name = 'О компании'
        verbose_name_plural = 'О компании'

    def __str__(self):
        return self.name


class CompanyHistoryEvent(models.Model):
    """Событие истории компании по годам"""
    company = models.ForeignKey(
        CompanyInfo, on_delete=models.CASCADE,
        related_name='history_events', verbose_name='Компания'
    )
    year = models.PositiveSmallIntegerField('Год')
    description = models.TextField('Описание события')

    class Meta:
        verbose_name = 'Событие истории'
        verbose_name_plural = 'История компании'
        ordering = ['year']

    def __str__(self):
        return f'{self.year}: {self.description[:50]}'


class Partner(models.Model):
    """Партнёр автосалона"""
    name = models.CharField('Название', max_length=200)
    logo = models.ImageField('Логотип', upload_to='partners/', blank=True, null=True)
    website = models.URLField('Сайт', blank=True)

    class Meta:
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Contact(models.Model):
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
