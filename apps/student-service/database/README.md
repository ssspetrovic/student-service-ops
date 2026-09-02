# Student Service Database

This directory contains the definitions for PosgtreSQL DB used by Student Service app.

The DB itself i managed by CNPG operator, check [its README](../../../infra/controllers/cloudnative-pg/README.md)
for more info.

## Database

There is only one instance of PostgreSQL run in the cluster and it's in `student-service-database` ns.

The DB is not exposed outside of the cluster.

The DB uses one `5Gi` volume from the `local-path` storage.

The volume is stored on a worker node and it's not replicated.

Only the backend service, migration job, CNPG operator and DB pods are allowed to connect to DB
due to the network policy configuration:

```yaml
podSelector:
    matchLabels:
        cnpg.io/cluster: student-service-db
```

As explained in the storage README, the caveat here is that the data can be lost if worker goes bad or down.

## Check State

```bash
kubectl -n student-service-database get pods,pvc,svc
kubectl cnpg status -n student-service-database student-service-db
```
