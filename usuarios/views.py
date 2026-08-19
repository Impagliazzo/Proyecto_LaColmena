from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Usuario, Perfil
from .forms import (RegistroForm, LoginForm, PerfilForm, CompletarPerfilForm,
                    ValidarTelefonoForm, ValidarEmailForm, CambiarTelefonoForm, CambiarEmailForm, PerfilBusquedaForm)
from notificaciones.models import Notificacion

def registro(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil automáticamente
            Perfil.objects.create(usuario=user)
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión')
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """Vista para inicio de sesión"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Verificar si es el primer login
                es_primer_login = user.last_login is None
                login(request, user)
                
                if es_primer_login:
                    messages.success(request, f'¡Bienvenido a LaColmena, {user.first_name or user.username}!')
                else:
                    messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.username}!')
                
                # Redirigir a la página que intentaba visitar o a inicio
                next_url = request.GET.get('next') or request.POST.get('next') or 'propiedades:inicio'
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('propiedades:inicio')


@login_required
def perfil_view(request, username):
    """Vista de perfil de usuario"""
    from .forms import PerfilBusquedaForm
    
    usuario = get_object_or_404(Usuario, username=username)
    
    # Crear perfil si no existe
    perfil, created = Perfil.objects.get_or_create(usuario=usuario)
    
    # Detectar modo vista previa
    preview_mode = request.GET.get('preview') == 'true'
    
    # Obtener publicaciones si es propietario
    publicaciones = None
    if usuario.es_propietario():
        publicaciones = usuario.publicaciones.select_related('categoria').prefetch_related('imagenes').all()
    
    # Opciones de etiquetas para edición inline
    etiquetas_opciones = {
        'habitos_vicios': PerfilBusquedaForm.HABITOS_VICIOS_CHOICES,
        'mascotas_tags': PerfilBusquedaForm.MASCOTAS_CHOICES,
        'convivencia_limpieza': PerfilBusquedaForm.CONVIVENCIA_LIMPIEZA_CHOICES,
        'horarios_trabajo': PerfilBusquedaForm.HORARIOS_TRABAJO_CHOICES,
        'comida_social': PerfilBusquedaForm.COMIDA_SOCIAL_CHOICES,
    }
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'publicaciones': publicaciones,
        'es_propio': request.user == usuario and not preview_mode,  # Si está en preview, no puede editar
        'preview_mode': preview_mode,
        'etiquetas_opciones': etiquetas_opciones,
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('usuarios:perfil', username=request.user.username)
    else:
        form = PerfilForm(instance=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})


@login_required
def convertir_a_propietario(request):
    """Permite a un usuario convertirse en propietario"""
    if request.method == 'POST':
        request.user.convertir_a_propietario()
        messages.success(request, '¡Ahora eres propietario! Ya puedes publicar tus inmuebles')
        return redirect('propiedades:mis_propiedades')
    return render(request, 'usuarios/convertir_propietario.html')


@login_required
def completar_perfil(request):
    """Vista para completar el perfil progresivo"""
    perfil = request.user.perfil
    
    if request.method == 'POST':
        form = CompletarPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            perfil.actualizar_estado_completitud()
            messages.success(request, '¡Perfil completado exitosamente!')
            
            # Redirigir según lo que el usuario estaba intentando hacer
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('propiedades:inicio')
    else:
        form = CompletarPerfilForm(instance=perfil)
    
    context = {
        'form': form,
        'porcentaje': perfil.porcentaje_completado(),
    }
    return render(request, 'usuarios/completar_perfil.html', context)


@login_required
def validar_telefono(request):
    """Vista para validar teléfono"""
    if request.user.telefono_validado:
        messages.info(request, 'Tu teléfono ya está validado')
        return redirect('propiedades:inicio')
    
    if not request.user.telefono:
        messages.error(request, 'Primero debes agregar un teléfono en tu perfil')
        return redirect('usuarios:editar_perfil')
    
    # Cerrar el banner de validación al entrar a esta página
    request.session['banner_validacion_cerrado'] = True
    
    codigo_enviado = request.session.get('codigo_telefono_enviado', False)
    
    if request.method == 'POST':
        # Verificar si se solicitó enviar código
        if 'enviar_codigo' in request.POST:
            request.session['codigo_telefono_enviado'] = True
            messages.info(request, f'Te hemos enviado un SMS con el código al {request.user.telefono}. (Usa: 123)')
            return redirect('usuarios:validar_telefono')
        
        # Procesar validación del código
        form = ValidarTelefonoForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            # Código hardcodeado para pruebas
            if codigo == '123':
                request.user.telefono_validado = True
                request.user.save()
                
                # Limpiar sesión
                request.session.pop('banner_validacion_cerrado', None)
                request.session.pop('codigo_telefono_enviado', None)
                
                messages.success(request, '¡Teléfono validado correctamente!')
                return redirect('propiedades:inicio')
            else:
                messages.error(request, 'Código incorrecto. Intenta de nuevo.')
    else:
        form = ValidarTelefonoForm()
    
    return render(request, 'usuarios/validar_telefono.html', {'form': form, 'codigo_enviado': codigo_enviado})


@login_required
def validar_email(request):
    """Vista para validar email"""
    if request.user.email_validado:
        messages.info(request, 'Tu email ya está validado')
        return redirect('propiedades:inicio')
    
    # Cerrar el banner de validación al entrar a esta página
    request.session['banner_validacion_cerrado'] = True
    
    codigo_enviado = request.session.get('codigo_email_enviado', False)
    
    if request.method == 'POST':
        # Verificar si se solicitó enviar código
        if 'enviar_codigo' in request.POST:
            request.session['codigo_email_enviado'] = True
            messages.info(request, f'Te hemos enviado un email con el código a {request.user.email}. (Usa: 123)')
            return redirect('usuarios:validar_email')
        
        # Procesar validación del código
        form = ValidarEmailForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            # Código hardcodeado para pruebas
            if codigo == '123':
                request.user.email_validado = True
                request.user.save()
                
                # Limpiar sesión
                request.session.pop('banner_validacion_cerrado', None)
                request.session.pop('codigo_email_enviado', None)
                
                messages.success(request, '¡Email validado correctamente!')
                return redirect('propiedades:inicio')
            else:
                messages.error(request, 'Código incorrecto. Intenta de nuevo.')
    else:
        form = ValidarEmailForm()
    
    return render(request, 'usuarios/validar_email.html', {'form': form, 'codigo_enviado': codigo_enviado})


@login_required
def cambiar_telefono(request):
    """Vista para cambiar teléfono (paso 1: verificar actual)"""
    if not request.user.telefono_validado:
        messages.error(request, 'Primero debes validar tu teléfono actual')
        return redirect('usuarios:validar_telefono')
    
    if request.method == 'POST':
        form = ValidarTelefonoForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            if codigo == '123':
                request.session['verificado_telefono_actual'] = True
                return redirect('usuarios:ingresar_nuevo_telefono')
            else:
                messages.error(request, 'Código incorrecto')
    else:
        form = ValidarTelefonoForm()
        messages.info(request, f'Verifica tu teléfono actual: {request.user.telefono} (Código: 123)')
    
    return render(request, 'usuarios/verificar_telefono_actual.html', {'form': form})


@login_required
def ingresar_nuevo_telefono(request):
    """Vista para cambiar teléfono (paso 2: ingresar nuevo)"""
    if not request.session.get('verificado_telefono_actual'):
        return redirect('usuarios:cambiar_telefono')
    
    if request.method == 'POST':
        form = CambiarTelefonoForm(request.POST)
        if form.is_valid():
            nuevo_telefono = form.cleaned_data['telefono']
            request.session['nuevo_telefono'] = nuevo_telefono
            return redirect('usuarios:verificar_nuevo_telefono')
    else:
        form = CambiarTelefonoForm()
    
    return render(request, 'usuarios/ingresar_nuevo_telefono.html', {'form': form})


@login_required
def verificar_nuevo_telefono(request):
    """Vista para cambiar teléfono (paso 3: verificar nuevo)"""
    nuevo_telefono = request.session.get('nuevo_telefono')
    if not nuevo_telefono:
        return redirect('usuarios:cambiar_telefono')
    
    if request.method == 'POST':
        form = ValidarTelefonoForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            if codigo == '123':
                request.user.telefono = nuevo_telefono
                request.user.save()
                
                # Limpiar sesión
                request.session.pop('verificado_telefono_actual', None)
                request.session.pop('nuevo_telefono', None)
                
                messages.success(request, 'Teléfono actualizado correctamente')
                return redirect('usuarios:perfil', username=request.user.username)
            else:
                messages.error(request, 'Código incorrecto')
    else:
        form = ValidarTelefonoForm()
        messages.info(request, f'Verifica tu nuevo teléfono: {nuevo_telefono} (Código: 123)')
    
    return render(request, 'usuarios/validar_telefono.html', {
        'form': form,
        'nuevo_telefono': nuevo_telefono
    })


@login_required
def cambiar_email(request):
    """Vista para cambiar email (paso 1: verificar actual)"""
    if not request.user.email_validado:
        messages.error(request, 'Primero debes validar tu email actual')
        return redirect('usuarios:validar_email')
    
    if request.method == 'POST':
        form = ValidarEmailForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            if codigo == '123':
                request.session['verificado_email_actual'] = True
                return redirect('usuarios:ingresar_nuevo_email')
            else:
                messages.error(request, 'Código incorrecto')
    else:
        form = ValidarEmailForm()
        messages.info(request, f'Verifica tu email actual: {request.user.email} (Código: 123)')
    
    return render(request, 'usuarios/verificar_email_actual.html', {'form': form})


@login_required
def ingresar_nuevo_email(request):
    """Vista para cambiar email (paso 2: ingresar nuevo)"""
    if not request.session.get('verificado_email_actual'):
        return redirect('usuarios:cambiar_email')
    
    if request.method == 'POST':
        form = CambiarEmailForm(request.POST)
        if form.is_valid():
            nuevo_email = form.cleaned_data['email']
            request.session['nuevo_email'] = nuevo_email
            return redirect('usuarios:verificar_nuevo_email')
    else:
        form = CambiarEmailForm()
    
    return render(request, 'usuarios/ingresar_nuevo_email.html', {'form': form})


@login_required
def verificar_nuevo_email(request):
    """Vista para cambiar email (paso 3: verificar nuevo)"""
    nuevo_email = request.session.get('nuevo_email')
    if not nuevo_email:
        return redirect('usuarios:cambiar_email')
    
    if request.method == 'POST':
        form = ValidarEmailForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            if codigo == '123':
                request.user.email = nuevo_email
                request.user.save()
                
                # Limpiar sesión
                request.session.pop('verificado_email_actual', None)
                request.session.pop('nuevo_email', None)
                
                messages.success(request, 'Email actualizado correctamente')
                return redirect('usuarios:perfil', username=request.user.username)
            else:
                messages.error(request, 'Código incorrecto')
    else:
        form = ValidarEmailForm()
        messages.info(request, f'Verifica tu nuevo email: {nuevo_email} (Código: 123)')
    
    return render(request, 'usuarios/validar_email.html', {
        'form': form,
        'nuevo_email': nuevo_email
    })


@login_required
def cerrar_banner_validacion(request):
    """Vista para cerrar el banner de validación permanentemente"""
    if request.method == 'POST':
        # Marcar como cerrado permanentemente (no se volverá a mostrar hasta completar validación)
        request.session['banner_validacion_cerrado'] = True
        request.session.modified = True
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@login_required
def completar_perfil_busqueda(request):
    """Vista para completar el perfil de búsqueda de compañero/a"""
    # Verificar que tenga validaciones completas
    if not request.user.tiene_validaciones_completas():
        messages.warning(request, 'Debes validar tu teléfono y email antes de completar tu perfil de búsqueda.')
        return redirect('usuarios:perfil', username=request.user.username)
    
    # Obtener el perfil del usuario (siempre existe)
    perfil = request.user.perfil
    
    if request.method == 'POST':
        form = PerfilBusquedaForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()

            if perfil.perfil_busqueda_completo():
                # Si tiene lugar y todavía no publicó, el siguiente paso natural
                # es crear esa publicación (no es lo mismo que publicar un inmueble
                # en alquiler/venta) — lo llevamos directo ahí.
                if perfil.situacion_actual == 'tengo_lugar' and not hasattr(request.user, 'publicacion_companero'):
                    messages.success(request, '¡Perfil de búsqueda completado! Ahora creá tu publicación para buscar compañero/a.')
                    return redirect('usuarios:crear_publicacion_companero')
                messages.success(request, '¡Perfil de búsqueda completado! Ya puedes buscar compañero/a.')
                return redirect('usuarios:perfil', username=request.user.username)
            else:
                messages.warning(request, 'Algunos campos obligatorios están incompletos. Por favor, revísalos.')
    else:
        form = PerfilBusquedaForm(instance=perfil)
    
    context = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'usuarios/completar_perfil_busqueda.html', context)


@login_required
def ver_perfil_busqueda(request, username):
    """Vista para ver el perfil de búsqueda de un usuario - OBSOLETA, redirige al perfil único"""
    return redirect('usuarios:perfil', username=username)


@login_required
def cambiar_avatar(request):
    """Vista AJAX para cambiar el avatar del usuario"""
    if request.method == 'POST':
        tipo = request.POST.get('tipo')  # 'foto' o 'icono'
        icono = request.POST.get('icono', '')
        
        usuario = request.user
        
        if tipo == 'icono' and icono:
            usuario.tipo_avatar = 'icono'
            usuario.icono_avatar = icono
            usuario.save()
            return JsonResponse({
                'success': True,
                'tipo': 'icono',
                'icono': icono
            })
        elif tipo == 'foto' and request.FILES.get('foto'):
            usuario.foto_perfil = request.FILES['foto']
            usuario.tipo_avatar = 'foto'
            usuario.save()
            return JsonResponse({
                'success': True,
                'tipo': 'foto',
                'url': usuario.foto_perfil.url
            })
        
        return JsonResponse({'success': False, 'error': 'Datos inválidos'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def actualizar_campo_perfil(request):
    """Vista AJAX para actualizar campos del perfil (nombre, apellido, biografía)"""
    if request.method == 'POST':
        campo = request.POST.get('campo')  # 'first_name', 'last_name', 'biografia'
        valor = request.POST.get('valor', '')
        
        usuario = request.user
        campos_permitidos = ['first_name', 'last_name', 'biografia']
        
        if campo not in campos_permitidos:
            return JsonResponse({'success': False, 'error': 'Campo no permitido'})
        
        # Validaciones específicas
        if campo in ['first_name', 'last_name'] and len(valor) > 150:
            return JsonResponse({'success': False, 'error': 'El nombre es demasiado largo'})
        
        if campo == 'biografia' and len(valor) > 500:
            return JsonResponse({'success': False, 'error': 'La biografía no puede tener más de 500 caracteres'})
        
        # Actualizar campo
        setattr(usuario, campo, valor)
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'campo': campo,
            'valor': valor
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def actualizar_etiquetas(request):
    """Vista AJAX para actualizar las etiquetas del perfil de búsqueda"""
    if request.method == 'POST':
        import json
        
        perfil = request.user.perfil
        
        # Obtener las etiquetas del POST
        habitos_vicios = json.loads(request.POST.get('habitos_vicios', '[]'))
        mascotas_tags = json.loads(request.POST.get('mascotas_tags', '[]'))
        convivencia_limpieza = json.loads(request.POST.get('convivencia_limpieza', '[]'))
        horarios_trabajo = json.loads(request.POST.get('horarios_trabajo', '[]'))
        comida_social = json.loads(request.POST.get('comida_social', '[]'))
        
        # Actualizar las etiquetas
        perfil.habitos_vicios = habitos_vicios
        perfil.mascotas_tags = mascotas_tags
        perfil.convivencia_limpieza = convivencia_limpieza
        perfil.horarios_trabajo = horarios_trabajo
        perfil.comida_social = comida_social
        perfil.save()
        
        # Obtener todas las etiquetas con descripciones para la respuesta
        etiquetas = perfil.get_todas_etiquetas_con_descripciones()
        
        return JsonResponse({
            'success': True,
            'etiquetas': etiquetas
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def crear_publicacion_companero(request):
    """Vista para crear/editar publicación de búsqueda de compañero/a"""
    from .models import PublicacionCompanero, ImagenPublicacionCompanero
    from .forms import PublicacionCompaneroForm
    
    # Verificar que el usuario tenga perfil de búsqueda completo y que tenga lugar
    if not request.user.perfil.perfil_busqueda_completo():
        messages.error(request, 'Primero debes completar tu perfil de búsqueda de compañero/a.')
        return redirect('usuarios:completar_perfil_busqueda')
    
    if request.user.perfil.situacion_actual != 'tengo_lugar':
        messages.error(request, 'Solo puedes publicar si ya tienes un lugar y buscas compañero/a.')
        return redirect('usuarios:perfil', username=request.user.username)
    
    # Obtener o crear publicación (solo puede tener una)
    publicacion = PublicacionCompanero.objects.filter(usuario=request.user).first()
    es_edicion = publicacion is not None
    
    if request.method == 'POST':
        form = PublicacionCompaneroForm(request.POST, request.FILES, instance=publicacion)
        
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.usuario = request.user
            publicacion.save()
            
            # Procesar imágenes subidas (solo agregar las nuevas)
            imagenes = request.FILES.getlist('imagenes')
            
            # Obtener el máximo orden actual
            from django.db.models import Max
            max_orden = publicacion.imagenes.aggregate(Max('orden'))['orden__max']
            if max_orden is None:
                max_orden = -1
            
            # Agregar las nuevas imágenes
            for i, imagen in enumerate(imagenes):
                ImagenPublicacionCompanero.objects.create(
                    publicacion=publicacion,
                    imagen=imagen,
                    orden=max_orden + 1 + i
                )
            
            mensaje = 'Publicación actualizada correctamente.' if es_edicion else 'Publicación creada correctamente.'
            messages.success(request, mensaje)
            return redirect('usuarios:perfil', username=request.user.username)
        else:
            # Si hay errores de validación, mostrarlos
            for field, errors in form.errors.items():
                field_label = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(request, f'{field_label}: {error}')
            return redirect('usuarios:perfil', username=request.user.username)
    else:
        form = PublicacionCompaneroForm(instance=publicacion)
    
    context = {
        'form': form,
        'publicacion': publicacion,
        'es_edicion': es_edicion,
    }
    
    return render(request, 'usuarios/crear_publicacion_companero.html', context)


@login_required
def eliminar_imagen_publicacion_companero(request, imagen_id):
    """Vista para eliminar una imagen de la publicación"""
    from .models import ImagenPublicacionCompanero
    
    if request.method == 'POST':
        try:
            imagen = ImagenPublicacionCompanero.objects.get(
                id=imagen_id,
                publicacion__usuario=request.user
            )
            imagen.delete()
            return JsonResponse({'success': True})
        except ImagenPublicacionCompanero.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Imagen no encontrada'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def cambiar_estado_publicacion_companero(request):
    """Vista para cambiar el estado de la publicación (activa/pausada/completada)"""
    from .models import PublicacionCompanero
    
    if request.method == 'POST':
        try:
            estado = request.POST.get('estado')
            publicacion = PublicacionCompanero.objects.get(usuario=request.user)
            
            if estado in dict(PublicacionCompanero.ESTADO_CHOICES).keys():
                publicacion.estado = estado
                publicacion.save()
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Publicación marcada como {publicacion.get_estado_display()}'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Estado inválido'})
                
        except PublicacionCompanero.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No tienes una publicación'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
