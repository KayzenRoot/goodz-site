#!/usr/bin/env bash
# Prove that two independent builds resolve the same Python and package closure.
# This is dependency/build-input reproducibility, not a byte-identical image claim.
set -euo pipefail
cd "$(dirname "$0")/.."

image="${1:-goodz-audit:ci}"
rebuilt="goodz-audit:repro"
first="$(mktemp)"
second="$(mktemp)"
trap 'rm -f "$first" "$second"' EXIT

snapshot() {
  docker run --rm -i "$1" python - <<'PY'
import importlib.metadata as metadata
import platform

print(f"python={platform.python_version()}")
for dist in sorted(metadata.distributions(), key=lambda item: (item.metadata["Name"] or "").lower()):
    print(f"{(dist.metadata['Name'] or '').lower()}=={dist.version}")
PY
}

docker image inspect "$image" >/dev/null
snapshot "$image" > "$first"
docker build --no-cache --tag "$rebuilt" .
snapshot "$rebuilt" > "$second"

if ! diff -u "$first" "$second"; then
  echo "FAIL: package/python closure differs between independent builds" >&2
  exit 1
fi
packages="$(grep -c '==' "$first")"
echo "IMAGE_REPRO_OK packages=$packages"
