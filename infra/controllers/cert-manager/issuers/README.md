# cert-manager Issuers

The cluster's internal root CA is stored in the SOPS-encrypted `student-service-root-ca.sops.yaml` Secret
It configures the `student-service-ca` issuer to use it. Services use this issuer for private TLS.

Do not generate a new CA unless performing an
explicit trust rotation.

## Check state

```bash
kubectl get clusterissuers
kubectl get certificate -n cert-manager
kubectl -n cert-manager get secret student-service-root-ca
```
