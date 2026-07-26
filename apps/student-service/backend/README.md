# Student Service Backend

This directory deploys the internal Django API:

- one backend replica
- an internal `ClusterIP` Service on port `8000`
- readiness and liveness probes at `GET /api/health/`

Flux deploys it only after the migration Job succeeds. The Service is available
inside the cluster at: `http://student-service-backend.student-service.svc.cluster.local:8000`

When a backend image is published from `main`, CI opens or updates a promotion
pull request with the new commit-SHA image tag. Merging that pull request lets
Flux run the matching migrations before updating the backend.
