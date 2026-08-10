# Gateway API

Creates the shared Cilium Gateway. Applications attach HTTPRoutes to it.

## Check state

```bash
kubectl -n gateway-system get gateway
kubectl get httproute -A
```
