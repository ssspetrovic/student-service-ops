# Cilium

Cilium provides pod networking, Kubernetes Service forwarding, LoadBalancer IP allocation, and L2 announcements.
It replaces both kube-proxy and the former MetalLB deployment, so the cluster does not need separate controllers for
those responsibilities.

## Initial bootstrap

Before Cilium is installed, Kubernetes has no pod network and the nodes remain `NotReady`. Install it once before
bootstrapping Flux. Flux then takes ownership of the same Helm release and keeps it aligned with the
`HelmRelease` configuration.

```bash
helm install cilium oci://quay.io/cilium/charts/cilium \
  --version 1.19.3 \
  --namespace kube-system \
  --set ipam.mode=kubernetes \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=localhost \
  --set k8sServicePort=7445 \
  --set securityContext.capabilities.ciliumAgent="{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}" \
  --set securityContext.capabilities.cleanCiliumState="{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}" \
  --set cgroup.autoMount.enabled=false \
  --set cgroup.hostRoot=/sys/fs/cgroup
```

After running the Cilium installation, it's important to wait for the nodes to become ready before proceeding with the
Flux bootstrap.

You can check the Cilium related pods like this:

```bash
kubectl -n kube-system get pods -l app.kubernetes.io/name=cilium --watch
kubectl get nodes --watch
```

## Check state

```bash
kubectl -n kube-system get pods -l app.kubernetes.io/name=cilium
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
```
