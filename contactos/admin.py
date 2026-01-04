from django.contrib import admin
from .models import SolicitudContacto

@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'propiedad', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['usuario__username', 'propiedad__titulo', 'mensaje']
    readonly_fields = ['fecha_solicitud', 'fecha_actualizacion']
