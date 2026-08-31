# Networking

For the security and of course the simplicity reason due to this being a temporarily deployed project
for the thesis, the cluster is configured as private / LAN-first.
Services are available on LAN and to authorized Tailscale devices - there is no public access configured.

Cilium provides the networking foundtaion for the cluster.
See [Cilium](../controllers/cilium/README.md) for more details.

Tailscale provides remote access to the LAN for authorized devices.

## Service addresses

The table below showcases the endpoints for this cluster and their IP addresses:

| Address         | Name                               | Service                  |
| --------------- | ---------------------------------- | ------------------------ |
| `192.168.1.240` | `student-service.internal`         | Student service frontend |
| `192.168.1.241` | `harbor.student-service.internal`  | Harbor                   |
| `192.168.1.242` | /                                  | Tailnet DNS              |
| `192.168.1.243` | `grafana.student-service.internal` | Grafana                  |

These addresses are announced on the LAN by Cilium. Each of the addresses is reserved
for its service through LB IP pool and L2 announcement policy.
One caveat here is that I didn't manage to statically assign these IPs on my router,
so there is a chance of potential conflict here if a router assigns one of these IPs to another device.

## DNS

CoreDNS lets apps inside the cluster find private services by name.
A separate DNS service at `192.168.1.242` lets Tailscale devices find those same services.

The services are accessible by the DNS hostname for Tailscale clients.

## Components

- [Cilium](../controllers/cilium/README.md)
- [Cilium L2](cilium-l2/README.md)
- [CoreDNS](coredns/README.md)
- [Tailnet DNS](tailnet-dns/README.md)

The frontend, Harbor, and Grafana each have their own private LoadBalancer IP and HTTPS certificate.

The backend is available only inside the cluster.
