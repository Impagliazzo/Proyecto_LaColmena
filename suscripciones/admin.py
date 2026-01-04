from django.contrib import admin
from .models import PlanSuscripcion, Suscripcion, Pago

@admin.register(PlanSuscripcion)
class PlanSuscripcionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'duracion_dias', 'max_publicaciones', 'activo', 'orden']
    list_editable = ['activo', 'orden']
    list_filter = ['activo', 'destacar_publicaciones']

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'plan', 'estado', 'fecha_inicio', 'fecha_vencimiento', 'auto_renovar']
    list_filter = ['estado', 'auto_renovar', 'fecha_inicio']
    search_fields = ['usuario__username', 'plan__nombre']
    readonly_fields = ['fecha_inicio']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['suscripcion', 'monto', 'metodo', 'estado', 'fecha_pago']
    list_filter = ['estado', 'metodo', 'fecha_pago']
    search_fields = ['suscripcion__usuario__username', 'referencia']
    readonly_fields = ['fecha_pago', 'fecha_actualizacion']
