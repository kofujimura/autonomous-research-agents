You are an expert peer reviewer. Review the research paper given below.

Context and rules
- This paper was produced by an autonomous AI research system: an AI agent chose the question, ran the study and wrote the paper. Judge the work on its merits as research, not on who or what wrote it.
- The paper is given below in Markdown. The figures it references are attached as images, in the order listed under "Attached figures".
- You may use web search to check prior work, novelty and factual statements in the paper. Distinguish "not found within the range searched" from "does not exist".
- Do not try to obtain the paper's own code, data or records, even if the paper mentions them. You cannot re-run the study. Assess correctness and verifiability from what the paper itself reports and describes.

What to assess (score each 1–5, 5 = best; give one line of reasoning each)
1. correctness: Correctness of claims. Are the main claims supported by the evidence reported in the paper? Are the analyses and interpretations sound?
2. verifiability: From the paper's description, could others check or reproduce the results (data, code, procedures, records, reported details)?
3. novelty: Is the contribution new relative to prior work? Is the novelty claim appropriate? Point out close prior work that the paper does not mention.
4. generality: Whether it holds beyond the targets studied; whether the targets studied represent the scope of the claims.
5. usefulness: Usefulness to readers: whether it changes the understanding or judgment of researchers and practitioners working on the problem.
6. clarity: Including the explanation of background and importance, the use of terms, and whether the abstract and text are not overloaded with exploratory results.

Also give
- verdict: one of "accept", "minor revision", "major revision", "reject".
- overall_10: an overall rating on the ICLR scale (1 strong reject, 3 reject, 5 marginally below the acceptance threshold, 6 marginally above the acceptance threshold, 8 accept, 10 strong accept), judged as a full paper at a strong peer-reviewed venue in the paper's own field.
- workshop_level: would this paper be accepted at a peer-reviewed workshop in its field with an acceptance rate around 70%? ("yes", "borderline", "no")
- main_track_level: would it be accepted at the main track of a top venue in its field (acceptance rate around 25–30%)? ("yes", "borderline", "no")
- research_question: restate the paper's main research question in one sentence; rate question_quality 1–5 (importance and sharpness of the question itself, independent of execution); and say whether the main answer was largely predictable before running the study from its design, definitions or how the data were produced ("yes", "partly", "no"), with one line of reasoning.
- main_issues: the most important problems, each with severity "critical", "moderate" or "minor" (at most 8).
- strengths: up to 4.
- closest_prior_work: up to 5 items of the closest prior work you know or found, each with a citation, a URL if you have one (empty string otherwise), and one line on how this paper differs.
- familiarity: do you recognize this specific paper, or know where it came from? Answer honestly in one line ("no" if not).
- figures_viewed: whether you looked at the attached figures.

Return only one JSON object with exactly these fields: summary, scores, score_reasons, verdict, overall_10, workshop_level, main_track_level, research_question, main_issues, strengths, closest_prior_work, familiarity, figures_viewed. Write all text fields in English.
