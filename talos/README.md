# Talos Bootstrap

| Node   | Role          | IP             |
| ------ | ------------- | -------------- |
| `cp01` | control plane | `192.168.1.50` |
| `wn01` | worker        | `192.168.1.51` |
| `wn02` | worker        | `192.168.1.52` |

All nodes use DHCP reservations on the bridged LAN. Workers trust Harbor and use `/dev/vdb` for local-path storage.

## Check the hardware first

Before generating or applying config, confirm the node interface is `eth0`, the install disk is `/dev/vda`,
and each worker has an unused `/dev/vdb` data disk:

```bash
talosctl get links --insecure --nodes 192.168.1.50
talosctl get links --insecure --nodes 192.168.1.51
talosctl get links --insecure --nodes 192.168.1.52
talosctl get disks --insecure --nodes 192.168.1.50
talosctl get disks --insecure --nodes 192.168.1.51
talosctl get disks --insecure --nodes 192.168.1.52
```

Make sure the values match. Update `talconfig.yaml` and the worker storage patch before proceeding and
don\t reuse `/dev/vda` or `/dev/vdb` before checking the actual values.

## Generate config

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
talhelper genconfig
export TALOSCONFIG=$(realpath ./clusterconfig/talosconfig)
```

Do not commit `clusterconfig/`.

## Bootstrap

```bash
talosctl apply-config --insecure --nodes 192.168.1.50 --file clusterconfig/student-service-cluster-cp01.yaml
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

AFter this,  complete the [Cilium initial bootstrap](../infra/controllers/cilium/README.md).
