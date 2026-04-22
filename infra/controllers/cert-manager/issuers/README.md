# cert-manager Issuers

Managed by Flux from `infra/controllers/cert-manager/issuers/`.

Current role:

- bootstraps the internal root CA for this cluster
- defines the shared `ClusterIssuer` used by service certificates
- does not belong to Harbor specifically

Current settings:

- bootstrap issuer: `student-service-bootstrap-selfsigned`
- root CA `Certificate`: `student-service-root-ca`
- CA `ClusterIssuer`: `student-service-ca`
- root CA Secret namespace: `cert-manager`

Current PKI model:

- `student-service-bootstrap-selfsigned` is used only to create the first root CA
- `student-service-root-ca` is the internal CA certificate and key material
- `student-service-ca` is the shared issuer for service certificates such as Harbor

The exported CA certificate from `student-service-root-ca` is a general trust anchor for certificates issued by `student-service-ca`.
Client-specific trust paths such as Docker registry trust are documented with the consuming service.

Client trust:

```bash
kubectl get secret -n cert-manager student-service-root-ca \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > student-service-root-ca.crt
```

Fedora / RHEL-style system trust:

```bash
sudo cp student-service-root-ca.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

Debian / Ubuntu-style system trust:

```bash
sudo cp student-service-root-ca.crt /usr/local/share/ca-certificates/student-service-root-ca.crt
sudo update-ca-certificates
```

Verification:

```bash
flux get kustomizations -A
kubectl get clusterissuers
kubectl get certificate -n cert-manager
kubectl get secret -n cert-manager student-service-root-ca
```
