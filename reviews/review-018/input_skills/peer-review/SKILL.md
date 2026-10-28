---
name: peer-review
description: Procedure and report format for reviewing a study and paper produced autonomously by another AI agent. Record a prior expectation, read the paper and records, re-run the verification steps on a copy of the submitted commit, check the timeline, evidence, references, novelty, methods, AI API use and safety, assess the value to readers, and write a REVIEW-1 report with scores, a verdict and numbered findings. Use it when reviewing a submitted research directory.
---

# Reviewing an autonomous study

This skill is the review procedure of the Free Research system. Use it together with your review instructions, which give the review ID, the target (research directory and tag), the review directory, the time limit and the permitted operations. "The research instructions" means the instructions the research side worked under, saved in the research directory as input_prompt.md (and input_skills/).

## 1. Prior expectation

Before reading the paper through, read only the title and the research-question section of paper.md, write the following in prior_expectation.md and save it, then obtain the save time with a tool and record it in events.jsonl. Do not rewrite it after saving (if you add to it, state that it is an addition and give the time).
- your expected answer to the research question, and your confidence
- how researchers and practitioners working on this problem would judge the matter at present (concretely)

This is a record for comparing, in section 5, whether the results could be predicted and whether readers' understanding or judgment changes.

## 2. Reading through

Read paper.md, claims.jsonl, VERIFY.md, README.md, protocol/ and research_log.md, and grasp the paper's central claims and the experiments and data that support them. Refer to experiments/, sources.jsonl, events.jsonl and interventions.jsonl as needed. You may also read the research side's self-check before submission (review/self-check.md), but do not take its results for granted; evaluate independently.

## 3. Running the verification

- Copy the submitted commit into the review directory (for example, `git clone --no-hardlinks`, then check out the submitted tag in the copy), and run the steps of VERIFY.md in the copy. Obtain data not in Git by the method in VERIFY.md, or copy it from the research directory into the review directory.
- If a step tries to write into the research directory, stop it and record this as a verifiability finding.
- Do not run steps that call AI APIs; run the steps that recompute results from saved responses. If saved responses alone are not enough for verification, record this as a verifiability finding.
- Verify the paper's central claims (those that appear in the abstract) first. If you cannot run everything within the time, state what you ran and what you did not.
- For each main claim, run the verify procedure in claims.jsonl, compare the value obtained with expected, and record the result as "match / mismatch / could not run / not done". For mismatches and could-not-run cases, add your view of the cause.
- If you ran only a reduced version of a procedure, state that it was reduced.
- Save in verification/, for each verification, the commands run, start and end times, exit codes, stdout/stderr and output files.

## 4. Checking the research process and the grounds

- Timeline: Compare the Git history with events.jsonl, and check whether the commit of each plan precedes the experimental results based on it, whether the plan and code commit IDs written in the experiment records exist, and whether metrics, exclusions and hypotheses decided after seeing the results are distinguished as exploratory. Also check whether the abstract distinguishes results planned in advance from exploratory results. Git times are self-reported and do not prove the absence of tampering. Write conclusions such as "no contradiction was found", and do not write "proved correct".
- Correspondence of evidence: Check whether the evidence_paths in claims.jsonl exist, and whether the numbers in the paper match the values in the output files. A sample check rather than a full check is acceptable, but record the targets and the number checked.
- References: For prior work that underpins the novelty or the central claims, check that it exists and what it says. For the rest, a sample check is acceptable. Treat non-existent literature, or citations that misrepresent the content, as critical findings.
- Novelty: Search yourself, and point out close prior work that the paper does not mention. Also check, in primary sources other than papers (published implementations and tools, bug reports, specifications, etc.), whether the facts have already been reported. Check whether standard methods or classic studies of the field are missing from the paper. Check whether the same problem has been studied under a different name in other fields, and whether facts already known from official statistics, reports or white papers are treated as discoveries. Distinguish "not found within the range searched" from "does not exist".
- Methods: Check problems such as the validity of comparison conditions, sample size, multiple comparisons, data leakage, and the evaluator being the same as the subject.
- Representativeness of the targets: Do the targets studied (tools, versions, data, models, settings, etc.) represent the scope of the paper's claims? If the claims go beyond the range studied, point this out as an "overclaim".
- Alternative explanations: Could the results be explained not by the factor the paper claims but by ceilings or floors of the measurement, how the targets or settings were chosen, or the definitions of the tasks or conditions themselves? Are results that could be predicted without experiments treated as findings? If such conditions apply, also check whether the research side counted the cases and showed them in the abstract and the results.
- Proposals of tools or methods: Check that the paper states that the evaluation is limited to reproduction on public data or case examples, and that it does not claim effects on users.
- AI API use: If the research side used AI APIs, check whether this follows research instructions §2.3. Specifically, check whether the use is limited to measurement (subjects, embeddings, evaluators planned in advance) and not used for research work such as writing code, writing text or reading literature; whether the records in api_calls.jsonl correspond to the saved responses and all responses used in the analysis are in the records; whether the actual cost is within the budget; and whether the plan contains a prior estimate. If you find the value of a key in the research directory, point out only its location without writing the value.
- Safety and ethics: Check whether content falling under research instructions §12 is handled as that section prescribes. For studies handling social data, also check §12.5 (terms of use of the data, identification of individuals, treatment of organizations and regions, separating value judgments from the data).

