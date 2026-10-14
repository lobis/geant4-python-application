#!/bin/sh
# CMAKE_CXX_LINKER_LAUNCHER for macOS CI: Apple's linker occasionally crashes
# with a segmentation fault on GitHub's runners; a second attempt succeeds.
i=1
while :; do
    "$@" && exit 0
    status=$?
    [ "$i" -ge 3 ] && exit "$status"
    echo "retry_link.sh: link failed (exit $status), retrying" >&2
    i=$((i + 1))
done
