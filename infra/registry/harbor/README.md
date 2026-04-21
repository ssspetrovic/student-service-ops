# Harbor

Current Harbor path:

- `infra/registry/harbor/`
- `clusters/student-service-cluster/harbor.yaml`

Flux ownership:

- `harbor` reconciles `./infra/registry/harbor`
- `harbor` depends on `storage` and `cilium-l2`

Current bootstrap values:

- chart `harbor` from `https://helm.goharbor.io`
- chart version `1.18.3`
- service exposure `LoadBalancer`
- private IP `192.168.1.241`
- `externalURL` `http://harbor.student-service.internal`
- PVCs pinned to `storageClass: local-path`
- Trivy disabled
- update strategy `Recreate`

Secrets:

- `infra/registry/harbor/harbor-values.sops.yaml` stores the encrypted Harbor values
- `harbor-values.secret.example.yaml` is the plaintext template
- the Secret name is `harbor-values`

The Harbor namespace is created by `namespace.yaml` in this directory.
Encrypted secrets in this directory are listed after `namespace.yaml` in `kustomization.yaml`.

Commands:

```bash
source ~/envs/k8s.sh
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization cilium-l2 -n flux-system
flux reconcile kustomization harbor -n flux-system
```

Verification:

```bash
flux get kustomizations -A
kubectl get pods -n harbor
kubectl get pvc -n harbor
kubectl get svc -n harbor
```
