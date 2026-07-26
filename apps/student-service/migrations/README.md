# Student Service Migrations

This directory contains the Django migration Job and the configuration shared with the backend:

- `ConfigMap/student-service-backend-config` with internal Django hosts and
  empty CORS/CSRF origin lists
- SOPS-encrypted `Secret/student-service-backend` with `DJANGO_SECRET_KEY`
- SOPS-encrypted `Secret/harbor-pull` with pull-only Harbor robot credentials
- `Job/student-service-migrations`

The Job uses the same immutable image as the backend and runs:

```bash
.venv/bin/python manage.py migrate --noinput
```

`DATABASE_URL` comes from `Secret/student-service-db-app`.
Both the Job and backend use the required backend label so the NetworkPolicy allows their connections.
