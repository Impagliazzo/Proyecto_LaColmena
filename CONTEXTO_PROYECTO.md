# Contexto del proyecto

Este archivo es la fuente de verdad de **negocio y producto** de LaColmena (nombre interno del
paquete Django: `Proyecto_BuscoTecho`). Complementa a [CLAUDE.md](CLAUDE.md), que cubre comandos y
arquitectura técnica — leelos juntos.

**Cómo usar este archivo**: antes de agregar una funcionalidad nueva, revisá el módulo
correspondiente acá abajo. La idea es reusar las reglas de negocio y patrones que ya existen en vez
de reinventarlos o contradecirlos sin darse cuenta.

## Por qué existe este documento

La app se construyó en distintas sesiones de IA y desde distintas cuentas de VS Code, módulo por
módulo, sin que una sesión tuviera memoria de las decisiones tomadas en la anterior. El código
funciona bien tal como está — **no se tocó nada de funcionamiento para escribir este documento**,
es puramente descriptivo — pero por eso conviven patrones distintos entre módulos, y algunas piezas
fueron rediseñadas más de una vez.

**El historial de git no cuenta la historia real.** Solo hay 3 commits (el inicial ya trae 112
archivos de una sola vez, como una importación). La mayor parte de la evolución real —todo el
subsistema de "búsqueda de compañero/a de piso", por ejemplo— pasó entre enero y marzo 2026 y nunca
se commiteó; vive solo en el working tree. Si necesitás entender qué está realmente vigente, mirá
`git status`/el código actual, no `git log`.

## Identidad de marca: BuscoTecho → LaColmena

El proyecto se llamó originalmente **BuscoTecho** y fue rebrandeado a **LaColmena**. El rebranding
es **cosmético, no estructural**:

- Sí llegó a: navbar, footer, título por defecto del home, la página "Quiénes somos", y los mails
  salientes de solicitud de contacto.
- No llegó a: el paquete Django sigue llamándose `Proyecto_BuscoTecho` (`settings.py`,
  `ROOT_URLCONF`, `WSGI_APPLICATION`, `DJANGO_SETTINGS_MODULE` todos lo referencian), 27 `<title>`
  de páginas individuales (incluyendo **todo** `contactos` y `notificaciones`) todavía dicen
  "BuscoTecho", y `README.md` está enteramente bajo el nombre viejo.

No es un bug — es simplemente un rename que no se terminó de propagar. No hace falta "corregirlo"
salvo que lo pidas explícitamente.

---

## Módulo `usuarios`

**Qué resuelve**: identidad de usuario, perfil, y dos flujos de "matching" distintos: conseguir
inquilino/comprador (vía `propiedades`) y conseguir compañero/a de piso (self-contained en este
módulo).

**Modelos clave**:
- `Usuario` (custom, `AUTH_USER_MODEL`) — extiende `AbstractUser`, tipo `usuario`/`propietario`.
- `Perfil` (1:1 con `Usuario`) — perfil general **más** todos los campos de búsqueda de
  compañero/a (situación laboral, hábitos, tags en `JSONField`, etc.). Esto se unificó acá después
  de vivir un tiempo en un modelo separado.
- `PerfilBusqueda` — **obsoleto**, reemplazado por los campos de arriba. Se mantiene solo para que
  las migraciones viejas no se rompan (`usuarios/models.py:474-475`, ya documentado en
  `CLAUDE.md:74-78`). *Inconsistencia a saber*: sigue totalmente registrado y editable en el admin
  de Django (`usuarios/admin.py`) pese a estar marcado como "no usar" — no es intencional, es un
  descuido del rebrand interno de `PerfilBusqueda`→`Perfil`.
- `PublicacionCompanero` / `ImagenPublicacionCompanero` — publicar "tengo lugar y busco
  compañero/a". **No es un alquiler/venta**, es un flujo totalmente separado de `Propiedad`: no
  tiene destacados, no cuenta contra el límite de publicaciones del plan de suscripción, no pasa
  por `SolicitudContacto`/`Valoracion`.

**Reglas de negocio a saber**:
- Validación de teléfono y email por código: en desarrollo el código válido está **hardcodeado en
  `123`** (`usuarios/views.py:181` y `:223`), y hasta se le avisa al usuario en el mensaje en
  pantalla ("Usa: 123"). Está documentado aparte en `COMO_TESTEAR_VALIDACIONES.md`. Es
  intencional para poder probar el flujo sin SMS/email real.
