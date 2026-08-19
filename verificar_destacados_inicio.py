#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar destacados de Julian en la página principal"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from django.contrib.auth import get_user_model
from propiedades.models import Propiedad, Destacado
from django.utils import timezone

User = get_user_model()

julian = User.objects.filter(username__icontains='julian').first()

if not julian:
    print("❌ Usuario no encontrado")
    exit()

print(f"\n{'='*60}")
print(f"DIAGNÓSTICO: Destacados de Julian en página principal")
print(f"{'='*60}\n")

# Propiedades de Julian
propiedades = Propiedad.objects.filter(propietario=julian, estado='activa')
print(f"📋 Propiedades activas de Julian: {propiedades.count()}")
for prop in propiedades:
    print(f"   - {prop.titulo}")
    print(f"     ID: {prop.pk}")
    print(f"     Campo destacada: {prop.destacada}")
    
    # Verificar destacados asociados
    destacados = Destacado.objects.filter(propiedad=prop)
    print(f"     Total destacados (todos): {destacados.count()}")
    
    destacados_activos = destacados.filter(activo=True)
    print(f"     Destacados activos: {destacados_activos.count()}")
    
    for dest in destacados_activos:
        print(f"       * Tipo: {dest.tipo}, Fin: {dest.fecha_fin}, Vigente: {dest.fecha_fin > timezone.now()}")
    
    print()

# Simular el query de la vista inicio()
print(f"\n{'='*60}")
print(f"SIMULACIÓN DEL QUERY DE LA VISTA INICIO()")
print(f"{'='*60}\n")

destacados_activos = Propiedad.objects.filter(
    estado='activa',
    destacados__activo=True,
    destacados__fecha_fin__gt=timezone.now()
).distinct()

print(f"Propiedades que aparecen en inicio (todas): {destacados_activos.count()}")
for prop in destacados_activos:
    print(f"   - {prop.titulo} (propietario: {prop.propietario.username})")

julian_destacadas = destacados_activos.filter(propietario=julian)
print(f"\nPropiedades de Julian que aparecen: {julian_destacadas.count()}")

if julian_destacadas.count() == 0:
    print("\n❌ PROBLEMA: Las propiedades de Julian NO aparecen en inicio")
    print("\nPosibles causas:")
    print("1. No tienen destacados activos (activo=True)")
    print("2. Los destacados tienen fecha_fin en el pasado")
    print("3. El campo propiedad.destacada no está marcado")

print(f"\n{'='*60}\n")
