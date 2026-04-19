# Cilium L2

Managed by Flux from `infra/networking/cilium-l2/`.

Current settings:

- `CiliumLoadBalancerIPPool`: `192.168.1.240-192.168.1.248`
- `CiliumL2AnnouncementPolicy`: `gateway-l2`
- service scope: `gateway-system`

Verify:

```bash
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
kubectl -n gateway-system get svc cilium-gateway-shared-gateway -o wide
```
