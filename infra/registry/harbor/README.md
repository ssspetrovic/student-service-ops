# Harbor

Harbor is the private image registry. Trusted clients reach it at
`https://harbor.student-service.internal`.

Its encrypted values are in `harbor-values.sops.yaml`. GitHub Actions uses the
`github-actions-build` robot account to push and pull images.

The Harbor Helm chart still uses `https://helm.goharbor.io`, because the proper OCI chart pin hasn't been published

## Check state

```bash
kubectl get pods,pvc,svc -n harbor
curl -v https://harbor.student-service.internal/v2/
```
