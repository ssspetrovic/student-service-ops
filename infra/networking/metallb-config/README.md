# MetalLB Config

Managed by Flux from `infra/networking/metallb-config/`.

Current settings:

- `IPAddressPool`: `private-ingress-pool`
- address range: `192.168.122.210-192.168.122.219`
- `L2Advertisement`: `private-ingress`

Verify:

```bash
flux get kustomizations -A
kubectl -n metallb-system get ipaddresspools.metallb.io
kubectl -n metallb-system get l2advertisements.metallb.io
```
