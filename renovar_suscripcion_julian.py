#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para renovar la suscripción de Julian"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from django.contrib.auth import get_user_model
from suscripciones.models import Suscripcion
from propiedades.models import Destacado
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Buscar al usuario julian
julian = User.objects.filter(username__icontains='julian').first()

if not julian:
    print("❌ Usuario no encontrado")
    exit()

print(f"\n✅ Usuario: {julian.username}")

# Obtener suscripción
suscripcion = Suscripcion.objects.filter(
    usuario=julian,
    estado='activa'
).first()

if not suscripcion:
    print("❌ No tiene suscripción")
    exit()

print(f"📋 Suscripción actual:")
print(f"   Plan: {suscripcion.plan.nombre}")
print(f"   Fecha vencimiento anterior: {suscripcion.fecha_vencimiento}")
print(f"   Está activa: {suscripcion.esta_activa()}")

# Renovar suscripción por 60 días
nueva_fecha_vencimiento = timezone.now() + timedelta(days=60)
suscripcion.fecha_vencimiento = nueva_fecha_vencimiento
suscripcion.save()

print(f"\n✅ Suscripción renovada!")
print(f"   Nueva fecha de vencimiento: {nueva_fecha_vencimiento}")
print(f"   Días hasta vencimiento: {(nueva_fecha_vencimiento - timezone.now()).days}")

# Limpiar destacados vencidos (marcarlos como inactivos)
destacados_vencidos = Destacado.objects.filter(
    propiedad__propietario=julian,
    activo=True,
    fecha_fin__lt=timezone.now()
)

count = destacados_vencidos.count()
if count > 0:
    destacados_vencidos.update(activo=False)
    print(f"\n🧹 Limpieza: {count} destacados vencidos marcados como inactivos")
else:
    print(f"\n✅ No hay destacados vencidos para limpiar")

# Mostrar estado final
destacados_activos_vigentes = Destacado.objects.filter(
    propiedad__propietario=julian,
    activo=True,
    fecha_fin__gte=timezone.now()
).count()

print(f"\n📊 Estado final:")
print(f"   Destacados activos y vigentes: {destacados_activos_vigentes}")
print(f"   Destacados disponibles: {suscripcion.plan.destacados_incluidos_mes - destacados_activos_vigentes}")

print("\n✅ ¡Listo! Ahora Julian puede destacar propiedades.")
