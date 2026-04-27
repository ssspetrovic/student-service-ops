# Harbor

Current Harbor path:

- `infra/registry/harbor/`
- `infra/registry/certificates/`
- `clusters/student-service-cluster/harbor.yaml`
- `clusters/student-service-cluster/harbor-certificates.yaml`

Flux ownership:

- `harbor` reconciles `./infra/registry/harbor`
- `harbor-certificates` reconciles `./infra/registry/certificates`
- `harbor` depends on `storage`, `cilium-l2`, and `harbor-certificates`

Current bootstrap values:

- chart `harbor` from `https://helm.goharbor.io`
- chart version `1.18.3`
- service exposure `LoadBalancer`
- private IP `192.168.1.241`
- external TLS Secret `harbor-tls`
- `externalURL` `https://harbor.student-service.internal`
- PVCs pinned to `storageClass: local-path`
- registry PVC size `180Gi`
- Trivy disabled
- update strategy `Recreate`

Secrets:

- `infra/registry/harbor/harbor-values.sops.yaml` stores the encrypted Harbor values
- `harbor-values.secret.example.yaml` is the plaintext template
- the Secret name is `harbor-values`
- GitHub Actions uses repository secrets `HARBOR_USERNAME` and `HARBOR_PASSWORD` for the Harbor image smoke workflow

Robot account:

- Harbor project `student-service` stores app and smoke-test images
- project robot account `github-actions-build` is used by GitHub Actions
- the robot account has repository push and pull permission
- ARC DinD runners trust Harbor through `infra/ci/actions-runner-scale-set/harbor-ca-configmap.yaml`

The Harbor namespace is created by `namespace.yaml` in this directory.
Encrypted secrets in this directory are listed after `namespace.yaml` in `kustomization.yaml`.

Commands:

```bash
source ~/envs/k8s.sh
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization cilium-l2 -n flux-system
flux reconcile kustomization harbor-certificates -n flux-system
flux reconcile kustomization harbor -n flux-system
```

Verification:

```bash
flux get kustomizations -A
kubectl get certificate -n harbor
kubectl get pods -n harbor
kubectl get pvc -n harbor
kubectl get svc -n harbor
curl -v https://harbor.student-service.internal/v2/
```

Client trust:

Harbor uses a leaf certificate issued by the shared `student-service-ca` issuer.
The internal CA export and OS trust-store steps are documented under `infra/controllers/cert-manager/issuers/`.
Docker still uses a Harbor-specific path because Docker trust is configured per registry hostname.

Docker trust:

```bash
kubectl get secret -n cert-manager student-service-root-ca \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > student-service-root-ca.crt

sudo mkdir -p /etc/docker/certs.d/harbor.student-service.internal
sudo cp student-service-root-ca.crt /etc/docker/certs.d/harbor.student-service.internal/ca.crt
sudo systemctl restart docker
```

Validation:

```bash
docker login harbor.student-service.internal
curl -v https://harbor.student-service.internal/v2/
```
