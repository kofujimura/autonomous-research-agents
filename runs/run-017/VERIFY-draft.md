# Verification procedure — in progress

This is a procedure draft, not a completed verification claim. Expected numeric values and a timed clean-copy rerun will be added after the experiments. `VERIFY.md` will be the submission entry point.

Verify on a copy of the submitted Git commit, in a new working location. The input copy is treated as immutable. Install `requirements.lock.txt` in a dedicated virtual environment in a separate working directory, with its package/matplotlib caches there. Use Python 3.13 (the development environment is macOS arm64; platform differences in optional raster rebuilding/refitting are not promised bitwise identical).

The offline entry point is:

```
PYTHONDONTWRITEBYTECODE=1 /path/to/verification-env/bin/python /path/to/input-copy/code/verify.py --out /path/to/new-output-directory
```

The output directory must not already exist and must be outside the input copy. This regenerates evaluated thresholds, per-core confusion counts, patch coverage, tables, paired block-bootstrap contrasts, allocation audits and inventory counts from bundled predictions and references. It compares frozen expected values with tolerance 1e-12. No AI API or network access is used. `verification.json` records the outcome and elapsed time; per-step stdout/stderr are written only to the output directory. The wrapper has a 1700-second internal deadline.

New large probability arrays are bundled beside Git to avoid duplicated storage. After making the commit copy, supplement it using:

```
python /path/to/input-copy/code/copy_large_inputs.py --bundle /path/to/research-bundle --copy /path/to/input-copy
```

The script copies precisely the arrays referenced by completed fit metadata in that commit and checks their recorded SHA-256 before and after copying. It preserves a differing existing file by stopping. Already-tracked probability arrays remain in Git. The session's own end-to-end rerun may use `--reuse-read-only` to link these immutable inputs into a new code/input working location within the 10 GiB storage limit; that shares input bytes and is not an independent data copy. In either mode the verification program writes only to its separate output directory. All raw prediction arrays, including those outside Git, remain covered by the final hash list.

Raw clipped predictor inputs and their source metadata are bundled for optional feature rebuilding. Feature-matrix NPZ files are regenerable caches excluded from Git. Rebuilding features and refitting classifiers are optional, separate checks on a writable copy; they are not required to recompute the reported results from saved measurements. A new API request is neither necessary nor expected to reproduce the candidate critic's answer.

Timeline inspection: initialization, topic selection, protocol v1–v4 and implementation/code commits precede their dependent batches, with the original E03 provenance mistake explicitly preserved in its correction file. Inspect `events.jsonl`, each `experiments/*/run.json`, the local Git log, `protocol/deviations.jsonl` and `protocol/implementation-clarifications.md`. Git dates are self-reported records, not proof against tampering.
