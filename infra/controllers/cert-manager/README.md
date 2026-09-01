# cert-manager

`cert-manager` is used for managing TLS certificates in k8s services used. Some of the ops it handles are:

- watches `Certificate` resources
- creates certificate and private keys for `Certificate` objects and stores them in k8s secrets
- renews the certs before they expire

## Trusting the internal CA

Since the cluster uses a private CA, and it's definitely not in the trust chain of client devices, that means that the
client devices need to trust the mentioned CA in order for the HTTPS access to work.

The public CA cert is saved at [student-service-root-ca.crt](student-service-root-ca.crt).

The process of trusting a CA depends on the OS a bit. Run the commands below from the root of repository.

**Debian-based OS**:

```bash
sudo cp infra/controllers/cert-manager/issuers/student-service-root-ca.crt \
  /usr/local/share/ca-certificates/student-service-root-ca.crt
sudo update-ca-certificates
```

**Fedora or RHEL OS**:

```bash
sudo cp infra/controllers/cert-manager/issuers/student-service-root-ca.crt \
  /etc/pki/ca-trust/source/anchors/student-service-root-ca.crt
sudo update-ca-trust
```

**Windows** (I haven't tested this):
First open the PowerShell as an Administrator, then run:

```powershell
Import-Certificate `
  -FilePath ".\infra\controllers\cert-manager\issuers\student-service-root-ca.crt" `
  -CertStoreLocation "Cert:\LocalMachine\Root"
```

**MacOS** (didn't test it here, but I had success with different CA on a MacOS with the same command):

```bash
sudo security add-trusted-cert \
  -d \
  -r trustRoot \
  -k /Library/Keychains/System.keychain \
  infra/controllers/cert-manager/issuers/student-service-root-ca.crt
```

Note: you might need to restart your browser in order for certificates to strrt working.

## Check state

```bash
kubectl get pods -n cert-manager
kubectl get certificates -A
```
