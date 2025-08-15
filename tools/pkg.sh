#!/usr/bin/env bash
# cspell: ignore euox
set -euo pipefail

PROJECT=$(python -c '''
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover (py311+)
    import tomli as tomllib
print(tomllib.load(open("pyproject.toml","rb"))["project"]["name"])
''')
echo "Packaging sanity testing for '${PROJECT}' ..."
rm -rf dist
python3 -c "import os.path, shutil, sys; dist_dir = 'dist'; os.path.isdir(dist_dir) or sys.exit(0); print('Removing {!s} contents...'.format(dist_dir), file=sys.stderr); shutil.rmtree(dist_dir)"
# We cannot use python build for workspaces as it does not --all-packages
# python3 -m build
uv build --all-packages

python3 -m twine check --strict dist/*

echo "Building wheels cache into .cache/wheels ..."
pip download -q --find-links=dist --dest=./.cache/wheels "dist/${PROJECT}-"*.whl

echo "Isolate pipx for testing..."
export PIPX_HOME="${TOX_WORK_DIR:-.tox}/.pipx"
export PIPX_BIN_DIR="${PIPX_HOME}/bin"
export PATH="${PIPX_BIN_DIR}:${PATH}"
# shellcheck disable=SC2034
rm -rf "${PIPX_HOME}"
PIP_ARGS="--find-links=.cache/wheels --find-links=.dist" pipx install --force "${PROJECT}"
