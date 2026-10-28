#!/bin/sh
# usage: tlimit.sh SECONDS cmd args...  (SIGALRM after SECONDS; 30-minute run limit)
s="$1"; shift
exec perl -e 'alarm shift; exec @ARGV or die "exec failed: $!"' "$s" "$@"
