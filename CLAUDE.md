# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

"BuscoTecho" (repo dir: `Proyecto_LaColmena`) is a Django 5.2 web app for property rental listings, with a
secondary "roommate search" feature. UI and code (variable/function names, comments, model fields) are in
Spanish — keep new code consistent with this.

## Commands

There are two venv directories (`venv/` and `.venv/`), both gitignored; the README's convention is `venv`.
Use whichever one exists locally — check with `ls venv/Scripts/python.exe .venv/Scripts/python.exe` first.

```powershell
# Install Python deps
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Migrations
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate

# Run dev server
.\venv\Scripts\python.exe manage.py runserver

# Django shell (for one-off data inspection/fixes)
.\venv\Scripts\python.exe manage.py shell

# Create a superuser
.\venv\Scripts\python.exe manage.py createsuperuser

# Sample data
.\venv\Scripts\python.exe manage.py crear_propiedades_ejemplo
```

Tailwind CSS (Node required, separate from the Python side):
```bash
npm install
npm run dev     # watch mode -> static/css/output.css
npm run build   # minified build
```
Tailwind input is `static/css/styles.css`; never edit `static/css/output.css` directly, it's generated.
`tailwind.config.js` lists every app's `templates/**/*.html` under `content` — if a new app is added, register
its templates there or Tailwind won't pick up its classes.

There is no configured test framework (no pytest/tox config, no `tests.py` content). The root-level
`test_*.py`, `actualizar_*.py`, `migrar_*.py`, `fix_*.py` scripts are ad-hoc one-off scripts, not a test
suite — they call `django.setup()` manually and are run directly with the venv's `python.exe`, e.g.:
```powershell
.\venv\Scripts\python.exe test_form_publicacion.py
```
Treat them as historical/disposable, not something to maintain or extend as a pattern.

## Architecture

**Apps** (all registered in `Proyecto_BuscoTecho/settings.py` `INSTALLED_APPS`, each with its own URL
namespace included from `Proyecto_BuscoTecho/urls.py`):
- `usuarios` — custom user model, profiles, roommate-search postings
- `propiedades` — property listings (the core rental-listing feature)
- `contactos` — contact requests between users and property owners
- `suscripciones` — owner subscription plans/payments
- `notificaciones` — in-app notifications

Global templates live in `templates/` (project-level, e.g. `base.html`); each app also has its own
`templates/<app>/`. `TEMPLATES.DIRS` includes the project-level `templates/` and `APP_DIRS=True` picks up
the per-app ones.

**Custom user model**: `AUTH_USER_MODEL = 'usuarios.Usuario'` (`usuarios/models.py`), extends
`AbstractUser` with a `tipo` field (`usuario` / `propietario`). Use `request.user.es_propietario()`,
`request.user.convertir_a_propietario()`, `request.user.notificaciones_no_leidas()`,
`request.user.tiene_validaciones_completas()` rather than re-deriving this logic.

**Profile model**: `Perfil` (1:1 with `Usuario`) holds both the general profile and — as of a relatively
recent unification — all "roommate search" fields (situación laboral, hábitos, tags via `JSONField` lists,
etc.), exposed through `get_etiquetas_por_categoria()` / `get_todas_etiquetas()`. `PerfilBusqueda` is a
**deprecated** model kept only so old migrations still apply — do not add new fields there or build new
features on it; extend `Perfil` instead.

**Two distinct "listing" concepts** — don't conflate them:
- `propiedades.Propiedad` — a property for rent/sale (the main listing type), with `ImagenPropiedad`,
  `Favorito`, `Valoracion` (ratings), `Destacado` (paid featured/boost placement), managed via
  `propiedades/views.py` + `propiedades/urls.py` (`crear_propiedad`, `editar_propiedad`, `mis_propiedades`, etc.).
- `usuarios.PublicacionCompanero` — a *roommate-wanted* posting by someone who already has a place. This is
  a separate model/flow from `Propiedad`, with its own images (`ImagenPublicacionCompanero`) — it is not a
  rental listing and has no `Destacado`/subscription-limit concept.

**No service layer** — business rules live directly in views/models. Notable examples worth reading before
touching related code:
- Rating rules (can't rate your own property; must have a prior `SolicitudContacto`; timing windows) in
  `propiedades/views.py::valorar_propiedad`.
- Image limits (max 10 per property) enforced in the view when saving `ImagenPropiedad`, not at the model
  level.
- `Destacado` (featured listings) pricing/priority logic lives on the model (`Destacado.get_precio`,
  `calcular_prioridad`) — see `propiedades/views.py::destacar_propiedad` / `toggle_destacado`.

**Subscriptions are intentionally simplified for this being a university project**: `suscripciones/models.py`
`Suscripcion.save()` sets `fecha_vencimiento` 100 years out, and `esta_activa()` / `esta_por_vencer()` never
report an active subscription as expiring. Don't "fix" this into real expiry logic without checking with the
user first — it's deliberate, not a bug.

**Query performance convention**: views commonly use `select_related()`/`prefetch_related()` (see
`propiedades/views.py`) — follow the same pattern for new queries touching related objects.

**Messaging/errors**: views use `django.contrib.messages` for user-facing feedback rather than custom error
pages — follow this for new views.

**Media/static**: user uploads go under `MEDIA_ROOT` (`media/`, gitignored); `ImagenPropiedad`/
`ImagenPublicacionCompanero` each define their own `upload_to`. Static source is `static/css/styles.css` →
built to `static/css/output.css` by Tailwind (see above).

**Cache**: local in-memory cache is configured (`CACHES` in settings.py, `LocMemCache`) and used in a few
views for expensive queries — this cache is per-process and cleared on server restart, keep that in mind
when debugging "stale-looking" data in dev.

**Email**: `EMAIL_BACKEND` is the console backend (dev only) — emails print to the runserver console, they
are not actually sent.
