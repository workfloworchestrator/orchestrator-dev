# orchestrator-dev

This is a full-stack development environment for the Workflow Orchestrator software framework, with batteries included.

At a glance, you get:

* A dead-simple WFO app that provides Files-On-Disk-As-A-Service ;)
* Hot-reloading for `orchestrator-core`
  * Currently no support for loading upstream packages like `pydantic-forms` and `oauth2_lib`
* Rebuildable use of `example-orchestrator-ui`
  * Currently, must rebuild the local image, no hot-reload
* Hot-reloading of `orchestrator-ui-library` into the UI container


To get started:
```
git clone https://github.com/workfloworchestrator/orchestrator-core.git
git clone https://github.com/workfloworchestrator/orchestrator-ui-library.git
git clone https://github.com/workfloworchestrator/example-orchestrator-ui.git
git clone https://github.com/workfloworchestrator/orchestrator-dev.git
cd orchestrator-dev
docker compose up
```

The initial frontend build will take a couple of minutes, but then you'll be hot-reloading.

To access the orchestrator, visit http://localhost:3000 and log in as `alice:alice` or `bob:bob`.

Changes in the other repos should load automatically, perhaps with a delay of a second or two.
