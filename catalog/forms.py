from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import Order, OrderItem, Review, Car, Client


class TelInput(forms.TextInput):
    """input type=tel — телефонная клавиатура на мобильных, но не блокирует ввод формата"""
    input_type = 'tel'


class ClientQuickForm(forms.ModelForm):
    """Форма быстрой фиксации / редактирования клиента сотрудником"""
    class Meta:
        model = Client
        fields = [
            'last_name', 'first_name', 'patronymic',
            'phone', 'email', 'address', 'city',
            'birth_date', 'passport_series', 'passport_number',
        ]
        widgets = {
            'last_name':       forms.TextInput(attrs={'class': 'input', 'placeholder': 'Фамилия'}),
            'first_name':      forms.TextInput(attrs={'class': 'input', 'placeholder': 'Имя'}),
            'patronymic':      forms.TextInput(attrs={'class': 'input', 'placeholder': 'Отчество'}),
            'phone':           TelInput(attrs={
                'class': 'input', 'placeholder': '+375 (29) XXX-XX-XX',
                'pattern': r'\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}',
                'title': 'Формат: +375 (XX) XXX-XX-XX',
            }),
            'email':           forms.EmailInput(attrs={'class': 'input'}),
            'address':         forms.TextInput(attrs={'class': 'input'}),
            'city':            forms.TextInput(attrs={'class': 'input', 'list': 'city-datalist'}),
            'birth_date':      forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'passport_series': forms.TextInput(attrs={'class': 'input', 'placeholder': 'HB'}),
            'passport_number': forms.TextInput(attrs={'class': 'input', 'placeholder': '1234567'}),
        }


class ClientOrderForm(forms.Form):
    """Форма оформления заказа клиентом — только комментарий,
    всё остальное заполняет менеджер при подтверждении."""
    comment = forms.CharField(
        required=False,
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={
            'class': 'input', 'rows': 3,
            'placeholder': 'Пожелания, вопросы, удобное время звонка…',
        })
    )


class OrderConfirmForm(forms.ModelForm):
    """Менеджер подтверждает заказ: заполняет цену, даты, статус"""
    class Meta:
        model = Order
        fields = ['status', 'sale_date', 'delivery_date', 'comment']
        widgets = {
            'status':        forms.Select(attrs={'class': 'input'}),
            'sale_date':     forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'comment':       forms.Textarea(attrs={'class': 'input', 'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        sale_date     = cleaned.get('sale_date')
        delivery_date = cleaned.get('delivery_date')
        if sale_date and delivery_date and delivery_date < sale_date:
            raise ValidationError('Дата доставки не может быть раньше даты продажи.')
        return cleaned


class OrderForm(forms.ModelForm):
    """Полная форма заказа (создание вручную менеджером/суперюзером)"""
    class Meta:
        model = Order
        fields = ['client', 'employee', 'status', 'sale_date', 'delivery_date', 'comment']
        widgets = {
            'client':        forms.Select(attrs={'class': 'input'}),
            'employee':      forms.Select(attrs={'class': 'input'}),
            'status':        forms.Select(attrs={'class': 'input'}),
            'sale_date':     forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'comment':       forms.Textarea(attrs={'class': 'input', 'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        sale_date     = cleaned.get('sale_date')
        delivery_date = cleaned.get('delivery_date')
        if sale_date and delivery_date and delivery_date < sale_date:
            raise ValidationError('Дата доставки не может быть раньше даты продажи.')
        return cleaned


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['car', 'quantity', 'unit_price']
        widgets = {
            'car':        forms.Select(attrs={'class': 'input'}),
            'quantity':   forms.NumberInput(attrs={'class': 'input', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
        }


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    extra=1, min_num=1, validate_min=True, can_delete=True,
)


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES, widget=forms.RadioSelect,
        initial=5, label='Оценка',
    )

    class Meta:
        model = Review
        fields = ['rating', 'text', 'car']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'input',
                                          'placeholder': 'Ваш отзыв…'}),
            'car':  forms.Select(attrs={'class': 'input'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) < 10:
            raise ValidationError('Отзыв должен содержать не менее 10 символов.')
        return text


class CarSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Поиск…'})
    )
    car_type = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'input'})
    )
    manufacturer = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'input'})
    )
    fuel = forms.ChoiceField(
        required=False,
        choices=[('', 'Любое'), ('petrol', 'Бензин'), ('diesel', 'Дизель'),
                 ('electric', 'Электро'), ('hybrid', 'Гибрид')],
        widget=forms.Select(attrs={'class': 'input'})
    )
    price_min = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Цена от'})
    )
    price_max = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Цена до'})
    )
    only_available = forms.BooleanField(
        required=False, label='Только в наличии',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[('', 'По умолчанию'), ('-created_at', 'Сначала новые'),
                 ('price', 'Цена ↑'), ('-price', 'Цена ↓'),
                 ('year', 'Год ↑'), ('-year', 'Год ↓')],
        widget=forms.Select(attrs={'class': 'input'})
    )


