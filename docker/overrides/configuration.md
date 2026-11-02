# Configuration

Some configuration options for the docker compose services can be overridden.

## Environment variables

For each service you can create a `<service>.env` file to override certain variables within each container's environment.
See `docker-compose.yml` for the expected filenames.

For example, to set/change orchestrator variables, create the file in `docker/overrides/orchestrator/orchestrator.env`.

