from django.contrib import admin

from .models import Localidad, Provincia


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia', 'departamento')
    list_filter = ('provincia',)
    search_fields = ('nombre', 'departamento')
    autocomplete_fields = ('provincia',)
