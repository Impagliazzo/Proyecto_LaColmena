"""
Utilidades para manejo de propiedades y suscripciones
"""
from .models import Propiedad


def gestionar_propiedades_por_suscripcion(usuario):
    """
    Gestiona las propiedades activas/suspendidas de un usuario según su suscripción.
    
    Reglas:
    - La primera propiedad publicada es siempre gratis y permanente
    - Sin suscripción: solo 1 propiedad activa (la primera)
    - Con suscripción: 1 gratis + max_publicaciones del plan
    - Se suspenden las propiedades más recientes cuando se excede el límite
    - Las suspendidas por suscripción se reactivan automáticamente al contratar plan
    
    Args:
        usuario: Instancia de Usuario propietario
    
    Returns:
        dict: Información sobre propiedades activadas/suspendidas
    """
    from suscripciones.models import Suscripcion
    
    # Obtener todas las propiedades ordenadas por fecha de publicación (más antigua primero)
    todas_propiedades = Propiedad.objects.filter(
        propietario=usuario
    ).order_by('fecha_publicacion')
    
    if not todas_propiedades.exists():
        return {'activas': 0, 'suspendidas': 0, 'cambios': []}
    
    # Verificar suscripción activa
    suscripcion_activa = Suscripcion.objects.filter(
        usuario=usuario,
        estado='activa'
    ).first()
    
    # Determinar límite
    if suscripcion_activa and suscripcion_activa.esta_activa():
        limite_total = 1 + suscripcion_activa.plan.max_publicaciones
    else:
        limite_total = 1  # Solo la primera gratis
    
    cambios = []
    
    # Procesar propiedades en orden de publicación
    for i, propiedad in enumerate(todas_propiedades):
        posicion = i + 1
        
        if posicion <= limite_total:
            # Esta propiedad debe estar activa
            if propiedad.estado == 'suspendida' and 'suscripción' in (propiedad.motivo_suspension or ''):
                propiedad.estado = 'activa'
                propiedad.motivo_suspension = ''
                propiedad.save()
                cambios.append(f'Reactivada: {propiedad.titulo}')
        else:
            # Esta propiedad excede el límite y debe estar suspendida
            if propiedad.estado == 'activa':
                propiedad.estado = 'suspendida'
                if posicion == 2 and limite_total == 1:
                    propiedad.motivo_suspension = 'Se requiere una suscripción activa para publicaciones adicionales. Tu primera publicación es gratis y permanente.'
                else:
                    propiedad.motivo_suspension = f'Has alcanzado el límite de tu plan. Esta es tu publicación #{posicion}. Mejora tu plan para activarla.'
                propiedad.save()
                cambios.append(f'Suspendida: {propiedad.titulo}')
    
    # Contar estados finales
    activas = todas_propiedades.filter(estado='activa').count()
    suspendidas = todas_propiedades.filter(estado='suspendida').count()
    
    return {
        'activas': activas,
        'suspendidas': suspendidas,
        'limite_total': limite_total,
        'cambios': cambios
    }


def puede_activar_propiedad(usuario, propiedad_id=None):
    """
    Verifica si un usuario puede activar una propiedad adicional.
    
    Args:
        usuario: Instancia de Usuario
        propiedad_id: ID de la propiedad a activar (None para nueva propiedad)
    
    Returns:
        tuple: (puede_activar: bool, mensaje: str, es_primera: bool)
    """
    from suscripciones.models import Suscripcion
    
    # Obtener primera propiedad del usuario
    primera_propiedad = Propiedad.objects.filter(
        propietario=usuario
    ).order_by('fecha_publicacion').first()
    
    # Si es la primera propiedad del usuario
    if not primera_propiedad:
        return (True, 'Tu primera publicación es gratis y permanente', True)
    
    # Si la propiedad a activar es la primera propiedad
    if propiedad_id and primera_propiedad.pk == propiedad_id:
        return (True, 'Esta es tu primera publicación (gratis y permanente)', True)
    
    # Para propiedades adicionales, verificar suscripción
    suscripcion_activa = Suscripcion.objects.filter(
        usuario=usuario,
        estado='activa'
    ).first()
    
    if not suscripcion_activa or not suscripcion_activa.esta_activa():
        return (False, 'Tu primera publicación es gratis. Para publicaciones adicionales necesitas una suscripción activa.', False)
    
    # Verificar límite del plan
    propiedades_activas = Propiedad.objects.filter(
        propietario=usuario,
        estado='activa'
    )
    
    if propiedad_id:
        propiedades_activas = propiedades_activas.exclude(pk=propiedad_id)
    
    activas_count = propiedades_activas.count()
    limite_total = 1 + suscripcion_activa.plan.max_publicaciones
    
    if activas_count >= limite_total:
        return (False, f'Has alcanzado el límite de {limite_total} publicaciones activas (1 gratis + {suscripcion_activa.plan.max_publicaciones} de tu plan {suscripcion_activa.plan.nombre})', False)
    
    return (True, f'Puedes activar esta propiedad. Tienes {limite_total - activas_count} espacio(s) disponible(s)', False)
