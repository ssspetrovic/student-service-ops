# Networking

Private networking for the LAN:

- `coredns/`: internal DNS names.
- `cilium-l2/`: LAN addresses for services.
- `gateway-api/`: the shared Gateway.
- `tailnet-dns/`: DNS for tailnet clients.

The shared Gateway uses `192.168.1.240`, Harbor uses `192.168.1.241`, and DNS uses `192.168.1.242`.

Tailscale sends only `student-service.internal` queries to this resolver. See [tailnet-dns](tailnet-dns/README.md).
