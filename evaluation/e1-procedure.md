# Evaluation phase: E1 procedure (fixed before the first review)

Written 2026-10-28T12:20Z, before any E1 review request was sent. The decisions are the human author's (2026-10-28); the management agent wrote this text and the files. Full procedure (Japanese): `../e1-eval/README.md`.

## Decisions

- E1 only, for a first preprint. The human evaluation (E2) is done separately and reported in a separate paper.
- No comparison with The AI Scientist-v2: the researcher models differ, and the period of the cited literature and a web search would reveal which system wrote a paper, so a blinded comparison is not possible.
- Absolute rating of the five final papers of run-014 to run-018 (tag `final`), unchanged, with their figures. First drafts are not rated.
- Reviewers: Gemini 4 Argon (Google) and Muse Wonder (Meta). The researcher is a GPT model, so this meets §6 of `preregistration.md` (at least two model families).
- The reviewers see only the paper and may use web search. They are not given the run's code, data or records (no artifact check).
- Two independent reviews per paper and reviewer. Order: review 1 of all five papers, then review 2.
- Budget: USD 10 per reviewer. A review is not sent when the expected cost would exceed the budget; papers left with one review are reported with n = 1.

## Files (SHA-256)

| File | SHA-256 |
|---|---|
| `e1-eval/README.md` | 5251506ca6c084dd813b24dbcb8e6ef6704c0e8cf429addcf5eb91d3fff47e20 |
| `e1-eval/prompt.md` | 6b4bd2694447cbac3e946633ef22d0d925f411594d6274dd8cebe973d94abade |
| `e1-eval/schema.json` | e26aa180df04a60c814b8c0426518f517c851666318d4bf9a4f61065a058e7bc |
| `e1-eval/prepare.py` | 9313b8662f31b9565d2a04e4c653c511d74ac7ee6bd1ed0f8670a90d99bebb33 |
| `e1-eval/run_e1.py` | 2da1fc0c9fa60155a9d23686998eee250fae79f03af23b50ac65c8b8c66e0479 |
| `e1-eval/bundle/manifest.json` | 1cc27a8694d443487c77b82012f60f408540a08b25d192eced8d1531dcaf327c |

## Pending at the time of fixing

- The Muse Wonder call (request format, the highest reasoning setting, the web-search tool and prices) is to be filled in `run_e1.py` from Meta's official documentation before its first review. The prompt, schema, papers and budget do not change. The change and the new SHA-256 of `run_e1.py` will be appended below.

## Changes after fixing

