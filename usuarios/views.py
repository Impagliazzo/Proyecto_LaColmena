from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Usuario, Perfil
from .forms import (RegistroForm, LoginForm, PerfilForm, CompletarPerfilForm,
                    ValidarTelefonoForm, ValidarEmailForm, CambiarTelefonoForm, CambiarEmailForm)
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
    usuario = get_object_or_404(Usuario, username=username)
    
    # Crear perfil si no existe
    perfil, created = Perfil.objects.get_or_create(usuario=usuario)
    
    # Obtener publicaciones si es propietario
    publicaciones = None
    if usuario.es_propietario():
        publicaciones = usuario.publicaciones.select_related('categoria').prefetch_related('imagenes').all()
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'publicaciones': publicaciones,
        'es_propio': request.user == usuario
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
