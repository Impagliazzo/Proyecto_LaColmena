#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para actualizar suscripciones a tiempo ilimitado"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from suscripciones.models import Suscripcion
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*60)
print("ACTUALIZACIÓN: Suscripciones con tiempo ilimitado")
print("="*60 + "\n")

# Obtener todas las suscripciones activas
suscripciones_activas = Suscripcion.objects.filter(estado='activa')

print(f"📋 Suscripciones activas encontradas: {suscripciones_activas.count()}\n")

# Fecha muy lejana (100 años en el futuro)
fecha_ilimitada = timezone.now() + timedelta(days=36500)

for suscripcion in suscripciones_activas:
    print(f"Actualizando suscripción de {suscripcion.usuario.username}...")
    print(f"   Plan: {suscripcion.plan.nombre}")
    print(f"   Fecha vencimiento anterior: {suscripcion.fecha_vencimiento}")
    
    suscripcion.fecha_vencimiento = fecha_ilimitada
    suscripcion.save()
    
    print(f"   ✅ Nueva fecha: {suscripcion.fecha_vencimiento}")
    print(f"   ✅ Está activa: {suscripcion.esta_activa()}")
    print(f"   ✅ Días restantes: {suscripcion.dias_restantes()}\n")

print("="*60)
print("✅ Todas las suscripciones activas ahora son ilimitadas")
print("="*60 + "\n")
