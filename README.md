# Letting AI Formulate the Research Question: Autonomous Research Agents

This repository accompanies the paper *Letting AI Formulate the Research Question: Autonomous Research Agents* (Ko Fujimura, 2026; [arXiv:2610.39620](https://arxiv.org/abs/2610.39620)). It contains the system, the five papers written by the agents, the records needed to reproduce and check them, and the evaluation.

An off-the-shelf coding agent (Codex CLI with gpt-6.1-sol) was given an instruction document and two skills, with no field, topic or template, only a hint toward societal problems that can be studied with open data. In each run it formulated its own research question, ran the study with local computation on a laptop without a GPU, wrote a paper, was reviewed by an AI reviewer from another model family that re-ran the first draft from its records, and submitted a revised paper. The system was frozen after a pilot run; the pilot and four pre-registered runs are reported (the pilot was counted by an amendment to the pre-registration, see `evaluation/`).

## The five papers

The papers were written by the agents and are attributed to "Autonomous Research Agents". Their wording is unchanged from the final versions; we only converted them from Markdown to PDF (`papers/build_pdfs.py`).

| Run | Paper |
|---|---|
| 014 | [Screening one-year tree-cover transitions in CONUS with annual satellite embeddings](papers/run-014.pdf) |
| 015 | [Spatial temperature-exceedance probabilities from ensemble summaries: an empirical partial-identification study](papers/run-015.pdf) |
| 016 | [Revisiting reference locations for changes in Swiss declared crop-group diversity: a resampling benchmark](papers/run-016.pdf) |
| 017 | [Training Point Allocation and Recovery of Small Wetland Patches from Satellite Embeddings](papers/run-017.pdf) |
| 018 | [Do annual satellite embedding distances improve matching of wetland inventory water regimes?](papers/run-018.pdf) |

They are AI-generated research papers, reviewed only by AI. They have not been peer reviewed by people.

## Contents

```
system/        the system as frozen for the evaluation: instructions, skills, operator protocol and
               the script that deploys them (see system/README.md)
papers/        the five papers as PDF, and the conversion script
runs/run-NNN/  the records of each run at its final Git tag (see below)
reviews/review-NNN/
               the in-loop AI review of each run: report (review-1.md), prior expectation, reader value,
               manifest, events, and the reviewer's own scripts and small outputs
evaluation/    the pre-registration, its amendment, the external AI evaluation (E1: procedure, prompts,
               scripts, raw responses, results) and every input sent to the research sessions
               (inputs/run-NNN.jsonl)
preprint/      LaTeX source of the paper and the script that generates its tables from the records
```

### What each run directory contains

Each `runs/run-NNN/` is taken from the run's Git tag `final`. It contains the paper and its Markdown sources, the README and `VERIFY.md` (how to reproduce), the final report, the research log, the plans and topic-selection records (`protocol/`), the code, the logs of events, interventions, claims, API calls and sources, the manifest, the review response (`review/`), figures, experiment records, data-terms notes, requirements, the run's SHA-256 list, and every file that a claim cites as evidence. `GIT_HISTORY.txt` lists the tags and all commits (time, subject, changed files), which shows that plans were committed before the experiments that used them.

### What was left out

To keep the release to what is needed to reproduce and check the runs, the following are not included:

- raw and intermediate data and most saved outputs (satellite embeddings, inventory and weather data, predictions), which the run's code re-fetches from the public sources listed in `sources.jsonl` and the README; the run's SHA-256 list lets you check re-fetched files;
- saved copies of literature and web pages (copyright);
- virtual environments, the reviewers' copies of the runs, and bulk outputs of re-runs.

Each run lists every file left out, with its size, in `EXCLUDED.tsv`.

## Reproducing a run

Follow `runs/run-NNN/VERIFY.md`. In outline: install the pinned requirements, re-fetch the inputs with the run's retrieval code, and run the single verification entry point, which regenerates the tables, figures, the paper's numbers and `claims.jsonl` without calling any AI API. Re-fetching can take hours and needs network access; some inputs are large.

## AI involvement

The five studies were formulated, carried out and written by AI agents; the in-loop reviews and the external evaluation are by AI models. The management agent (Claude Opus 5.5) operated the runs with fixed messages and drafted the paper and this repository from the records. The human author set up the system, made the decisions recorded in `evaluation/`, and is responsible for the release.

## Licences

- **Code — MIT License** (`LICENSE`). This covers the code written by the agents in the runs and reviews, and the scripts in `system/operator/`, `papers/`, `evaluation/e1/` and `preprint/`.
- **Text, records and figures — CC BY 4.0** (`LICENSE-CC-BY-4.0.txt`). This covers the papers, the instructions and skills, plans, logs, reviews, evaluation responses, analysis outputs and figures. Attribution: cite the paper (see Citation).
- **Third-party material keeps its original terms.** Each run records the terms and required credits of the data it used, in its README, `sources.jsonl` and, where present, `DATA_LICENSES.md` (run 016) or `DATA_TERMS.md` (run 018). Nothing in this repository grants rights beyond those terms. In summary, as the runs recorded:

| Run | Third-party data | Terms and credits recorded in |
|---|---|---|
| 014 | LCMAP and NLCD reference labels; AlphaEarth and TESSERA embeddings | `runs/run-014/README.md` |
| 015 | ECMWF Open Data ensemble forecasts; Natural Earth | `runs/run-015/README.md` |
| 016 | SwissCrop25 declarations; AlphaEarth and TESSERA embeddings | `runs/run-016/DATA_LICENSES.md` |
| 017 | US National Wetlands Inventory; AlphaEarth embeddings; Copernicus Sentinel-2 | `runs/run-017/README.md` |
| 018 | US National Wetlands Inventory; AlphaEarth and TESSERA embeddings; JRC Global Surface Water; USGS 3DEP; ASF HAND; Census TIGER/Line | `runs/run-018/DATA_TERMS.md` |

AlphaEarth embeddings are CC BY 4.0: "The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind." For TESSERA embeddings the runs found public licence statements that differ (CC0, CC BY and CC BY-SA); files that contain TESSERA embedding values keep TESSERA's attribution and are treated as share-alike, as the runs recorded, rather than placed under this repository's CC BY 4.0 grant.

## Citation

Please cite the paper ([arXiv:2610.39620](https://arxiv.org/abs/2610.39620)):

```bibtex
@misc{fujimura2026letting,
  title         = {Letting {AI} Formulate the Research Question: Autonomous Research Agents},
  author        = {Fujimura, Ko},
  year          = {2026},
  eprint        = {2610.39620},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  doi           = {10.48550/arXiv.2610.39620},
  url           = {https://arxiv.org/abs/2610.39620}
}
```

`CITATION.cff` gives the same information in machine-readable form.
