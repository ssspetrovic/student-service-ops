# Talos Cluster Bootstrap

## Host and virtualization setup

The runtime environment for this project is living on a desktop machine running Ubuntu 24.04 LTS Server operating system.

As I don't have multiple of those machines, I used QEMU/KVM stack via `libvirt`.
I've also installed `cockpit` which allowed for easier VM handling through GUI on a remote laptop,
instead of dealing with `libvirt` CLI.

The VM setup included 3 nodes - 1 control plane node and 2 worker nodes.

## Talos image and first boot

The boot image was created using [Talos Linux Image Factory](https://factory.talos.dev/). A vanilla NoCloud ISO was
used without any extra add-ons to start the nodes in maintenance mode.

The machine configurations use the following installer image to install Talos onto `/dev/vda`:

```text
factory.talos.dev/nocloud-installer/376567988ad370138ad8b2698212367b8edcb69b5fd68c80be1f2ec7d603b4ba
```

The image was downloaded onto the server and imported through `cockpit` for each of these VM nodes.

## Networking

Initially, the bootstrap was done using the libvirt's NAT network.
This approach worked fine until the load balancer deployment came into picture.
For this to be properly accessed, the netwoking was switched to bridged home LAN.

The table bellow displays the basic nodes info as well as their matching IP:

| Node   | Role          | IP             |
| ------ | ------------- | -------------- |
| `cp01` | control plane | `192.168.1.50` |
| `wn01` | worker        | `192.168.1.51` |
| `wn02` | worker        | `192.168.1.52` |

Talos uses DHCP on `eth0`. The router keeps the addresses stable through DHCP reservations associated with each VM's
MAC address. Without these reservations, the addresses may change and no longer match `talconfig.yaml`.

Workers trust Harbor and use `/dev/vdb` for local-path storage.

## Check the hardware first

Keeping the IP static and matching it properly isn't the only key step to Talos bootstrap process.

It's also important that you verify what are the disk and the network adapter configurations on these nodes.

For this setup, the deafult network interface was `eth0`, and the default disk was `/dev/vda`.
I have also created an additional `/dev/vdb` disk on each worker during a later stage of the project. Talos formats it
as XFS and mounts it at `/var/mnt/local-path-provisioner` for persistent volumes using the `local-path` StorageClass.

You can confirm the default network adapters like this:

```bash
talosctl get links --insecure --nodes 192.168.1.50
talosctl get links --insecure --nodes 192.168.1.51
talosctl get links --insecure --nodes 192.168.1.52
```

And you can also check for the disk layout as well:

```bash
talosctl get disks --insecure --nodes 192.168.1.50
talosctl get disks --insecure --nodes 192.168.1.51
talosctl get disks --insecure --nodes 192.168.1.52
```

Make sure the values match the [`talconfig.yaml`](./talconfig.yaml) and the worker storage patch before proceeding.

Do not blindly reuse `/dev/vda` or `/dev/vdb` before checking the actual values if you intend to create a new cluster.
Configurations may and usually will vary in different scenarios.

## Generate config

NOTE: all of the Talos related commands should be run from `talos/` directory.

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
talhelper genconfig
export TALOSCONFIG=$(realpath ./clusterconfig/talosconfig)
```

Do not commit `clusterconfig/`.

## Bootstrap

```bash
talosctl apply-config --insecure --nodes 192.168.1.50 --file clusterconfig/student-service-cluster-cp01.yaml
```

Wait for `cp01` to install Talos, reboot and become reachable using the generated `talosconfig`. Then bootstrap the
control plane once:

```bash
talosctl bootstrap --nodes 192.168.1.50
```

When the control plane is ready, apply both worker files:

```bash
talosctl apply-config --insecure --nodes 192.168.1.51 --file clusterconfig/student-service-cluster-wn01.yaml
talosctl apply-config --insecure --nodes 192.168.1.52 --file clusterconfig/student-service-cluster-wn02.yaml
```

Then fetch the kubeconfig:

```bash
talosctl kubeconfig ../kubeconfig --nodes 192.168.1.50 --merge=false --force
export KUBECONFIG=$(realpath ../kubeconfig)
kubectl get nodes
```

The nodes may remain `NotReady` because the built-in CNI is disabled.
Complete the [Cilium initial bootstrap](../infra/controllers/cilium/README.md) before checking their final state.
