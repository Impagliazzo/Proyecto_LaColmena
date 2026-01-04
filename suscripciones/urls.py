from django.urls import path
from . import views

app_name = 'suscripciones'

urlpatterns = [
    path('planes/', views.planes, name='planes'),
    path('suscribirse/<int:plan_id>/', views.suscribirse, name='suscribirse'),
    path('mi-suscripcion/', views.mi_suscripcion, name='mi_suscripcion'),
    path('cancelar/', views.cancelar_suscripcion, name='cancelar'),
]
