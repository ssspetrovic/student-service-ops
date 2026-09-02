# student-service-ops

## App overview

This repository is home to a Student Service application. It serves two purposes:

- Handling the infrastructure around the application
- Handling the application itself, its backend, frontend as well as its deployment to k8s.

This project represents a simple take on a student service application. The 3 main actors in this
application are student, professor and admin.

Students are enabled with the following functinalities:

- registration and login
- wallet status and deposit option
- views for available exams, curriculum, cousre enrollments, exam registrations, as well as grades
- exam registration option

Professors can do the following:

- check their exams
- create exams for the courses/curriculums they are in charge of
- grade students on those exams

Administrators have various privileges such as:

- creating new users
- editing existing users
- creating curricula
- creating courses and reassigning course professors

## Accessing the services

The services are available from the home LAN or through the project's Tailscale tailnet. Tailscale split DNS
resolves the internal service names, so users do not need to add them manually to `/etc/hosts`.

The following services can be accessed:

- [Web application (UI)](https://student-service.internal)
- [Grafana](https://grafana.student-service.internal)
- [Harbor](https://harbor.student-service.internal)

All services use HTTPS certificates issued by the project's internal CA. Before opening them, users must install the
`student-service-root-ca.crt` certificate in their operating system or browser trust store. Check out
[cert-manager README.md](infra/controllers/cert-manager/README.md) for info on how to do that.

## Technologies

The main technologies used in this project are:

- Backend: Python, Django and Django REST Framework
- Frontend: React, Vite and Bootstrap
- Database: PostgreSQL managed by CloudNativePG
- Platform: Talos Linux and Kubernetes
- GitOps: Flux, Kustomize and Helm
- Networking: Cilium LB IPAM + L2 announcements and Tailscale DNS
- Container registry: Harbor
- Secrets and certificates: SOPS, age and cert-manager
- CI/CD and monitoring: GitHub Actions, Trivy, Prometheus and Grafana

## Repo structure

The different functionalities are spread across different directories or entrypoints:

- `talos/`: contains Talos related configuration, initial cluster setup
- `clusters/`: Flux bootstrap point, contains apps and services entrypoints for Flux
- `infra/`: services shared across cluster, networking, ARC, etc.
- `apps/student-service/`: actual application deployment entrypoints for backend and frontend
- `backend/` and `frontend/`: actual source code for the application(s)

## CI/CD

This repository includes a comprehensive CI/CD workflow. Depending on the changes made, the PRs can go through the
following CI/CD workflows:

- Lint (yaml, markdown, shell, etc.)
- Backend testing - lint, API tests as well as trivial build tes
- Frontend testing - lint, trivial build test
- PR agent for review (GPT-based AI review on each PR)
- Image promotion for both backend and frontend (certain changes trigger new PRs that auto updates image hashes that
  Flux deploys afterwards)
- Trivy for scanning dependencies and OS packages for vulnerabilities and YAML configs for any misconfigurations
- GitHub-configured checks such as GitLeaks and CodeQL
- There is also the pre-commit checker for potential credential leaks, lint check, etc.

## Prerequisites

Environment in this repo is managed via `mise`. Mise is a tool that helps organize environment and keep its details in
[mise.toml](mise.toml). For more info about `mise`, check its
[source repository](https://github.com/jdx/mise).
Besides it being helpful in pinning versions, it also allows for creating easy workflows like lint commands, starting
local backend dev server, etc.

To install the prerequisites, run:

```bash
mise install
```

This installs various tools like `SOPS`, `age`, `talhelper` and others.

### Common commands

Install pre-commit hooks for this repo:

```bash
mise run pre-commit:install
```

You can also run the pre-commit checks manually:

```bash
mise run pre-commit:run
```

Run all repository lint checks:

```bash
mise run lint
```

Apply fixes if applicable:

```bash
mise run lint:fix
```

## Creating the cluster

`talhelper` is a tool used in cluster creation steps. It helps keep the Talos cluster configuration repository scoped
and version controlled. More info can be found in its [repo](https://github.com/budimanjojo/talhelper).

Check [talos/README.md](talos/README.md) for more info.

1. Initial step in creating the cluster is verifying the network and storage settings of the nodes and creating the
   control plane and worker node configs based on that. For more details, see [talos/README.md](talos/README.md).
2. After the Talos has been bootstrapped, the next step is to bootstrap Cilium:
   [Cilium initial bootstrap](infra/controllers/cilium/README.md).
3. Following the previous steps, the next thing to do is to fetch the cluster's `kubeconfig` file, bootstrap Flux and
   install the existing `age` private identity as the `sops-age` Secret in the `flux-system` namespace. See
   [clusters/student-service-cluster/README.md](clusters/student-service-cluster/README.md).
4. After the Flux has been deployed properly and the actual Kustomizations and deployments are created, Flux then
   deploys the shared deployments from `infra/`, followed by workloads from `apps/student-service/`.

By default, Flux automatically reconciles and updates the deployments states accordingly.
If a change should be applied immediately, run:

```bash
flux reconcile kustomization flux-system -n flux-system --with-source
```

## Secrets

In order to keep the Talos configuration and various other sensitive information secure, `SOPS` and `age` are used
throughout the repository.

### AGE

`age` is a simple, modern and secure file encryption tool, format, and Go library. For more info about how `age` works,
check its [repo](https://github.com/filosottile/age).
In this repo scope, `age` is used to generate the initial key pair and as the encryption backend that `SOPS` uses for
encryption and decryption.

For this project, a simple `age-keygen` command was used for generating the mentioned key:

```bash
age-keygen -o age.key
```

The public recipient is stored in [.sops.yaml](.sops.yaml), while the private identity must not be committed to Git.
The public recipient can encrypt new files, while the private identity is required to decrypt or edit existing
encrypted files.

### SOPS

`SOPS` is an editor of encrypted files that supports YAML, JSON, ENV, INI and BINARY formats and encrypts with AWS KMS,
GCP KMS, Azure Key Vault, HuaweiCloud KMS, age, and PGP. (for more info, check the
[source repository](https://github.com/getsops/sops)).
In this repo, `SOPS` is used for the actual encryption step.
To decrypt or edit an existing encrypted file, the `$SOPS_AGE_KEY_FILE` environment variable is required to be set:

```bash
export SOPS_AGE_KEY_FILE=./age.key
```

You can encrypt the files in place:

```bash
sops encrypt --in-place apps/example/secret.sops.yaml
```

You can also check whether the encryption was succesful:

```bash
sops filestatus apps/example/secret.sops.yaml
```

If an encrypted file requires some tinkering, you can decrypt it and edit it as you like:

```bash
sops apps/example/secret.sops.yaml
```

### Cluster decryption

The naming convention for the `SOPS`-encrypted files is `*.sops.yaml`. These encrypted files can be stored in Git.

For Flux to be able to successfully decrypt these encrypted files, a k8s secret is needed:

```bash
kubectl -n flux-system create secret generic sops-age \
  --from-file=age.agekey="$SOPS_AGE_KEY_FILE"
```

Flux Kustomizations that use encrypted files reference this Secret:

```yaml
decryption:
  provider: sops
  secretRef:
    name: sops-age
```

The `sops-age` Secret contains the existing `age` private identity. During reconciliations, Flux uses it to decrypt the
files before applying them.
