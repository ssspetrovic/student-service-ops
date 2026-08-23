# cert-manager

`cert-manager` issues certificates for cluster services. This enables HTTPS.

## Trust the internal CA

The services use certificates issued by the project's internal CA.
You can fetch the CA cert from the directly from the cluster via `kubectl`:

```bash
kubectl get secret -n cert-manager student-service-root-ca \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > student-service-root-ca.crt
```

On Debian or Ubuntu, install it with:

```bash
sudo cp student-service-root-ca.crt /usr/local/share/ca-certificates/student-service-root-ca.crt
sudo update-ca-certificates
```

On Fedora or RHEL, install it with:

```bash
sudo cp student-service-root-ca.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

If the certificates are not loading after this, try restarting the browser after cert installation.

## Check state

```bash
kubectl get pods -n cert-manager
kubectl get crds | grep cert-manager.io
```
