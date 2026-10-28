#!/bin/sh
# End-of-review target state check (same as start)
R=/Users/fujimura/Research/ai-free-research-en/run-018
V=/Users/fujimura/Research/ai-free-research-en/review-018/verification/state
cd "$V"
{
echo "observed_at_utc: $(date -u +%FT%TZ)"
echo "HEAD: $(git -C $R rev-parse HEAD)"
echo "tag submission-1 -> $(git -C $R rev-parse 'submission-1^{commit}') (tag object $(git -C $R rev-parse submission-1))"
echo "git --no-optional-locks status:"
git -C $R --no-optional-locks status
echo "events.jsonl diff vs HEAD (line counts):"
git -C $R --no-optional-locks diff --stat
} > end_state.txt 2>&1
../tlimit.sh 1700 python3 -I check_sums.py $R $R/review/submission-1/SHA256SUMS end_sha_check.json > end_sha_check.stdout 2>&1
echo "sha_exit=$?" >> end_state.txt
cat end_state.txt; cat end_sha_check.stdout
