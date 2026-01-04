from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .models import Usuario, Perfil
from .forms import RegistroForm, LoginForm, PerfilForm, CompletarPerfilForm

def registro(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil automáticamente
            Perfil.objects.create(usuario=user)
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a BuscoTecho')
            # Redirigir a completar perfil
            return redirect('usuarios:completar_perfil')
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
                login(request, user)
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
        publicaciones = usuario.publicaciones.all()
    
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
            return redirect('usuarios:perfil', username=request.user.username)
    else:
        form = CompletarPerfilForm(instance=perfil)
    
    context = {
        'form': form,
        'porcentaje': perfil.porcentaje_completado(),
    }
    return render(request, 'usuarios/completar_perfil.html', context)
