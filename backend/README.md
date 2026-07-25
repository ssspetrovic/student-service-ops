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

## Container

Build the backend image from the repository root:

```bash
docker build -t student-service-backend backend
```

Run it with a production environment file:

```bash
docker run --rm -p 8000:8000 \
  --env-file backend/.env.production \
  student-service-backend
```

The production environment must provide `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, and `DATABASE_URL`. Keep `.env.production` out of git.
Database migrations should run as a separate deployment step.

The `Backend Image` GitHub Actions workflow builds this image for pull
requests. After a backend change reaches `main`, it publishes both the commit
SHA and `latest` tags under:

```text
harbor.student-service.internal/student-service/backend
```

GitOps workloads should use the immutable commit-SHA tag.
