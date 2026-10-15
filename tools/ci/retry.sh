#!/bin/sh
# Run a command, retrying with a growing pause if it fails. CI downloads from
# GitHub, python.org and conda occasionally fail with 5xx errors or timeouts.
# Usage: retry.sh <command> [args...]   (RETRY_ATTEMPTS overrides the default 5)
attempts=${RETRY_ATTEMPTS:-5}
i=1
while :; do
    "$@" && exit 0
    status=$?
    if [ "$i" -ge "$attempts" ]; then
        echo "retry.sh: giving up after $i attempts: $*" >&2
        exit "$status"
    fi
    echo "retry.sh: attempt $i failed (exit $status), retrying: $*" >&2
    sleep $((i * 20))
    i=$((i + 1))
done
