# student-service-ops

GitOps and infrastructure repository for the student-service platform.

Current state:

- Talos cluster bootstrapped with `1` control plane and `2` workers
- Talos configuration lives under [infra/talos](/home/spetrovic/dev/student-service-ops/infra/talos/README.md)
- Flux is bootstrapped from `clusters/student-service-cluster`
- Cilium is deployed as the current CNI
- Networking design for MetalLB and ingress is documented under [infra/networking](/home/spetrovic/dev/student-service-ops/infra/networking/README.md)

Current nodes:

| Node   | Role          | IP                |
| ------ | ------------- | ----------------- |
| `cp01` | control plane | `192.168.122.46`  |
| `wn01` | worker        | `192.168.122.122` |
| `wn02` | worker        | `192.168.122.44`  |

## Repository Scope

- `infra/talos/` contains the Talos cluster definition and bootstrap workflow
- `clusters/` contains Flux bootstrap output and cluster entrypoints
- `infra/` holds shared cluster infrastructure managed by Flux
- `infra/networking/` groups cluster networking components such as Cilium,
  MetalLB, and ingress
- `apps/` will hold workload manifests managed by Flux

## Secrets

This repo uses `SOPS` with `age`.

- Encryption rules are defined in [`.sops.yaml`](/home/spetrovic/dev/student-service-ops/.sops.yaml)
- Encrypted files should use the `.sops.yaml` suffix
- Plaintext secret material must not be committed
- Generated Talos render output must not be committed
- `SOPS_AGE_KEY_FILE` should point to your local `age` private key before working with encrypted files

Current encrypted Talos cluster secrets file:

- [infra/talos/talsecret.sops.yaml](/home/spetrovic/dev/student-service-ops/infra/talos/talsecret.sops.yaml)

Basic local workflow:

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
```

Create or regenerate the Talos secrets file:

```bash
talhelper gensecret > infra/talos/talsecret.sops.yaml
sops -e -i infra/talos/talsecret.sops.yaml
```

Edit an existing encrypted secret file:

```bash
sops infra/talos/talsecret.sops.yaml
```

`sops <file>` opens the encrypted file for editing and writes it back encrypted on save.

## Talos

Talos-specific bootstrap and operator steps are documented in [infra/talos/README.md](/home/spetrovic/dev/student-service-ops/infra/talos/README.md).
