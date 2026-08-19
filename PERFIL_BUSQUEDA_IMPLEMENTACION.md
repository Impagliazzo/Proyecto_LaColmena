# Sistema de Perfil de Búsqueda de Compañero/a - Implementación

## Descripción General
Se implementó un sistema completo de perfil extendido para la funcionalidad "Buscar Compañero/a". Los usuarios deben completar un perfil detallado antes de poder acceder a la búsqueda de compañeros de vivienda.

## Requisitos para Acceso
Para acceder a "Buscar Compañero/a", el usuario debe:
1. ✅ Tener teléfono validado
2. ✅ Tener email validado  
3. ✅ Completar el perfil de búsqueda con todos los campos obligatorios

## Estructura del Perfil de Búsqueda

### 1. Situación Actual
- **situacion_actual**: Si ya tiene lugar o busca con quién compartir
  - Opciones: "Ya tengo un lugar y busco compañero/a" | "No tengo lugar, busco con quién compartir"

### 2. Información Personal
- **edad**: Edad del usuario (mínimo 18 años)
- **genero**: Género (Masculino, Femenino, Otro, Prefiero no decir)

### 3. Situación Laboral/Académica
- **situacion_laboral**: Estudiante | Trabajador/a | Ambas | Otra

#### Campos condicionales para Estudiantes:
- **universidad**: Nombre de la universidad
- **modalidad_estudio**: Presencial | Virtual | Híbrida

#### Campos condicionales para Trabajadores:
- **empresa_rubro**: Empresa o rubro laboral
- **modalidad_trabajo**: Presencial | Remoto | Híbrido

### 4. Preferencias de Convivencia
- **presupuesto_maximo**: Rango de presupuesto mensual
  - Hasta $50.000
  - $50.000 - $100.000
  - $100.000 - $150.000
  - $150.000 - $200.000
  - $200.000 - $300.000
  - Más de $300.000
- **zona_preferida**: Zona o barrio preferido (texto libre)
- **fecha_ingreso**: Fecha aproximada de ingreso (DateField)
- **duracion_minima**: 3 meses | 6 meses | 1 año | 2 años | Indefinido

### 5. Hábitos y Estilo de Vida
- **fumador**: Boolean (¿Fumas?)
- **mascotas**: Boolean (¿Tienes mascotas?)
- **preferencia_convivencia**: Tranquila | Equilibrada | Social
- **horario_descanso**: Temprano (antes 22:00) | Normal (22:00-00:00) | Tarde (después 00:00)
- **orden_limpieza**: Básico | Prolijo | Muy prolijo | Indistinto
- **visitas**: Ocasionales | Frecuentes | No me molesta | Prefiero sin visitas
- **uso_espacios_comunes**: Compartir espacios | Usar en horarios distintos | Indistinto

## Archivos Modificados/Creados

### Modelos
- **usuarios/models.py**: Agregado modelo `PerfilBusqueda` con OneToOneField a Usuario
  - Método `esta_completo()`: Valida que todos los campos obligatorios estén completos

### Formularios
- **usuarios/forms.py**: Agregado `PerfilBusquedaForm`
  - Validación condicional de campos según situación laboral
  - Validación de edad mínima (18 años)
  - Estilos Tailwind CSS aplicados

### Vistas
- **usuarios/views.py**: 
  - Nueva vista `completar_perfil_busqueda`: Maneja la creación/edición del perfil
  - Importado `PerfilBusqueda` y `PerfilBusquedaForm`
  
- **propiedades/views.py**:
  - Modificada vista `buscar_companero`: Ahora verifica validaciones y perfil completo
  - Redirige a completar perfil si no está completo

### URLs
- **usuarios/urls.py**: Agregada ruta `completar-perfil-busqueda/`

### Templates
- **usuarios/templates/usuarios/completar_perfil_busqueda.html**: 
  - Diseño moderno con secciones divididas
  - Campos condicionales con JavaScript (se muestran según situación laboral)
  - Transiciones suaves
  - Barra de progreso
  - Iconos por sección

- **propiedades/templates/propiedades/buscar_companero.html**:
  - Agregado mensaje de confirmación cuando el perfil está completo

### Admin
- **usuarios/admin.py**: Registrado `PerfilBusquedaAdmin` con fieldsets organizados

## Flujo de Usuario

1. Usuario intenta acceder a "Buscar Compañero/a"
2. Si no tiene validaciones completas → redirige a perfil con warning
3. Si no tiene perfil de búsqueda → redirige a `completar_perfil_busqueda` con mensaje informativo
4. Si tiene perfil incompleto → redirige a `completar_perfil_busqueda` con warning
5. Si tiene perfil completo → accede a la página de búsqueda

## Validaciones Implementadas

### En el Formulario:
- Edad mínima 18 años
- Campos de estudiante obligatorios si `situacion_laboral` es "estudiante" o "ambas"
- Campos de trabajador obligatorios si `situacion_laboral` es "trabajador" o "ambas"

### En el Modelo:
- Método `esta_completo()` verifica:
  - Todos los campos base estén completos
  - Campos condicionales según situación laboral

## JavaScript Implementado

### Campos Condicionales:
```javascript
// Muestra/oculta campos según situación laboral seleccionada
- Si es "estudiante" o "ambas" → muestra campos de universidad
- Si es "trabajador" o "ambas" → muestra campos de empresa
- Transiciones suaves con clases CSS
```

## Migraciones
- **usuarios/migrations/0004_perfilbusqueda.py**: Crea la tabla del nuevo modelo

## Próximos Pasos Sugeridos

1. **Sistema de Matching**: Implementar algoritmo para emparejar usuarios compatibles
2. **Búsqueda y Filtros**: Permitir buscar perfiles con filtros avanzados
3. **Chat/Mensajería**: Sistema de mensajería interna entre usuarios
4. **Verificación**: Sistema de verificación de identidad más robusto
5. **Reportes**: Sistema para reportar perfiles sospechosos
6. **Favoritos**: Permitir guardar perfiles favoritos

## Notas Técnicas

- El modelo usa OneToOneField, por lo que cada usuario solo puede tener UN perfil de búsqueda
- Los campos condicionales son opcionales en el modelo pero validados en el formulario
- Las choices están en español siguiendo la convención del proyecto
- Todos los estilos usan Tailwind CSS con la paleta amber (siguiendo el theme de LaColmena)
