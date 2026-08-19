#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar el estado de destacados de Julian"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from django.contrib.auth import get_user_model
from suscripciones.models import Suscripcion, PlanSuscripcion
from propiedades.models import Destacado, Propiedad
from django.utils import timezone

User = get_user_model()

# Listar todos los usuarios propietarios
print("\n📋 Usuarios registrados:")
for user in User.objects.all():
    print(f"   - {user.username} ({user.email}) - Propietario: {user.es_propietario()}")

# Buscar al usuario Julian (o similar)
try:
    # Intentar encontrar usuario con nombre similar a Julian
    julian = User.objects.filter(username__icontains='julian').first()
    if not julian:
        # Buscar el primer propietario con propiedades
        julian = User.objects.filter(perfil__es_propietario=True).first()
    
    if not julian:
        print("\n❌ No se encontró ningún usuario propietario")
        exit()
        
    julian = User.objects.get(pk=julian.pk)
    print(f"\n✅ Usuario encontrado: {julian.username}")
    print(f"   Email: {julian.email}")
    print(f"   Es propietario: {julian.es_propietario()}")
    
    # Verificar suscripción  
    suscripcion = Suscripcion.objects.filter(
        usuario=julian,
        estado='activa'
    ).select_related('plan').first()
    
    if suscripcion:
        print(f"\n✅ Suscripción activa encontrada:")
        print(f"   Plan: {suscripcion.plan.nombre}")
        print(f"   Está activa: {suscripcion.esta_activa()}")
        print(f"   Destacados incluidos por mes: {suscripcion.plan.destacados_incluidos_mes}")
        print(f"   Puede comprar destacados: {suscripcion.plan.puede_comprar_destacados}")
        print(f"   Fecha vencimiento: {suscripcion.fecha_vencimiento}")
    else:
        print(f"\n❌ No tiene suscripción activa")
    
    # Contar propiedades
    propiedades = Propiedad.objects.filter(propietario=julian)
    print(f"\n📋 Propiedades de Julian: {propiedades.count()}")
    for prop in propiedades:
        print(f"   - {prop.titulo} (Estado: {prop.estado})")
    
    # Verificar destacados activos
    destacados_activos = Destacado.objects.filter(
        propiedad__propietario=julian,
        activo=True
    )
    print(f"\n⭐ Destacados ACTIVOS actualmente: {destacados_activos.count()}")
    for dest in destacados_activos:
        print(f"   - {dest.propiedad.titulo}: Tipo={dest.tipo}, Fin={dest.fecha_fin}, Vigente={dest.esta_activo()}")
    
    # Verificar todos los destacados (incluso inactivos)
    todos_destacados = Destacado.objects.filter(
        propiedad__propietario=julian
    )
    print(f"\n📊 Todos los destacados (activos e inactivos): {todos_destacados.count()}")
    for dest in todos_destacados:
        print(f"   - {dest.propiedad.titulo}: Activo={dest.activo}, Tipo={dest.tipo}, Fin={dest.fecha_fin}")
    
    # Calcular destacados disponibles (como en la vista)
    if suscripcion and suscripcion.esta_activa():
        plan = suscripcion.plan
        destacados_activos_actuales = destacados_activos.count()
        destacados_disponibles = plan.destacados_incluidos_mes - destacados_activos_actuales
        
        print(f"\n🔢 Cálculo de disponibilidad:")
        print(f"   Destacados en el plan: {plan.destacados_incluidos_mes}")
        print(f"   Destacados activos actualmente: {destacados_activos_actuales}")
        print(f"   Destacados disponibles: {destacados_disponibles}")
        print(f"   Puede destacar: {destacados_disponibles > 0 or plan.puede_comprar_destacados}")
        
        if destacados_disponibles <= 0:
            print(f"\n❌ PROBLEMA: destacados_disponibles <= 0")
            print(f"   Por eso el botón está deshabilitado!")
        else:
            print(f"\n✅ OK: Tiene {destacados_disponibles} destacados disponibles")
    else:
        print(f"\n❌ PROBLEMA PRINCIPAL: La suscripción NO está activa!")
        print(f"   Motivo: fecha_vencimiento ({suscripcion.fecha_vencimiento}) < ahora ({timezone.now()})")
        print(f"   Por eso NO se calculan destacados disponibles")
        print(f"   puede_destacar = False en la vista mis_propiedades")
        print(f"   Y el botón muestra 'Mejora tu plan para destacar propiedades'")

    
except User.DoesNotExist:
    print("❌ Usuario 'Julian' no encontrado")

print("\n" + "="*60)
print("Verificación completada")
print("="*60 + "\n")
