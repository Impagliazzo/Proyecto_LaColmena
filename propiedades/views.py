from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Propiedad, Categoria, Favorito, Valoracion, ImagenPropiedad, ReporteValoracion, Destacado
from .forms import PropiedadForm, BusquedaForm, ValoracionForm

def inicio(request):
    """Página principal con búsqueda y propiedades destacadas"""
    from django.utils import timezone
    from django.db.models import Q, Prefetch
    
    # Sistema de Slots Fijos para la página principal
    # 6 destacados totales: 3 premium + 3 normales
    
    # Obtener destacados activos y vigentes
    destacados_activos = Propiedad.objects.filter(
        estado='activa',
        destacados__activo=True,
        destacados__fecha_fin__gt=timezone.now()
    ).select_related('propietario', 'categoria').prefetch_related('imagenes', 'destacados').distinct()
    
    # Aplicar algoritmo de prioridad
    propiedades_con_prioridad = []
    for prop in destacados_activos:
        destacado = prop.destacados.filter(
            activo=True,
            fecha_fin__gt=timezone.now()
        ).first()
        
        if destacado:
            prioridad = destacado.calcular_prioridad()
            propiedades_con_prioridad.append({
                'propiedad': prop,
                'destacado': destacado,
                'prioridad': prioridad
            })
    
    # Ordenar por prioridad descendente
    propiedades_con_prioridad.sort(key=lambda x: x['prioridad'], reverse=True)
    
    # Separar por tipo y aplicar slots
    premium_destacadas = [
        item['propiedad'] for item in propiedades_con_prioridad 
        if item['destacado'].tipo == 'premium'
    ][:3]  # Máximo 3 premium
    
    normal_destacadas = [
        item['propiedad'] for item in propiedades_con_prioridad 
        if item['destacado'].tipo == 'normal'
    ][:3]  # Máximo 3 normales
    
    # Combinar destacadas (6 totales)
    propiedades_destacadas = premium_destacadas + normal_destacadas
    
    # NO rellenar con propiedades recientes - solo mostrar las que tienen prioridad activa
    
    # Propiedades especiales para estudiantes
    propiedades_estudiantes = list(Propiedad.objects.filter(
        estado='activa',
        especial_estudiantes=True
    ).select_related('propietario').prefetch_related('imagenes')[:4])
    
    # Categorías
    categorias = Categoria.objects.all()
    
    # Formulario de búsqueda
    form = BusquedaForm(request.GET)
    
    context = {
        'propiedades_destacadas': propiedades_destacadas,
        'propiedades_estudiantes': propiedades_estudiantes,
        'categorias': categorias,
        'form': form,
    }
    return render(request, 'propiedades/inicio.html', context)



def listado_propiedades(request):
    """Listado de propiedades con filtros y búsqueda"""
    propiedades = Propiedad.objects.filter(estado='activa').select_related(
        'propietario', 'categoria'
    ).prefetch_related('imagenes')
    
    # Aplicar filtros
    form = BusquedaForm(request.GET)
    if form.is_valid():
        busqueda = form.cleaned_data.get('busqueda')
        if busqueda:
            propiedades = propiedades.filter(
                Q(titulo__icontains=busqueda) |
                Q(descripcion__icontains=busqueda) |
                Q(ciudad__icontains=busqueda) |
                Q(distrito__icontains=busqueda)
            )
        
        tipo = form.cleaned_data.get('tipo')
        if tipo:
            propiedades = propiedades.filter(tipo=tipo)
        
        ciudad = form.cleaned_data.get('ciudad')
        if ciudad:
            propiedades = propiedades.filter(ciudad__icontains=ciudad)
        
        precio_min = form.cleaned_data.get('precio_min')
        if precio_min:
            propiedades = propiedades.filter(precio__gte=precio_min)
        
        precio_max = form.cleaned_data.get('precio_max')
        if precio_max:
            propiedades = propiedades.filter(precio__lte=precio_max)
    
    # Filtro por tipo desde la URL (para botones de filtro rápido)
    tipo_url = request.GET.get('tipo')
    if tipo_url and tipo_url in ['departamento', 'casa', 'cuarto', 'local', 'terreno', 'oficina']:
        propiedades = propiedades.filter(tipo=tipo_url)
    
    # Filtro por operación (alquiler o venta) desde la URL
    operacion = request.GET.get('operacion')
    if operacion and operacion in ['alquiler', 'venta']:
        propiedades = propiedades.filter(operacion=operacion)
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        propiedades = propiedades.filter(categoria_id=categoria_id)
    
    # Filtro por especial estudiantes
    especial_estudiantes = request.GET.get('especial_estudiantes')
    if especial_estudiantes:
        propiedades = propiedades.filter(especial_estudiantes=True)
    
    # Filtros adicionales (características)
    if request.GET.get('amoblado'):
        propiedades = propiedades.filter(amoblado=True)
    
    if request.GET.get('mascotas'):
        propiedades = propiedades.filter(mascotas=True)
    
    if request.GET.get('estacionamiento'):
        propiedades = propiedades.filter(estacionamiento=True)
    
    if request.GET.get('incluye_expensas'):
        propiedades = propiedades.filter(incluye_expensas=True)
    
    habitaciones = request.GET.get('habitaciones')
    if habitaciones and habitaciones.isdigit():
        propiedades = propiedades.filter(habitaciones__gte=int(habitaciones))
    
    banos = request.GET.get('banos')
    if banos and banos.isdigit():
        propiedades = propiedades.filter(banos__gte=int(banos))
    
    area_min = request.GET.get('area_min')
    if area_min and area_min.replace('.', '', 1).isdigit():
        propiedades = propiedades.filter(area__gte=float(area_min))
    
    area_max = request.GET.get('area_max')
    if area_max and area_max.replace('.', '', 1).isdigit():
        propiedades = propiedades.filter(area__lte=float(area_max))
    
    tipo_contacto = request.GET.get('tipo_contacto')
    if tipo_contacto in ['dueno', 'inmobiliaria']:
        propiedades = propiedades.filter(tipo_contacto=tipo_contacto)
    
    # Filtros de comodidades
    if request.GET.get('balcon'):
        propiedades = propiedades.filter(balcon=True)
    
    if request.GET.get('patio'):
        propiedades = propiedades.filter(patio=True)
    
    if request.GET.get('parrilla'):
        propiedades = propiedades.filter(parrilla=True)
    
    if request.GET.get('aire_acondicionado'):
        propiedades = propiedades.filter(aire_acondicionado=True)
    
    if request.GET.get('calefaccion'):
        propiedades = propiedades.filter(calefaccion=True)
    
    if request.GET.get('ascensor'):
        propiedades = propiedades.filter(ascensor=True)
    
    # Filtros de edificio
    if request.GET.get('seguridad'):
        propiedades = propiedades.filter(seguridad=True)
    
    if request.GET.get('amenities'):
        propiedades = propiedades.filter(amenities=True)
    
    if request.GET.get('accesibilidad'):
        propiedades = propiedades.filter(accesibilidad=True)
    
    # Paginación
    paginator = Paginator(propiedades, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'propiedades/listado.html', context)


