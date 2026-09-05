# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from .models import Propiedad, ImagenPropiedad, Valoracion
from usuarios.models import PublicacionCompanero
from ubicaciones.models import Provincia

class PropiedadForm(forms.ModelForm):
    """Formulario para crear/editar propiedades"""
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'tipo', 'operacion', 'precio', 'moneda',
            'incluye_expensas', 'tipo_contacto',
            'provincia', 'ciudad', 'distrito', 'direccion',
            'area', 'habitaciones', 'banos',
            'estacionamiento', 'amoblado', 'mascotas',
            'balcon', 'patio', 'parrilla', 'aire_acondicionado', 'calefaccion', 'ascensor',
            'terraza', 'wifi', 'lavanderia',
            'seguridad', 'accesibilidad', 'piscina', 'gimnasio', 'sauna', 'jacuzzi',
            'quincho', 'solarium', 'area_deportiva',
            'especial_estudiantes'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
            # El campo visible de provincia es un autocomplete de LaColmena
            # (ver static/js/ubicacion.js); este input oculto es el que
            # realmente guarda el id de ubicaciones.Provincia seleccionado.
            'provincia': forms.HiddenInput(),
            'ciudad': forms.TextInput(attrs={'placeholder': 'Ej: Merlo', 'autocomplete': 'off'}),
            'distrito': forms.TextInput(attrs={'placeholder': 'Ej: Centro', 'autocomplete': 'off'}),
            'direccion': forms.TextInput(attrs={'autocomplete': 'off'}),
        }
        labels = {
            'especial_estudiantes': 'Especial para estudiantes',
            'aire_acondicionado': 'Aire acondicionado',
            'calefaccion': 'Calefacción',
            'balcon': 'Balcón',
            'wifi': 'Wi-Fi',
            'lavanderia': 'Lavandería',
            'area_deportiva': 'Área deportiva',
        }
        help_texts = {
            'especial_estudiantes': 'Marca esta opción si tu propiedad está dirigida especialmente a estudiantes',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el campo título obligatorio
        self.fields['titulo'].required = True
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'rounded text-yellow-500 focus:ring-yellow-500'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent'


class ImagenPropiedadForm(forms.ModelForm):
    """Formulario para subir imágenes de propiedades"""
    class Meta:
        model = ImagenPropiedad
        fields = ['imagen', 'orden', 'es_principal']


class BusquedaForm(forms.Form):
    """Formulario de búsqueda de propiedades"""
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-11 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Barrio, localidad o dirección...',
            # El reset global de <input> en base.html pisa el padding-left de
            # Tailwind con !important - este atributo activa la excepción de
            # ese mismo archivo (mismo patron que el input del modal "Mi
            # ubicacion") para que el icono no tape el texto.
            'data-busqueda-hero': 'true',
        })
    )
    tipo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Propiedad.TIPO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )
    operacion = forms.ChoiceField(
        required=False,
        choices=[('', 'Selecciona'), ('alquiler', 'Alquiler'), ('venta', 'Venta')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.all(),
        required=False,
        empty_label='Todas las provincias',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )
    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Ciudad'
        })
    )
    distrito = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Barrio / Distrito'
        })
    )
    moneda = forms.ChoiceField(
        required=False,
        choices=Propiedad.MONEDA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )
    precio_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Mínimo',
            'style': 'appearance: textfield; -moz-appearance: textfield; -webkit-appearance: none;'
        })
    )
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Máximo',
            'style': 'appearance: textfield; -moz-appearance: textfield; -webkit-appearance: none;'
        })
    )


class BusquedaCompaneroForm(forms.Form):
    """Formulario de búsqueda de publicaciones de compañero/a"""
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Palermo, 2 ambientes...'
        })
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.all(),
        required=False,
        empty_label='Todas las provincias',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )
    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Ciudad'
        })
    )
    distrito = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Barrio / Distrito'
        })
    )
    moneda = forms.ChoiceField(
        required=False,
        choices=PublicacionCompanero.MONEDA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )
    precio_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Mínimo',
            'style': 'appearance: textfield; -moz-appearance: textfield; -webkit-appearance: none;'
        })
    )
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Máximo',
            'style': 'appearance: textfield; -moz-appearance: textfield; -webkit-appearance: none;'
        })
    )
    preferencia_genero = forms.ChoiceField(
        required=False,
        choices=[('', 'Cualquiera')] + PublicacionCompanero._meta.get_field('preferencia_genero').choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
        })
    )


class ValoracionForm(forms.ModelForm):
    """Formulario para valorar propiedades y propietarios"""
    class Meta:
        model = Valoracion
        fields = [
            'claridad_informacion', 'coincidencia_fotos', 'ubicacion_correcta',
            'tiempo_respuesta', 'trato', 'confiabilidad',
            'comentario'
        ]
        widgets = {
            'claridad_informacion': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'coincidencia_fotos': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'ubicacion_correcta': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'tiempo_respuesta': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'trato': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'confiabilidad': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Comparte tu experiencia (opcional)'
            }),
        }
        labels = {
            'claridad_informacion': 'Claridad de la información',
            'coincidencia_fotos': 'Coincidencia fotos / realidad',
            'ubicacion_correcta': 'Ubicación correcta',
            'tiempo_respuesta': 'Tiempo de respuesta',
            'trato': 'Trato',
            'confiabilidad': 'Confiabilidad',
            'comentario': 'Comentario (opcional)'
        }
    
    def __init__(self, *args, puede_valorar_publicacion=True, **kwargs):
        super().__init__(*args, **kwargs)
        # Si no puede valorar publicación, hacer esos campos opcionales y ocultos
        if not puede_valorar_publicacion:
            self.fields['claridad_informacion'].required = False
            self.fields['coincidencia_fotos'].required = False
            self.fields['ubicacion_correcta'].required = False

