from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/<str:username>/', views.perfil_view, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),    path('convertir-propietario/', views.convertir_a_propietario, name='convertir_propietario'),
    path('cambiar-avatar/', views.cambiar_avatar, name='cambiar_avatar'),
    path('actualizar-campo/', views.actualizar_campo_perfil, name='actualizar_campo_perfil'),
    path('actualizar-etiquetas/', views.actualizar_etiquetas, name='actualizar_etiquetas'),
    
    # Perf il de búsqueda de compañero/a
    path('completar-perfil-busqueda/', views.completar_perfil_busqueda, name='completar_perfil_busqueda'),
    path('perfil-busqueda/<str:username>/', views.ver_perfil_busqueda, name='ver_perfil_busqueda'),
        # Publicación de compañero/a (para usuarios que tienen lugar)
    path('publicacion-companero/crear/', views.crear_publicacion_companero, name='crear_publicacion_companero'),
    path('publicacion-companero/eliminar-imagen/<int:imagen_id>/', views.eliminar_imagen_publicacion_companero, name='eliminar_imagen_publicacion_companero'),
    path('publicacion-companero/cambiar-estado/', views.cambiar_estado_publicacion_companero, name='cambiar_estado_publicacion_companero'),
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