def detalle_propiedad(request, pk):
    """Detalle de una propiedad"""
    propiedad = get_object_or_404(
        Propiedad.objects.select_related('propietario', 'categoria').prefetch_related('imagenes', 'valoraciones'),
        pk=pk
    )
    
    # Detectar modo preview
    preview_mode = request.GET.get('preview') == '1'
    
    # Incrementar vistas
    propiedad.incrementar_vistas()
    
    # Verificar si es favorito
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, propiedad=propiedad).exists()
    
    # Valoraciones
    valoraciones = propiedad.valoraciones.select_related('usuario').all()
    
    # Propiedades similares
    propiedades_similares = Propiedad.objects.filter(
        estado='activa',
        categoria=propiedad.categoria
    ).exclude(pk=propiedad.pk).select_related('propietario', 'categoria').prefetch_related('imagenes')[:4]
    
    context = {
        'propiedad': propiedad,
        'es_favorito': es_favorito,
        'valoraciones': valoraciones,
        'propiedades_similares': propiedades_similares,
        'preview_mode': preview_mode,
    }
    return render(request, 'propiedades/detalle.html', context)


@login_required
def crear_propiedad(request):
    """Crear nueva propiedad"""
    # Verificar que sea propietario
    if not request.user.es_propietario():
        messages.warning(request, 'Debes ser propietario para publicar. Conviértete en propietario primero.')
        return redirect('usuarios:convertir_propietario')
    
    # Verificar validaciones completas
    if not request.user.tiene_validaciones_completas():
        messages.warning(request, 'Debes validar tu teléfono y email antes de publicar propiedades')
        return redirect('usuarios:perfil', username=request.user.username)
    
    # Contar cuántas propiedades tiene el usuario (activas o suspendidas)
    total_propiedades = Propiedad.objects.filter(propietario=request.user).count()
    
    # La primera propiedad es gratis, las demás requieren suscripción
    if total_propiedades >= 1:
        # Verificar que tenga una suscripción activa para publicaciones adicionales
        from suscripciones.models import Suscripcion
        suscripcion_activa = Suscripcion.objects.filter(
            usuario=request.user,
            estado='activa'
        ).first()
        
        if not suscripcion_activa or not suscripcion_activa.esta_activa():
            messages.warning(request, 'Tu primera publicación es gratis. Para publicar más propiedades necesitas una suscripción activa.')
            return redirect('suscripciones:planes')
        
        # Verificar límite de publicaciones según el plan (no contar la primera que es gratis)
        propiedades_activas = Propiedad.objects.filter(
            propietario=request.user,
            estado='activa'
        ).count()
        
        # El límite del plan es adicional a la primera publicación gratis
        limite_total = suscripcion_activa.plan.max_publicaciones + 1
        
        if propiedades_activas >= limite_total:
            messages.warning(request, f'Has alcanzado el límite de publicaciones activas (1 gratis + {suscripcion_activa.plan.max_publicaciones} del plan {suscripcion_activa.plan.nombre}). Mejora tu plan para publicar más.')
            return redirect('suscripciones:planes')
    
    if request.method == 'POST':
        form = PropiedadForm(request.POST)
        imagenes = request.FILES.getlist('imagenes')
        
        if form.is_valid() and imagenes:
            propiedad = form.save(commit=False)
            propiedad.propietario = request.user
            propiedad.save()
            
            # Guardar imágenes (máximo 10)
            for i, imagen in enumerate(imagenes[:10]):
                ImagenPropiedad.objects.create(
                    propiedad=propiedad,
                    imagen=imagen,
                    orden=i,
                    es_principal=(i == 0)
                )
            
            messages.success(request, '¡Propiedad publicada exitosamente!')
            return redirect('propiedades:detalle', pk=propiedad.pk)
        else:
            if not imagenes:
                messages.error(request, 'Debes subir al menos una imagen')
    else:
        form = PropiedadForm()
    
    return render(request, 'propiedades/crear.html', {'form': form})


