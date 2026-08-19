from django.contrib import admin
from .models import SolicitudContacto, SolicitudContactoCompanero

@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'propiedad', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['usuario__username', 'propiedad__titulo', 'mensaje']
    readonly_fields = ['fecha_solicitud', 'fecha_actualizacion']


@admin.register(SolicitudContactoCompanero)
class SolicitudContactoCompaneroAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'publicacion', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['usuario__username', 'publicacion__titulo', 'mensaje']
    readonly_fields = ['fecha_solicitud', 'fecha_actualizacion']
