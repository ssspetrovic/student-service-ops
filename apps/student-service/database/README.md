# Student Service Database

Deploys the private PostgreSQL database on a `5Gi` `local-path` volume. It has no replica or external backup.

Only the backend and migration Job can connect to it.