@login_required
def editar_propiedad(request, pk):
    """Editar propiedad existente"""
    from django.utils import timezone
    from datetime import timedelta
    
    propiedad = get_object_or_404(Propiedad, pk=pk, propietario=request.user)
    
    # Obtener información de suscripción y destacados disponibles
    from suscripciones.models import Suscripcion
    suscripcion = Suscripcion.objects.filter(
        usuario=request.user,
        estado='activa'
    ).select_related('plan').first()
    
    destacados_disponibles = 0
    puede_destacar = False
    
    if suscripcion and suscripcion.esta_activa():
        plan = suscripcion.plan
        if plan.destacados_incluidos_mes > 0:
            # Contar destacados usados en el mes actual
            inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            destacados_usados_mes = Destacado.objects.filter(
                propiedad__propietario=request.user,
                fecha_compra__gte=inicio_mes,
                activo=True
            ).count()
            destacados_disponibles = plan.destacados_incluidos_mes - destacados_usados_mes
            puede_destacar = destacados_disponibles > 0 or plan.puede_comprar_destacados
        else:
            puede_destacar = plan.puede_comprar_destacados
    
    # Obtener destacado activo actual
    destacado_activo = propiedad.obtener_destacado_activo()
    
    if request.method == 'POST':
        # Manejar toggle de destacado
        accion_destacado = request.POST.get('accion_destacado')
        
        if accion_destacado == 'activar':
            # Verificar que tenga suscripción y destacados disponibles
            if not suscripcion or not suscripcion.esta_activa():
                messages.error(request, 'Necesitas una suscripción activa para destacar propiedades.')
                return redirect('suscripciones:planes')
            
            if destacados_disponibles <= 0:
                messages.error(request, 'No tienes destacados disponibles. Ya usaste todos los destacados incluidos este mes.')
                return redirect('propiedades:editar', pk=pk)
            
            # Crear destacado (usar tipo normal y duración de 30 días por defecto)
            fecha_inicio = timezone.now()
            fecha_fin = fecha_inicio + timedelta(days=30)
            
            Destacado.objects.create(
                propiedad=propiedad,
                tipo='normal',
                duracion_dias=30,
                precio_pagado=0,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                activo=True
            )
            
            # Actualizar campo destacada de la propiedad
            propiedad.destacada = True
            propiedad.save(update_fields=['destacada'])
            
            messages.success(request, f'¡Propiedad destacada exitosamente por 30 días! Te quedan {destacados_disponibles - 1} destacados disponibles.')
            return redirect('propiedades:editar', pk=pk)
        
        elif accion_destacado == 'desactivar':
            # Desactivar destacado actual
            if destacado_activo:
                destacado_activo.activo = False
                destacado_activo.save()
                
                # Actualizar campo destacada de la propiedad
                propiedad.destacada = False
                propiedad.save(update_fields=['destacada'])
                
                messages.success(request, 'Destacado desactivado correctamente.')
                return redirect('propiedades:editar', pk=pk)
        
        # Procesar formulario normal de edición
        form = PropiedadForm(request.POST, request.FILES, instance=propiedad)
        if form.is_valid():
            # Verificar suscripción si se está reactivando la propiedad
            estado_nuevo = form.cleaned_data.get('estado')
            estado_anterior = propiedad.estado
            
            if estado_anterior != 'activa' and estado_nuevo == 'activa':
                # Verificar si es la primera propiedad del usuario
                primera_propiedad = Propiedad.objects.filter(
                    propietario=request.user
                ).order_by('fecha_publicacion').first()
                
                # Si NO es la primera propiedad, requiere suscripción
                if primera_propiedad.pk != propiedad.pk:
                    suscripcion_activa = Suscripcion.objects.filter(
                        usuario=request.user,
                        estado='activa'
                    ).first()
                    
                    if not suscripcion_activa or not suscripcion_activa.esta_activa():
                        messages.warning(request, 'Tu primera publicación es gratis y permanente. Para reactivar propiedades adicionales necesitas una suscripción activa.')
                        return redirect('suscripciones:planes')
                    
                    # Verificar límite de publicaciones según el plan
                    propiedades_activas = Propiedad.objects.filter(
                        propietario=request.user,
                        estado='activa'
                    ).exclude(pk=propiedad.pk).count()
                    
                    # El límite del plan es adicional a la primera publicación gratis
                    limite_total = suscripcion_activa.plan.max_publicaciones + 1
                    
                    if propiedades_activas >= limite_total:
                        messages.warning(request, f'Has alcanzado el límite de publicaciones activas (1 gratis + {suscripcion_activa.plan.max_publicaciones} del plan {suscripcion_activa.plan.nombre}).')
                        return redirect('suscripciones:planes')
                
                # Limpiar motivo de suspensión al reactivar
                propiedad.motivo_suspension = ''
            
            form.save()
            
            # Procesar nuevas imágenes si se adjuntaron
            imagenes_nuevas = request.FILES.getlist('imagenes')
            if imagenes_nuevas:
                # Contar imágenes existentes
                imagenes_actuales = propiedad.imagenes.count()
                max_nuevas = 10 - imagenes_actuales
                
                if max_nuevas > 0:
                    # Agregar nuevas imágenes (máximo 10 total)
                    orden_inicial = imagenes_actuales
                    for i, imagen in enumerate(imagenes_nuevas[:max_nuevas]):
                        ImagenPropiedad.objects.create(
                            propiedad=propiedad,
                            imagen=imagen,
                            orden=orden_inicial + i,
                            es_principal=False
                        )
                    messages.success(request, f'Propiedad actualizada y {len(imagenes_nuevas[:max_nuevas])} imagen(es) agregada(s) correctamente')
                else:
                    messages.warning(request, 'Propiedad actualizada. No se agregaron imágenes porque ya tienes el máximo (10 imágenes).')
            else:
                messages.success(request, 'Propiedad actualizada correctamente')
            
            return redirect('propiedades:detalle', pk=propiedad.pk)
    else:
        form = PropiedadForm(instance=propiedad)
    
    context = {
        'form': form,
        'propiedad': propiedad,
        'suscripcion': suscripcion,
        'destacados_disponibles': destacados_disponibles,
        'puede_destacar': puede_destacar,
        'destacado_activo': destacado_activo,
    }
    return render(request, 'propiedades/editar.html', context)


