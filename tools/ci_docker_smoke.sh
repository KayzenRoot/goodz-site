#!/usr/bin/env bash
# Ephemeral local-only Docker qualification; never deploys to production.
set -euo pipefail
cd "$(dirname "$0")/.."
NAME="goodz-audit-${GITHUB_RUN_ID:-$}"
VOLUME="goodz-audit-volume-${GITHUB_RUN_ID:-$}"
cleanup() {
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker volume rm "$VOLUME" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker build --tag goodz-audit:ci .
docker compose config --quiet
docker volume create "$VOLUME" >/dev/null
docker run --detach --name "$NAME" --read-only \
  --tmpfs /tmp:rw,nosuid,noexec,size=32m \
  --security-opt no-new-privileges:true --cap-drop ALL \
  --publish 127.0.0.1:18080:8000 \
  --mount "type=volume,source=$VOLUME,target=/app/data" \
  -e COOKIE_SECURE=0 -e GOODZ_DATA_DIR=/app/data goodz-audit:ci >/dev/null
for _ in $(seq 1 60); do
  if curl --fail --silent http://127.0.0.1:18080/health >/dev/null; then break; fi
  sleep 1
done
curl --fail --silent http://127.0.0.1:18080/health | grep -q '"ok"'
curl --fail --silent http://127.0.0.1:18080/api/site | grep -q '"settings"'
[ "$(docker inspect "$NAME" --format '{{.HostConfig.ReadonlyRootfs}}')" = true ]
[ "$(docker inspect "$NAME" --format '{{.Config.User}}')" = goodz ]
docker exec "$NAME" python -c "from app.main import connect; from pathlib import Path; p=Path('/app/data/goodz.sqlite3'); c=connect(p); db=c.__enter__(); db.execute('UPDATE settings SET value=? WHERE key=?', ('Docker restart passed', 'hero_title')); c.__exit__(None,None,None)"
docker restart "$NAME" >/dev/null
for _ in $(seq 1 60); do
  if curl --fail --silent http://127.0.0.1:18080/api/site | grep -q 'Docker restart passed'; then
    echo 'Docker PASS: build, loopback, nonroot, read-only, persisted SQLite on restart'
    exit 0
  fi
  sleep 1
done
echo 'FAIL: persistence after Docker restart' >&2
exit 1
