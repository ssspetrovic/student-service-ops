# cert-manager Issuers

This path creates the cluster's internal CA and the `student-service-ca` issuer. Services can use it for TLS certificates.

## Check state

```bash
kubectl get clusterissuers
kubectl get certificate -n cert-manager
```
