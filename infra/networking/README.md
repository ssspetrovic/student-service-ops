# Networking

Components:

- `coredns/`
- `cilium-l2/`
- `gateway-api/`

Flux paths:

- `infra` -> `./infra` via `infra/kustomization.yaml`
- `infra/kustomization.yaml` includes `controllers` for shared cluster controllers
- `cilium-l2` -> `./infra/networking/cilium-l2`
- `gateway-api` -> `./infra/networking/gateway-api`

Current network settings:

- Talos subnet: `192.168.1.0/24`
- node addresses: `192.168.1.50-192.168.1.52`
- Cilium Gateway IP pool: `192.168.1.240`
- Cilium Harbor IP pool: `192.168.1.241`
- shared Gateway IP: `192.168.1.240`

Current structure:

- `infra/networking/coredns/` holds the Git-managed CoreDNS ConfigMap overrides for cluster DNS
- `infra/networking/cilium-l2/` contains `gateway/` and `harbor/` for LB IPAM and L2 policy
- `infra/networking/gateway-api/` holds the shared Gateway resources

DNS bootstrap:

- `/etc/hosts` on the client machine:
  `192.168.1.240 ingress.student-service.internal`
- CoreDNS static records in-cluster:
  `192.168.1.240 ingress.student-service.internal`
  `192.168.1.241 harbor.student-service.internal`

Verification:

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
