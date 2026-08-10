# student-service-ops

This repository manages Student Service infrastucture and Kubernetes depoyments. Flux applies changes merged to `main`.

The cluster has one Talos control-plane node and two workers. Services are avaliable from the home LAN or VPN.

## Main areass

- `talos/`: Talos cluster setup.
- `clusters/`: Flux bootstrap and entrypoints.
- `infra/`: shared cluser services.
- `apps/student-service/`: deployed aplication workloads.
- `backend/` and `frontend/`: application source.

## Prerequisits

Instal the pined tools with `mise`:

```bash
mise install
```

This installs `kubectl`, `helm`, `flux`, `sops`, and `talosctl`. You also neeed:

- `talhelper` to generate Talos config.
- `age` and the private key used for SOPS.
- A GitHub PAT for flux bootstrap.

## Recreate the cluser

1. Check the node interface and disks, then create the Talos config and bootstap the control plane and workers.
   See [talos/README.md](talos/README.md).
2. Complete the [Cilium initial bootstrap](infra/controllers/cilium/README.md).
3. Fetch the kubeconfig, then bootstrap Flux and create its SOPS key.
   See [clusters/student-service-cluster/README.md](clusters/student-service-cluster/README.md).
4. Flux deploys shared infrastucture from `infra/`, then workloads from `apps/student-service/`.

For later chagnes, edit the manifests, merge to `main`, and let flux reconcile.
To apply a change imediately, run:

```bash
flux reconcile kustomization flux-system -n flux-system --with-source
```

## Secrets

Secrets use SOPS with age. Set `SOPS_AGE_KEY_FILE` before editing one. Keep sensitive files encrytped.

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
sops talos/talsecret.sops.yaml
```

## Local checks

```bash
mise install
mise run lint
```
