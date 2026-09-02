# Student Service Frontend

Frontend is built as a React application bootstrapped by Vite.

Ther are both Nginx frontend deployment (check [deployment README](../apps/student-service/frontend/README.md))
and the option to locally run the app for testing purposes.

To run the frontend server locally, you can do the following:

```bash
mise run frontend:sync # install deps
mise run frontend:run
```

The frontend app will by default become available at <http://localhost:5173>.

The following `mise` checks are also available:

```bash
mise run frontend:lint
mise run frontend:build
```
