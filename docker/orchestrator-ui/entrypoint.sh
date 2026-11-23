#!/usr/bin/env bash
#
# Starts the example-orchestrator-ui app, bind-mounted at /app, with `next dev`.
#
# If a local orchestrator-ui-library clone is mounted at ./orchestrator-ui-components
# (ORCH_UI_LIB_DIR in .env), the app uses it instead of the npm release, the same way
# example-orchestrator-ui's use-local-orchestrator-ui-components.sh does:
#   1. install and build the library,
#   2. point the dependency in package.json to file:./orchestrator-ui-components and reinstall,
#   3. rebuild the library on changes and copy the output into the installed package.
# Step 2 changes package.json and pnpm-lock.yaml in your example-orchestrator-ui clone.
#
set -euo pipefail

PACKAGE="@orchestrator-ui/orchestrator-ui-components"
LIB_DIR="orchestrator-ui-components"
LOCAL_SPEC="file:./$LIB_DIR"

cd /app

current_spec=$(node -p "require('./package.json').dependencies['$PACKAGE'] ?? ''")
if [ -z "$current_spec" ]; then
    echo "Error: $PACKAGE is not listed in dependencies of package.json." >&2
    exit 1
fi

if [ ! -f "$LIB_DIR/package.json" ]; then
    if [ "$current_spec" = "$LOCAL_SPEC" ]; then
        echo "Error: ORCH_UI_LIB_DIR is not set, but package.json still points $PACKAGE to $LOCAL_SPEC" >&2
        echo "from an earlier run with a local library. To use the npm release, run in your" >&2
        echo "example-orchestrator-ui clone:" >&2
        echo "  git checkout package.json pnpm-lock.yaml pnpm-workspace.yaml" >&2
        echo "and start the container again. Or set ORCH_UI_LIB_DIR to keep using the local library." >&2
        exit 1
    fi
    echo "▶ Using $PACKAGE $current_spec from npm"
    pnpm install --frozen-lockfile
    echo "▶ Starting next dev"
    exec pnpm run dev
fi

echo "▶ Using local $PACKAGE from ORCH_UI_LIB_DIR"

echo "▶ Installing and building the library"
# Build before installing in the app: pnpm copies the files that exist at install time.
(cd "$LIB_DIR" && pnpm install --frozen-lockfile && pnpm run build)

if [ "$current_spec" != "$LOCAL_SPEC" ]; then
    echo "▶ Pointing $PACKAGE to $LOCAL_SPEC in package.json (don't commit this)"
    node -e '
const fs = require("fs");
const [pkgName, spec] = process.argv.slice(1);
const raw = fs.readFileSync("package.json", "utf8");
const indent = raw.match(/^[ \t]+/m)?.[0] ?? 2;
const pkg = JSON.parse(raw);
pkg.dependencies[pkgName] = spec;
fs.writeFileSync("package.json", JSON.stringify(pkg, null, indent) + "\n");
' "$PACKAGE" "$LOCAL_SPEC"
fi
# CI=true makes pnpm default to a frozen lockfile; the lockfile has to change here.
pnpm install --no-frozen-lockfile

# Replace the files in the installed copy after every rebuild (--remove-destination), so
# the file watcher of `next dev` sees the change. Writing through a hardlink would not
# trigger it.
INSTALLED="$(readlink -f "node_modules/$PACKAGE")"

# Run the library watcher and next dev side by side. If either one stops, stop the
# other too, so the container exits instead of silently running without hot-reload.
trap 'kill 0' TERM INT

echo "▶ Watching the library for changes"
(cd "$LIB_DIR" && pnpm run dev --onSuccess "cp -r --remove-destination dist/. '$INSTALLED/dist/'") &

echo "▶ Starting next dev"
pnpm run dev &

status=0
wait -n || status=$?
echo "▶ The library watcher or next dev exited (status $status); stopping" >&2
kill 0
exit "$status"
