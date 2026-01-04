from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Perfil

class RegistroForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    
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
