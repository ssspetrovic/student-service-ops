# Actions Runner Scale Set

Current paths:

- `infra/ci/actions-runner-scale-set`
- `clusters/student-service-cluster/actions-runner-scale-set.yaml`

Flux ownership:

- `actions-runner-scale-set` reconciles `./infra/ci/actions-runner-scale-set`.
- `actions-runner-controller` reconciles `./infra/controllers/actions-runner-controller`.

Current settings:

- The scale set registers repository runners for `https://github.com/ssspetrovic/student-service-ops`.
- Workflows use `runs-on: student-service-runner`.
- Runner pods use Docker-in-Docker and run in the privileged `arc-runners` namespace.
- The scale set can run up to `2` concurrent ephemeral runners and scales to `0` when idle.
- GitHub authentication is stored in the SOPS-encrypted `github-auth` Secret.
- Harbor CA trust for the Docker CLI and DinD daemon is provided by the `harbor-ca` ConfigMap.
- The Harbor CA is also mounted into `/etc/ssl/certs/harbor-ca.crt` for system TLS trust in the runner and DinD containers.
- `.github/workflows/runner-smoke.yaml` verifies runner scheduling.
- `.github/workflows/harbor-image-smoke.yaml` verifies Docker build, Harbor push, Harbor pull, and Docker logout.
- `.github/workflows/pr-agent.yml` runs PR-Agent on the same self-hosted runner label.
- Harbor login in workflows uses GitHub repository secrets `HARBOR_USERNAME` and `HARBOR_PASSWORD`.
- PR-Agent uses GitHub repository secret `OPENAI_KEY`.

Verification:

```bash
flux get kustomization actions-runner-scale-set -n flux-system
flux get helmrelease actions-runner-scale-set -n arc-runners
kubectl get pods -n arc-runners
```
