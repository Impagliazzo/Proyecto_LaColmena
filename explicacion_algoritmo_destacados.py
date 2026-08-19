#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ALGORITMO DE BALANCE DE PUBLICACIONES DESTACADAS EN LA PÁGINA PRINCIPAL
=========================================================================

La página principal (inicio) usa un sistema de SLOTS FIJOS y PRIORIDAD:

1. CAPACIDAD TOTAL: 6 destacados
   - 3 slots para destacados PREMIUM
   - 3 slots para destacados NORMALES

2. CRITERIOS DE FILTRADO:
   - Solo propiedades activas (estado='activa')
   - Solo destacados activos (destacados__activo=True)
   - Solo destacados vigentes (destacados__fecha_fin > ahora)

3. ALGORITMO DE PRIORIDAD (método Destacado.calcular_prioridad()):
   
   Puntos base por PLAN de suscripción del propietario:
   - Plan Avanzado:   +1000 puntos
   - Plan Intermedio: +500 puntos
   - Plan Básico:     +100 puntos
   
   Puntos por TIPO de destacado:
   - Premium: +50 puntos
   - Normal:  +10 puntos
   
   Puntos por ANTIGÜEDAD (favorece recientes):
   - Se resta 1 punto por cada día desde la fecha_compra
   - Destacados más nuevos tienen mayor prioridad
   
   Puntos por MÉTRICAS de la propiedad:
   - +1 punto por cada 10 vistas
   - +5 puntos por cada favorito
   
   FÓRMULA TOTAL:
   prioridad = puntos_plan + puntos_tipo - días_antigüedad + (vistas/10) + (favoritos*5)

4. PROCESO DE SELECCIÓN:
   a) Se obtienen TODOS los destacados activos y vigentes
   b) Se calcula la prioridad de cada uno
   c) Se ordenan de mayor a menor prioridad
   d) Se separan en dos listas: premium y normal
   e) Se toman los 3 primeros de cada lista
   f) Se combinan para mostrar 6 en total

5. IMPORTANTE:
   - NO se rellenan slots vacíos con propiedades normales
   - Solo se muestran propiedades con destacado activo y vigente
   - El orden favorece: plan > tipo > recientes > populares

EJEMPLO ACTUAL:
===============
Si hay 10 propiedades destacadas:
- 5 premium (se muestran las 3 con mayor prioridad)
- 5 normales (se muestran las 3 con mayor prioridad)

Si solo hay 2 destacadas:
- Se muestran solo esas 2 (no se rellena con otras)

ACTUALIZACIÓN PARA PROYECTO UNIVERSITARIO:
==========================================
- Las suscripciones son ilimitadas (nunca vencen)
- Los destacados se vinculan a la fecha de vencimiento de la suscripción
- Como las suscripciones vencen en ~100 años, los destacados son prácticamente ilimitados
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from propiedades.models import Propiedad, Destacado
from django.utils import timezone

print(__doc__)

# Simular el algoritmo
print("\n" + "="*70)
print("SIMULACIÓN DEL ALGORITMO CON DATOS ACTUALES")
print("="*70 + "\n")

destacados_activos = Propiedad.objects.filter(
    estado='activa',
    destacados__activo=True,
    destacados__fecha_fin__gt=timezone.now()
).select_related('propietario').prefetch_related('imagenes', 'destacados').distinct()

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

# Ordenar por prioridad
propiedades_con_prioridad.sort(key=lambda x: x['prioridad'], reverse=True)

print(f"Total de propiedades destacadas activas: {len(propiedades_con_prioridad)}\n")
print("RANKING POR PRIORIDAD:\n")

for i, item in enumerate(propiedades_con_prioridad, 1):
    prop = item['propiedad']
    dest = item['destacado']
    pri = item['prioridad']
    
    print(f"{i}. {prop.titulo}")
    print(f"   Propietario: {prop.propietario.username}")
    print(f"   Tipo destacado: {dest.get_tipo_display()}")
    print(f"   Prioridad: {pri} puntos")
    print(f"   Vistas: {prop.vistas}")
    print(f"   Favoritos: {prop.favoritos.count()}")
    print()

# Separar por tipo
premium = [item for item in propiedades_con_prioridad if item['destacado'].tipo == 'premium'][:3]
normal = [item for item in propiedades_con_prioridad if item['destacado'].tipo == 'normal'][:3]

print("="*70)
print("PROPIEDADES QUE SE MOSTRARÁN EN LA PÁGINA PRINCIPAL:")
print("="*70 + "\n")

print("DESTACADOS PREMIUM (máximo 3):")
if premium:
    for item in premium:
        print(f"   - {item['propiedad'].titulo} ({item['prioridad']} puntos)")
else:
    print("   (ninguno)")

print("\nDESTACADOS NORMALES (máximo 3):")
if normal:
    for item in normal:
        print(f"   - {item['propiedad'].titulo} ({item['prioridad']} puntos)")
else:
    print("   (ninguno)")

print(f"\nTOTAL EN PÁGINA PRINCIPAL: {len(premium) + len(normal)} de 6 slots\n")