@login_required
def eliminar_propiedad(request, pk):
    """Eliminar propiedad"""
    propiedad = get_object_or_404(Propiedad, pk=pk, propietario=request.user)
    
    if request.method == 'POST':
        propiedad.delete()
        messages.success(request, 'Propiedad eliminada correctamente')
        return redirect('propiedades:mis_propiedades')
    
    return render(request, 'propiedades/eliminar.html', {'propiedad': propiedad})


@login_required
def suspender_propiedad(request, pk):
    """Suspender/Reactivar propiedad"""
    propiedad = get_object_or_404(Propiedad, pk=pk, propietario=request.user)
    
    if propiedad.estado == 'activa':
        # Suspender propiedad (sin motivo = suspensión manual)
        propiedad.estado = 'suspendida'
        propiedad.motivo_suspension = ''  # Suspensión manual no tiene motivo
        propiedad.save()
        messages.info(request, 'Propiedad suspendida correctamente')
    else:
        # Intentar reactivar propiedad
        from propiedades.utils import puede_activar_propiedad
        
        puede, mensaje, es_primera = puede_activar_propiedad(request.user, propiedad.pk)
        
        if puede:
            propiedad.estado = 'activa'
            propiedad.motivo_suspension = ''
            propiedad.save()
            messages.success(request, 'Propiedad reactivada correctamente')
        else:
            messages.warning(request, mensaje)
    
    return redirect('propiedades:mis_propiedades')


@login_required
def mis_propiedades(request):
    """Listado de propiedades del propietario"""
    from django.utils import timezone
    from datetime import timedelta
    from django.core.paginator import Paginator
    
    if not request.user.es_propietario():
        messages.warning(request, 'Debes ser propietario para acceder a esta sección')
        return redirect('usuarios:convertir_propietario')
    
    propiedades_list = Propiedad.objects.filter(
        propietario=request.user
    ).prefetch_related('imagenes').annotate(
        total_valoraciones=Count('valoraciones'),
        total_favoritos=Count('favoritos')
    ).order_by('-estado', '-fecha_publicacion')  # Activas primero, luego por fecha
    
    # Paginación
    paginator = Paginator(propiedades_list, 5)  # 5 propiedades por página
    page_number = request.GET.get('page')
    propiedades = paginator.get_page(page_number)
    
    # Estadísticas (se calculan sobre todas las propiedades, no solo la página actual)
    activas = propiedades_list.filter(estado='activa').count()
    suspendidas = propiedades_list.filter(estado='suspendida').count()
    total_vistas = sum(p.vistas for p in propiedades_list)
    total_favoritos = sum(p.total_favoritos for p in propiedades_list)
    
    # Obtener información de destacados disponibles
    from suscripciones.models import Suscripcion
    suscripcion = Suscripcion.objects.filter(
        usuario=request.user,
        estado='activa'
    ).select_related('plan').first()
    
    destacados_disponibles = 0
    puede_destacar = False
    
    if suscripcion and suscripcion.esta_activa():
        plan = suscripcion.plan
        if plan.destacados_incluidos_mes > 0:
            # Contar destacados activos actualmente (no por mes, sino los que están ON ahora)
            destacados_activos_actuales = Destacado.objects.filter(
                propiedad__propietario=request.user,
                activo=True
            ).count()
            destacados_disponibles = plan.destacados_incluidos_mes - destacados_activos_actuales
            puede_destacar = True
        else:
            puede_destacar = plan.puede_comprar_destacados
    
    context = {
        'propiedades': propiedades,
        'activas': activas,
        'suspendidas': suspendidas,
        'total_vistas': total_vistas,
        'total_favoritos': total_favoritos,
        'suscripcion': suscripcion,
        'destacados_disponibles': destacados_disponibles,
        'puede_destacar': puede_destacar,
    }
    return render(request, 'propiedades/mis_propiedades.html', context)