- 2026-10-28T12:20Z, before any review was sent: the first start stopped because `run_e1.py` did not accept the `export ` prefix in the key file. The key reader was fixed (one line); nothing else changed. New SHA-256 of `run_e1.py`: cbc6108599da247f60352dd738d27f45fba4692fd4bf5e450d623d96a7b7c08c.
- 2026-10-28T12:22Z, while the Gemini reviews were running (the running process had already loaded the earlier file): the Muse Wonder call was filled in from Meta's official documentation (dev.meta.ai: overview, models, pricing-rate-limits, reasoning, search-grounding, image-understanding), as planned above. Responses API in background mode with polling; `reasoning.effort` "max" (allowed values minimal, low, medium, high, xhigh, max); `max_output_tokens` 128000; tool `web_search` with `include: ["web_search_call.results"]`; output format `json_schema`, with the same fallback as Gemini (schema in the prompt) if the API rejects the combination; images as base64 `input_image`. Prices: input USD 4, cached input 0.20, output 20 per million tokens; search USD 2.50 per 1,000 queries. Output tokens, including reasoning tokens, are counted at the output price. An optional limit on the number of reviews sent per start was added, so that the cost of the first Muse review can be checked before the rest. The Gemini path is unchanged. New SHA-256 of `run_e1.py`: f632b0b34a7db3adbc49ecda9fcf9f9fc8ce216c27eef7432cc861fc623b59dc.
- 2026-10-28T13:23Z, after the ten Markdown reviews by Gemini 4 Argon had been completed and read (all ten passed the schema; USD 2.03): the human author decided (2026-10-28) to publish the five papers as arXiv-style PDFs (author "Autonomous Research Agents", on GitHub) and to have them reviewed again in that form. Changes:
  - The five papers were converted from Markdown to PDF without changes to the wording (`papers-pdf/build_pdfs.py`, SHA-256 1fd67e408d23d27f69bcb1010f74b497e485158bcc7c03898aa79fed8ece8215; pandoc 3.12.1 and XeLaTeX). The title and abstract were moved into the title block, the one-line note between them into the title footnote, and the footnote states the run, the tag and commit, and the conversion. PDFs: run-014.pdf `7f050169441b485f1898f46fd26c5032472f125156f6dfc93725104571eec579`; run-015.pdf `f417ac6b8dc0c98bb87c1065b2f2e630f68042dd2355e475b547bd8477c3884c`; run-016.pdf `6080e5e8c7c61772db85e8b533204faa5d8445feea0faf21f9935960003e4ebe`; run-017.pdf `976584879e22a1fa536e7f1f68ee3acd3e6b53719d2787f73dfd2ae7ae5a0f93`; run-018.pdf `f420451e045d6d85b79445fbdd907d3aa90ba2e01abc03ba14cdee7c7e9ea57b`;
  - `prompt-pdf.md` (SHA-256 f3d2369113736cd4a7ffebe8ec2315ac9cb83b12f6e555b3678b001d1ebbb18b) is `prompt.md` with one sentence changed: the paper is attached as a PDF including its figures and tables, instead of Markdown text with figures as images.
  - Reviewers on the PDFs: Gemini 4 Argon (reviewer key `gemini-pdf`, two reviews per paper) and Muse Wonder (`muse`, PDFs only; it has not reviewed the Markdown). The Muse PDF is sent as an `input_file` with a base64 data URL; this form follows the OpenAI-compatible Responses API and was not found in Meta's documentation, so it is checked on the first Muse review.
  - The budget stays USD 10 per reviewer model, now counted across the Markdown and PDF reviews.
  - Reporting: the PDF reviews are the main E1 result, because the PDFs are the published form and both reviewers read the same input. The ten Markdown reviews are reported as well. This choice was made after the Markdown results had been seen.
  - New SHA-256 of `run_e1.py`: 80592ac39938dfa29f647138c234da2d2157fdb6cb5cba02c7c99d17ac5af5f2.

- 2026-10-28T13:24Z: the first start of `gemini-pdf` sent nothing (the call function was looked up by reviewer name; ten failed entries with zero cost in `runs.jsonl`). Fixed by looking it up by model (one line). New SHA-256 of `run_e1.py`: 63eee143500ae6751755af17b79e0e0f0765d238c98e076727cd835671148dc8.
- 2026-10-28T13:54Z, after the five first-round Muse reviews (USD 6.55; one review per paper): the human author raised the Muse Wonder budget to USD 20 (2026-10-28, "$20に上げて2回目も実施してください") so that every paper gets two Muse reviews, as for Gemini. The Gemini budget stays USD 10. New SHA-256 of `run_e1.py`: de6525afaea5fc7a5bedba9124ed4062273ebe72a276e718eb798be470ab0d4c.
- 2026-10-28T14:38Z: E1 complete. 20 reviews on the PDFs (Gemini 4 Argon 10, Muse Wonder 10) and 10 on the Markdown (Gemini 4 Argon), all valid. The last Gemini PDF review (run-018, review 2) was first refused with HTTP 402 (prepaid credits depleted, no cost) and sent again after the human topped up the credits. Costs: Gemini USD 4.31 (Markdown 2.03, PDF 2.28), Muse USD 12.83. Summary: `e1-eval/results.md` (analyze.py).
