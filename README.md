# student-service-ops

GitOps and infrastructure repository for the student-service platform.

Current state:

- Talos cluster bootstrapped with `1` control plane and `2` workers
- Talos configuration lives under [talos](/home/spetrovic/dev/student-service-ops/talos/README.md)
- Flux is bootstrapped from `clusters/student-service-cluster`
- Cilium is deployed as the current CNI
- cert-manager is deployed as the current certificate controller
- Local Path Provisioner is deployed as the current storage backend
- Actions Runner Controller manifests are present for repository-scoped GitHub Actions runners
- The GitHub runner scale set is configured for Docker-in-Docker
- GitHub workflow smoke tests exist for runner scheduling and Harbor image push/pull
- Networking design for Cilium L2 and  Cilium Gateway API is documented under [infra/networking](/home/spetrovic/dev/student-service-ops/infra/networking/README.md)
- Storage design for Local Path Provisioner is documented under [infra/storage](/home/spetrovic/dev/student-service-ops/infra/storage/README.md)
- Cilium L2 and Gateway API manifests live under `infra/networking/` and target a shared private ingress IP on `192.168.1.240`
- Gateway API CRDs are sourced from the official
  `kubernetes-sigs/gateway-api` repository and reconciled before Cilium Gateway
  API is enabled
- `local-path` is the current default `StorageClass`
- A disposable test backend and `HTTPRoute` currently verify end-to-end ingress through `ingress.student-service.internal`

Current nodes:

| Node   | Role          | IP             |
| ------ | ------------- | -------------- |
| `cp01` | control plane | `192.168.1.50` |
| `wn01` | worker        | `192.168.1.51` |
| `wn02` | worker        | `192.168.1.52` |

## Repository Scope

- `talos/` contains the Talos cluster definition and bootstrap workflow
- `clusters/` contains Flux bootstrap output and cluster entrypoints
- `infra/` holds shared cluster infrastructure managed by Flux
- `infra/controllers/` groups shared cluster controllers such as Cilium and Actions Runner Controller
- `infra/ci/` groups CI runner infrastructure managed by Flux
- `infra/networking/` groups cluster networking components such as Cilium,
  Cilium L2, and Gateway API
- `infra/storage/` groups shared storage sources and notes

## Secrets

This repo uses `SOPS` with `age`.

- Encryption rules are defined in [`.sops.yaml`](/home/spetrovic/dev/student-service-ops/.sops.yaml)
- Encrypted files should use the `.sops.yaml` suffix
- Plaintext secret material must not be committed
- Generated Talos render output must not be committed
- `SOPS_AGE_KEY_FILE` should point to your local `age` private key before working with encrypted files

Current encrypted Talos cluster secrets file:

- [talos/talsecret.sops.yaml](/home/spetrovic/dev/student-service-ops/talos/talsecret.sops.yaml)

Current encrypted platform secrets:

- [infra/ci/actions-runner-scale-set/github-auth.sops.yaml](/home/spetrovic/dev/student-service-ops/infra/ci/actions-runner-scale-set/github-auth.sops.yaml)

Basic local workflow:

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
```

Create or regenerate the Talos secrets file:

```bash
talhelper gensecret > talos/talsecret.sops.yaml
sops -e -i talos/talsecret.sops.yaml
```

Edit an existing encrypted secret file:

```bash
sops talos/talsecret.sops.yaml
```

`sops <file>` opens the encrypted file for editing and writes it back encrypted on save.

## Talos

Talos-specific bootstrap and operator steps are documented in [talos/README.md](/home/spetrovic/dev/student-service-ops/talos/README.md).

## GitHub Actions Runners

GitHub runner deployment details are documented in [infra/ci/actions-runner-scale-set/README.md](/home/spetrovic/dev/student-service-ops/infra/ci/actions-runner-scale-set/README.md).

## Harbor

Harbor deployment details are documented in [infra/registry/harbor/README.md](/home/spetrovic/dev/student-service-ops/infra/registry/harbor/README.md).

## Developer Setup

This repo uses `mise` as the local entry point for operator tooling and validation tasks.

Install the pinned toolchain:

```bash
mise install
```

Install and run the repo pre-commit hook:

```bash
mise run pre-commit:install
mise run pre-commit:run
```

Pre-commit runs the repo lint suite through `mise run lint`.

Common validation commands:

```bash
mise run lint
mise run lint:fix
mise run lint:yaml
mise run lint:fix:yaml
mise run lint:markdown
mise run lint:fix:markdown
mise run lint:sh
mise run lint:fix:sh
mise run lint:actions
mise run lint:kubernetes
```

If you want only the fix/format step for a single category, use the task-specific commands directly,
for example `mise run lint:fix:yaml`, `mise run lint:fix:markdown`, or `mise run lint:fix:sh`.

Current validation scope:

- `yamllint` for YAML structure and style
- `yamlfmt` for YAML formatting fixes
- `markdownlint-cli2` for Markdown linting and Markdown auto-fixes
- `shellcheck` for shell linting
- `shfmt` for shell formatting fixes
- `actionlint` for GitHub Actions workflows
- `kubeconform` for built-in Kubernetes schema validation

`mise run lint:fix` currently applies:

- YAML formatting fixes through `yamlfmt`
- auto-fixable Markdown rules through `markdownlint-cli2`
- shell formatting fixes through `shfmt`

GitHub Actions, Kubernetes, and `shellcheck` findings remain report-only.
