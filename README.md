# orchestrator-dev

This is a full-stack development environment for the Workflow Orchestrator software framework, with batteries included.

At a glance, you get:

* A dead-simple WFO app that provides Files-On-Disk-As-A-Service ;)
* AuthN|Z via Keycloak, preconfigured with a realm and a couple of users.
* Hot-reloading for `orchestrator-core`
  * Currently no support for loading upstream packages like `pydantic-forms` and `oauth2_lib`
* Rebuildable use of `example-orchestrator-ui`
  * Currently doesn't hot-reload. Users must rebuild the local image with `docker compose up --build orchestrator-ui`.
* Hot-reloading of `orchestrator-ui-library` into the UI container


To get started:
```
git clone https://github.com/workfloworchestrator/orchestrator-core.git
git clone https://github.com/workfloworchestrator/orchestrator-ui-library.git
git clone https://github.com/workfloworchestrator/example-orchestrator-ui.git
# WFO Python dependencies
git clone https://github.com/workfloworchestrator/pydantic-forms.git
git clone https://github.com/workfloworchestrator/oauth2-lib.git
git clone https://github.com/workfloworchestrator/nwa-stdlib.git
git clone https://github.com/workfloworchestrator/orchestrator-dev.git
cd orchestrator-dev
cp .env.example .env
docker compose up --build
```


The initial frontend build will take a couple of minutes, but then you'll be hot-reloading.

Changes in the other repos should load automatically, perhaps with a delay of a second or two.

Subsequent runs should only require `docker compose up` unless you've changed the `example-orchestrator-ui`.

To access the orchestrator, visit http://localhost:3000 and log in as `alice:alice` or `bob:bob`.

To access keycloak itself, visit http://localhost:8085 and log in as `admin:admin`.

## Notes
### Hot-reloading Python dependencies
Local copies of Python dependencies can be installed in editable mode.
Using `orchestrator-core` as an example:

* `.env.example` specifies two variables:
    * `CORE_SRC`: local directory on your host system, presumably `../orchestrator-core` relative to this repo.
    * `CORE_DST`: where to mount this code into the image. Defaults to `/home/orchestrator/<PACKAGE_NAME>`.
* `docker-compose.yml`:
    * `services:orchestrator:environment:` maps `CORE_DST` into the container's environment for the entrypoint
    * `services:orchestrator:volumes:` maps `CORE_SRC` to `CORE_DST`
* `docker/orchestrator/entrypoint.sh`: installs the mounted package in editable mode via the `reload` function.

### Orchestrator UI & backend docker image overrides

In [docker-compose.yml](./docker-compose.yml), the `orchestrator` and
`orchestrator-ui` services use pre-built images to spin up their respective
applications (i.e., there is no `build:` directive specified). The docker image
tag defaults to use the artifacts built in the workfloworchestrator project's
Github Container Registry, but can be overridden by setting environment
variables.

For example,

```bash
ORCH_UI_TAG=my-local-image:tag docker compose up -d --force-recreate
```

#### `orchestrator-core` Version and `ORCH_BACKEND_TAG`
Users must ensure that the `orchestrator-core` version pinned in `pyproject.toml` is compatible with the image specified via `ORCH_BACKEND_TAG` in their `.env`, as uv does not yet support variable expansion within `pyproject.toml`.

### Artifacts
When `orchestrator-ui-library` is bind-mounted, its `node_modules` is overriden by another volume, so this won't touch the host FS for the repo. However, all the other places that Node, Husky, and Turbo write to the filesystem are still bind-mounted. `git clean -xdn` will do a dry-run cleanup of these files, and `git clean -xdf` will execute the cleanup.