- **La validación de fortaleza de contraseña está deshabilitada a propósito** en `RegistroForm`
  (`usuarios/forms.py:58-70`): `clean_password2` solo chequea que las dos contraseñas coincidan, y
  `_post_clean` se sobreescribe específicamente para saltear los `AUTH_PASSWORD_VALIDATORS` de
  Django. O sea que hoy se acepta cualquier contraseña, sin mínimo de longitud ni complejidad. Es
  una decisión de diseño explícita (hay un comentario "Remover validación de contraseñas por
  ahora"), no un olvido — pero es el tipo de cosa que conviene tener presente si en algún momento
  se toca seguridad de cuentas.
- Edad mínima 18 años para el perfil de búsqueda de compañero/a, validada en el form
  (`PerfilBusquedaForm.clean()`), no en el modelo.
- El vocabulario de "tags" (hábitos, mascotas, limpieza, horarios, comida — con emojis) vive
  hardcodeado como choices en `usuarios/forms.py`, no en una constante compartida ni en el modelo.

**Terminología del dominio**: `tipo` (usuario/propietario), `es_propietario()`, `convertir_a_propietario()`,
`tiene_validaciones_completas()`, `perfil_completo` vs `perfil_busqueda_completo()` (son dos
"completitudes" distintas — la primera es del perfil general, la segunda específica de búsqueda de
compañero/a).

---

## Módulo `propiedades`

**Qué resuelve**: el flujo central de alquiler/venta — publicar, buscar, contactar, valorar y
destacar propiedades.

**Modelos clave**: `Categoria`, `Propiedad`, `ImagenPropiedad`, `Favorito`, `Valoracion`,
`ReporteValoracion`, `Destacado`.

**Reglas de negocio a saber**:
- **Valoraciones en dos niveles** (`propiedades/views.py::valorar_propiedad`): para calificar una
  propiedad hace falta tener una `SolicitudContacto` previa a esa propiedad, y esperar 7 días desde
  esa solicitud. Recién ahí se puede calificar al **propietario** (trato, confiabilidad, tiempo de
  respuesta). Calificar la **publicación en sí** (claridad de info, coincidencia de fotos, ubicación
  correcta) requiere además que el propietario haya respondido (`fecha_respuesta` seteada) y que
  hayan pasado 24h desde esa respuesta — si el propietario nunca respondió, esa parte queda
  bloqueada indefinidamente. La elegibilidad se calcula en la vista y se aplica en el form
  (`ValoracionForm.__init__(puede_valorar_publicacion=...)`, `propiedades/forms.py:137-144`).
  Una valoración por (usuario, propiedad), editable hasta 30 días.
- **`Destacado`** (listados pagos/boost): prioridad calculada por plan + tipo + antigüedad
  (`Destacado.calcular_prioridad`). El sistema pasó antes por un modelo de "cupos mensuales" que se
  eliminó (ver migración `0013`) a favor del modelo actual, más simple, de `activo`/`fecha_fin`.
- Límite de 10 imágenes por propiedad, aplicado en la vista al guardar `ImagenPropiedad`, no en el
  modelo.
- Reportar una valoración (`ReporteValoracion`) crea una notificación al propietario y queda
  disponible para moderación manual en el admin (única acción masiva custom de todo el proyecto:
  `marcar_como_revisado`, `propiedades/admin.py`).

**⚠️ Hallazgo, no tocar sin pedirlo explícitamente**: tres vistas activas y con lógica de negocio
completa **no tienen template** — confirmado contra el filesystem:
  - `eliminar_propiedad` → busca `propiedades/eliminar.html` (no existe)
  - `destacar_propiedad` → busca `propiedades/destacar.html` (no existe)
  - `mis_destacados` → busca `propiedades/mis_destacados.html` (no existe)

  Hoy, si un usuario llega a esas URLs (`eliminar/<pk>/`, `destacar/<pk>/`, `mis-destacados/`), el
  servidor tira error. No lo arreglé porque me pediste no cambiar funcionamiento — queda anotado
  para cuando quieras que lo resuelva.

**Terminología del dominio**: `promedio_propietario()` vs `promedio_publicacion()` vs
`promedio_total()` (tres promedios distintos de `Valoracion`), `tiene_destacado_activo()`,
`incrementar_vistas()`.

---

## Módulo `contactos`

**Qué resuelve**: el puente entre "me interesa esta propiedad" y poder calificarla después — es el
prerequisito de todo el sistema de valoraciones de `propiedades`.

**Modelo**: `SolicitudContacto` — máquina de estados simple: `pendiente` → `contactado` /
`rechazado`. Solo el propietario de la propiedad puede cambiar el estado
(`cambiar_estado_solicitud`). Al pasar a `contactado` se sella `fecha_respuesta`, que es lo que
arranca el reloj de 24h para poder valorar la publicación (ver módulo `propiedades` arriba).

**Reglas a saber**:
- No hay límite de solicitudes duplicadas: un usuario puede mandar varias solicitudes a la misma
  propiedad.
- No hay flujo dedicado para `rechazado` — se llega al mismo endpoint de cambio de estado, pero no
  dispara notificación (a diferencia de `contactado`, que sí notifica al solicitante).
- Requiere `tiene_validaciones_completas()` (teléfono + email validados) antes de poder contactar.
- El cambio de estado es un link GET, no una acción POST protegida — no es un problema de seguridad
  crítico dado el `login_required` + verificación de dueño, pero no sigue el patrón REST habitual.

---

## Módulo `suscripciones`

**Qué resuelve**: planes para propietarios (cuántas publicaciones pueden tener activas, si pueden
destacar, etc.).

**Decisión de diseño deliberada — "proyecto universitario"**: las suscripciones **no vencen
nunca**. `Suscripcion.save()` fija `fecha_vencimiento` a +100 años, y `esta_activa()` /
`esta_por_vencer()` están escritos para no reportar vencimiento jamás. Los pagos
(`Pago`) se marcan siempre como `completado` sin pasar por ninguna pasarela real — no hay
integración de pagos implementada. Esto no es un bug ni algo a "completar" salvo que lo pidas: es
así a propósito para simplificar el proyecto.

Nota histórica (no afecta el comportamiento actual): esta simplificación surgió después de un
incidente real donde a un usuario de prueba se le venció la suscripción y se le desactivó el botón
de "Destacar" — se solucionó parcheando la base a mano y después se generalizó a "las suscripciones
no vencen". Los scripts sueltos en la raíz del repo (ver más abajo) son el rastro de ese incidente.

---

## Módulo `notificaciones`

**Qué resuelve**: bandeja de notificaciones in-app (campanita en el navbar).

**Estado real vs modelado**: `Notificacion.TIPO_CHOICES` define 6 tipos (`favorito`, `contacto`,
`suscripcion`, `valoracion`, `validacion`, `sistema`), pero **solo 2 se disparan hoy en la
práctica**: `contacto` (nueva solicitud recibida / solicitud respondida, desde `contactos/views.py`)
y `sistema` (reporte de valoración, desde `propiedades/views.py`). Los tipos `favorito`,
`suscripcion` y `valoracion` están completamente estilizados en el template
(`notificaciones/templates/notificaciones/listar.html`) pero nada en el código los crea — son
funcionalidad prevista, no implementada. También existe un helper `crear_notificacion()` en
`notificaciones/views.py` que no se usa desde ningún lado (código muerto).

**No hay tiempo real**: no hay polling ni websockets — el contador de no leídas se calcula del lado
del servidor en cada carga de página completa.

**Detalle menor**: la llamada que crea la notificación de reporte de valoración
(`propiedades/views.py:944-949`) no pasa `titulo`, así que esa notificación en particular se guarda
con título vacío.

---

## Scripts sueltos en la raíz del repo

No son parte de ninguna app Django ni se ejecutan vía `manage.py` — son artefactos de debugging de
sesiones anteriores. Tratalos como históricos/descartables, no como un patrón a seguir (ya está
anotado en `CLAUDE.md`). En resumen:

- `check_julian_destacados.py`, `renovar_suscripcion_julian.py`, `verificar_destacados_inicio.py`,
  `actualizar_fechas_destacados.py` — el rastro del incidente de suscripción vencida mencionado
  arriba en `suscripciones`.
- `actualizar_suscripciones_ilimitadas.py` — aplicó a toda la base la decisión de "suscripciones
  ilimitadas".
- `explicacion_algoritmo_destacados.py` — explica/simula el algoritmo de prioridad de `Destacado`;
  ojo que su docstring ya no coincide exactamente con la fórmula actual del modelo.
- `migrar_perfiles_busqueda.py` — migración de datos de `PerfilBusqueda` al `Perfil` unificado.
- `fix_perfil_template.py`, `reordenar_perfil.ps1` — reordenamiento puntual de secciones en
  `perfil.html`.
- `test_form_publicacion.py`, `test_publicacion_companero.py`, `test_form_render.py` — smoke tests
  manuales (no pytest) del formulario de `PublicacionCompanero`.
- `image_carousel.html`, `temp_publicacion_companero_section.html` — fragmentos de borrador que
  luego se integraron a mano en templates reales; no están incluidos por ningún `{% include %}`.
