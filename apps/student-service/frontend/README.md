# Student Service Frontend

Serves `student-service.internal` through a Cilium LoadBalancer at `192.168.1.240` and proxies `/api/` to the private
backend Service. Nginx redirects HTTP to HTTPS and terminates TLS with the cert-manager-managed certificate.

It reuses the encrypted `harbor-pull` image-pull Secret.
