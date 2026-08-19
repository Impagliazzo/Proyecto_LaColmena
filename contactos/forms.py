from django import forms
from .models import SolicitudContacto, SolicitudContactoCompanero

class SolicitudContactoForm(forms.ModelForm):
    """Formulario para solicitar contacto con propietario"""
    class Meta:
        model = SolicitudContacto
        fields = ['mensaje', 'telefono', 'email']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Escribe tu mensaje al propietario...'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Tu teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Tu email'
            }),
        }


class SolicitudContactoCompaneroForm(forms.ModelForm):
    """Formulario para solicitar contacto con quien publicó una búsqueda de compañero/a"""
    class Meta:
        model = SolicitudContactoCompanero
        fields = ['mensaje', 'telefono', 'email']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Escribe tu mensaje...'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Tu teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Tu email'
            }),
        }
