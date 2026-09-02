# CloudNativePG

CNPG (CloudNativePG) manages PostgreSQL DBs inside of k8s.

It is pretty much an operator that watches the CNPG `Cluster` resources and handles any DB pods,
Services and storage resources that are used.

## Check state

```bash
kubectl get pods -n cnpg-system
kubectl cnpg status -n student-service-database student-service-db
```
