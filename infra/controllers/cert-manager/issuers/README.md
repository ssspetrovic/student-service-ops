# cert-manager Issuers

Private certificate authority (CA) used by services in the cluster.

There are 2 important files in this directory:

- [student-service-root-ca.sops.yaml](student-service-root-ca.sops.yaml) -
  contains the CA cert + pivate signing key, it's SOPS encrypted as the name suggests
- [student-service-root-ca.crt](student-service-root-ca.crt) -
  contains the public CA certificate only, used for enabling access for client devices.

## Terminology

Some of these abbreviations and terms are a bit confusing so here's a quick reference guide:

- TLS: transport layer security - this is what makes the HTTPS connection secure by encryption and identity
  verification
- CA: certificate authority used for signing and verifiyng certificates.
- `Certificate`: this is a k8s object that connects a hostname to a pubkey
- `cert-manager`: used for creating, storing and renewing ceritficates in k8s.

## What's used here

The root CA is stored in a SOPS-encrypted yaml. `ClusterIssuer` uses it for signing the cluster certificats.

`ClusterIssuer` is used here because the services run in different namespaces, making the regular `Issuer` more painful
to use due to duplication that it would require.

## Self-signe dissuer

There used to be a self-signed issuer to create the initial root CA. It has been deleted because it's no longer needed
because the CA keypair is saved in the mentioned encrypted yaml.

## Check state

```bash
kubectl get clusterissuer student-service-ca
kubectl -n cert-manager get secret student-service-root-ca
```
