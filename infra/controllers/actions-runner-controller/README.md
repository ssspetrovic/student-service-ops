# Actions Runner Controller

Action Runner Controller (ARC) is what manages the self-hosted GitHub Actions runners in the cluster.

The controller creates or removes runner pods as jobs from workflows get scheduled.

The runner pool configuration is described in the [runner scale-set README](../../ci/actions-runner-scale-set/README.md).

## CHeck state

```bash
kubectl get pods -n arc-systems
```
