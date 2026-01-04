from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo', 'fecha_registro', 'is_active']
    list_filter = ['tipo', 'is_active', 'fecha_registro']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo', 'telefono', 'foto_perfil', 'fecha_nacimiento', 'direccion', 'biografia', 'recibir_notificaciones')
        }),
    )

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'verificado', 'puntuacion_promedio', 'total_valoraciones']
    list_filter = ['verificado']
    search_fields = ['usuario__username', 'usuario__email']
