# Talos Bootstrap

| Node | Role | IP |
| --- | --- | --- |
| `cp01` | control plane | `192.168.1.50` |
| `wn01` | worker | `192.168.1.51` |
| `wn02` | worker | `192.168.1.52` |

All nodes use DHCP reservations on the bridged LAN. Workers trust Harbor and
use `/dev/vdb` for local-path storage.

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

Apply the worker files after the control plane is ready.
