from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import Order, OrderItem, Review, Car, Client


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
            'last_name':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'first_name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'patronymic':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'phone':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375 (29) XXX-XX-XX'}),
            'email':           forms.EmailInput(attrs={'class': 'form-control'}),
            'address':         forms.TextInput(attrs={'class': 'form-control'}),
            'city':            forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HB'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567'}),
        }


class ClientOrderForm(forms.Form):
    """Форма оформления заказа клиентом — только комментарий,
    всё остальное заполняет менеджер при подтверждении."""
    comment = forms.CharField(
        required=False,
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'Пожелания, вопросы, удобное время звонка…',
        })
    )


class OrderConfirmForm(forms.ModelForm):
    """Менеджер подтверждает заказ: заполняет цену, даты, статус"""
    class Meta:
        model = Order
        fields = ['status', 'sale_date', 'delivery_date', 'comment']
        widgets = {
            'status':        forms.Select(attrs={'class': 'form-select'}),
            'sale_date':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comment':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
            'client':        forms.Select(attrs={'class': 'form-select'}),
            'employee':      forms.Select(attrs={'class': 'form-select'}),
            'status':        forms.Select(attrs={'class': 'form-select'}),
            'sale_date':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comment':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
            'car':        forms.Select(attrs={'class': 'form-select'}),
            'quantity':   forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    extra=1, min_num=1, validate_min=True, can_delete=True,
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text', 'car']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'text':   forms.Textarea(attrs={'rows': 4, 'class': 'form-control',
                                            'placeholder': 'Ваш отзыв…'}),
            'car':    forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) < 10:
            raise ValidationError('Отзыв должен содержать не менее 10 символов.')
        return text


class CarSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск…'})
    )
    car_type = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    manufacturer = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fuel = forms.ChoiceField(
        required=False,
        choices=[('', 'Любое'), ('petrol', 'Бензин'), ('diesel', 'Дизель'),
                 ('electric', 'Электро'), ('hybrid', 'Гибрид')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    price_min = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена от'})
    )
    price_max = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена до'})
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[('', 'По умолчанию'), ('-created_at', 'Сначала новые'),
                 ('price', 'Цена ↑'), ('-price', 'Цена ↓'),
                 ('year', 'Год ↑'), ('-year', 'Год ↓')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