@login_required
def toggle_destacado(request, pk):
    """Activar/desactivar destacado rápido desde mis propiedades"""
    from django.utils import timezone
    from datetime import timedelta
    from suscripciones.models import Suscripcion
    
    if not request.user.es_propietario():
        messages.error(request, 'Solo los propietarios pueden destacar propiedades')
        return redirect('propiedades:mis_propiedades')
    
    propiedad = get_object_or_404(Propiedad, pk=pk, propietario=request.user)
    
    # Verificar si tiene destacado activo
    destacado_activo = propiedad.obtener_destacado_activo()
    
    if destacado_activo:
        # Desactivar destacado
        destacado_activo.activo = False
        destacado_activo.save()
        
        # Actualizar campo destacada de la propiedad
        propiedad.destacada = False
        propiedad.save(update_fields=['destacada'])
        
        messages.success(request, f'Prioridad desactivada para "{propiedad.titulo}". Podés reactivarla cuando quieras sin que cuente como uso adicional.')
    else:
        # Activar destacado - verificar disponibilidad
        suscripcion = Suscripcion.objects.filter(
            usuario=request.user,
            estado='activa'
        ).select_related('plan').first()
        
        if not suscripcion or not suscripcion.esta_activa():
            messages.error(request, 'Necesitás una suscripción activa para destacar propiedades.')
            return redirect('suscripciones:planes')
        
        plan = suscripcion.plan
        
        # Contar destacados activos actualmente (no por mes, sino los que están ON ahora)
        destacados_activos_actuales = Destacado.objects.filter(
            propiedad__propietario=request.user,
            activo=True
        ).count()
        destacados_disponibles = plan.destacados_incluidos_mes - destacados_activos_actuales
        
        if destacados_disponibles <= 0:
            messages.error(request, 'No tenés destacados disponibles. Ya estás usando todos los destacados incluidos en tu plan. Desactivá alguno para poder activar otro.')
            return redirect('propiedades:mis_propiedades')
        
        # Buscar si ya existe un destacado para esta propiedad (inactivo)
        destacado_existente = Destacado.objects.filter(propiedad=propiedad).first()
        
        if destacado_existente:
            # Reactivar destacado existente
            destacado_existente.activo = True
            destacado_existente.save()
        else:
            # Crear nuevo destacado vinculado al período de suscripción
            fecha_inicio = timezone.now()
            fecha_fin = suscripcion.fecha_vencimiento  # Se vincula a la fecha de vencimiento de la suscripción
            
            Destacado.objects.create(
                propiedad=propiedad,
                tipo='normal',
                duracion_dias=(fecha_fin - fecha_inicio).days,
                precio_pagado=0,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                activo=True
            )
        
        # Actualizar campo destacada de la propiedad
        propiedad.destacada = True
        propiedad.save(update_fields=['destacada'])
        
        messages.success(request, f'¡"{propiedad.titulo}" ahora tiene prioridad! Se mantendrá hasta que se renueve tu suscripción. Te quedan {destacados_disponibles - 1} destacados disponibles.')
    
    return redirect('propiedades:mis_propiedades')


@login_required
def toggle_especial_estudiantes(request, pk):
    """Activar/desactivar especial para estudiantes"""
    if not request.user.es_propietario():
        messages.error(request, 'Solo los propietarios pueden marcar propiedades como especiales para estudiantes')
        return redirect('propiedades:mis_propiedades')
    
    propiedad = get_object_or_404(Propiedad, pk=pk, propietario=request.user)
    
    # Toggle del campo especial_estudiantes
    propiedad.especial_estudiantes = not propiedad.especial_estudiantes
    propiedad.save(update_fields=['especial_estudiantes'])
    
    if propiedad.especial_estudiantes:
        messages.success(request, f'"{propiedad.titulo}" marcada como especial para estudiantes')
    else:
        messages.success(request, f'"{propiedad.titulo}" desmarcada como especial para estudiantes')
    
    return redirect('propiedades:mis_propiedades')


@login_required
def toggle_favorito(request, pk):
    """Agregar/quitar de favoritos"""
    propiedad = get_object_or_404(Propiedad, pk=pk)
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        propiedad=propiedad
    )
    
    if not created:
        favorito.delete()
        messages.info(request, 'Removido de favoritos')
    else:
        messages.success(request, 'Agregado a favoritos')
    
    return redirect('propiedades:detalle', pk=pk)


@login_required
def mis_favoritos(request):
    """Listado de propiedades favoritas"""
    favoritos = Favorito.objects.filter(
        usuario=request.user
    ).select_related('propiedad__propietario', 'propiedad__categoria').prefetch_related('propiedad__imagenes')
    
    return render(request, 'propiedades/favoritos.html', {'favoritos': favoritos})


