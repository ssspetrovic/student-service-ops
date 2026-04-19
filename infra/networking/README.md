# Networking

Components:

- `controllers/`
- `metallb-config/`
- `gateway-api/`

Flux paths:

- `infra` -> `./infra/networking/controllers`
- `metallb-config` -> `./infra/networking/metallb-config`
- `gateway-api` -> `./infra/networking/gateway-api`

Current network settings:

- Talos subnet: `192.168.1.0/24`
- node addresses: `192.168.1.50-192.168.1.52`
- MetalLB pool: `192.168.1.240-192.168.1.248`
- shared Gateway IP: `192.168.1.240`

DNS bootstrap:

- `/etc/hosts` on the client machine:
  `192.168.1.240 ingress.student-service.internal`

Verify:

```bash
flux get kustomizations -A
flux get helmreleases -A
kubectl -n metallb-system get pods
kubectl -n metallb-system get ipaddresspools.metallb.io
kubectl -n metallb-system get l2advertisements.metallb.io
kubectl -n gateway-system get gateway
kubectl -n gateway-system get svc
```
