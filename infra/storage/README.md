# Storage

This cluster uses Rancher's Local Path Provisioner for storage. It stores data on worker-node disks without replication.

Apps can create PVC and k8s provisions storage for it on a worker node. The caveat here is that the PVC will get tied
to the node the storage was provisoined on.
The storage will stay persistent across pod restarts, but it's not replicated across nodes.
If the node or the storage is lost, the data becomes lost as well.

## Talos storage config

For the Local Path provisoined to use the storage, the Talos workers have to provide the storage path.
The storage path in this case is set to: `/var/mnt/local-path-provisioner` on both of the worker nodes.

## Check state

```bash
kubectl get storageclass
kubectl get pods -n local-path-storage
```
