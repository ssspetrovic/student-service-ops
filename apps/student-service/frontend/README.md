# Student Service Frontend

Frontend is served as an Nginx deployment.
It can be accessed form <https://student-service.internal>.
Nginx also forwards the API requests to the backend application.

Frontend has its own certificate secret that Nginx mounts and uses to provide HTTPS endpoint.

LoadBalancer Service is used to expose the frontend at `192.168.1.240`.

## State check

```bash
kubectl -n student-service get deployment,service,certificate
curl https://student-service.internal/healthz
```
