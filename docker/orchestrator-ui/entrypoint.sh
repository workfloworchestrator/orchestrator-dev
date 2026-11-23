#!/usr/bin/env bash
#
# Starts the example-orchestrator-ui app with `next dev`.
#
# If a local orchestrator-ui-library clone is mounted at ./orchestrator-ui-components
# (ORCH_UI_LIB_DIR in .env), the app uses it instead of the npm release, the same way
# example-orchestrator-ui's use-local-orchestrator-ui-components.sh does:
#   1. install and build the library,
#   2. point the dependency in package.json to file:./orchestrator-ui-components and reinstall,
#   3. rebuild the library on changes and copy the output into the installed package.
# These changes only affect the copy of the app inside the container, not the host clone.
#
set -euo pipefail

PACKAGE="@orchestrator-ui/orchestrator-ui-components"
LIB_DIR="orchestrator-ui-components"

cd /app

if [ ! -f "$LIB_DIR/package.json" ]; then
    version=$(node -p "require('./package.json').dependencies['$PACKAGE']")
    echo "▶ Using $PACKAGE $version from npm"
    exec pnpm run dev
fi

echo "▶ Using local $PACKAGE from ORCH_UI_LIB_DIR"

echo "▶ Installing and building the library"
# Build before installing in the app: pnpm copies the files that exist at install time.
(cd "$LIB_DIR" && pnpm install --frozen-lockfile && pnpm run build)

echo "▶ Pointing $PACKAGE to file:./$LIB_DIR"
node -e '
const fs = require("fs");
const [pkgName, spec] = process.argv.slice(1);
const raw = fs.readFileSync("package.json", "utf8");
const indent = raw.match(/^[ \t]+/m)?.[0] ?? 2;
const pkg = JSON.parse(raw);
if (!pkg.dependencies?.[pkgName]) {
    console.error(`Error: ${pkgName} is not listed in dependencies of package.json.`);
    process.exit(1);
}
pkg.dependencies[pkgName] = spec;
fs.writeFileSync("package.json", JSON.stringify(pkg, null, indent) + "\n");
' "$PACKAGE" "file:./$LIB_DIR"
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
