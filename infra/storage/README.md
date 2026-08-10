# Storage

This cluster uses Rancher's Local Path Provisioner for storage. It stores data on worker-node disks without replication.

## Check state

```bash
kubectl get storageclass
kubectl get pods -n local-path-storage
```
