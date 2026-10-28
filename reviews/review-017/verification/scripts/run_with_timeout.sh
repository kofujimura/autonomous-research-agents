#!/bin/sh
# usage: run_with_timeout.sh SECONDS cmd args...  (uses perl alarm; macOS has no coreutils timeout)
secs="$1"; shift
exec perl -e 'alarm shift @ARGV; exec @ARGV or die "exec failed: $!"' "$secs" "$@"
