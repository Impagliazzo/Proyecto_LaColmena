from django.urls import path
from . import views

app_name = 'contactos'

urlpatterns = [
    path('solicitar/<int:propiedad_pk>/', views.solicitar_contacto, name='solicitar'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('solicitudes-recibidas/', views.solicitudes_recibidas, name='solicitudes_recibidas'),
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_solicitud, name='cambiar_estado'),
]
