from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/<str:username>/', views.perfil_view, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),    path('convertir-propietario/', views.convertir_a_propietario, name='convertir_propietario'),
    
    # Validaciones
    path('validar-telefono/', views.validar_telefono, name='validar_telefono'),
    path('validar-email/', views.validar_email, name='validar_email'),
    path('cerrar-banner-validacion/', views.cerrar_banner_validacion, name='cerrar_banner_validacion'),
    
    # Cambiar teléfono y email
    path('cambiar-telefono/', views.cambiar_telefono, name='cambiar_telefono'),
    path('ingresar-nuevo-telefono/', views.ingresar_nuevo_telefono, name='ingresar_nuevo_telefono'),
    path('verificar-nuevo-telefono/', views.verificar_nuevo_telefono, name='verificar_nuevo_telefono'),
    path('cambiar-email/', views.cambiar_email, name='cambiar_email'),
    path('ingresar-nuevo-email/', views.ingresar_nuevo_email, name='ingresar_nuevo_email'),
    path('verificar-nuevo-email/', views.verificar_nuevo_email, name='verificar_nuevo_email'),
]
