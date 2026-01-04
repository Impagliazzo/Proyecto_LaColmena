from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.listar_notificaciones, name='listar'),
    path('marcar-leida/<int:pk>/', views.marcar_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('eliminar/<int:pk>/', views.eliminar_notificacion, name='eliminar'),
]
