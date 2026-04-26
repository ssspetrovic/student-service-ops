# Actions Runner Controller

Current paths:

- `infra/controllers/actions-runner-controller`
- `clusters/student-service-cluster/actions-runner-controller.yaml`

Flux ownership:

- `actions-runner-controller` reconciles `./infra/controllers/actions-runner-controller`.

Current settings:

- The controller chart is `gha-runner-scale-set-controller`.
- The controller chart source is `oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller`.
- The chart version is pinned to `0.14.1`.
- The Helm release name is `arc`.
- Controller pods run in `arc-systems`.

Verification:

```bash
flux get kustomization actions-runner-controller -n flux-system
flux get sources oci -n flux-system
flux get helmrelease actions-runner-controller -n flux-system
kubectl get pods -n arc-systems
```
