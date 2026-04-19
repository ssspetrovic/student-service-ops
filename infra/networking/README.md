# Networking

Components:

- `controllers/`
- `cilium-l2/`
- `gateway-api/`

Flux paths:

- `infra` -> `./infra/networking/controllers`
- `cilium-l2` -> `./infra/networking/cilium-l2`
- `gateway-api` -> `./infra/networking/gateway-api`

Current network settings:

- Talos subnet: `192.168.1.0/24`
- node addresses: `192.168.1.50-192.168.1.52`
- Cilium LB pool: `192.168.1.240-192.168.1.248`
- shared Gateway IP: `192.168.1.240`

DNS bootstrap:

- `/etc/hosts` on the client machine:
  `192.168.1.240 ingress.student-service.internal`

Verify:

```bash
flux get kustomizations -A
flux get helmreleases -A
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
kubectl -n gateway-system get gateway
kubectl -n gateway-system get svc
kubectl -n test-ingress get httproute
curl http://ingress.student-service.internal
```
