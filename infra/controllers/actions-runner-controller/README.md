# Actions Runner Controller

This controller runs the repository's GitHub Actions runners.

## Check state

```bash
flux get kustomization actions-runner-controller -n flux-system
kubectl get pods -n arc-systems
```
