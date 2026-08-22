# Tailnet DNS

Runs two CoreDNS replicas at `192.168.1.242` for `student-service.internal`.

## Tailscale setup

Keep `desktop-ts` advertising `192.168.1.0/24`.

- Add `192.168.1.242` as a restricted nameserver for `student-service.internal`.
- Leave **Override DNS servers** disabled.
- Do not add a search domain.
- Enable **Use with exit node** only if needed.

Keep `accept-dns` enabled. Linux clients also need `accept-routes`. The current allow-all policy needs no ACL change.

## Verify

```bash
kubectl -n tailnet-dns rollout status deployment/student-service-dns
kubectl -n tailnet-dns get deployment,service,endpointslice \
  -l app.kubernetes.io/name=student-service-dns
```

```bash
dig @192.168.1.242 student-service.internal A
dig @192.168.1.242 harbor.student-service.internal A
dig @192.168.1.242 student-service.internal A +tcp
dig @192.168.1.242 harbor.student-service.internal A +tcp
dig @192.168.1.242 missing.student-service.internal A
dig @192.168.1.242 example.com A
```
