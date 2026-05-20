Backend service for the student-service platform.

## Local development

Run commands from the repository root through `mise`:

```bash
mise run backend:sync
mise run backend:check
mise run backend:run
```

Local Django commands default to `student_service.settings.local`.
Production servers use `student_service.settings.production` through ASGI/WSGI.
