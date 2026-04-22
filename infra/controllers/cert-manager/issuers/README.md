# cert-manager Issuers

Managed by Flux from `infra/controllers/cert-manager/issuers/`.

Current settings:

- bootstrap issuer: `student-service-bootstrap-selfsigned`
- root CA `Certificate`: `student-service-root-ca`
- CA `ClusterIssuer`: `student-service-ca`
- root CA Secret namespace: `cert-manager`

Verification:

```bash
flux get kustomizations -A
kubectl get clusterissuers
kubectl get certificate -n cert-manager
kubectl get secret -n cert-manager student-service-root-ca
```
