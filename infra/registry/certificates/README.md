# Harbor Certificate

Creates Harbor's TLS certificate from the internal CA.

## Check state

```bash
kubectl get certificate -n harbor
kubectl get secret -n harbor harbor-tls
```
