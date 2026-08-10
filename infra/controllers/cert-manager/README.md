# cert-manager

`cert-manager` issues certificates for cluster services.

## Check state

```bash
kubectl get pods -n cert-manager
kubectl get crds | grep cert-manager.io
```
