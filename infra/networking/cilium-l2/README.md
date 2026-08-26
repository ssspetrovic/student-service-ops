# Cilium L2

Gives the frontend, Harbor, tailnet DNS, and Grafana LoadBalancer Services their reserved LAN addresses through
Cilium L2 announcements.

## Check state

```bash
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
```
