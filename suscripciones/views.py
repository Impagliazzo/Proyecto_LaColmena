from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PlanSuscripcion, Suscripcion, Pago

def planes(request):
    """Listado de planes de suscripción"""
    planes = PlanSuscripcion.objects.filter(activo=True)
    
    # Obtener suscripción activa del usuario si está autenticado
    suscripcion_activa = None
    if request.user.is_authenticated:
        suscripcion_activa = Suscripcion.objects.filter(
            usuario=request.user,
            estado='activa'
        ).first()
    
    context = {
        'planes': planes,
        'suscripcion_activa': suscripcion_activa,
    }
    return render(request, 'suscripciones/planes.html', context)


@login_required
def suscribirse(request, plan_id):
    """Proceso de suscripción a un plan"""
    plan = get_object_or_404(PlanSuscripcion, pk=plan_id, activo=True)
    
    # Verificar que sea propietario
    if not request.user.es_propietario():
        messages.warning(request, 'Debes ser propietario para suscribirte')
        return redirect('usuarios:convertir_propietario')
    
    # Verificar perfil completo
    if not request.user.perfil.perfil_completo:
        messages.warning(request, 'Completá tu perfil antes de cambiar de plan')
        return redirect('usuarios:completar_perfil')
    
    # Verificar si ya tiene una suscripción activa
    suscripcion_existente = Suscripcion.objects.filter(
        usuario=request.user,
        estado='activa'
    ).first()
    
    # Si el plan es Gratis (max_publicaciones=0), cancelar suscripción actual
    if plan.max_publicaciones == 0 and suscripcion_existente:
        from django.utils import timezone
        suscripcion_existente.estado = 'cancelada'
        suscripcion_existente.fecha_cancelacion = timezone.now()
        suscripcion_existente.save()
        
        # Suspender propiedades excedentes
        from propiedades.utils import gestionar_propiedades_por_suscripcion
        resultado = gestionar_propiedades_por_suscripcion(request.user)
        
        messages.info(request, 'Has cambiado al plan Gratis. Solo tu primera publicación permanecerá activa.')
        return redirect('propiedades:mis_propiedades')
    
    # Si ya tiene suscripción, permitir cambio de plan
    if suscripcion_existente:
        if request.method == 'POST':
            # Cambiar plan: cancelar la actual y crear nueva
            from django.utils import timezone
            suscripcion_existente.estado = 'cancelada'
            suscripcion_existente.fecha_cancelacion = timezone.now()
            suscripcion_existente.save()
            
            # Crear nueva suscripción
            nueva_suscripcion = Suscripcion.objects.create(
                usuario=request.user,
                plan=plan
            )
            
            # Registrar pago
            Pago.objects.create(
                suscripcion=nueva_suscripcion,
                monto=plan.precio,
                metodo='tarjeta',  # Por ahora
                estado='completado'
            )
            
            # Gestionar propiedades según nuevo plan
            from propiedades.utils import gestionar_propiedades_por_suscripcion
            resultado = gestionar_propiedades_por_suscripcion(request.user)
            
            messages.success(request, f'¡Plan cambiado a {plan.nombre}! Ahora puedes tener hasta {1 + plan.max_publicaciones} propiedades activas.')
            return redirect('propiedades:mis_propiedades')
        
        # Mostrar confirmación de cambio
        context = {
            'plan': plan,
            'suscripcion_actual': suscripcion_existente,
            'cambio_plan': True,
        }
        return render(request, 'suscripciones/suscribirse.html', context)
    
    # Nueva suscripción (no tiene ninguna activa)
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        
        # Crear suscripción
        suscripcion = Suscripcion.objects.create(
            usuario=request.user,
            plan=plan
        )
        
        # Crear pago
        pago = Pago.objects.create(
            suscripcion=suscripcion,
            monto=plan.precio,
            metodo=metodo_pago,
            estado='completado'  # En producción, esto dependerá del procesador de pagos
        )
        
        # Reactivar propiedades suspendidas automáticamente usando utilidad
        from propiedades.utils import gestionar_propiedades_por_suscripcion
        
        resultado = gestionar_propiedades_por_suscripcion(request.user)
        
        if resultado['cambios']:
            messages.success(request, f'¡Suscripción activada! Se reactivaron automáticamente {len(resultado["cambios"])} propiedad(es).')
        else:
            limite_total = resultado['limite_total']
            messages.success(request, f'¡Suscripción activada! Ahora puedes publicar hasta {limite_total} propiedades en total (1 gratis + {plan.max_publicaciones} del plan)')
        
        return redirect('propiedades:mis_propiedades')
    
    context = {
        'plan': plan,
    }
    return render(request, 'suscripciones/suscribirse.html', context)


@login_required
def mi_suscripcion(request):
    """Ver detalles de la suscripción actual"""
    suscripcion = Suscripcion.objects.filter(
        usuario=request.user
    ).select_related('plan').prefetch_related('pagos').first()
    
    if not suscripcion:
        messages.info(request, 'No tienes una suscripción activa')
        return redirect('suscripciones:planes')
    
    # Calcular publicaciones usadas
    publicaciones_activas = request.user.publicaciones.filter(estado='activa').count()
    
    context = {
        'suscripcion': suscripcion,
        'publicaciones_activas': publicaciones_activas,
        'publicaciones_disponibles': suscripcion.plan.max_publicaciones - publicaciones_activas,
    }
    return render(request, 'suscripciones/mi_suscripcion.html', context)


@login_required
def cancelar_suscripcion(request):
    """Cancelar suscripción"""
    suscripcion = Suscripcion.objects.filter(
        usuario=request.user,
        estado='activa'
    ).first()
    
    if not suscripcion:
        messages.error(request, 'No tienes una suscripción activa')
        return redirect('suscripciones:planes')
    
    if request.method == 'POST':
        from django.utils import timezone
        suscripcion.estado = 'cancelada'
        suscripcion.fecha_cancelacion = timezone.now()
        suscripcion.save()
        
        # Suspender propiedades excedentes automáticamente
        from propiedades.utils import gestionar_propiedades_por_suscripcion
        
        resultado = gestionar_propiedades_por_suscripcion(request.user)
        
        if resultado['cambios']:
            messages.warning(request, f'Suscripción cancelada. Se suspendieron {len(resultado["cambios"])} propiedad(es) que excedían el límite gratuito. Tu primera publicación permanece activa.')
        else:
            messages.info(request, 'Suscripción cancelada correctamente. Tu primera publicación permanece activa.')
        
        return redirect('propiedades:mis_propiedades')
    
    return render(request, 'suscripciones/cancelar.html', {'suscripcion': suscripcion})
