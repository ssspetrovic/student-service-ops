# Student Service Database

This directory contains the definitions for PosgtreSQL DB used by Student Service app.

The DB itself i managed by CNPG operator, check [its README](../../../infra/controllers/cloudnative-pg/README.md)
for more info.

## Database

The DB is configured for two PostgreSQL instances in `student-service-database` ns:
one primary and one asynchronous standby, with required anti-affinity keeping them on different worker nodes.

The DB is not exposed outside of the cluster.

Each instance uses its own `5Gi` volume from the `local-path` storage.

The volumes are stored on worker nodes with replicas set to `2` and CNPG can promote the standby if the primary fails.

Only the backend service, migration job, CNPG operator and DB pods are allowed to connect to DB due to the network
policy configuration:

```yaml
podSelector:
    matchLabels:
        cnpg.io/cluster: student-service-db
```

## Check State

```bash
kubectl -n student-service-database get pods,pvc,svc
kubectl cnpg status -n student-service-database student-service-db
```
