#!/usr/bin/env bash
# Verify that the Dockerfile pins the official multi-arch Python 3.12 base by digest.
set -euo pipefail
cd "$(dirname "$0")/.."

ref="$(awk '/^FROM / {print $2; exit}' Dockerfile)"
case "$ref" in
  python:3.12-slim@sha256:*) ;;
  *)
    echo "FAIL: Dockerfile must pin python:3.12-slim@sha256:<digest>" >&2
    exit 1
    ;;
esac
pinned="${ref#*@}"

manifest="$(mktemp)"
trap 'rm -f "$manifest"' EXIT
docker buildx imagetools inspect "$ref" --format '{{json .Manifest}}' > "$manifest"

python_bin="${PYTHON_BIN:-python3}"
if ! "$python_bin" -c "" >/dev/null 2>&1; then
  python_bin=python
fi
if ! "$python_bin" -c "" >/dev/null 2>&1; then
  echo "FAIL: no working Python interpreter for manifest verification" >&2
  exit 1
fi
"$python_bin" - "$pinned" "$manifest" <<'PY'
import json
import sys

pinned, path = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as handle:
    manifest = json.load(handle)
if manifest.get("digest") != pinned:
    raise SystemExit(f"FAIL: resolved digest {manifest.get('digest')} != pinned {pinned}")
platforms = {
    f"{(item.get('platform') or {}).get('os', '')}/{(item.get('platform') or {}).get('architecture', '')}"
    for item in manifest.get("manifests", [])
}
required = {"linux/amd64", "linux/arm64"}
missing = required - platforms
if missing:
    raise SystemExit(f"FAIL: base image missing {sorted(missing)}; found {sorted(platforms)}")
print(f"BASE_IMAGE_OK digest={pinned} platforms={','.join(sorted(required))} python=3.12")
PY
