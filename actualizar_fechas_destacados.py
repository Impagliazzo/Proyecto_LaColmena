#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para actualizar fechas de destacados activos"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from propiedades.models import Destacado
from suscripciones.models import Suscripcion
from django.utils import timezone
from datetime import timedelta

print(f"\n{'='*60}")
print(f"ACTUALIZACIÓN: Fechas de destacados activos")
print(f"{'='*60}\n")

# Obtener todos los destacados activos con fecha vencida
destacados_activos_vencidos = Destacado.objects.filter(
    activo=True,
    fecha_fin__lt=timezone.now()
)

print(f"📋 Destacados activos con fecha vencida: {destacados_activos_vencidos.count()}\n")

for destacado in destacados_activos_vencidos:
    propietario = destacado.propiedad.propietario
    
    # Buscar suscripción activa del propietario
    suscripcion = Suscripcion.objects.filter(
        usuario=propietario,
        estado='activa'
    ).first()
    
    print(f"Actualizando destacado de: {destacado.propiedad.titulo}")
    print(f"   Propietario: {propietario.username}")
    print(f"   Fecha fin anterior: {destacado.fecha_fin}")
    
    if suscripcion and suscripcion.esta_activa():
        # Vincular al período de suscripción (fecha_vencimiento)
        nueva_fecha_fin = suscripcion.fecha_vencimiento
        destacado.fecha_fin = nueva_fecha_fin
        destacado.fecha_inicio = timezone.now()
        destacado.duracion_dias = (nueva_fecha_fin - timezone.now()).days
        destacado.save()
        
        print(f"   ✅ Nueva fecha fin: {nueva_fecha_fin}")
        print(f"   ✅ Días de duración: {destacado.duracion_dias}")
    else:
        # No tiene suscripción activa, marcar como inactivo
        destacado.activo = False
        destacado.save()
        print(f"   ⚠️ Sin suscripción activa, marcado como inactivo")
    
    print()

print(f"{'='*60}")
print(f"✅ Actualización completada")
print(f"{'='*60}\n")

# Verificar resultado
destacados_vigentes = Destacado.objects.filter(
    activo=True,
    fecha_fin__gt=timezone.now()
)
print(f"📊 Destacados activos y vigentes ahora: {destacados_vigentes.count()}")
for dest in destacados_vigentes:
    print(f"   - {dest.propiedad.titulo} ({dest.propiedad.propietario.username})")

print()
