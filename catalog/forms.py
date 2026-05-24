from django import forms
from django.core.exceptions import ValidationError
from .models import Order, Review, Car


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['car', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'car': forms.HiddenInput(),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text', 'car']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Ваш отзыв...'}),
            'car': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'rating': 'Оценка',
            'text': 'Текст отзыва',
            'car': 'Автомобиль (необязательно)',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) < 10:
            raise ValidationError('Отзыв должен содержать не менее 10 символов.')
        return text


class CarSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по марке, модели, VIN…'})
    )
    car_type = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    manufacturer = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    fuel = forms.ChoiceField(
        required=False,
        choices=[('', 'Любое топливо'), ('petrol', 'Бензин'), ('diesel', 'Дизель'),
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
        choices=[
            ('', 'По умолчанию'), ('-created_at', 'Сначала новые'),
            ('price', 'Цена ↑'), ('-price', 'Цена ↓'),
            ('year', 'Год ↑'), ('-year', 'Год ↓'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )