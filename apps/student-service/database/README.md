# Student Service Database

This path defines the first application PostgreSQL cluster and its access
boundary.

Resources:

- namespaces `student-service` and `student-service-database`
- `Cluster/student-service-db` in `student-service-database`
- one `5Gi` `local-path` data volume
- SOPS-encrypted bootstrap credentials in
  `database-credentials.sops.yaml`
- the matching SOPS-encrypted backend `DATABASE_URL` in
  `backend-database-url.sops.yaml`
- ingress policy for the CNPG operator, CNPG instances, and backend identity

The read-write endpoint is:

```text
student-service-db-rw.student-service-database.svc.cluster.local:5432
```

The database and owner are both `student_service`. Future migration Jobs and
backend pods must carry:

```text
app.kubernetes.io/name: student-service-backend
```

The namespaces and CNPG Cluster disable Flux pruning because their removal
could also remove Local Path data. Deliberate retirement therefore requires an
explicit operator procedure.

This is a single-instance thesis/demo database. It has no replica or external
backup, and Local Path volumes cannot be expanded in place.

## Credential Creation and Rotation

The initial credential was created with one invocation of:

```bash
openssl rand -hex 32
```

The result was held only in a shell variable, inserted into both new Secret
manifests, and immediately encrypted in place with:

```bash
sops encrypt --in-place <manifest>
```

Encryption used the public age recipient selected by the `apps/` creation rule
in the repository root `.sops.yaml`. SOPS encryption does not require the age
private key. The plaintext value was not printed or written to a separate
file.

For later rotation, use the age private key and update both already-encrypted
files in one isolated subshell:

```bash
(
  db_password="$(openssl rand -hex 32)"
  database_uri="postgresql://student_service:${db_password}@student-service-db-rw.student-service-database.svc.cluster.local:5432/student_service"

  jq -Rn --arg value "$db_password" '$value' |
    sops set --value-stdin \
      apps/student-service/database/database-credentials.sops.yaml \
      '["stringData"]["password"]'

  jq -Rn --arg value "$database_uri" '$value' |
    sops set --value-stdin \
      apps/student-service/database/backend-database-url.sops.yaml \
      '["stringData"]["uri"]'

  unset db_password database_uri
)
```

This rotation command expects `SOPS_AGE_KEY_FILE` to identify the local age
private key. It prints neither the password nor the URI. Because the bootstrap
Secret initializes the database owner only when the cluster is first created,
rotating these Kubernetes Secrets for an existing database also requires a
coordinated PostgreSQL role-password change before workloads use the new URI.
