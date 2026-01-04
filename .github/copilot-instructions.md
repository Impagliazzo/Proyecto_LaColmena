## Purpose
Short instructions to help an AI code assistant be immediately productive in this Django project.

## Big picture (what this repo is)
- Django 5.2 web app for property listings (Spanish UI). Main apps: `usuarios`, `propiedades`, `contactos`, `suscripciones`, `notificaciones`.
- Entry points: `manage.py`, settings in `Proyecto_BuscoTecho/settings.py`, main URL config in `Proyecto_BuscoTecho/urls.py`.
- Templates: project-level templates in `templates/` and app templates under each app's `templates/<app>/`.

## Key workflows (dev, build, debug) — Windows PowerShell
- Create venv & install Python deps:
  - `.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt` (project README uses `venv`; adapt path to your venv)
- DB migrations and dev server:
  - `.\\.venv\\Scripts\\python.exe manage.py makemigrations`
  - `.\\.venv\\Scripts\\python.exe manage.py migrate`
  - `.\\.venv\\Scripts\\python.exe manage.py runserver`
- Tailwind CSS (front-end assets): Node.js required
  - `npm install`
  - Dev watch: `npm run dev` (runs `tailwindcss --watch` and writes to `static/css/output.css`)

## Project-specific conventions & patterns
- Language: Spanish variable/function names and UI strings — prefer consistent Spanish in new views/templates.
- Custom user model: `AUTH_USER_MODEL = 'usuarios.Usuario'` (see `usuarios/models.py`). Use `request.user.es_propietario()` and related profile helpers where relevant.
- Media: user-uploaded files go to `MEDIA_ROOT` (configured in `settings.py`) and images are uploaded to `propiedades/` (see `ImagenPropiedad.upload_to`).
- Query patterns: views commonly use `select_related()` and `prefetch_related()` for performance (see `propiedades/views.py`). Follow same pattern for ORM efficiency.
- Business rules are encoded in views/models (not in separate service layer). Example: rating rules (can't rate own property; must have a `SolicitudContacto`; 7-day/24-hour timing checks) in `propiedades/views.py` → `valorar_propiedad`.
- Limits and validations are implemented at model/form level (e.g., max 10 images enforced in view when saving `ImagenPropiedad`). Reuse existing helpers where possible.

## Integration points & external dependencies
- Email: currently `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` in `settings.py` — update for production.
- Payments: not implemented yet (see README "Integrar Pasarela de Pagos").
- Tailwind CSS + npm: scripts in `package.json` (`dev`, `build`). CSS input is `static/css/styles.css` and output is `static/css/output.css`.
- Admin & management commands: check `propiedades/management/commands/` for example data loader `crear_propiedades_ejemplo.py` and root `crear_propiedades.py` for helpers.

## Where to look for concrete examples
- Property lifecycle and image handling: `propiedades/models.py` and `propiedades/views.py` (functions: `crear_propiedad`, `incrementar_vistas`, image save loop).
- Contact flow & notifications: `contactos/views.py`, `notificaciones/models.py` and `notificaciones/views.py`.
- User auth and profile flows: `usuarios/views.py` and `usuarios/forms.py` (custom registration/login and `convertir_a_propietario`).
- URL structure: `Proyecto_BuscoTecho/urls.py` maps app namespaces (`propiedades`, `usuarios`, `contactos`, `suscripciones`, `notificaciones`). Use these namespaces when creating links or redirects.

## Quick implementation “contract” for small tasks
- Inputs: use existing forms where available (`PropiedadForm`, `BusquedaForm`, etc.).
- Outputs: templates use Tailwind classes; update `static/css/styles.css` or add a template-level `extra_css` block.
- Error modes: views use `django.contrib.messages` for user feedback; follow this pattern.

## Small gotchas to preserve
- Keep template context keys (e.g., `form`, `propiedad`, `page_obj`) consistent — templates expect these names.
- Many methods assume `request.user` has helper properties like `es_propietario`, `recibir_notificaciones`, `notificaciones_no_leidas`, and a related `perfil` model — use the existing interfaces.
- Tests are not present; when adding logic-heavy code add a minimal unit test and run migrations locally.

## Notes for the AI assistant
- Prefer small, focused edits that reuse existing forms, helpers and template blocks.
- When changing behavior that affects business rules (ratings, contact flow, subscription limits), reference the relevant files above and add short rationale in the PR description.
- Provide Windows PowerShell-friendly run instructions in PRs (the README uses PowerShell examples).

If anything here is unclear or you want more detail about a specific area (subscriptions, notifications, or the payments plan), tell me which part and I will expand the guidance or add examples.
 