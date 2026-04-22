# Registry Certificates

Managed by Flux from `infra/registry/certificates/`.

Current settings:

- `Certificate` file: `harbor.yaml`
- `Certificate` name: `harbor-tls`
- Secret name: `harbor-tls`
- issuer: `student-service-ca`
- DNS name: `harbor.student-service.internal`

Verification:

```bash
flux get kustomizations -A
kubectl get certificate -n harbor
kubectl get secret -n harbor harbor-tls
```
