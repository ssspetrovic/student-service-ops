# Harbor Certificate

Harbor uses the TLS certificate to serve the API and GUI over HTTPS.

`student-service-ca` is the issuer of this TLS certificate and the cert itself is managed through
`cert-manager` controller.

The certificate is finally mounted by Harbor which allows for the HTTPS serving.

## Check state

```bash
kubectl get certificate -n harbor
kubectl get secret -n harbor harbor-tls
```
