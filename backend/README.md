# Student Service Backend

The backend is a Django with DRF for the Student Service application.
Both the k8sa app deployment and the local server version are available.

For the k8s deployment, check [the deployment README](../apps/student-service/backend/README.md).

For the local setup, first configure the env file:

```bash
cp ./backend/.env.example ./backend/.env
```

You can then use the preconfigured mise tasks to run the backend server:

```bash
mise run backend:sync # setup uv environment
mise run backend:migrate
mise run backend:run
```

The local app will become available at <http://127.0.0.1:8000> by default.

There are some other checks that are preconfigured through mise:

```bash
mise run backend:check # check for common errors and warnings
mise run backend:lint # lint chcek
mise run backend:test # runs the test suite
mise run backend:shell # creates the Django shell
mise run backend:createsuperuser # superuser creation process
```
