# Student Service Backend

IN this directory, both migrations and backend are covered.

## Migrations

In order for the backend to have the actual models as fields in databases, migration applying is required.
Migrations are not only required for the initial database table fill, it's also required for other updates that can be
introduced with promotion flows.

For migrations to work, there are some prerequisites reuqired like Django config settings (variables).
Those configs are placed in the `bootstrap/` directory which contains Django related secrets, DB connection string,
Harbor CA, etc.

What the migration job itself does is quite simple:

```bash
./venv/bin/python manage.py migrate --noinput
```

## Backend access

Backend app is only accessible inside of hte cluster, it's not exposed to the outer workld.

It's accessible through the internal connection: `student-service-backend.student-service.svc.cluster.local:8000`

## Checking backend state

There are two simple checks that backend deployment uses:

- `/api/ready`: used to check whether the pod can receive any traffic
- `/api/health`: used to check whether the deployment container is healthy or if it needs to be restarted

## Check state

```bash
kubectl -n student-service get svc student-service-backend
kubectl -n student-service get job student-service-migrations
kubectl -n student-service logs job/student-service-migrations
```
