from django.urls import path
from . import views

app_name = 'contactos'

urlpatterns = [
    path('solicitar/<int:propiedad_pk>/', views.solicitar_contacto, name='solicitar'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('solicitudes-recibidas/', views.solicitudes_recibidas, name='solicitudes_recibidas'),
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_solicitud, name='cambiar_estado'),

    # Solicitudes de contacto para publicaciones de compañero/a
    path('solicitar-companero/<int:publicacion_pk>/', views.solicitar_contacto_companero, name='solicitar_companero'),
    path('mis-solicitudes-companero/', views.mis_solicitudes_companero, name='mis_solicitudes_companero'),
    path('solicitudes-recibidas-companero/', views.solicitudes_recibidas_companero, name='solicitudes_recibidas_companero'),
    path('cambiar-estado-companero/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_solicitud_companero, name='cambiar_estado_companero'),
]
