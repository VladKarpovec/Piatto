from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address', 'email', 'payment_method']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше ім’я'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефону'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Адреса доставки', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Електронна пошта'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Ім’я',
            'phone': 'Телефон',
            'address': 'Адреса доставки',
            'email': 'Email',
            'payment_method': 'Спосіб оплати',
        }
