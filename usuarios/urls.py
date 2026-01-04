from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/<str:username>/', views.perfil_view, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),    path('convertir-propietario/', views.convertir_a_propietario, name='convertir_propietario'),
]
