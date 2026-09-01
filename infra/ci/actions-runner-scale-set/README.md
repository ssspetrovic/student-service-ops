# GitHub Actions Runners

This directory contains the actual definitions for GH Actions runner pool for the repo.

Some of the options configured for this pool are:

- Runner count going from 0 to 2
- `dind` (Docker-in-Docker) - for the ability to run docker opreations inside of the runner pods
- Harbor CA configuration - to be able to pull and push images from Harbor
- GitHub authentication configured through SOPS-encrypted secret

## Check state

```bash
kubectl get pods -n arc-runners
```
