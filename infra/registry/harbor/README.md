# Harbor

Harbor is a private registry used in this cluster. It stores the main apps backend and frontend images
that are used in deployments.

## Access

Harbor is accessible at <https://harbor.student-service.internal/harbor/projects>.

## Storage

Harbor stores registry data, Harbor database as well as job logs in the cluster's configured `local-path`.
For more info about `local-path` check the storage [README](../../storage/README.md).

## Images and CI

GitHub actions uses Harbor by pushing images to it in pipelines created by feature PRs and also by deploying the images
that get set as the current live version in promotion PRss.

The Harbor Helm chart still uses `https://helm.goharbor.io`, because the proper OCI chart pin hasn't been published

## Check state

Note: `/v2` is what actually checks the container registry API.

```bash
kubectl get pods,pvc,svc -n harbor
curl https://harbor.student-service.internal/v2/
```
