# MetalLB

Managed by Flux from `infra/networking/controllers/metallb/`.

Current settings:

- subnet: `192.168.122.0/24`
- pool reserved for MetalLB: `192.168.122.210-192.168.122.219`
- reserved ingress IP: `192.168.122.210`
- mode: layer 2
- `wait: true`
- `timeout: 5m`

Verify:

```bash
flux get helmreleases -A
kubectl -n metallb-system get pods
```
