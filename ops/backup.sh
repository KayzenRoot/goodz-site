#!/usr/bin/env bash
# Run from the release directory with its Compose project and restic environment.
set -Eeuo pipefail
umask 077
: "${RESTIC_REPOSITORY:?configure an encrypted off-host restic repository}"
: "${RESTIC_PASSWORD_FILE:?specify the protected password-file path}"
: "${GOODZ_BACKUP_TMP:?specify a private staging directory on encrypted storage}"
exec 9>"$GOODZ_BACKUP_TMP/backup.lock"
flock -n 9 || exit 1
stage=$(mktemp -d "$GOODZ_BACKUP_TMP/snapshot.XXXXXXXX")
restart=0
cleanup() {
    local result=$?
    if (( restart )); then docker compose start site >&2 || result=1; fi
    rm -f -- "$stage/goodz.tar"
    rmdir -- "$stage"
    exit "$result"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
test -n "$(docker compose ps --status running -q site)"
restart=1
docker compose stop site
docker compose run --rm -T --no-deps site sh -ec \
    'cd /app/data; test -s goodz.sqlite3; test -d uploads; tar -cf - .' > "$stage/goodz.tar"
docker compose start site
restart=0
restic backup --tag goodz --stdin --stdin-filename goodz.tar < "$stage/goodz.tar"
