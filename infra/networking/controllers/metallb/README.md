# MetalLB

Managed by Flux from `infra/networking/controllers/metallb/`.

Current settings:

- subnet: `192.168.1.0/24`
- reserved VIP range: `192.168.1.240-192.168.1.248`
- mode: layer 2
- `wait: true`
- `timeout: 5m`
