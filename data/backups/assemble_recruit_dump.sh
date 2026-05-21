#!/usr/bin/env bash
# Wrapper — see scripts/migration/assemble-recruit-dump.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec "${ROOT}/scripts/migration/assemble-recruit-dump.sh" --backups-dir "$(dirname "$0")" "$@"