## 5. Value to readers

After reading through and verifying, write the following in reader_value.md.
- Compared with your expectation in section 1, which parts of the results were as expected and which differed, and why
- Which understanding or judgment of the intended readers this study could change, the claim_ids that support it, and how far you trust those claims given the verification results
- Whether the abstract is accurate in light of the text and the verification results, and whether it overgeneralizes
- If nothing changes, or everything was as expected, write that as it is

This is a self-report, not a measurement of actual changes in behavior. State this limitation.

## 6. Writing the review result

Write the review result in review-1.md in the following format. The first line must be "REVIEW-1". The research side receives a message beginning with this line as the review result.

```
REVIEW-1
- Review ID:
- Target: tag, commit ID
- Reviewer's model: identifier confirmed from the execution environment / name given in the conversation (write them separately)
- Review period: start and end times (UTC), excluded usage-limit stop time
- Scope of verification carried out:

## 1. Summary of the paper
What the paper claims, in 3–5 sentences.

## 2. Overall verdict
One of Accept / Minor revision / Major revision / Reject, with 2–4 sentences of reasons.

## 3. Scores (1–5, one line of reason each)
- Correctness of claims
- Verifiability
- Novelty
- Generality (whether it holds beyond the targets studied; whether the targets studied represent the scope of the claims)
- Usefulness to readers (whether it changes the understanding or judgment of researchers and practitioners working on the problem)
- Clarity (including the explanation of background and importance, the use of terms, and whether the abstract and text are not overloaded with exploratory results)

## 4. Verification results
| claim_id | Claim (shortened) | Procedure run | Result | Record path |

## 5. Findings
### R1-1
- Severity: Critical / Moderate / Minor
- Type: Error / Insufficient evidence / Overclaim / Unverifiable / Inconsistent records / Insufficient description / Suggestion
- Target: file, section, claim_id
- Content: write the observed facts (with the run results or record paths) separately from the inferences drawn from them
- Requested action: concretely
- Feasibility of the action: can be done within the research environment / cannot be done because of environment constraints

## 6. Value to readers
Summary of reader_value.md.

## 7. Points that can be supported

## 8. What could not be confirmed / limitations of this review
```

Notes on writing:
- List the findings in descending order of severity, numbered consecutively from R1-1. Always give grounds for critical findings.
- When you ask for additional experiments or analyses, limit them to what the research side can run within 2 hours, with local compute and public data, using only permitted operations, and give priorities.
- For problems that cannot be addressed because of the research side's environment constraints (models, data or resources that are not available, etc.), do not ask for additional experiments; ask instead that the claims be narrowed to the range studied and that this be stated in the limitations. Do not lower the severity because a problem cannot be addressed. The research side's environment can be checked in the research directory's input_prompt.md.
- Do not ask for a change of research topic or propose a different study. The scope of the review is the submitted study.
- State clearly which claims can be supported.
- Do not write that you ran a verification you did not run. Describe your own re-run not as an "independent reproduction" but as "a re-run by another agent on the same machine".
- Do not rewrite the research side's paper or records. Write proposed corrections within the findings.
