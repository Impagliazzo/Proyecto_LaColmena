from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from propiedades.models import Propiedad
from notificaciones.models import Notificacion
from .models import SolicitudContacto
from .forms import SolicitudContactoForm

@login_required
def solicitar_contacto(request, propiedad_pk):
    """Solicitar contacto con propietario"""
    # Verificar perfil completo
    if not request.user.perfil.perfil_completo:
        messages.warning(request, 'Completá tu perfil antes de contactar propietarios')
        return redirect('usuarios:completar_perfil')
    
    propiedad = get_object_or_404(Propiedad, pk=propiedad_pk)
    
    # No puede contactarse a sí mismo
    if request.user == propiedad.propietario:
        messages.error(request, 'No puedes contactarte a ti mismo')
        return redirect('propiedades:detalle', pk=propiedad_pk)
    
    if request.method == 'POST':
        form = SolicitudContactoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.propiedad = propiedad
            solicitud.save()
            
            # Crear notificación para el propietario
            Notificacion.objects.create(
                usuario=propiedad.propietario,
                tipo='contacto',
                titulo=f'Nueva solicitud de contacto',
                mensaje=f'{request.user.get_full_name() or request.user.username} está interesado en tu propiedad "{propiedad.titulo}"',
                url=reverse('contactos:solicitudes_recibidas')
            )
            
            # Enviar notificación por email al propietario
            if propiedad.propietario.recibir_notificaciones:
                asunto = f'Nueva solicitud de contacto para {propiedad.titulo}'
                mensaje = f"""
                Hola {propiedad.propietario.first_name},
                
                {request.user.get_full_name() or request.user.username} está interesado en tu propiedad "{propiedad.titulo}".
                
                Mensaje:
                {solicitud.mensaje}
                
                Datos de contacto:
                - Email: {solicitud.email}
                - Teléfono: {solicitud.telefono or 'No proporcionado'}
                
                Saludos,
                Equipo LaColmena
                """
                
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@lacolmena.com',
                    [propiedad.propietario.email],
                    fail_silently=True,
                )
            
            messages.success(request, '¡Solicitud enviada! El propietario se pondrá en contacto contigo pronto.')
            return redirect('propiedades:detalle', pk=propiedad_pk)
    else:
        initial = {
            'email': request.user.email,
            'telefono': request.user.telefono,
        }
        form = SolicitudContactoForm(initial=initial)
    
    context = {
        'form': form,
        'propiedad': propiedad,
    }
    return render(request, 'contactos/solicitar.html', context)


@login_required
def mis_solicitudes(request):
    """Ver solicitudes de contacto realizadas por el usuario"""
    solicitudes = SolicitudContacto.objects.filter(
        usuario=request.user
    ).select_related('propiedad').order_by('-fecha_solicitud')
    
    return render(request, 'contactos/mis_solicitudes.html', {'solicitudes': solicitudes})


@login_required
def solicitudes_recibidas(request):
    """Ver solicitudes de contacto recibidas (para propietarios)"""
    if not request.user.es_propietario():
        messages.warning(request, 'Solo los propietarios pueden ver esta sección')
        return redirect('propiedades:inicio')
    
    solicitudes = SolicitudContacto.objects.filter(
        propiedad__propietario=request.user
    ).select_related('usuario', 'propiedad').order_by('-fecha_solicitud')
    
    return render(request, 'contactos/solicitudes_recibidas.html', {'solicitudes': solicitudes})


@login_required
def cambiar_estado_solicitud(request, pk, nuevo_estado):
    """Cambiar estado de una solicitud de contacto"""
    solicitud = get_object_or_404(
        SolicitudContacto,
        pk=pk,
        propiedad__propietario=request.user
    )
    
    if nuevo_estado in dict(SolicitudContacto.ESTADO_CHOICES):
        solicitud.estado = nuevo_estado
        
        # Si se marca como contactado, guardar fecha de respuesta
        if nuevo_estado == 'contactado' and not solicitud.fecha_respuesta:
            from django.utils import timezone
            solicitud.fecha_respuesta = timezone.now()
        
        solicitud.save()
        
        # Si se marca como contactado, notificar al usuario que envió la solicitud
        if nuevo_estado == 'contactado':
            Notificacion.objects.create(
                usuario=solicitud.usuario,
                tipo='contacto',
                titulo='El propietario vio tu solicitud',
                mensaje=f'El propietario de "{solicitud.propiedad.titulo}" ha visto tu solicitud y pronto se comunicará contigo.',
                url=reverse('propiedades:detalle', args=[solicitud.propiedad.pk])
            )
        
        messages.success(request, 'Estado actualizado correctamente')
    
    return redirect('contactos:solicitudes_recibidas')
