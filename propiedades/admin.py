from django.contrib import admin
from .models import Categoria, Propiedad, ImagenPropiedad, Favorito, Valoracion, ReporteValoracion

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'color', 'orden']
    list_editable = ['orden']

class ImagenPropiedadInline(admin.TabularInline):
    model = ImagenPropiedad
    extra = 1
    max_num = 10

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'propietario', 'tipo', 'precio', 'ciudad', 'estado', 'vistas', 'fecha_publicacion']
    list_filter = ['estado', 'tipo', 'ciudad', 'destacada']
    search_fields = ['titulo', 'descripcion', 'ciudad', 'distrito']
    inlines = [ImagenPropiedadInline]
    readonly_fields = ['vistas', 'fecha_publicacion', 'fecha_actualizacion']

@admin.register(ImagenPropiedad)
class ImagenPropiedadAdmin(admin.ModelAdmin):
    list_display = ['propiedad', 'orden', 'es_principal', 'fecha_subida']
    list_filter = ['es_principal']

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'propiedad', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['usuario__username', 'propiedad__titulo']

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'propiedad', 'promedio_total_display', 'fecha_valoracion', 'reportada', 'total_reportes']
    list_filter = ['fecha_valoracion', 'reportada']
    search_fields = ['usuario__username', 'propiedad__titulo', 'comentario']
    readonly_fields = ['fecha_valoracion', 'fecha_ultima_edicion', 'total_reportes']
    
    def promedio_total_display(self, obj):
        return f'{obj.promedio_total():.1f}⭐'
    promedio_total_display.short_description = 'Promedio Total'


@admin.register(ReporteValoracion)
class ReporteValoracionAdmin(admin.ModelAdmin):
    list_display = ['valoracion', 'reportado_por', 'motivo', 'fecha_reporte', 'revisado']
    list_filter = ['motivo', 'revisado', 'fecha_reporte']
    search_fields = ['valoracion__propiedad__titulo', 'reportado_por__username', 'descripcion']
    readonly_fields = ['fecha_reporte']
    actions = ['marcar_como_revisado']
    
    def marcar_como_revisado(self, request, queryset):
        queryset.update(revisado=True)
    marcar_como_revisado.short_description = 'Marcar como revisado'
