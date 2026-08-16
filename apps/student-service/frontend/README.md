# Student Service Frontend

Serves the React app at `http://ingress.student-service.internal` and proxies `/api/` to the private backend Service.

It reuses the encrypted `harbor-pull` image-pull Secret.
