# INSTRUCCIONES DE INICIO RÁPIDO

## ⚡ Inicio Rápido (5 pasos)

### 1. Crear un superusuario (administrador)
```bash
.\venv\Scripts\python.exe manage.py createsuperuser
```
Ingresa:
- Username: admin
- Email: admin@buscotecho.com
- Password: (elige una contraseña)

### 2. Iniciar el servidor
```bash
.\venv\Scripts\python.exe manage.py runserver
```

### 3. Acceder a la aplicación
Abre tu navegador en: http://127.0.0.1:8000/

### 4. Acceder al panel de administración
http://127.0.0.1:8000/admin/
- Usuario: admin
- Contraseña: (la que configuraste)

### 5. Probar la aplicación
1. Crea un usuario normal desde el sitio
2. Conviértete en propietario
3. Publica una propiedad
4. Navega y prueba las funcionalidades

---

## 📋 Checklist de Funcionalidades

### ✅ Sistema de Usuarios
- [x] Registro de usuarios
- [x] Inicio de sesión
- [x] Perfiles editables
- [x] Conversión a propietario
- [x] Sistema de favoritos

### ✅ Propiedades
- [x] Crear publicación (hasta 10 imágenes)
- [x] Editar publicación
- [x] Suspender/Reactivar
- [x] Eliminar
- [x] Búsqueda y filtros avanzados
- [x] Categorías
- [x] Propiedades destacadas
- [x] Sistema de valoraciones (1-5 estrellas)
- [x] Contador de vistas

### ✅ Panel de Propietarios
- [x] Dashboard con estadísticas
- [x] Listado de publicaciones
- [x] Gestión completa de propiedades

### ✅ Contacto
- [x] Solicitar contacto con propietarios
- [x] Ver solicitudes enviadas
- [x] Ver solicitudes recibidas
- [x] Notificación por email

### ✅ Suscripciones
- [x] Planes de suscripción
- [x] Primera publicación gratis
- [x] Límites según plan
- [x] Gestión de pagos

### ✅ Notificaciones
- [x] Sistema de notificaciones
- [x] Marcar como leída
- [x] Diferentes tipos de notificaciones

---

## 🎨 Diseño

El diseño está basado en Tailwind CSS con:
- Colores principales: Amarillo (#FBBF24) y Naranja
- Diseño responsive
- Iconos Font Awesome
- Animaciones suaves
- Interfaz moderna y limpia

---

## 🔧 Comandos Útiles

### Crear nuevas migraciones
```bash
.\venv\Scripts\python.exe manage.py makemigrations
```

### Aplicar migraciones
```bash
.\venv\Scripts\python.exe manage.py migrate
```

### Crear superusuario
```bash
.\venv\Scripts\python.exe manage.py createsuperuser
```

### Ejecutar servidor
```bash
.\venv\Scripts\python.exe manage.py runserver
```

### Acceder al shell de Django
```bash
.\venv\Scripts\python.exe manage.py shell
```

---

## 📁 URLs Principales

- **Inicio**: http://127.0.0.1:8000/
- **Propiedades**: http://127.0.0.1:8000/propiedades/
- **Login**: http://127.0.0.1:8000/usuarios/login/
- **Registro**: http://127.0.0.1:8000/usuarios/registro/
- **Mis Alquileres**: http://127.0.0.1:8000/propiedades/mis-propiedades/
- **Crear Propiedad**: http://127.0.0.1:8000/propiedades/crear/
- **Planes**: http://127.0.0.1:8000/suscripciones/planes/
- **Admin**: http://127.0.0.1:8000/admin/

---

## 🚀 Próximos Pasos Sugeridos

1. **Configurar Email Real**
   - Actualizar SMTP en settings.py
   - Probar envío de notificaciones

2. **Agregar Google Maps**
   - Integrar mapa en detalle de propiedad
   - Geocodificación de direcciones

3. **Sistema de Pagos**
   - Integrar Stripe/PayPal
   - Procesar pagos de suscripciones

4. **Búsqueda Avanzada**
   - Filtros por precio, ubicación
   - Ordenamiento personalizado

5. **Chat en Tiempo Real**
   - Mensajería entre usuarios
   - Usando WebSockets

6. **Optimizaciones**
   - Caché de consultas
   - Compresión de imágenes
   - CDN para archivos estáticos

---

## 💡 Consejos

- **Desarrollo**: Usa `DEBUG = True` en settings.py
- **Producción**: Cambia a `DEBUG = False` y configura `ALLOWED_HOSTS`
- **Seguridad**: Cambia `SECRET_KEY` en producción
- **Base de Datos**: Para producción, usa PostgreSQL en vez de SQLite
- **Archivos Media**: En producción, usa un servicio como AWS S3

---

## 📞 Soporte

Si encuentras algún problema:
1. Verifica que el entorno virtual esté activado
2. Asegúrate de que las migraciones estén aplicadas
3. Revisa la consola para ver errores
4. Verifica que Django y Pillow estén instalados

¡Éxito con tu proyecto BuscoTecho! 🏠✨
