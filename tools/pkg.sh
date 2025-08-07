#!/usr/bin/env bash
# cspell: ignore euox
set -euox pipefail
env | grep TOX

echo "Isolate pipx for testing..."
export PIPX_HOME="${TOX_WORK_DIR:-.tox}/.pipx"
export PIPX_BIN_DIR="${PIPX_HOME}/bin"
export PATH="${PIPX_BIN_DIR}:${PATH}"
rm -rf "${PIPX_HOME}"
pipx install --force -e .

rm -rf dist
python3 -c "import os.path, shutil, sys; dist_dir = 'dist'; os.path.isdir(dist_dir) or sys.exit(0); print('Removing {!s} contents...'.format(dist_dir), file=sys.stderr); shutil.rmtree(dist_dir)"
python3 -m build

python3 -m twine check --strict dist/*
python3 -m pip install "mk @ file://$(pwd)/$(echo dist/*.whl)"
python3 -m pip uninstall -y mk
