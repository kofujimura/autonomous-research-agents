# Output hash scope

`OUTPUT_SHA256.jsonl` contains one scope record followed by a SHA-256 and byte length for each included regular file. Paths are relative to the research bundle. It includes original/raw predictor clips, references, selected-position/proposal/weight data, every saved prediction array (including arrays outside Git), original AI requests/responses, source/protocol records, failed-run logs, analysis outputs, figures, manuscript/report files, submission snapshot copies, and newly generated self-verification measurements/logs.

Excluded: Git internal storage; the dedicated environment; package/plot caches and Python bytecode; regenerable `data/derived/features/*.npz` feature-matrix caches; duplicated selected working-copy inputs under `verification-work/*/input/`; automatic verification output caches; and the hash lists themselves. Symbolic links are not separately hashed: original probability files are included at their actual bundled paths, and selected-copy links point to those same bytes. This exclusion does not discard raw self-rerun measurements under `verification-work/*/output/`.

The root list refers to files prepared for the final snapshot; the archived first-draft list remains under review/submission-1/. Git commit/submission receipts must be appended to the working event log after the commit exists. To check tracked files in that snapshot together with bundled files outside Git, use:

```sh
python code/check_hashes.py --revision final
python code/check_hashes.py --revision submission-1 --list review/submission-1/OUTPUT_SHA256.jsonl
```

On a full archive of the tagged tree supplemented with the included non-Git files, omit `--revision`. A numerically minimal verification input copy deliberately omits many files unused by the offline calculation; use `VERIFY.md` there rather than expecting it to contain the entire output-hash scope.

Hashes establish byte agreement with the listed snapshot. They do not prove truth, independence, completeness, absence of tampering or an external timestamp. Retain the directory and local Git history. No external publication is implied.
