# Storage

Current storage path:

- `infra/storage/source.yaml`
- `clusters/student-service-cluster/storage.yaml`

Target backend:

- `local-path-provisioner` from Rancher upstream

Flux ownership:

- `infra` reconciles `infra/storage/source.yaml`
- `storage` reconciles the upstream Rancher `deploy/` path

Talos-specific settings:

- root path `/var/mnt/local-path-provisioner`
- namespace `local-path-storage`
- namespace label `pod-security.kubernetes.io/enforce: privileged`
- worker nodes need a Talos user volume mounted at `/var/mnt/local-path-provisioner`

Verification:

```bash
kubectl get storageclass
kubectl get pods -n local-path-storage
```
