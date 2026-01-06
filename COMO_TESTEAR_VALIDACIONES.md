# Cómo Testear el Sistema de Validaciones

## 🎯 Sistema Implementado

El sistema de validación de teléfono y email está completamente implementado con código hardcodeado "123" para pruebas.

## 📋 Pasos para Testear

### 1. Crear un nuevo usuario
1. Ve a http://127.0.0.1:8000/usuarios/registro/
2. Completa el formulario de registro:
   - Nombre
   - Apellido
   - Usuario
   - Contraseña
   - Confirmar Contraseña
   - Teléfono (ejemplo: 3512345678)
   - Email (ejemplo: test@test.com)
3. Al registrarte, verás:
   - Un mensaje de bienvenida
   - Te redirige a completar perfil
   - Se crea una notificación recordando validar la cuenta

### 2. Visualizar alertas de validación

Una vez logueado, verás el banner amarillo en todas las páginas que dice:
- **"¡Validá tu cuenta!"** 
- Indica qué falta validar (Teléfono, Email, o ambos)
- Botón "Validar ahora"

### 3. Acceder al Panel de Validaciones

**Opción A:** Click en "Validar ahora" desde el banner
**Opción B:** Ir directamente a http://127.0.0.1:8000/usuarios/validaciones/
**Opción C:** Desde tu perfil, en la sección "Estado de Validación"

### 4. Validar Teléfono

1. En el panel de validaciones, click en "Enviar código de verificación" del teléfono
2. Verás un mensaje: "Se ha enviado un código de verificación al número..."
3. Ingresa el código: **123**
4. Click en "Validar teléfono"
5. ✅ Verás mensaje de éxito y el teléfono quedará validado
6. Se crea una notificación confirmando la validación

### 5. Validar Email

1. En el panel de validaciones, click en "Enviar código de verificación" del email
2. Verás un mensaje: "Se ha enviado un código de verificación al email..."
3. Ingresa el código: **123**
4. Click en "Validar email"
5. ✅ Verás mensaje de éxito y el email quedará validado
6. Se crea una notificación confirmando la validación

### 6. Verificar que todo funciona

Una vez ambas validaciones completas:
- ✅ El banner amarillo desaparece
- ✅ En tu perfil, ambos items muestran estado "Validado" en verde
- ✅ Puedes contactar propietarios sin restricciones
- ✅ Puedes publicar propiedades sin restricciones

### 7. Probar las Restricciones

**Sin validaciones completadas:**

1. Intenta contactar un propietario:
   - Ve a cualquier propiedad
   - Click en "Contactar"
   - ❌ Te redirige al panel de validaciones
   - Mensaje: "Debes validar tu teléfono y email antes de contactar propietarios"

2. Intenta publicar una propiedad (siendo propietario):
   - Ve a "Publicar propiedad"
   - ❌ Te redirige al panel de validaciones
   - Mensaje: "Debes validar tu teléfono y email antes de publicar propiedades"

**Con validaciones completadas:**
- ✅ Puedes contactar propietarios sin problemas
- ✅ Puedes publicar propiedades sin problemas

## 🔍 Dónde Ver las Validaciones

### 1. Banner Superior (Base.html)
- Visible en TODAS las páginas si no estás validado
- Muestra qué falta validar
- Botón directo al panel

### 2. Perfil de Usuario
- Sección completa "Estado de Validación"
- Tarjetas visuales para Teléfono y Email
- Estados: Verde = Validado, Amarillo = Pendiente
- Mensaje explicativo si falta validar

### 3. Panel de Validaciones (`/usuarios/validaciones/`)
- Vista principal para gestionar validaciones
- Muestra estado general
- Botones para validar cada uno

### 4. Notificaciones
- Al registrarte: notificación recordatoria
- Al validar teléfono: notificación de confirmación
- Al validar email: notificación de confirmación

## 🧪 URLs del Sistema

```
/usuarios/validaciones/                    → Panel principal
/usuarios/solicitar-validacion-telefono/   → Solicitar código SMS
/usuarios/validar-telefono/                → Ingresar código SMS
/usuarios/solicitar-validacion-email/      → Solicitar código email
/usuarios/validar-email/                   → Ingresar código email
```

## 📝 Código de Verificación

**Para todas las validaciones:**
```
Código: 123
```

Este código está hardcodeado en los formularios:
- `ValidarTelefonoForm.clean_codigo()` en `usuarios/forms.py`
- `ValidarEmailForm.clean_codigo()` en `usuarios/forms.py`

## 🔄 Para Resetear las Validaciones (Testeo)

Si quieres volver a probar desde cero:

1. Abre Django shell:
```powershell
.\.venv\Scripts\python.exe manage.py shell
```

2. Ejecuta:
```python
from usuarios.models import Usuario
user = Usuario.objects.get(username='TU_USUARIO')
user.telefono_validado = False
user.email_validado = False
user.save()
```

3. Ahora puedes volver a validar

## 🚀 Próximos Pasos (Implementación Real)

Cuando quieras implementar el envío real:

### Para SMS:
- Integrar servicio como Twilio, MessageBird, etc.
- Modificar `solicitar_validacion_telefono()` en `usuarios/views.py`
- Generar código aleatorio y guardarlo en sesión o BD
- Enviar SMS con el código

### Para Email:
- Ya tienes Django email configurado (console backend)
- Modificar `solicitar_validacion_email()` en `usuarios/views.py`
- Generar código aleatorio y guardarlo en sesión o BD
- Usar `send_mail()` para enviar el código

Los lugares exactos están marcados con comentarios `# TODO` en el código.

## ✅ Checklist de Pruebas

- [ ] Registrar usuario nuevo
- [ ] Ver banner amarillo de validación
- [ ] Ver notificación de bienvenida
- [ ] Acceder al panel de validaciones
- [ ] Intentar contactar sin validar (debe bloquear)
- [ ] Intentar publicar sin validar (debe bloquear)
- [ ] Validar teléfono con código 123
- [ ] Validar email con código 123
- [ ] Ver banner desaparecer
- [ ] Ver perfil con estados en verde
- [ ] Contactar propietario (debe funcionar)
- [ ] Publicar propiedad (debe funcionar)
- [ ] Ver notificaciones de validación exitosa

## 🎨 Flujo Visual

```
Registro → Notificación → Banner Amarillo → Panel de Validaciones
                                          ↓
                                    Validar Teléfono
                                          ↓
                                     Código: 123
                                          ↓
                                    ✅ Validado
                                          ↓
                                    Validar Email
                                          ↓
                                     Código: 123
                                          ↓
                                    ✅ Validado
                                          ↓
                            Banner desaparece - Todo OK!
```

---

**Nota:** Todo el sistema está funcional y listo para usar con el código "123". Los usuarios verán los mensajes indicando que es versión de prueba.
