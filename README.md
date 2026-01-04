# Guía de Inicio - BuscoTecho

## Instalación y Configuración

### 1. Activar entorno virtual e instalar dependencias
```bash
# Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\python.exe

# Instalar dependencias Python
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Instalar Tailwind CSS (Node.js requerido)
npm install
```

### 2. Crear base de datos y migraciones
```bash
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate
```

### 3. Crear superusuario
```bash
.\venv\Scripts\python.exe manage.py createsuperuser
```

### 4. Cargar datos iniciales (opcional)
Puedes crear categorías manualmente desde el admin o usando el siguiente comando de Python:

```python
.\venv\Scripts\python.exe manage.py shell

# Dentro del shell de Django:
from propiedades.models import Categoria

categorias = [
    {'nombre': 'Departamentos', 'icono': 'fa-building', 'color': 'blue', 'orden': 1},
    {'nombre': 'Casas', 'icono': 'fa-home', 'color': 'green', 'orden': 2},
    {'nombre': 'Locales', 'icono': 'fa-store', 'color': 'purple', 'orden': 3},
    {'nombre': 'Oficinas', 'icono': 'fa-briefcase', 'color': 'orange', 'orden': 4},
    {'nombre': 'Terrenos', 'icono': 'fa-map', 'color': 'yellow', 'orden': 5},
    {'nombre': 'Bodegas', 'icono': 'fa-warehouse', 'color': 'pink', 'orden': 6},
    {'nombre': 'Alojamiento', 'icono': 'fa-bed', 'color': 'red', 'orden': 7},
]

for cat in categorias:
    Categoria.objects.get_or_create(nombre=cat['nombre'], defaults=cat)

exit()
```

### 5. Compilar CSS con Tailwind (en otra terminal)
```bash
npm run dev
```

### 6. Iniciar servidor de desarrollo
```bash
.\venv\Scripts\python.exe manage.py runserver
```

Accede a: http://127.0.0.1:8000/

## Estructura del Proyecto

```
Proyecto_BuscoTecho/
├── manage.py
├── requirements.txt
├── package.json
├── tailwind.config.js
├── Proyecto_BuscoTecho/          # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── usuarios/                      # App de gestión de usuarios
│   ├── models.py                  # Usuario, Perfil
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── propiedades/                   # App de propiedades
│   ├── models.py                  # Propiedad, Categoria, Imagen, Favorito, Valoracion
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── contactos/                     # App de solicitudes de contacto
│   ├── models.py                  # SolicitudContacto
│   ├── views.py
│   └── templates/
├── suscripciones/                 # App de planes y suscripciones
│   ├── models.py                  # PlanSuscripcion, Suscripcion, Pago
│   ├── views.py
│   └── templates/
├── notificaciones/                # App de notificaciones
│   ├── models.py                  # Notificacion
│   ├── views.py
│   └── templates/
├── templates/                     # Templates globales
│   └── base.html
├── static/                        # Archivos estáticos
│   └── css/
└── media/                         # Archivos subidos
```

## Funcionalidades Implementadas

### ✅ Usuarios
- Registro de usuarios
- Inicio de sesión
- Perfil de usuario editable
- Conversión a propietario
- Autenticación personalizada

### ✅ Propiedades
- Publicación de propiedades (con hasta 10 imágenes)
- Búsqueda y filtrado avanzado
- Categorías de propiedades
- Vista de detalle
- Propiedades destacadas
- Marcador de favoritos
- Sistema de valoraciones (1-5 estrellas)
- Estadísticas de vistas

### ✅ Gestión de Propietarios
- Panel "Mis Alquileres"
- Crear, editar, suspender y eliminar publicaciones
- Estadísticas (vistas, favoritos, valoraciones)
- Límite de publicaciones según plan

### ✅ Contactos
- Solicitudes de contacto entre usuarios y propietarios
- Notificaciones por email
- Gestión de solicitudes recibidas
- Estados de solicitud

### ✅ Suscripciones
- Planes de suscripción
- Primera publicación gratuita
- Gestión de pagos
- Auto-renovación
- Alertas de vencimiento

### ✅ Notificaciones
- Sistema de notificaciones en tiempo real
- Notificaciones de favoritos
- Notificaciones de contacto
- Recordatorios de suscripción
- Marcado de leídas/no leídas

## Próximos Pasos

1. **Configurar Email Real**: Actualizar settings.py con credenciales SMTP
2. **Integrar Pasarela de Pagos**: Stripe, PayPal, etc.
3. **Agregar Google Maps**: Para mostrar ubicaciones
4. **Sistema de Mensajería**: Chat entre usuarios
5. **Notificaciones Push**: Usando WebSockets o similar
6. **Búsqueda Avanzada**: Con Elasticsearch o similar
7. **Tests**: Agregar tests unitarios y de integración
8. **Deploy**: Configurar para producción

## Panel de Administración

Accede al admin en: http://127.0.0.1:8000/admin/

Desde el admin puedes:
- Gestionar usuarios
- Moderar propiedades
- Ver solicitudes de contacto
- Administrar planes de suscripción
- Ver notificaciones

## Tecnologías Utilizadas

- **Backend**: Django 5.2.9
- **Frontend**: Tailwind CSS 3.4
- **Base de Datos**: SQLite (desarrollo)
- **Imágenes**: Pillow
- **Iconos**: Font Awesome 6.5

## Contacto

Para soporte o consultas sobre el proyecto, contacta al equipo de desarrollo.
