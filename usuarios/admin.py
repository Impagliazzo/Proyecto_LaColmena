from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil, PerfilBusqueda, PublicacionCompanero, ImagenPublicacionCompanero

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


@admin.register(PerfilBusqueda)
class PerfilBusquedaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'situacion_actual', 'edad', 'genero', 'situacion_laboral', 'fecha_creacion']
    list_filter = ['situacion_actual', 'genero', 'situacion_laboral', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__email', 'universidad', 'empresa_rubro']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Situación Actual', {
            'fields': ('situacion_actual',)
        }),
        ('Información Personal', {
            'fields': ('edad', 'genero')
        }),
        ('Situación Laboral/Académica', {
            'fields': ('situacion_laboral', 'universidad', 'modalidad_estudio', 'empresa_rubro', 'modalidad_trabajo')
        }),
        ('Hábitos y Estilo de Vida - Etiquetas', {
            'fields': ('habitos_vicios', 'mascotas_tags', 'convivencia_limpieza', 'horarios_trabajo', 'comida_social')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


class ImagenPublicacionCompaneroInline(admin.TabularInline):
    model = ImagenPublicacionCompanero
    extra = 1


@admin.register(PublicacionCompanero)
class PublicacionCompaneroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'ciudad', 'precio_mensual', 'estado', 'vistas', 'fecha_creacion']
    list_filter = ['estado', 'ciudad', 'preferencia_genero']
    search_fields = ['titulo', 'descripcion', 'usuario__username', 'ciudad', 'distrito']
    inlines = [ImagenPublicacionCompaneroInline]
    readonly_fields = ['vistas', 'fecha_creacion', 'fecha_actualizacion']


@admin.register(ImagenPublicacionCompanero)
class ImagenPublicacionCompaneroAdmin(admin.ModelAdmin):
    list_display = ['publicacion', 'orden', 'fecha_subida']
