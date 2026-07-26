# Flux Bootstrap

This cluster is bootstrapped from this repository at:

- `clusters/student-service-cluster`

## Bootstrap Steps

Export the GitHub token:

```bash
export GITHUB_TOKEN=<github-pat>
```

Run bootstrap from the repository root:

```bash
flux bootstrap github \
  --token-auth=true \
  --owner=ssspetrovic \
  --repository=student-service-ops \
  --branch=main \
  --path=clusters/student-service-cluster \
  --personal
```

Verify Flux:

```bash
flux check
flux get all -A
```

Create the SOPS age secret for Flux:

```bash
kubectl -n flux-system create secret generic sops-age \
  --from-file=age.agekey="$SOPS_AGE_KEY_FILE"
```

Verify the secret exists:

```bash
kubectl -n flux-system get secret sops-age
```

## Reconciliation

Flux reconciles on its own based on the configured intervals.

Run a manual reconcile after a merge to `main` if you want the cluster to pick up changes immediately.

The root reconciliation is normally enough. Flux handles the remaining
dependencies:

```bash
flux reconcile kustomization flux-system -n flux-system --with-source
```

Check the overall state with:

```bash
flux get all -A
```

The application database reconciles from
`apps/student-service/database` after both `cloudnative-pg` and `storage`.
Flux decrypts its two SOPS Secrets with `sops-age` and waits for
`Cluster/student-service-db` to become healthy.

The database endpoint is internal only:

```text
student-service-db-rw.student-service-database.svc.cluster.local:5432
```

The database and owner are both `student_service`. Future migration Jobs and
backend pods must use this label to pass the database ingress policy:

```text
app.kubernetes.io/name: student-service-backend
```

After reconciliation, verify metadata without printing secret values:

```bash
flux get kustomization student-service-database -n flux-system
kubectl get cluster student-service-db -n student-service-database
kubectl get pods,pvc,svc -n student-service-database -o wide
kubectl get secret student-service-db-app -n student-service-database \
  -o json | jq '{type, keys: (.data | keys)}'
kubectl get secret student-service-db-app -n student-service \
  -o json | jq '{type, keys: (.data | keys)}'
```

Flux deploys the database first, runs the migration Job, and then deploys the
backend. If migrations fail, the backend is not deployed.

After merging, use the reconciliation command above and check the workloads:

```bash
kubectl get jobs,deployments,pods,services -n student-service
```

The backend is available only inside the cluster:

```text
http://student-service-backend.student-service.svc.cluster.local:8000
```

Its health endpoint is `GET /api/health/`.
