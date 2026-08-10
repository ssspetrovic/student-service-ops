# GitHub Actions Runners

This is the GitHub Actions runner pool for this repository. Workflows use `runs-on: student-service-runner`.

The pool starts runners when needed and scales to zero when idle.
Runner credentials are stored in the encrypted `github-auth` Secret.

## Check state

```bash
flux get kustomization actions-runner-scale-set -n flux-system
kubectl get pods -n arc-runners
```
