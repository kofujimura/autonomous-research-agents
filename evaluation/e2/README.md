# E2: ratings by human researchers

E2 is the human evaluation planned in `../preregistration.md` (Evaluation). Three researchers in computer and information science, H1–H3, rated the five final papers: the same PDFs as in E1 (`../../papers/`). E2 is reported in the journal version of the paper, prepared for IEICE Transactions on Information and Systems (`../amendment-2.md`). arXiv v1 does not include it.

The individual responses are not released. The raters were told that their answers would be reported in aggregate, under codes such as H1 and without their names. The numbers are reported in the paper.

## The rating form

`form/` holds the rating site as the raters used it (form v1.0, in Japanese):

- `index.html`: the request, the conditions and the procedure;
- `app.js`: the items, the reading order, and saving and exporting the answers;
- `style.css`: the page style.

These are the files of commit `b368dd1` of [kofujimura/autonomous-research-agents-e2](https://github.com/kofujimura/autonomous-research-agents-e2). From 2026-11-03 they were served at https://web.fujimura.com/autonomous-research-agents-e2/ (GitHub Pages). The site also served the five PDFs under `papers/`. They are the same files as `../../papers/` and are not copied again; to open them from a local copy of the form, copy them into `form/papers/`.

| File | SHA-256 |
|---|---|
| `form/index.html` | 57a6240b029892a2dda6f43b1ce02f5c05821de5a3a4b483c9bc7cb53bc31bfa |
| `form/style.css` | 6a8ad134789860e547e11a2e563ecdca48aafb8ff24549560e94cfabfd505569 |
| `form/app.js` | ef788c3d0d3b11f0a978146f78c1367e9e1fb3882e11f0418dba92fb847fd093 |

### Conditions given to the raters

These were on the site. The request e-mail gave the site's address, the rater ID and the deadline, and repeated conditions 5 and 6.

1. The papers were written by an autonomous AI research system. Rate the research, not who or what wrote it.
2. Rate each paper on its own, not by its rank among the five.
3. Web search may be used to check prior work, novelty and facts in the paper. Distinguish "not found in my search" from "does not exist".
4. Do not obtain the code, data or records the papers mention. Judge correctness and verifiability from what the paper reports.
5. Until the answers have been sent, do not look at the paper on the research that produced the five papers, or at its public repository, because they contain the AI ratings.
6. Do not discuss the papers or the ratings with the other raters.

### Items for each paper

Fifteen items were required (marked \*). The rest were optional.

- **Before reading:**
  - self-rated expertise in the paper's field\* (1–5: 1 knows little about it, 3 researcher in a related field, 5 expert in the field);
  - whether the rater had read or seen the paper before\*, and if so, where.
- **The six axes of E1\***, each 1–5, with an optional one-line reason: correctness, verifiability, novelty, generality, usefulness and clarity. The definitions are translated from `../e1/prompt-pdf.md`.
- **Overall judgments:**
  - verdict\* (accept, minor revision, major revision, reject);
  - overall score\* on the ICLR scale (1–10), rating the paper as a full paper at a strong peer-reviewed venue of its field;
  - workshop level\*: would it be accepted at a peer-reviewed workshop of the field (acceptance about 70%)?
  - main-track level\*: would it be accepted at the main track of a top conference of the field (acceptance about 25–30%)?

  The two levels are answered yes, borderline or no.
- **The research question:**
  - the paper's main research question, in one sentence;
  - the quality of the question\* (1–5): its importance and sharpness, apart from how well the study was carried out;
  - whether the main answer was predictable\* (yes, partly, no): could it be roughly foreseen, before the study, from its design, its definitions and how its data were made? An optional reason follows.
- **Text:** a summary; critical, moderate and minor issues (up to eight in all); strengths (up to four); the closest prior work (up to five); comments.
- **Last:** whether the rater looked at the figures and tables\*; the time taken, in minutes.

### Reading order and answers

The reading order is a fixed function of the rater ID (`orderFor` in `app.js`). It was recorded before the requests were sent:

| ID | Order of runs |
|---|---|
| H1 | 017, 015, 014, 016, 018 |
| H2 | 016, 017, 018, 015, 014 |
| H3 | 015, 018, 014, 016, 017 |

The answers stayed in the rater's browser. Each rater exported them as a JSON file and sent it by e-mail. The `review` part of the file uses the field names of E1 (`../e1/schema.json`), with two differences: `closest_prior_work` is free text, and text answers may be in Japanese.

## Summary method

The method was fixed on 2026-11-03, before any rating had arrived. The calculation was not changed afterwards.

- **For each paper:**
  - the raters' mean on each axis;
  - each rater's expertise, overall score, verdict, and workshop and main-track levels, next to the E1 values.
- **Over all ratings (raters × papers):**
  - the mean on each axis;
  - the mean and range of the overall score;
  - the numbers of yes, borderline and no for the workshop level and for the main-track level;
  - the number of each verdict;
  - the mean quality of the question, and the numbers of yes, partly and no for predictability;
  - the number of ratings in which the rater had seen the paper before;
  - the median expertise;
  - the median time, where given.

No statistical test and no measure of agreement between raters is computed. Text answers are neither quoted nor summarised in the results.

## Record

- **2026-10-26, `../preregistration.md`:** E2 is to be done by the author and 2–3 Japanese colleague researchers. The form and the procedure are to be fixed before any colleague reads a paper. The author's ratings are to be reported separately.
- **2026-10-28, `../e1-procedure.md`:** E2 is to be reported in a separate paper.
- **2026-11-03:**
  - Form v1.0 was published.
  - `../amendment-2.md`: E2 is reported in the journal paper, under reporting rules fixed before any rating existed.
  - `../amendment-3.md`: the author does not rate the papers.
  - The requests were sent. The deadline in the request e-mail was 10 November 2026.
  - Five researchers were asked. The first two asked as H1 declined, and H1 was then asked of a third. H1, H2 and H3 agreed.
  - The summary method was fixed (above).
- **2026-11-09:** the ratings of H1 and H3 had arrived, before the deadline. The management agent opened them and reported a summary to the author: the mean overall score, the workshop-level judgments, the verdicts and the self-rated expertise.
- **2026-11-11, `../amendment-4.md`:** H2's ratings had not arrived by the deadline. They are to be used if they arrive by the first submission.
- **2026-11-20:** H2's ratings arrived.
- **2026-11-21:** `../amendment-4.md` was completed (§5), and its SHA-256 was recorded before H2's file was opened.

### Response files (not released)

| Rater | File | SHA-256 | Exported (time in the file) |
|---|---|---|---|
| H1 | `e2-H1-20261109-1317.json` | 278fe47042000af1529d4b095ba9412e3e18ee331f841f4b9f6398d5e61aabda | 2026-11-09 13:17 JST |
| H2 | `e2-H2-20261120-1347.json` | 2b9588af1eefec2de872d61e8cbf9223fc1da1f88a0ee198032212f755518a88 | 2026-11-20 13:47 JST |
| H3 | `e2-H3-20261108-1606.json` | cfad9f134586ea05f48fa475eda1689295187d5229992140924bdb672faaf428 | 2026-11-08 16:06 JST |

## Deviations from the plan

1. **The deadline and the confirmations.**
   - What was planned:
     - `../amendment-2.md` §4 left the request deadline blank, to be filled in before the first request was sent.
     - §1 of amendments 2 and 3 asked the author to confirm, before then, that no researcher had yet been asked.
   - What happened:
     - Neither was recorded before the requests were sent.
     - Shortly after sending them, the author reported that no rating had arrived yet. The author gave the deadline afterwards.
   - So both amendments were written before any rating existed. Whether they were written before the requests were sent is not known, because the time of sending was not recorded.
2. **H2's late ratings.**
   - H2's ratings arrived after the request deadline. Under `../amendment-2.md` §4 they would not have been used in the first submission.
   - `../amendment-4.md` let them be used. It was written after the author had seen the summary of H1's and H3's ratings, and before H2's ratings had arrived.
3. **What the paper states.**
   - What was planned: the amendments said the paper would state
     - that E2 was first planned as a separate paper (`../amendment-2.md` §4);
     - that ratings by the author were planned and then dropped (`../amendment-3.md` §4);
     - the request deadline, the date H2's ratings arrived, and amendment 4 (`../amendment-4.md` §4).
   - What the paper does: it states none of these. It reports the three researchers' ratings as one set and does not treat H2 differently. This follows the author's decisions of 21 and 22 November 2026 (`../amendment-4.md` §5).
   - The history is recorded here instead.
