# MetalLB Config

Managed by Flux from `infra/networking/metallb-config/`.

Current settings:

- `IPAddressPool`: `private-ingress-pool`
- address range: `192.168.1.240-192.168.1.248`
- `L2Advertisement`: `private-ingress`

Verify:

```bash
flux get kustomizations -A
kubectl -n metallb-system get ipaddresspools.metallb.io
kubectl -n metallb-system get l2advertisements.metallb.io
```
