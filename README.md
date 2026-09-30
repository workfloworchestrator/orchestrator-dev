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
git clone https://github.com/workfloworchestrator/orchestrator-dev.git
cd orchestrator-dev
docker compose up --build
```


The initial frontend build will take a couple of minutes, but then you'll be hot-reloading.

Changes in the other repos should load automatically, perhaps with a delay of a second or two.

Subsequent runs should only require `docker compose up` unless you've changed the `example-orchestrator-ui`.

To access the orchestrator, visit http://localhost:3000 and log in as `alice:alice` or `bob:bob`.

To access keycloak itself, visit http://localhost:8085 and log in as `admin:admin`.

## Notes

When `orchestrator-ui-library` is bind-mounted, its `node_modules` is overriden by another volume, so this won't touch the host FS for the repo. However, all the other places that Node, Husky, and Turbo write to the filesystem are still bind-mounted. `git clean -xdn` will do a dry-run cleanup of these files, and `git clean -xdf` will execute the cleanup.


