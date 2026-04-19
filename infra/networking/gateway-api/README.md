# Gateway API

Managed by Flux from `infra/networking/gateway-api/`.

Current settings:

- namespace: `gateway-system`
- gateway name: `shared-gateway`
- gateway class: `cilium`
- listener: HTTP on port `80`
- bootstrap hostname: `ingress.student-service.internal`
- intended load balancer IP: `192.168.1.240`
- route attachment: all namespaces

Verify:

```bash
flux get kustomizations -A
kubectl -n gateway-system get gateway
kubectl -n gateway-system get svc
kubectl describe gateway -n gateway-system shared-gateway
kubectl get httproute -A
```
