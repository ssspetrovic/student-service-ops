Backend service for the student-service platform.

Current state:

- Django project scaffold exists under `backend/student_service/`.
- Settings are split into `base`, `local`, and `production`.
- Local commands default to `student_service.settings.local`.
- ASGI/WSGI entrypoints use `student_service.settings.production`.

## Local development

Run commands from the repository root through `mise`:

```bash
mise run backend:sync
mise run backend:check
mise run backend:run
```

Production runtime must provide environment values required by `student_service.settings.production`.
