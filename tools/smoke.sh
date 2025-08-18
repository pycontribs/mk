#!/usr/bin/env bash
# cspell: ignore euox
set -euo pipefail

mk --version
mk --show-completion
mk commands
mk -vv detect
