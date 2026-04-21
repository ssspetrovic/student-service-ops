# Cilium L2

Managed by Flux from `infra/networking/cilium-l2/`.

Current layout:

- `kustomization.yaml`
- `gateway/`
  - `kustomization.yaml`
  - `ippool.yaml`
  - `l2policy.yaml`

Current settings:

- `CiliumLoadBalancerIPPool`: `gateway-pool`
- `CiliumL2AnnouncementPolicy`: `gateway-l2`
- IP range: `192.168.1.240-192.168.1.248`
- service scope: `gateway-system`

Verify:

```bash
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
kubectl -n gateway-system get svc cilium-gateway-shared-gateway -o wide
```
