from django import forms
from .models import Ad
from .constants import CATEGORIES

class ProductForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название товара'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Опишите товар подробно'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Введите URL изображения'}),
            'category': forms.Select(choices=CATEGORIES, attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }
