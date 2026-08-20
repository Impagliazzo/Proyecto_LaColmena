from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Perfil

class RegistroForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    telefono = forms.CharField(max_length=15, required=True, label='Teléfono')
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
        
        # Quitar validaciones de contraseña
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Configurar username
        self.fields['username'].max_length = 150
        self.fields['username'].help_text = None
    
    def clean_first_name(self):
        """Validar que el nombre comience con mayúscula"""
        nombre = self.cleaned_data.get('first_name', '').strip()
        if nombre:
            # Capitalizar: primera letra en mayúscula, resto en minúscula
            nombre = nombre.capitalize()
        return nombre
    
    def clean_last_name(self):
        """Validar que el apellido comience con mayúscula"""
        apellido = self.cleaned_data.get('last_name', '').strip()
        if apellido:
            # Capitalizar: primera letra en mayúscula, resto en minúscula
            apellido = apellido.capitalize()
        return apellido
    
    def clean_username(self):
        """Validar que el usuario no esté vacío y no esté duplicado"""
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            raise forms.ValidationError('El nombre de usuario es obligatorio.')
        
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        
        return username
    
    def clean_password2(self):
        """Remover validación de contraseñas por ahora"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return password2
    
    def _post_clean(self):
        """Sobrescribir para omitir validaciones de contraseña de Django"""
        super(forms.ModelForm, self)._post_clean()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telefono = self.cleaned_data.get('telefono', '')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent',
            'placeholder': 'Contraseña'
        })
    )


class CompletarPerfilForm(forms.ModelForm):
    """Formulario para completar el perfil progresivo"""
    class Meta:
        model = Perfil
        fields = ['tipo_usuario', 'objetivo_principal']
        labels = {
            'tipo_usuario': '¿Quién sos?',
            'objetivo_principal': '¿Qué estás buscando?',
        }
        widgets = {
            'tipo_usuario': forms.RadioSelect(),
            'objetivo_principal': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los radios
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-radio text-yellow-500'


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil"""
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 
                  'direccion', 'biografia', 'foto_perfil', 'recibir_notificaciones']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'biografia': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'rounded text-yellow-500 focus:ring-yellow-500'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent'


class ValidarTelefonoForm(forms.Form):
    """Formulario para validar teléfono con código"""
    codigo = forms.CharField(
        max_length=6,
        label='Código de verificación',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-amber-500',
            'placeholder': 'Ingresa el código de 6 dígitos'
        })
    )


class ValidarEmailForm(forms.Form):
    """Formulario para validar email con código"""
    codigo = forms.CharField(
        max_length=6,
        label='Código de verificación',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-amber-500',
            'placeholder': 'Ingresa el código de 6 dígitos'
        })
    )


class CambiarTelefonoForm(forms.Form):
    """Formulario para cambiar teléfono"""
    telefono = forms.CharField(
        max_length=15,
        label='Nuevo teléfono',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-amber-500',
            'placeholder': '+54 11 1234-5678'
        })
    )


class CambiarEmailForm(forms.Form):
    """Formulario para cambiar email"""
    email = forms.EmailField(
        label='Nuevo email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-amber-500',
            'placeholder': 'nuevo@ejemplo.com'
        })
    )


