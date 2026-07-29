# Student Service Database

This directory deploys:

- one CNPG PostgreSQL instance in `student-service-database`
- a `5Gi` `local-path` volume
- database and owner `student_service`
- SOPS-encrypted database credentials and backend `DATABASE_URL`
- a NetworkPolicy allowing only CNPG and backend access

The internal read-write endpoint is:

```text
student-service-db-rw.student-service-database.svc.cluster.local:5432
```

The migration Job and backend pods use this label for database access:

```text
app.kubernetes.io/name: student-service-backend
```

Flux pruning is disabled for the namespaces and CNPG Cluster to protect the
Local Path data from accidental deletion.

This is a single-instance demo database. It has no replica or external backup.

## Secrets

The initial password was generated once with `openssl rand -hex 32`, added to
both Secret manifests, and immediately encrypted with SOPS.
