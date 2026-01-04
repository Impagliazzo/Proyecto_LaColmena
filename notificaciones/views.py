from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notificacion

@login_required
def listar_notificaciones(request):
    """Listado de notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Separar leídas y no leídas
    no_leidas = notificaciones.filter(leida=False)
    leidas = notificaciones.filter(leida=True)[:20]  # Limitar a las últimas 20
    
    context = {
        'no_leidas': no_leidas,
        'leidas': leidas,
    }
    return render(request, 'notificaciones/listar.html', context)


@login_required
def marcar_leida(request, pk):
    """Marcar una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.marcar_como_leida()
    
    if notificacion.url:
        return redirect(notificacion.url)
    return redirect('notificaciones:listar')


@login_required
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    from django.utils import timezone
    Notificacion.objects.filter(usuario=request.user, leida=False).update(
        leida=True,
        fecha_lectura=timezone.now()
    )
    messages.success(request, 'Todas las notificaciones marcadas como leídas')
    return redirect('notificaciones:listar')


@login_required
def eliminar_notificacion(request, pk):
    """Eliminar una notificación"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.delete()
    messages.success(request, 'Notificación eliminada')
    return redirect('notificaciones:listar')


def crear_notificacion(usuario, tipo, titulo, mensaje, url=''):
    """Función auxiliar para crear notificaciones"""
    if usuario.recibir_notificaciones:
        Notificacion.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            url=url
        )