class PerfilBusquedaForm(forms.ModelForm):
    """Formulario para completar el perfil de búsqueda de compañero/a"""
    
    # Definir las opciones para cada categoría de etiquetas
    HABITOS_VICIOS_CHOICES = [
        ('fumador', '🚬 Fumador'),
        ('vaper', '💨 Vaper'),
        ('drink_friendly', '🍺 Drink Friendly'),
        ('abstemio', '🥤 Abstemio'),
        ('ruidoso_pero_majo', '📢 Ruidoso Pero Majo'),
        ('modo_silencio', '🔇 Modo Silencio'),
        ('gamer', '🎮 Gamer'),
    ]
    
    MASCOTAS_CHOICES = [
        ('dog_lover', '🐕 Dog Lover'),
        ('cat_lover', '🐈 Cat Lover'),
        ('mascota_exotica', '🦎 Mascota Exótica'),
        ('pet_friendly', '🐾 Pet Friendly'),
    ]
    
    CONVIVENCIA_LIMPIEZA_CHOICES = [
        ('limpio', '🍽️ Limpio'),
        ('manana_lo_lavo', '🕐 Mañana Lo Lavo'),
        ('caos_bajo_control', '🌪️ Caos Bajo Control'),
        ('team_limpieza', '✨ Team Limpieza'),
        ('sin_filtros', '💬 Sin Filtros'),
        ('nudista_light', '🩲 Nudista Light'),
    ]
    
    HORARIOS_TRABAJO_CHOICES = [
        ('home_office', '💻 Home Office'),
        ('casi_nunca_estoy', '🚪 Casi Nunca Estoy'),
        ('night_owl', '🦉 Night Owl'),
        ('early_bird', '🐓 Early Bird'),
        ('ronco_un_poco', '😴 Ronco Un Poco'),
    ]
    
    COMIDA_SOCIAL_CHOICES = [
        ('chef_en_casa', '👨‍🍳 Chef En Casa'),
        ('rey_del_delivery', '📦 Rey Del Delivery'),
        ('vegan_vibes', '🥗 Vegan Vibes'),
        ('casa_social', '🎉 Casa Social'),
        ('full_privacidad', '🔒 Full Privacidad'),
        ('pareja_visitante', '💑 Pareja Visitante'),
    ]
    
    # Campos de checkboxes múltiples para cada categoría
    habitos_vicios = forms.MultipleChoiceField(
        choices=HABITOS_VICIOS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Hábitos y Vicios'
    )
    
    mascotas_tags = forms.MultipleChoiceField(
        choices=MASCOTAS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Mascotas'
    )
    
    convivencia_limpieza = forms.MultipleChoiceField(
        choices=CONVIVENCIA_LIMPIEZA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Convivencia y Limpieza'
    )
    
    horarios_trabajo = forms.MultipleChoiceField(
        choices=HORARIOS_TRABAJO_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Horarios y Trabajo'
    )
    
    comida_social = forms.MultipleChoiceField(
        choices=COMIDA_SOCIAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Comida y Social'
    )
    
    class Meta:
        model = Perfil
        fields = [
            'situacion_actual',
            'presentacion',
            'edad',
            'genero',
            'situacion_laboral',
            'universidad',
            'modalidad_estudio',
            'empresa_rubro',
            'modalidad_trabajo',
            'habitos_vicios',
            'mascotas_tags',
            'convivencia_limpieza',
            'horarios_trabajo',
            'comida_social',
        ]
        labels = {
            'situacion_actual': '¿Cuál es tu situación actual?',
            'presentacion': 'Sobre mí',
            'edad': 'Edad',
            'genero': 'Género',
            'situacion_laboral': 'Situación laboral/académica',
            'universidad': 'Universidad',
            'modalidad_estudio': 'Modalidad de estudio',
            'empresa_rubro': 'Empresa o rubro en el que trabajas',
            'modalidad_trabajo': 'Modalidad de trabajo',
        }
        widgets = {
            'situacion_actual': forms.RadioSelect(),
            'presentacion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ejemplo: Hola! Soy estudiante de Ingeniería, busco un lugar tranquilo para compartir cerca de la facultad. Me gusta la música pero uso auriculares, soy ordenado y responsable con los gastos...'}),
            'genero': forms.RadioSelect(),
            'situacion_laboral': forms.RadioSelect(),
            'modalidad_estudio': forms.RadioSelect(),
            'modalidad_trabajo': forms.RadioSelect(),
            'edad': forms.NumberInput(attrs={'min': '18', 'max': '100'}),
            'universidad': forms.TextInput(),
            'empresa_rubro': forms.TextInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando un perfil existente, cargar las etiquetas seleccionadas
        if self.instance and self.instance.pk:
            self.fields['habitos_vicios'].initial = self.instance.habitos_vicios or []
            self.fields['mascotas_tags'].initial = self.instance.mascotas_tags or []
            self.fields['convivencia_limpieza'].initial = self.instance.convivencia_limpieza or []
            self.fields['horarios_trabajo'].initial = self.instance.horarios_trabajo or []
            self.fields['comida_social'].initial = self.instance.comida_social or []
        
        # Estilos base para todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = 'form-radio text-amber-500 focus:ring-amber-500'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'rounded text-amber-500 focus:ring-amber-500 h-5 w-5'
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'checkbox-group'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none'
            elif isinstance(field.widget, (forms.Select, forms.TextInput, forms.NumberInput, forms.DateInput)):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent'
        
        # Asegurar que situacion_actual no tenga valor inicial
        self.fields['situacion_actual'].initial = None
        self.fields['genero'].initial = None
        self.fields['situacion_laboral'].initial = None
        
        # Campos condicionales - inicialmente no son requeridos
        self.fields['universidad'].required = False
        self.fields['modalidad_estudio'].required = False
        self.fields['empresa_rubro'].required = False
        self.fields['modalidad_trabajo'].required = False
    
    def clean(self):
        """Validación personalizada para campos condicionales"""
        cleaned_data = super().clean()
        
        # Validar edad mínima
        edad = cleaned_data.get('edad')
        if edad and edad < 18:
            self.add_error('edad', 'Debes tener al menos 18 años.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar las etiquetas seleccionadas en formato lista"""
        instance = super().save(commit=False)
        
        # Guardar las etiquetas seleccionadas
        instance.habitos_vicios = self.cleaned_data.get('habitos_vicios', [])
        instance.mascotas_tags = self.cleaned_data.get('mascotas_tags', [])
        instance.convivencia_limpieza = self.cleaned_data.get('convivencia_limpieza', [])
        instance.horarios_trabajo = self.cleaned_data.get('horarios_trabajo', [])
        instance.comida_social = self.cleaned_data.get('comida_social', [])
        
        if commit:
            instance.save()
        
        return instance

class PublicacionCompaneroForm(forms.ModelForm):
    """Formulario para crear/editar publicación de búsqueda de compañero/a"""
    
    class Meta:
        # Importar el modelo directamente - ya no hay importación circular porque
        # el modelo está definido en el mismo archivo models.py antes de importarse aquí
        from .models import PublicacionCompanero
        model = PublicacionCompanero
        fields = [
            'titulo', 'descripcion', 'provincia', 'ciudad', 'distrito', 'direccion',
            'habitaciones_totales', 'habitaciones_disponibles', 'banos', 'amoblado',
            'balcon', 'cocina', 'wifi', 'lavarropas', 'aire_acondicionado', 'calefaccion',
            'moneda', 'precio_mensual', 'expensas_incluidas', 'servicios_incluidos',
            'preferencia_genero', 'acepta_mascotas', 'fumador_acepto',
            'fecha_disponibilidad'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Ej: Busco compañero/a para compartir depto 2 ambientes en Palermo'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Contanos sobre el departamento, la zona, y qué buscás en un compañero/a...'
            }),
            # El campo visible de provincia es un autocomplete de LaColmena
            # (ver static/js/ubicacion.js); este input oculto guarda el id
            # de ubicaciones.Provincia realmente seleccionado.
            'provincia': forms.HiddenInput(),
            'ciudad': forms.TextInput(attrs={'placeholder': 'Ej: Ciudad de Buenos Aires', 'autocomplete': 'off'}),
            'distrito': forms.TextInput(attrs={'placeholder': 'Ej: Palermo', 'autocomplete': 'off'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Ej: Cerca de Av. Santa Fe y Av. Scalabrini Ortiz', 'autocomplete': 'off'}),
            'fecha_disponibilidad': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'Desde cuándo está disponible'
            }),
        }
        labels = {
            'titulo': 'Título de tu publicación',
            'descripcion': 'Descripción',
            'provincia': 'Provincia',
            'ciudad': 'Ciudad',
            'distrito': 'Barrio/Distrito',
            'direccion': 'Dirección aproximada',
            'habitaciones_totales': 'Habitaciones totales del depto',
            'habitaciones_disponibles': 'Habitaciones disponibles',
            'banos': 'Baños',
            'amoblado': 'Habitación amoblada',
            'balcon': 'Tiene balcón o terraza',
            'cocina': 'Cocina equipada',
            'wifi': 'WiFi',
            'lavarropas': 'Lavarropas',
            'aire_acondicionado': 'Aire acondicionado',
            'calefaccion': 'Calefacción',
            'precio_mensual': 'Precio por persona',
            'moneda': 'Moneda',
            'expensas_incluidas': 'Expensas incluidas',
            'servicios_incluidos': 'Servicios incluidos (luz, gas, agua, internet)',
            'preferencia_genero': 'Preferencia de género',
            'acepta_mascotas': 'Acepta mascotas',
            'fumador_acepto': 'Acepta fumadores',
            'fecha_disponibilidad': 'Disponible desde',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Marcar campos como requeridos explícitamente
        self.fields['precio_mensual'].required = True
        self.fields['titulo'].required = True
        self.fields['descripcion'].required = True
        self.fields['ciudad'].required = True
        self.fields['distrito'].required = True
        self.fields['direccion'].required = True
        self.fields['habitaciones_totales'].required = True
        self.fields['habitaciones_disponibles'].required = True
        self.fields['banos'].required = True
        self.fields['preferencia_genero'].required = True
        
        # Los campos booleanos no deben ser requeridos (False por defecto)
        self.fields['amoblado'].required = False
        self.fields['balcon'].required = False
        self.fields['cocina'].required = False
        self.fields['wifi'].required = False
        self.fields['lavarropas'].required = False
        self.fields['aire_acondicionado'].required = False
        self.fields['calefaccion'].required = False
        self.fields['expensas_incluidas'].required = False
        self.fields['servicios_incluidos'].required = False
        self.fields['acepta_mascotas'].required = False
        self.fields['fumador_acepto'].required = False
        
        # Aplicar estilos Tailwind
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'rounded text-amber-500 focus:ring-amber-500 h-5 w-5'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none'
            elif isinstance(field.widget, (forms.Select, forms.TextInput, forms.NumberInput, forms.DateInput)):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent'
    
    def clean_habitaciones_disponibles(self):
        """Validar que las habitaciones disponibles no sean mayores que las totales"""
        disponibles = self.cleaned_data.get('habitaciones_disponibles')
        totales = self.cleaned_data.get('habitaciones_totales')
        
        if disponibles and totales and disponibles > totales:
            raise forms.ValidationError(
                'Las habitaciones disponibles no pueden ser más que las habitaciones totales.'
            )
        
        return disponibles
    
    def clean_precio_mensual(self):
        """Validar que el precio sea razonable (los límites dependen de la moneda)"""
        precio = self.cleaned_data.get('precio_mensual')

        if not precio:
            raise forms.ValidationError('El precio mensual es obligatorio.')

        if self.cleaned_data.get('moneda') == 'USD':
            minimo, maximo = 10, 5000
        else:
            minimo, maximo = 1000, 1000000

        if precio < minimo:
            raise forms.ValidationError('El precio parece demasiado bajo. Verificá que sea correcto.')

        if precio > maximo:
            raise forms.ValidationError('El precio parece demasiado alto. Verificá que sea correcto.')

        return precio