@login_required
@login_required
def valorar_propiedad(request, pk):
    """Valorar una propiedad"""
    from django.utils import timezone
    from datetime import timedelta
    from contactos.models import SolicitudContacto
    
    propiedad = get_object_or_404(Propiedad, pk=pk)
    
    # ❌ No puede valorar su propia propiedad
    if request.user == propiedad.propietario:
        messages.error(request, 'No puedes valorar tu propia propiedad')
        return redirect('propiedades:detalle', pk=pk)
    
    # ❌ No se puede valorar sin interacción - Verificar que haya una solicitud de contacto
    solicitud = SolicitudContacto.objects.filter(
        usuario=request.user,
        propiedad=propiedad
    ).first()
    
    if not solicitud:
        messages.error(request, 'Debes contactar al propietario antes de poder valorar')
        return redirect('propiedades:detalle', pk=pk)
    
    # Verificar que hayan pasado 7 días desde el contacto
    dias_transcurridos = (timezone.now() - solicitud.fecha_solicitud).days
    if dias_transcurridos < 7:
        messages.info(request, f'Podrás valorar esta propiedad en {7 - dias_transcurridos} días')
        return redirect('propiedades:detalle', pk=pk)
    
    # ⏱️ Verificar si puede valorar la PUBLICACIÓN
    # Se habilita 24h después de que el propietario responda
    puede_valorar_publicacion = False
    horas_desde_respuesta = None
    
    if solicitud.fecha_respuesta:
        horas_desde_respuesta = (timezone.now() - solicitud.fecha_respuesta).total_seconds() / 3600
        puede_valorar_publicacion = horas_desde_respuesta >= 24
    else:
        # Si han pasado 7 días y el propietario NO respondió, NO se puede valorar publicación
        puede_valorar_publicacion = False
    
    # ❌ no se puede valorar dos veces - verificar si ya existe
    try:
        valoracion_existente = Valoracion.objects.get(usuario=request.user, propiedad=propiedad)
        
        # ❌ no se puede editar después de X días
        if not valoracion_existente.puede_editar():
            messages.error(request, 'El plazo para editar tu valoración ha expirado (30 días)')
            return redirect('propiedades:detalle', pk=pk)
        
        # Modo edición
        if request.method == 'POST':
            form = ValoracionForm(request.POST, instance=valoracion_existente, puede_valorar_publicacion=puede_valorar_publicacion)
            if form.is_valid():
                valoracion = form.save(commit=False)
                # Si no puede valorar publicación, asignar NULL
                if not puede_valorar_publicacion:
                    valoracion.claridad_informacion = None
                    valoracion.coincidencia_fotos = None
                    valoracion.ubicacion_correcta = None
                valoracion.save()
                # Actualizar puntuación del propietario
                propiedad.propietario.perfil.actualizar_puntuacion()
                messages.success(request, 'Valoración actualizada correctamente')
                return redirect('propiedades:detalle', pk=pk)
        else:
            form = ValoracionForm(instance=valoracion_existente, puede_valorar_publicacion=puede_valorar_publicacion)
        
        es_edicion = True
    except Valoracion.DoesNotExist:
        # Modo creación
        if request.method == 'POST':
            form = ValoracionForm(request.POST, puede_valorar_publicacion=puede_valorar_publicacion)
            if form.is_valid():
                valoracion = form.save(commit=False)
                valoracion.usuario = request.user
                valoracion.propiedad = propiedad
                # Si no puede valorar publicación, asignar NULL
                if not puede_valorar_publicacion:
                    valoracion.claridad_informacion = None
                    valoracion.coincidencia_fotos = None
                    valoracion.ubicacion_correcta = None
                valoracion.save()
                # Actualizar puntuación del propietario
                propiedad.propietario.perfil.actualizar_puntuacion()
                messages.success(request, '¡Valoración publicada! Gracias por tu opinión')
                return redirect('propiedades:detalle', pk=pk)
        else:
            form = ValoracionForm(puede_valorar_publicacion=puede_valorar_publicacion)
        
        es_edicion = False
    
    context = {
        'form': form,
        'propiedad': propiedad,
        'es_edicion': es_edicion,
        'solicitud': solicitud,
        'dias_transcurridos': dias_transcurridos,
        'puede_valorar_publicacion': puede_valorar_publicacion,
        'horas_desde_respuesta': horas_desde_respuesta,
    }
    return render(request, 'propiedades/valorar.html', context)


