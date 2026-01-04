from django.urls import path
from . import views

app_name = 'propiedades'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('propiedades/', views.listado_propiedades, name='listado'),
    path('propiedad/<int:pk>/', views.detalle_propiedad, name='detalle'),
    path('crear/', views.crear_propiedad, name='crear'),
    path('editar/<int:pk>/', views.editar_propiedad, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_propiedad, name='eliminar'),
    path('suspender/<int:pk>/', views.suspender_propiedad, name='suspender'),
    path('mis-propiedades/', views.mis_propiedades, name='mis_propiedades'),
    path('toggle-destacado/<int:pk>/', views.toggle_destacado, name='toggle_destacado'),
    path('toggle-especial-estudiantes/<int:pk>/', views.toggle_especial_estudiantes, name='toggle_especial_estudiantes'),
    path('favorito/<int:pk>/', views.toggle_favorito, name='toggle_favorito'),
    path('mis-favoritos/', views.mis_favoritos, name='favoritos'),
    path('valorar/<int:pk>/', views.valorar_propiedad, name='valorar'),
    path('reportar-valoracion/<int:pk>/', views.reportar_valoracion, name='reportar_valoracion'),
    # API endpoints
    path('api/sugerencias-ubicacion/', views.sugerencias_ubicacion, name='sugerencias_ubicacion'),
    # Destacados
    path('destacar/<int:pk>/', views.destacar_propiedad, name='destacar'),
    path('mis-destacados/', views.mis_destacados, name='mis_destacados'),
    # Páginas especiales
    path('estudiantes/', views.estudiantes, name='estudiantes'),
    path('inversiones/', views.inversiones, name='inversiones'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('buscar-companero/', views.buscar_companero, name='buscar_companero'),
]
