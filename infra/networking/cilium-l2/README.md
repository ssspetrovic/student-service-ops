# Cilium L2

Cilium L2 is what makes the LoadBalancer (LB) addresses reachable on the LAN.
L2 is common for on-prem servers and LAN environments.

For the list of service addresses and a other general info, check [networking overview](../README.md),

## How it works

Each service here that's configured for LB / L2 has two following Cilium resources:

- an LB IP pool - which in this case reserves a single fixed address for the Service
- an L2 announcement policy - which actually makes the mentioned address visible on LAN,
  by having a node answer ARP requests for it.

## Lease ownership

Cilium elects one node to be in charge of and announce each service IP. This is tracked through a k8s lease.
The node that's been elected is responsible for answering ARP requests for the IP. That node doesn't need to run
the actual service pod.
Once traffic reaches that elected node, Cilium then forwards it to a fitting pod on any node in the cluster.
If node that's doing the announcing goes down, Cilium re-elects a different node and updates the lease.

## Managed services

This folder contains the IP pool and L2 announcement policy for:

- Student Service frontend
- Harbor
- Tailnet DNS
- Grafana

## Check state

```bash
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
```