@login_required
def reportar_valoracion(request, pk):
    """Vista para reportar una valoración como injusta o inapropiada"""
    valoracion = get_object_or_404(Valoracion, pk=pk)
    
    # No se puede reportar la propia valoración
    if request.user == valoracion.usuario:
        messages.error(request, 'No puedes reportar tu propia valoración')
        return redirect('propiedades:detalle', pk=valoracion.propiedad.pk)
    
    # Verificar si ya reportó esta valoración
    reporte_existente = ReporteValoracion.objects.filter(
        valoracion=valoracion,
        reportado_por=request.user
    ).exists()
    
    if reporte_existente:
        messages.warning(request, 'Ya has reportado esta valoración previamente')
        return redirect('propiedades:detalle', pk=valoracion.propiedad.pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not motivo:
            messages.error(request, 'Debes seleccionar un motivo')
            return redirect('propiedades:reportar_valoracion', pk=pk)
        
        # Crear el reporte
        reporte = ReporteValoracion.objects.create(
            valoracion=valoracion,
            reportado_por=request.user,
            motivo=motivo,
            descripcion=descripcion
        )
        
        # Incrementar contador de reportes
        valoracion.total_reportes += 1
        
        # Si hay 3 o más reportes, marcar como reportada
        if valoracion.total_reportes >= 3:
            valoracion.reportada = True
        
        valoracion.save()
        
        # Crear notificación para el sistema/admin (opcional)
        from notificaciones.models import Notificacion
        Notificacion.objects.create(
            usuario=valoracion.propiedad.propietario,  # Notificar al propietario
            tipo='sistema',
            mensaje=f'Se ha reportado una valoración en tu propiedad "{valoracion.propiedad.titulo}"',
            url=f'/propiedades/{valoracion.propiedad.pk}/'
        )
        
        messages.success(request, 'Reporte enviado correctamente. Será revisado por nuestro equipo')
        return redirect('propiedades:detalle', pk=valoracion.propiedad.pk)
    
    context = {
        'valoracion': valoracion,
        'motivos': ReporteValoracion.MOTIVO_CHOICES
    }
    return render(request, 'propiedades/reportar_valoracion.html', context)


def estudiantes(request):
    """Página dedicada para estudiantes"""
    propiedades_estudiantes = Propiedad.objects.filter(
        estado='activa',
        especial_estudiantes=True
    ).select_related('propietario').prefetch_related('imagenes')[:12]
    
    # Debug: imprimir en consola
    print(f"DEBUG: Propiedades encontradas: {propiedades_estudiantes.count()}")
    for prop in propiedades_estudiantes:
        print(f"  - {prop.id}: {prop.titulo}")
    
    context = {
        'propiedades_estudiantes': propiedades_estudiantes,
    }
    return render(request, 'propiedades/estudiantes.html', context)


def inversiones(request):
    """Página dedicada para inversiones"""
    # Propiedades para venta
    propiedades_venta = Propiedad.objects.filter(
        estado='activa',
        operacion='venta'
    ).select_related('propietario', 'categoria').prefetch_related('imagenes')[:12]
    
    context = {
        'propiedades_venta': propiedades_venta,
    }
    return render(request, 'propiedades/inversiones.html', context)


def quienes_somos(request):
    """Página Quiénes somos"""
    return render(request, 'propiedades/quienes_somos.html')


def buscar_companero(request):
    """Página para buscar compañero de departamento"""
    return render(request, 'propiedades/buscar_companero.html')


@login_required
def destacar_propiedad(request, pk):
    """Vista para destacar una propiedad"""
    from django.utils import timezone
    from datetime import timedelta
    from suscripciones.models import Suscripcion
    
    propiedad = get_object_or_404(Propiedad, pk=pk, propietario=request.user)
    
    # Verificar que el usuario tenga una suscripción activa
    suscripcion = Suscripcion.objects.filter(
        usuario=request.user,
        estado='activa'
    ).select_related('plan').first()
    
    if not suscripcion or not suscripcion.esta_activa():
        messages.error(request, 'Necesitas una suscripción activa para destacar propiedades')
        return redirect('suscripciones:planes')
    
    plan = suscripcion.plan
    
    # Verificar si el plan permite destacar
    if plan.destacados_incluidos_mes == 0 and not plan.puede_comprar_destacados:
        messages.error(request, 'Tu plan actual no incluye destacados. Actualiza tu plan para acceder a esta funcionalidad')
        return redirect('suscripciones:planes')
    
    # Contar destacados activos del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    destacados_mes = Destacado.objects.filter(
        propiedad__propietario=request.user,
        fecha_compra__gte=inicio_mes,
        activo=True
    ).count()
    
    destacados_disponibles = plan.destacados_incluidos_mes - destacados_mes
    puede_usar_incluido = destacados_disponibles > 0
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'normal')
        duracion = int(request.POST.get('duracion', 7))
        usar_incluido = request.POST.get('usar_incluido') == 'true'
        
        # Validar tipo y duración
        if tipo not in ['normal', 'premium']:
            messages.error(request, 'Tipo de destacado inválido')
            return redirect('propiedades:destacar', pk=pk)
        
        if duracion not in [7, 15, 30]:
            messages.error(request, 'Duración inválida')
            return redirect('propiedades:destacar', pk=pk)
        
        # Si quiere usar incluido, verificar disponibilidad
        if usar_incluido:
            if destacados_disponibles <= 0:
                messages.error(request, 'Ya has usado todos tus destacados incluidos este mes')
                return redirect('propiedades:destacar', pk=pk)
            precio = 0
        else:
            # Verificar si puede comprar
            if not plan.puede_comprar_destacados:
                messages.error(request, 'Tu plan no permite comprar destacados adicionales')
                return redirect('propiedades:destacar', pk=pk)
            precio = Destacado.get_precio(tipo, duracion)
        
        # Crear el destacado
        fecha_inicio = timezone.now()
        fecha_fin = fecha_inicio + timedelta(days=duracion)
        
        destacado = Destacado.objects.create(
            propiedad=propiedad,
            tipo=tipo,
            duracion_dias=duracion,
            precio_pagado=precio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        if precio == 0:
            messages.success(request, f'¡Propiedad destacada exitosamente por {duracion} días usando tu destacado incluido!')
        else:
            messages.success(request, f'¡Propiedad destacada exitosamente por {duracion} días! Precio: S/. {precio}')
        
        return redirect('propiedades:mis_destacados')
    
    context = {
        'propiedad': propiedad,
        'suscripcion': suscripcion,
        'plan': plan,
        'destacados_disponibles': destacados_disponibles,
        'puede_usar_incluido': puede_usar_incluido,
        'puede_comprar': plan.puede_comprar_destacados,
        'precios': Destacado.PRECIOS,
        'destacados_mes': destacados_mes,
    }
    return render(request, 'propiedades/destacar.html', context)


@login_required
def mis_destacados(request):
    """Vista para ver todos los destacados del usuario"""
    from django.utils import timezone
    
    destacados_activos = Destacado.objects.filter(
        propiedad__propietario=request.user,
        activo=True,
        fecha_fin__gt=timezone.now()
    ).select_related('propiedad').order_by('-fecha_inicio')
    
    destacados_expirados = Destacado.objects.filter(
        propiedad__propietario=request.user
    ).filter(
        Q(activo=False) | Q(fecha_fin__lte=timezone.now())
    ).select_related('propiedad').order_by('-fecha_inicio')[:10]
    
    # Información de suscripción
    from suscripciones.models import Suscripcion
    suscripcion = Suscripcion.objects.filter(
        usuario=request.user,
        estado='activa'
    ).select_related('plan').first()
    
    if suscripcion:
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        destacados_usados_mes = Destacado.objects.filter(
            propiedad__propietario=request.user,
            fecha_compra__gte=inicio_mes,
            activo=True
        ).count()
        destacados_disponibles = suscripcion.plan.destacados_incluidos_mes - destacados_usados_mes
    else:
        destacados_usados_mes = 0
        destacados_disponibles = 0
    
    context = {
        'destacados_activos': destacados_activos,
        'destacados_expirados': destacados_expirados,
        'suscripcion': suscripcion,
        'destacados_usados_mes': destacados_usados_mes,
        'destacados_disponibles': destacados_disponibles,
    }
    return render(request, 'propiedades/mis_destacados.html', context)




def sugerencias_ubicacion(request):
    """Endpoint para autocompletado de ubicaciones basado en inmuebles activos"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'sugerencias': [], 'mensaje': None})
    
    # Filtrar solo propiedades activas
    propiedades_activas = Propiedad.objects.filter(estado='activa')
    
    sugerencias = []
    ciudades_agregadas = set()
    distritos_agregados = set()
    
    # Buscar ciudades con propiedades activas
    ciudades = propiedades_activas.filter(
        ciudad__icontains=query
    ).values('ciudad').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for ciudad in ciudades:
        if ciudad['ciudad'] and ciudad['ciudad'].strip():
            ciudad_lower = ciudad['ciudad'].lower()
            if ciudad_lower not in ciudades_agregadas:
                ciudades_agregadas.add(ciudad_lower)
                sugerencias.append({
                    'texto': ciudad['ciudad'],
                    'texto_completo': ciudad['ciudad'],
                    'tipo': 'ciudad',
                    'count': ciudad['count'],
                    'icono': 'fa-city'
                })
    
    # Buscar distritos/barrios con propiedades activas
    distritos = propiedades_activas.filter(
        distrito__icontains=query
    ).values('distrito', 'ciudad').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for distrito in distritos:
        if distrito['distrito'] and distrito['distrito'].strip():
            distrito_lower = distrito['distrito'].lower()
            if distrito_lower not in distritos_agregados:
                distritos_agregados.add(distrito_lower)
                texto = distrito['distrito']
                texto_completo = texto
                if distrito['ciudad'] and distrito['ciudad'].strip():
                    texto_completo += f", {distrito['ciudad']}"
                
                sugerencias.append({
                    'texto': texto,
                    'texto_completo': texto_completo,
                    'tipo': 'barrio',
                    'count': distrito['count'],
                    'icono': 'fa-map-marker-alt'
                })
    
    # Ordenar por relevancia (count) y limitar a 10 resultados
    sugerencias.sort(key=lambda x: x['count'], reverse=True)
    sugerencias = sugerencias[:10]
    
    # Mensaje si no hay resultados
    mensaje = None
    if not sugerencias:
        # Sugerir ubicaciones con más propiedades
        top_ubicaciones = propiedades_activas.values('ciudad').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        ubicaciones_sugeridas = [loc['ciudad'] for loc in top_ubicaciones if loc['ciudad']]
        
        if ubicaciones_sugeridas:
            mensaje = f"No encontramos resultados para '{query}'. Te sugerimos buscar en: {', '.join(ubicaciones_sugeridas)}"
        else:
            mensaje = f"No encontramos resultados para '{query}'. Intenta con otra ubicación."
    
    return JsonResponse({'sugerencias': sugerencias, 'mensaje': mensaje})
