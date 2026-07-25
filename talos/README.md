# Talos Bootstrap

This directory contains the Talos cluster definition for `student-service-cluster`.

Current pinned versions:

- Talos: `v1.12.6`
- Kubernetes: `v1.35.3`

Current bootstrap topology:

| Node   | Role          | IP             | Interface | Disk       |
| ------ | ------------- | -------------- | --------- | ---------- |
| `cp01` | control plane | `192.168.1.50` | `eth0`    | `/dev/vda` |
| `wn01` | worker        | `192.168.1.51` | `eth0`    | `/dev/vda` |
| `wn02` | worker        | `192.168.1.52` | `eth0`    | `/dev/vda` |

Shared network settings:

| Setting                | Value                       |
| ---------------------- | --------------------------- |
| Control plane endpoint | `https://192.168.1.50:6443` |
| Node addressing        | DHCP reservations on LAN    |
| Subnet                 | `192.168.1.0/24`            |

## Current Talos Configuration Choices

- The installer image / schematic ID is the source of truth for Talos image customization for all nodes.
- The same installer image is pinned for both control plane and worker nodes via `talosImageURL`.
- All current nodes use DHCP on the bridged home LAN with router reservations matching the IPs above.
- Worker nodes carry a shared registry trust patch for `harbor.student-service.internal`.
- Worker nodes are configured to carry a `UserVolumeConfig` patch for `local-path-provisioner` on `/dev/vdb`.

Current installer image source of truth:

- `factory.talos.dev/nocloud-installer/376567988ad370138ad8b2698212367b8edcb69b5fd68c80be1f2ec7d603b4ba`

## Harbor Registry Trust Patch

Current shared registry trust patch path:

- `talos/patches/workers/registry-harbor-ca.yaml`

Current registry trust intent:

- add a worker-local host entry for `harbor.student-service.internal -> 192.168.1.241`
- trust the internal CA for `harbor.student-service.internal`
- allow future worker node image pulls from Harbor over verified TLS

Apply the registry trust patch to worker nodes:

```bash
talosctl --nodes 192.168.1.51,192.168.1.52 patch mc \
  --patch @talos/patches/workers/registry-harbor-ca.yaml
```

Verify the applied registry config:

```bash
talosctl -n 192.168.1.51 get machineconfig v1alpha1 -o jsonpath='{.spec}' | grep -A12 "extraHostEntries"
talosctl -n 192.168.1.52 get machineconfig v1alpha1 -o jsonpath='{.spec}' | grep -A12 "extraHostEntries"
talosctl -n 192.168.1.51 get machineconfig v1alpha1 -o jsonpath='{.spec}' | grep -A8 "harbor.student-service.internal"
talosctl -n 192.168.1.52 get machineconfig v1alpha1 -o jsonpath='{.spec}' | grep -A8 "harbor.student-service.internal"
```

## Verify Network Interface

Verify the active interface name from Talos maintenance mode before keeping static network settings:

```bash
talosctl get links --insecure --nodes 192.168.1.50
talosctl get links --insecure --nodes 192.168.1.51
talosctl get links --insecure --nodes 192.168.1.52
```

For the current nodes, the active interface is `eth0`.

## Verify Install Disk

Verify the install disk before keeping `installDisk` in `talconfig.yaml`:

```bash
talosctl get disks --insecure --nodes 192.168.1.50
talosctl get disks --insecure --nodes 192.168.1.51
talosctl get disks --insecure --nodes 192.168.1.52
```

For the current nodes, the install disk is `/dev/vda`.

## Worker Storage Patch

Current worker storage patch path:

- `talos/patches/workers/local-path-provisioner-volume.yaml`

Current worker storage intent:

- add a second worker disk at `/dev/vdb`
- provision a Talos user volume named `local-path-provisioner`
- mount it at `/var/mnt/local-path-provisioner`

Verify the extra disk before applying worker config:

```bash
talosctl get disks --nodes 192.168.1.51
talosctl get disks --nodes 192.168.1.52
```

Apply the worker storage patch:

```bash
talosctl --nodes 192.168.1.51,192.168.1.52 patch mc \
  --patch @talos/patches/workers/local-path-provisioner-volume.yaml
```

Verify the user volume after applying worker config:

```bash
talosctl -n 192.168.1.51 get volumestatus u-local-path-provisioner
talosctl -n 192.168.1.52 get volumestatus u-local-path-provisioner
talosctl -n 192.168.1.51 ls /var/mnt/local-path-provisioner
talosctl -n 192.168.1.52 ls /var/mnt/local-path-provisioner
```

## Prerequisites

- `talhelper`
- `talosctl`
- `sops`
- `age`
- repo-root [`.sops.yaml`](../.sops.yaml) updated with the correct public key
- local `age` private key available via `SOPS_AGE_KEY_FILE`

## Generate Encrypted Talos Secrets

Run from the repository root:

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
talhelper gensecret > talos/talsecret.sops.yaml
sops -e -i talos/talsecret.sops.yaml
```

General flow:

1. export `SOPS_AGE_KEY_FILE`
2. generate Talos cluster secrets with `talhelper gensecret`
3. encrypt the resulting file with `sops -e -i`
4. edit later with `sops talos/talsecret.sops.yaml`

Verify the file is encrypted before committing it.

Important:

- `talhelper genconfig` treats `talsecret.sops.yaml` as the cluster secrets file by default.
- `talenv.sops.yaml` is a different input type used for environment variable substitution.
- Image customization should follow the installer image / schematic ID you actually boot with.
- The current schematic uses `customization: {}` and does not include `qemu-guest-agent`.

## Render Machine Configs

Run from `talos/`:

```bash
talhelper genconfig
```

Rendered files are written to `clusterconfig/` by default and must not be committed.

Expected generated files include:

- `clusterconfig/student-service-cluster-cp01.yaml`
- `clusterconfig/student-service-cluster-wn01.yaml`
- `clusterconfig/student-service-cluster-wn02.yaml`
- `clusterconfig/talosconfig`

After generating configs, set `TALOSCONFIG` for the rest of the Talos bootstrap session:

```bash
export TALOSCONFIG=$(realpath ./clusterconfig/talosconfig)
```

## Apply Control Plane Config

Run from `talos/`:

```bash
talosctl apply-config --insecure --nodes 192.168.1.50 --file clusterconfig/student-service-cluster-cp01.yaml
```

The node will install Talos to `/dev/vda` and reboot.

## Bootstrap the Cluster

Wait for the node to come back, then run:

```bash
talosctl --nodes 192.168.1.50 get machinestatus
talosctl bootstrap --nodes 192.168.1.50
```

Bootstrap is run once for the initial control plane.

## Apply Worker Configs

Run from `talos/`:

```bash
talosctl apply-config --insecure --nodes 192.168.1.51 --file clusterconfig/student-service-cluster-wn01.yaml
talosctl apply-config --insecure --nodes 192.168.1.52 --file clusterconfig/student-service-cluster-wn02.yaml
```

Both workers should appear in Kubernetes after they reboot and join the cluster.

## Fetch Kubeconfig

From `talos/`:

```bash
talosctl kubeconfig ../kubeconfig --nodes 192.168.1.50 --merge=false --force
```

Then export `KUBECONFIG` for the rest of the Kubernetes bootstrap session:

```bash
export KUBECONFIG=$(realpath ../kubeconfig)
```

Then use `kubectl` normally:

```bash
kubectl get nodes
```

With `cniConfig.name: none`, all nodes may remain `NotReady` until a CNI is deployed.
