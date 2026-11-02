#!/bin/bash

# Exit on errors or unset variables
set -eu

# Tell uv not to ever download python, but use whatever version is set in https://github.com/workfloworchestrator/orchestrator-core/blob/main/Dockerfile
# This version should match with pyproject.toml
export UV_PYTHON_DOWNLOADS=never

# Install extra requirements for our repo
uv sync
source .venv/bin/activate

setup() {
    echo "▶ db upgrade heads"
    python main.py db upgrade heads

    echo "▶ index subscriptions"
    python main.py index subscriptions

    echo "▶ index products"
    python main.py index products

    echo "▶ index processes"
    python main.py index processes

    echo "▶ index workflows"
    python main.py index workflows
}

RELOAD_DIRS=(
    --reload-dir db
    --reload-dir graphql_utils
    --reload-dir products
    --reload-dir services
    --reload-dir translations
    --reload-dir utils
    --reload-dir workflows
)

reload() {
    pkg_name="$1"
    pkg_dst="$2"
    pkg_extras="$3"  # comma delimited list of extras
    # Override dir must be an actual Python package
    if [ -f ${pkg_dst}/pyproject.toml ]; then
        echo "⏭️ Use editable install of ${pkg_name}"
	# Do not quote this; it's not how this array works.
        RELOAD_DIRS+=(--reload-dir ${pkg_dst})

        install_spec="$pkg_dst"
        if [ -n "$pkg_extras" ]; then
            # Example: '/path/to/core[agent,search]'
            install_spec="$pkg_dst"'['"${pkg_extras%,}"']'
        fi

        echo "Installing ${pkg_name} with spec: '${install_spec}'"
        uv pip install -e "$install_spec"
    else
        echo "⏭️ Use ${pkg_name} as specified in pyproject.toml $(uv pip freeze | grep ${pkg_name})"
    fi
}

# reload package-name dst extras
reload "orchestrator-core" "$CORE_DST" ""
reload "pydantic-forms" "$FORMS_DST" ""
reload "oauth2-lib" "$OAUTH2LIB_DST" ""
reload "nwa-stdlib" "$NWASTDLIB_DST" ""

setup
uvicorn --host 0.0.0.0 --port 8080 ${UVICORN_ARGS:-} wsgi:app --reload --proxy-headers "${RELOAD_DIRS[@]}"
