# Cilium

Managed by Flux from the networking domain layer under
`infra/networking/cilium/`.

## Initial Bootstrap

Cilium is installed manually once before Flux becomes healthy, because the
nodes need a CNI to become `Ready`.

## Prerequisites

```bash
helm repo add cilium https://helm.cilium.io/
helm repo update
```

## Install

```bash
helm install cilium cilium/cilium \
  --version 1.19.3 \
  --namespace kube-system \
  --set ipam.mode=kubernetes \
  --set kubeProxyReplacement=false \
  --set securityContext.capabilities.ciliumAgent="{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}" \
  --set securityContext.capabilities.cleanCiliumState="{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}" \
  --set cgroup.autoMount.enabled=false \
  --set cgroup.hostRoot=/sys/fs/cgroup
```

## Verify

```bash
kubectl -n kube-system get pods -l app.kubernetes.io/name=cilium --watch
kubectl get nodes --watch
kubectl -n flux-system get pods --watch
flux check
```
