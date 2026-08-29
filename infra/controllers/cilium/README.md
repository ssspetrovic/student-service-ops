# Cilium

Cilium provides cluster networking, Kubernetes Service forwarding, LoadBalancer IP allocation, and L2 announcements.

## Initial bootstrap

Install Cilium once before flux to enable networking for pods.
Flux later manages the release with the same kube-proxy replacement and KubePrism settings.

```bash
helm repo add cilium https://helm.cilium.io/
helm repo update
helm install cilium cilium/cilium \
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

Wait for Cilium and the nodes to become ready before bootstrapping flux:

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
