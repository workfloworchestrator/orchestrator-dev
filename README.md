# orchestrator-dev

This is a full-stack development environment for the Workflow Orchestrator software framework, with batteries included.

At a glance, you get:

* A dead-simple WFO app that provides Files-On-Disk-As-A-Service ;)
* AuthN|Z via Keycloak, preconfigured with a realm and a couple of users.
* Hot-reloading for `orchestrator-core`
  * Currently no support for loading upstream packages like `pydantic-forms` and `oauth2_lib`
* Hot-reloading of `example-orchestrator-ui`, served with `next dev` from your bind-mounted clone
* The UI component library from npm, or hot-reloaded from a local `orchestrator-ui-library` clone
  (see [Orchestrator UI component library: npm or local](#orchestrator-ui-component-library-npm-or-local))


To get started, clone this repo and the UI app side by side:
```
git clone https://github.com/workfloworchestrator/orchestrator-dev.git
git clone https://github.com/workfloworchestrator/example-orchestrator-ui.git
# Optional, both enabled by default in .env.example:
#  - hot-reload the UI component library (comment out ORCH_UI_LIB_DIR to use the npm release)
git clone https://github.com/workfloworchestrator/orchestrator-ui-library.git
#  - hot-reload orchestrator-core (comment out CORE_SRC to use the version in uv.lock)
git clone https://github.com/workfloworchestrator/orchestrator-core.git
cd orchestrator-dev
cp .env.example .env
docker compose up --build
```

If you want to hack on the other WFO Python dependencies, clone them next to the
others as well and uncomment the matching `*_SRC` line in your `.env`
(see [Hot-reloading Python dependencies](#hot-reloading-python-dependencies)):
```
git clone https://github.com/workfloworchestrator/pydantic-forms.git
git clone https://github.com/workfloworchestrator/oauth2-lib.git
git clone https://github.com/workfloworchestrator/nwa-stdlib.git
```

Any Python library that isn't cloned is installed at the version pinned in `uv.lock`.


The first start of the frontend takes a couple of minutes to install its dependencies, but then you'll be hot-reloading.

Changes in the other repos should load automatically, perhaps with a delay of a second or two.

Subsequent runs should only require `docker compose up`.

To access the orchestrator, visit http://localhost:3000 and log in as `alice:alice` or `bob:bob`.

Visit http://localhost:8080/api/docs to view the Swagger UI.

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

In `.env.example`, `CORE_SRC` is enabled and the other variables are commented out. Uncomment the ones that you'd like to take advantage of in your `.env`.

Note that `docker-compose.yml` provides fallbacks for each of these variables. Ignoring a `_SRC` variable will use the `./docker/overrides/<package>/` directory; by default, this will be empty. Ignoring a `_DST` variable mounts the `_SRC` in the expected location: `/home/orchestrator/<package>`. If the directory in the container lacks a `pyproject.toml`, as is the case for an empty or missing `./docker/overrides/<package>/` directory, then the version of the package specified in `uv.lock` is instead used.

### Orchestrator UI & backend sources

In [docker-compose.yml](./docker-compose.yml), the `orchestrator` service uses a
pre-built image. It defaults to the image in the workfloworchestrator project's
Github Container Registry set in `ORCH_BACKEND_TAG`, which you can override:

```bash
ORCH_BACKEND_TAG=my-local-image:tag docker compose up -d --force-recreate orchestrator
```

The `orchestrator-ui` service bind-mounts your `example-orchestrator-ui` clone,
set by `ORCH_UI_DIR` (default `../example-orchestrator-ui`), at `/app` and runs
`pnpm install` and `next dev` on it, so changes to the app hot-reload. The image
only holds the tools (Node 24, pnpm via corepack).

Things that must differ between your host and the container are kept on Docker
volumes instead of in your clone: `node_modules` (Linux builds of native packages),
`.next`, and the pnpm store. You can keep running `pnpm dev` on your host as well;
the two don't share these folders. After changing dependencies, restart the
container (`docker compose restart orchestrator-ui`) so it runs `pnpm install` again.

Environment variables from `docker/orchestrator-ui/orchestrator-ui.env` take
precedence over a `.env` file in your clone.

### Orchestrator UI component library: npm or local

The UI app depends on `@orchestrator-ui/orchestrator-ui-components`. You choose
where it comes from with `ORCH_UI_LIB_DIR` in your `.env`:

| `ORCH_UI_LIB_DIR` | Library used |
|---|---|
| Set, e.g. `../orchestrator-ui-library` (default in `.env.example`) | Your local clone, rebuilt and hot-reloaded on every change |
| Commented out | The version pinned in `example-orchestrator-ui`'s `package.json`, from npm |

After changing it, run `docker compose up -d orchestrator-ui`; compose recreates
the container.

In local mode, [`docker/orchestrator-ui/entrypoint.sh`](./docker/orchestrator-ui/entrypoint.sh)
does inside the container what `example-orchestrator-ui`'s own
`use-local-orchestrator-ui-components.sh` does on a host:

1. The clone is mounted at `/app/orchestrator-ui-components`, and the library is
   installed (`pnpm install`) and built.
2. The app's dependency is pointed to `file:./orchestrator-ui-components` and
   the app is reinstalled. The library's own dependencies are installed too,
   so the app doesn't need to pin the same library version.
3. `tsup --watch` rebuilds the library on every change and copies the output
   into the installed package, where `next dev` picks it up.

Step 2 changes `package.json` and `pnpm-lock.yaml` in your `example-orchestrator-ui`
clone. Don't commit these; the app's pre-commit hook refuses them. To go back to the
npm release, comment out `ORCH_UI_LIB_DIR`, run
`git checkout package.json pnpm-lock.yaml pnpm-workspace.yaml` in your
`example-orchestrator-ui` clone, and recreate the container. If you forget the
checkout, the container stops with these instructions.

The container stops if either the library watcher or `next dev` exits; check
`docker logs orchestrator-ui`.

The first start in local mode takes a minute or two for the library install and build.

#### `orchestrator-core` Version and `ORCH_BACKEND_TAG`
Users must ensure that the `orchestrator-core` version pinned in `pyproject.toml` is compatible with the image specified via `ORCH_BACKEND_TAG` in their `.env`, as uv does not yet support variable expansion within `pyproject.toml`.

You may pull a version of the UI library that requires a greater version of the core, which should be highlighted in the Incompatible Versions warning the web UI. This means you need to update the above files. If the release isn't available yet, you may need to instead use a release candidate (such as 5.6.0rc1 instead of 5.6.0.)

This adds a bit of friction to steadily bump these versions, but it allows devs to sync very specific versions of each library as needed.

### Artifacts
When `orchestrator-ui-library` is bind-mounted, its `node_modules` is on a Docker volume (`ui_lib_node_modules`), so it doesn't touch your clone. The build does write `dist/` and `src/configuration/version.ts` into the clone; both are gitignored. `git clean -xdn` will do a dry-run cleanup of ignored files, and `git clean -xdf` will execute the cleanup.
