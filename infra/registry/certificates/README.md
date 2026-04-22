# Registry Certificates

Managed by Flux from `infra/registry/certificates/`.

Current settings:

- `Certificate` file: `harbor.yaml`
- `Certificate` name: `harbor-tls`
- Secret name: `harbor-tls`
- issuer: `student-service-ca`
- DNS name: `harbor.student-service.internal`

This path contains service certificates for the registry tier.
The CA bootstrap and shared issuer are documented under `infra/controllers/cert-manager/issuers/`.

Verification:

```bash
flux get kustomizations -A
kubectl get certificate -n harbor
kubectl get secret -n harbor harbor-tls
```
