# Tailnet DNS

Tailnet DNS enables the authorized clients that are running the Tailscale VPN to access the services from the cluster
through their actual private service names.
For example, this allows you to open [https://student-service.internal](https://student-service.internal)
without having to manually configure DNS entries on your local system.

For the service ddresses and a more abstract picture, check [networking overview](../README.md).

## How it works

A DNS server runs at `192.168.1.142`. Tailscale uses this server only for `student-service.internal` names.
All other names use the usual DNS server that's default on the device.

## Tailscale setup

`desktop-ts`, which is the server where the cluster is running on, advertises `192.168.1.0/24` LAN subnet.
This is configured by running the following command on the `desktop-ts`:

```bash
tailscale up --advertise-routes=192.168.1.0/24
```

The advertised route needs to be approved in the
[Machine settings on Tailscale admin page](https://console.tailscale.com/admin/machines)

The Tailscale DNS was enabled by creating a Split DNS entry at [Tailscale DNS settings](https://console.tailscale.com/admin/dns).
The options used in creating the nameserver were:

- address: `192.168.1.242`
- Restricted to domain: `Enabled`
- Domain: `student-service.internal`
- Use with exit node: `Disabled`

Overriding DNS servers is disabled.

On the client-side, it's important to have `accept-dns` and `accept-routes` enabled:

```bash
tailscale up --accept-dns --accept-routes
```

## Check state

```bash
kubectl -n tailnet-dns get deployment,service
dig @192.168.1.242 student-service.internal
```

One DNS lookup is enough to confirm the service is running and answering requests.
