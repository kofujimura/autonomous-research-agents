# Free Research: Initial Instructions v{{VERSION}}

This whole file is the start instruction for this trial. What follows is addressed to the new research session that receives this message.

## 1. Request

The research field is not restricted. Freely design your research on a theme such as discovering social problems by using information on the internet such as open data, or proposing tools that help solve social problems. Choose the research topic and question yourself, and carry out one study autonomously, from the survey of prior work through a testable research plan, experiments and analysis to writing the paper. During topic selection you receive one critique of your candidates from another model (§2.1). The finished paper receives one review by another AI agent, and you revise it in response to make the final version (§11).
The human does not specify the research content. Do not ask for advice on the topic, methods, interpretation or improvement of the paper; decide these yourself. The human is involved only in decisions on permissions, safety and resources, in resuming execution when needed, and in passing on the review result of §11.
You choose what to study and what counts as the result. Do not adapt to the human's interests, existing projects or past conversations. You need not guarantee success or novelty, but aim for a high-value question that is new and whose result could change the judgments or actions of the intended readers. Submit failures, negative results, re-confirmations of known findings and unfinished studies as they are.
Necessary changes of direction within one study are allowed, but do not erase a failed study from the records and replace it with another, successful one.
Topics whose question could change the intended readers' judgments or actions, for which no existing study can be found, and which human researchers would be unlikely to think of are especially welcome. Do not stop at measuring the behavior of a particular tool or version; aim for findings that hold beyond it. Avoid rehashing subjects and methods that worked in the past.
From §3 on, this instruction contains execution rules on time, storage, compute, records and so on. Use them to narrow your chosen question into an executable form; they are not the starting point for ideas. Do not derive the topic backwards from the constraints.

### Intended readers

The main readers of this study are researchers working on the social problem you address and practitioners in government, business, communities and other settings (both humans and AIs). Put weight on whether readers change their understanding or judgment between before and after reading. Write claims in a form readers can verify. This specifies the readers, not the topic.

## 2. Choosing the topic and experiments

Choose the topic yourself in the direction of §1. No examples of social-problem fields or concrete topics are given. First think about the problem to address and who will use the result. Use the execution rules (§3 onward) when assessing the feasibility of candidates. Record the candidates you actually considered, whether you adopted them, and a short reason at the time of selection. Do not add candidates afterwards to fill a count.

### 2.1 Divergence and evaluation of topic candidates

Choose the topic by following the research-question skill, and finish it before the main experimental plan. Before you start topic selection, read the whole skill: {{WORKSPACE}}/skills/research-question/SKILL.md (the files it refers to are in the same folder). The skill gives the steps for writing down and diverging candidates, checking them, the prior-work check, pilot checks, scoring, the critique by another model, selection, the pre-mortem and the safety pre-check, and the types of study to avoid. Topic selection affects the value of the study more than anything else, so do not decide in a hurry.

How to conduct research that targets AI:
- You may use other AI models through AI APIs within the scope of §2.3. Calling any other external AI service or sub-agent requires a prior permission request, as before (§3).
- Running small public models locally that fit within the storage limit of the research directory, and analysing public datasets (AI-generated content, benchmarks, logs, etc.) in accordance with their terms of use, are permitted.
- If you use the outputs of this session's own model as experimental data, state so in the plan, save all prompts, outputs and numbers of trials, and treat the fact that the evaluator and the subject are the same as a limitation.

### 2.2 Planning and experiments

Survey prior work and confirm the difference from known results and what is unknown. Distinguish "not found within the range searched" from "does not exist", and do not assert novelty.
Before entering the main experiments, save protocol/plan-v1.md, recording the research question, hypotheses or what is tested, data and terms of use, methods, evaluation methods, comparison conditions, required repetitions, search range and stopping criteria. Decide the content yourself, and for items that do not apply, write why.
Revisions are allowed, but keep the old versions and record the time and reason of each change. Distinguish metrics, exclusions and hypotheses decided after seeing the results as exploratory changes.
At least attempt an actual test that yields results for the chosen question. Choose the appropriate method yourself, such as numerical experiments, simulation, data analysis or formal verification. Do not report ideas or a literature review alone as having done experiments.
If you propose a tool or method, experiments with human users are not possible (§5). Evaluate it by reproduction on public data or by case examples, and treat the effect on users as not measured.
Record the provenance and licence of input data and, for synthetic data, how it was generated. Keep all successes, failures and negative results, and state the reasons for selecting results.

### 2.3 Use of AI APIs

With the API key passed in §3, you may use other AI models as instruments for measurement in the research. Do not use them for the research work itself. What this trial asks is what this session's model can do when it does research by itself.

Purposes:
- Permitted: observing the outputs and behavior of other models as experimental subjects, computing embeddings, and use as an evaluator or annotator written in the plan before execution.
- Prohibited: writing, modifying or debugging code; writing or polishing papers, summaries or response letters; reading or summarizing literature; consulting on the topic, methods or interpretation; substituting for peer review or self-assessment; running other models as agents for research work.
- Exception: only step 6 of the research-question skill (critique of topic candidates by another model, §2.1) is permitted. Use that touches research decisions is limited to this one place.
- Do not attempt prompt injection or jailbreaks against third-party AI services, as stated in §12.1.
- Send only public data and data you created yourself, and do not send personal information. Check each provider's terms of use (such as restrictions on using outputs to train other models), and record the date you checked.

Plan and budget:
- For each experiment that uses an API, write in the pre-execution plan (protocol/) the purpose, provider and model, why local public models are not enough, the number of calls, the maximum input and output tokens per call, the estimated cost, and how the results will be analysed.
- Confirm prices in each provider's official price list, and record the source and the date checked. Do not use models whose prices cannot be confirmed.
- Before each call, confirm that the cumulative actual cost plus the maximum cost of the next call (computed from the input tokens and the output limit) does not exceed the budget (§3); if it would, do not call. If shrinking the plan is not enough, request an additional budget in the format of §5.
- Compute the actual cost from the usage included in the response and the price list, and record it separately from estimates. Include charges for failed calls and retries, and reasoning tokens billed as output.

Calls and records:
- Call AI APIs only through one wrapper (module or script) in the research directory. The wrapper performs the budget check, the recording and the retry limit (at most 3 per request).
- In api_calls.jsonl, record for each call call_id, experiment_id, purpose, requested_at_utc, provider, model_requested, model_returned (the model identifier shown in the response), parameters (temperature, maximum tokens, seed, etc.), request_path, response_path, usage, cost_usd, cumulative_cost_usd, status and error. Save the original requests and responses in files, and include them in the SHA-256 list.
- If the same input need not be sent repeatedly, reuse saved responses.
- Make it possible for the reviewer and third parties to recompute the results from saved responses without calling the API (§9). API models are updated and retired, and outputs can change even for the same input, so agreement with the results of a new call is not required.
- In the paper, identify the models used by the identifier shown in the responses and the date of use, and state in the limitations that the results are limited to those models and that period.

Handling of the key:
- Do not display, output, record or commit the key's value. Do not write the key in command-line arguments or files; read it from the environment variable.
- Before each Git commit and each submission, confirm, by a method that does not display the value, that the key's value is not contained in the research directory. If it is, stop work immediately and notify the conversation. The human revokes the key.

## 3. Conditions of this trial

- Trial ID: free-research-{{RUN_NO}}
- Research directory: {{WORKSPACE}}/run-{{RUN_NO}}
- Starting point: the current time first obtained with a tool after receiving this instruction. Record it in UTC and with the time zone.
- Time limit of the research period: submit the first draft (§10) within 12 hours of elapsed time from the starting point. This includes waiting for human replies, stops and sleep. However, it does not include stop time due to the AI usage limit (next item). Extending the time requires separate permission.
- Time limit of the review-response period: 2 hours from the time first obtained with a tool after receiving the review result (§11). The waiting time from submitting the first draft to receiving the review result is included in neither period. Do not work during this waiting time. Stop time due to the AI usage limit is not included in this period either.
- Handling of stops due to the usage limit: If execution stops because the AI usage limit (the usage limit per 5 hours) has been reached and later resumes, the stop time runs from the last time obtained with a tool before the stop to the first time obtained with a tool after resuming; extend the deadline of that period by the stop time. Do not exclude a stop whose reason cannot be confirmed as the usage limit from the runtime's error display or the human's resume message. Compute the stop time, the basis of confirmation, the original deadline and the extended deadline with tools, and record them in manifest.json, events.jsonl and interventions.jsonl (runtime_resume). If any of your experiment processes kept running during the stop, record that too. Such stops can happen without notice, so obtain the time at each major milestone and keep checkpoint.md updated.
- To prepare for the end, as a guide, refrain from starting new long experiments when 60 minutes remain in the research period and 30 minutes remain in the review-response period, and give priority to writing, tidying up and the end-to-end run of the verification procedure (§9). Check the time with a tool, and do not start experiments that are unlikely to finish before the deadline.
- Total storage limit of the research directory: 10 GiB, including dependencies, data and logs. When approaching the limit, stop new downloads and experiments and keep a record.
- Concurrent experiment processes: at most 2. Manage only those you started.
- Run limit of one experiment process: 30 minutes. Set a timeout.
- Model: the model set at the start of this session. Do not change the model or provider on your own initiative.
- Models, search tools, etc. normally available in the current session may consume their existing usage allowance. This does not permit unlimited use.
- AI API: you may use only the API key passed by the human in an environment variable, for the purposes and with the procedure of §2.3. The budget is 20 US dollars in total for the research period and the review-response period.
  - Provider and environment variable name: OpenAI / FREE_RESEARCH_OPENAI_API_KEY (this is not the SDK's default environment variable name, so pass this variable's value when creating the client)
  - Model used for critiquing topic candidates (step 6 of the research-question skill, §2.1): gpt-6-astra, reasoning effort xhigh
  - If there is no entry, or the corresponding environment variable is not set, do not use AI APIs.
- Any other new paid API use, adding billing routes, purchases and contracting cloud compute are prohibited. If the billing category of an existing tool cannot be confirmed, record it as unknown, and request permission before any action that may require additional charges. Do not fill in prices or token counts by guessing.
- Choose by yourself a safe study that works only with public information and local compute (including the AI API of §2.3).
- Calling sub-agents or another AI or CLI requires a prior permission request (except AI API calls within §2.3). If needed, define the purpose yourself, use it only if approved, and save the provenance of inputs, model, replies and outputs.

These values are the starting conditions of this trial. Do not relax them later on your own; if a change is approved, record the old condition, the new condition, the time and the permission. These are limits on your behavior; do not assume that the OS or runtime enforces them automatically.

## 4. Operations permitted in advance

- Create the parent of the research directory as needed, and create the research directory anew.
- Within that directory, create and update code, data, figures, research records, the paper and a local Git history.
- Read, search and download into the research directory public web pages, papers and public data, following their terms of use.
- Install ordinary public packages into a dedicated environment within the research directory. Global installation is prohibited. Keep package caches etc. within the research directory as far as possible.
- Obtain the minimum environment information needed for the research and records: date and time, OS, runtime versions, model and provider identifiers, the version of the execution environment (Hermes, Claude Code, etc.). Do not output the whole set of environment variables, secret configuration files or credentials.
- Read the research-question skill named in §2.1 ({{WORKSPACE}}/skills/research-question/) and copy it into the research directory (§6).
- Consult official documentation needed to use tools and runtimes correctly, and Skills already installed. Record the use of Skills and any influence on the topic or methods.
- Return to the requesting conversation permission requests, minimal progress, the first-draft submission and the final results.

## 5. Operations not permitted, and requests

Do not do the following: viewing or changing user files outside the research directory (other than reading the skill in §4), investigating personal GitHub repositories or past conversations, obtaining secrets, sudo, changing system or runtime settings, persistent memory or persistent Skills, stopping existing services, posting, uploading, publishing or sending messages externally, experiments on human participants, faking experiments, dangerous research, and circumventing terms of use or access restrictions.
Caches and session histories that normal tool use or the runtime generates automatically are an exception to the prohibition on writing outside the research directory. Do not interpret this as permission to access other files.
Follow higher-level system and developer instructions, safety policies and required Skill use. Do not override them with this instruction. If conditions or changes deriving from higher-level instructions can be observed, record the fact. You need not disclose the text of secret instructions.

Only when a permission is really needed, request it in the following format and stop before carrying out the action. While a request is pending, the whole work stops, and the human cannot always answer right away. Limit requests to operations essential to continuing the research; if the goal can be achieved without a request, use that way. Stop processes you started by relying on the experiment time limit (§3) or by waiting for them to end; do not request permission for that.

PERM-001 (numbered consecutively thereafter)
- Operation needed: target, whether it reads, writes or sends, what is done
- Scope of permission: target paths, destinations, amount, number of times, period
- Research purpose: a short explanation. Do not make the human judge the merits of the research
- Cost and risk: what has been confirmed. Mark unknowns as unknown
- If not permitted: the alternative you have chosen

The human answers "PERM-001: granted / denied / granted with conditions. Scope: …". Save requests and answers, excluding secrets, in the research records. Do not treat ambiguous replies, silence or timeouts as permission. If a request is denied, choose an alternative yourself; do not hide the denial or get around it by another route.
If an approval button in the runtime, /approve or the like is also required, follow that mechanism. If the model cannot observe the approval operation, do not guess the approver, time or content; record "not directly observable".

## 6. Records at the start

First check the date and time with a tool, and check whether the research directory exists. If it contains existing files, do not overwrite them; stop and request permission to use another directory.
Next create the record files, initialize local Git (§9), save the original text of this instruction to input_prompt.md, and copy the folder {{WORKSPACE}}/skills/research-question/ unchanged to input_skills/research-question/. If you can copy an attachment, copy the original text as it is; if you cannot obtain the original text, state clearly that it is incomplete. Do not treat a summary as the original text.

Record the following in manifest.json.
- Trial ID, start time, first-draft deadline, research directory and the configured resource limits. When you extend a deadline because of a usage-limit stop, and when you receive the review result, append the time and the new deadline
- Session ID, and the IDs of continuation sessions derived during the work (null if unknown)
- Model, provider, reasoning effort and other model settings (as far as they can be confirmed), the execution environment, OS and versions of the main runtimes
- Tools, Skills and project rules that can be confirmed, and whether persistent memory or user profiles exist
- The source of each piece of information you confirmed. Distinguish the model name presented in the conversation from identifiers confirmed from the execution environment
- Unknown conditions, visibility of prices and usage, missing records
- The AI API budget, the available providers, and whether the key's environment variable exists (do not record its value)

/new is a condition for starting a conversation; do not regard it as having erased persistent memory, Skills or the model's trained knowledge. Do not use a user profile that is already visible for topic selection on your own initiative; record only its existence. Do not copy the text of personal information into the research records. Do not search past sessions to fill gaps.

## 7. Research records

Create and update the following when needed. Do not treat files not yet created, or stages not carried out, as complete.

- input_prompt.md: the original text of the start instruction. Do not change it once finalized.
- input_skills/: the skill used for topic selection, copied unchanged at the start. Do not change it.
- manifest.json: experimental conditions, environment, provenance, unknowns.
- events.jsonl: append events in time order.
- research_log.md: an easy-to-read account of the course of the research.
- sources.jsonl: bibliographic information of references, URL/DOI/paper version, date obtained, range checked, and which claim it supports. Distinguish search only, abstract only and full text checked.
- protocol/: plans before running experiments, and later revisions.
- experiments/: for each experiment, code references, settings, input data, seed, start and end times, commands run, exit codes, stdout/stderr, raw results and analysis outputs.
- interventions.jsonl: permission decisions, resumptions of execution, safety stops, technical support, advice on research content, peer review and other human interventions.
- api_calls.jsonl: records of all AI API calls (§2.3).
- claims.jsonl: the paper's main claims and their correspondence to evidence and verification steps.
- paper.md: the research paper written by the AI itself. If unfinished, say so.
- VERIFY.md: the procedure for the reviewer and humans to verify the research (§9).
- review/: the self-check before submission, copies of submitted versions, the original text of review results, and response letters (§10, §11).
- README.md: the list of outputs and the procedure for an independent person to re-run them (may refer to VERIFY.md for details).
- final_report.md: the scope carried out, results, limitations, remaining work, and tallies of interventions and usage.
- checkpoint.md: where to resume from after a stop. Keep the original conditions and deadlines.

Each line of events.jsonl must be a valid JSON object with at least event_id, observed_at_utc, type, summary, artifact_paths and related_ids.
Important events are: topic candidates and selection, fixing the research question, fixing the experimental plan, start, end and failure of experiments, changes of direction, permission requests and answers, stops and resumptions, changes of model etc., missing records, the Git commits at the points set in §9, first-draft submission, receipt of the review result, final submission, and finalizing the paper. If the time of writing differs from the time of the event, use separate fields, and give later additions retrospective:true and the source of the information.
Each line of interventions.jsonl must have intervention_id, type, observed_at_utc, request_id, request, human_response, decision, scope, expires_at, message_ids, observability and effect. Set values that cannot be obtained to null; do not make up content. Distinguish type as permission_request / permission_decision / runtime_resume / technical_support / scientific_feedback / peer_review / stop, etc. Record message_ids only when they can be obtained. Requests and answers may be separate events.
If unplanned research advice arrives, record it as scientific_feedback without confusing it with a permission decision, and state clearly the deviation from the original "permission-only intervention" condition, whether you adopted it, and what changed. The review of §11 is a planned intervention; record it as peer_review.
Do not fix errors in logs by deleting existing lines; append correction events. Your explanations may be concise summaries of decisions; do not claim to have made a full record of internal thinking or of true motives.
You need not transcribe every small tool call by hand. The messages and tool history saved by the execution environment are a separate record layer. The research log is an index that refers to them, not an independent immutable audit log. However, assume the reviewer cannot see the execution environment's history, and make verification possible from the research directory alone (§9). Distinguish sub-agent reports, tool exit codes and your own checks.
If record files cannot be created or are missing, notify the conversation at that point and stop, and do not continue the main experiments until the recording infrastructure is restored. Do not go and get secrets that cannot be obtained, or information to which access is prohibited, for the sake of records.

Always obtain times with a tool and record them. Do not record estimated times.
Include raw data (measurement results, generated outputs, logs) in the SHA-256 list even when you exclude them from Git for size reasons, and record why they were excluded.

## 8. The paper and evidence for claims

The paper must include a title, abstract, introduction (background and importance of the research), research question, prior work, methods, results, discussion, limitations, references and a reference to the reproduction procedure. Write the paper in English. This specifies the report format, not the topic.
In the first chapter (introduction), explain the background and importance of the research before going into technical content. In the words that researchers and practitioners working on the problem usually use (including widely used names), write in what applications or systems the problem arises, whose judgments or outcomes it affects and how, and why it is worth studying now, and lead from there to the research question. Base the importance on facts and literature that can be confirmed, and do not exaggerate. In the first sentence of the abstract, also state the problem and its importance.
In the abstract, write the main results planned in advance first, and state that exploratory results added after seeing the results are exploratory. Include in the abstract only exploratory results that change the interpretation of the main results; collect the other exploratory results in an appendix.
Use the terms established in the field. For a concept whose established name is in another language (for example, the official name of a program or institution), give the original name in parentheses at its first use. Do not create new translations or coined terms. In the text, use internal numbers (experiment IDs, claim IDs, etc.) only as references, and do not rely on numbers for explanations.

In claims.jsonl, give each main claim claim_id, text, status, evidence_paths, source_ids, experiment_ids, scope, verify, expected, exploratory and reader_implication. Set status to supported / partially_supported / unsupported / hypothesis, etc., according to the evidence. scope is the conditions under which the claim holds and the conditions not checked; verify is the procedure for checking the claim (a re-run command, or the files and places to look at); expected is the value or output that procedure should give; exploratory is whether the claim depends on metrics, exclusions or hypotheses decided after seeing the results (true / false); reader_implication is the implication for the intended readers' understanding or judgment (null if none). Make failed experiments referable too.
Do not describe experiments not run, literature that does not exist, fabricated numbers, unconfirmed significant differences or approvals not observed. Do not call your own evaluation external peer review or independent reproduction. Describe the review of §11 as "review by an AI agent", and do not call it human peer review or independent reproduction.
Cite as supporting evidence only literature whose relevant passage you have checked in the full text. Do not use literature checked only through search results or abstracts as evidence; if you mention it, state the range checked in the text. Generate the numbers in tables, figures and text from analysis outputs; do not transcribe them by hand. Round only once, immediately before display.
Submit the work as it is even if the results are weak, failed or unfinished, and do not make up for it in prose as if it had succeeded. Do not write, in place of the human, the observational article the human will write later, and do not mix it into this paper.

## 9. Verifiability of the research process

Make it possible for the reviewer (§11) and humans to confirm the following three points using only the research directory. Assume the execution environment's session history is not given to the reviewer.
- that the claims follow from the evidence
- that the research was carried out in the recorded order (that the plan was fixed before the results, and when metrics, exclusions and hypotheses were decided)
- that re-running the main results gives the same values

To this end, observe the following.
- Local Git: manage the research directory with local Git, and commit at least at the initialization of the records, fixing the topic selection, fixing each plan version (before starting experiments based on that plan), the end of each main experiment, first-draft submission and final submission. Write the corresponding event_id in the commit message, and write the commit ID in events.jsonl. Do not rewrite history (amend, rebase, forced updates, etc.). Understand and treat Git times as self-reported; they do not prove the absence of tampering.
- Linking experiments to plans: in each experiment record, write the path and commit ID of the plan file at the time of execution, the commit ID of the code, and the SHA-256 of the input data.
- External data: record the source URL, time obtained, licence and SHA-256. If it cannot be obtained again, write why and whether it is bundled in the research directory.
- Deviations from the plan: list differences from the plan, analyses added exploratorily and data excluded, each with the time of the decision and its event_id.
- VERIFY.md: write a verification procedure for the reviewer. The reviewer does not change the research directory and verifies on a copy of the submitted commit made elsewhere, so the procedure must be executable outside the research directory and must not write into it. Write: environment setup; preparation of data (including how to obtain or copy data not in Git); the confirmation steps and time required for each main claim (matching verify and expected in claims.jsonl); a single entry point (such as one script) that regenerates the main tables and figures together; steps that need an external network; steps that call AI APIs (written separately from the steps that recompute from saved responses, so that the reviewer can verify without calling APIs); how to check the timeline (which commits and events to look at); and a reference to the list of deviations from the plan. For verification that takes more than 30 minutes, prepare a reduced version, and state clearly that it is reduced and how it relates to the original results.
- End-to-end run: before submitting the first draft, run the procedure of VERIFY.md yourself in a new working location inside the research directory (such as a copy of the commit to be submitted), and record whether the values obtained matched expected. The working location may be excluded from Git, but it counts toward the storage limit; record that it was excluded. If the values do not match, fix this before submission or state the mismatch as it is. This is a re-run by yourself; do not call it an independent reproduction.

Records for verifiability within the scope above are sufficient. Do not give further recording or auditing work priority over the research content.

## 10. Continuing, stopping and first-draft submission

Within the scope of permissions and resources, continue with actual tool execution without asking for approval at each stage. Do not end with a mere plan or a promise of "next I will do". However, if there is a turn limit, an interruption or a tool restriction, save to checkpoint.md, state that the work is not complete and what resumption operation is needed, and stop. Do not circumvent limits with cron or resident processes.
If 2 hours or more remain before the research-period deadline when you have finished the planned experiments, do not end; deepen the content of the research. First check whether the main results withstand alternative explanations (the self-check below), and fix the weaknesses of the main comparisons. Then investigate how far the results hold (other data, more realistic inputs, frequency in actual use), and stronger comparison methods and boundary conditions. Do not add extensions to new questions only loosely related to the main results (the time limit of each experiment and the "60 minutes remaining" rule still apply).
When you reach the deadline, the storage or safety limits, or the user's instruction to stop, do not start new experiments; stop. Do not fabricate a finished product because the deadline has come. Stop the child processes you started, and state clearly any that remain. If the work is not finished by the deadline, preserve the incomplete results.
Before submitting the first draft, check yourself the consistency of code, data, figures and claims, and do the end-to-end run of §9. Distinguish a re-run by yourself from reproduction by an independent third party.

Self-check before submission: before submitting the first draft, check the following from the reviewer's standpoint, and write the results and how you dealt with them in review/self-check.md. If time remains before the deadline, give priority to this check and to dealing with the problems found over submitting early.
- Close prior work: in light of what you learned after topic selection, search papers and primary sources (step 3 of the research-question skill) again.
- Citations: did you check in the full text, down to the relevant passage, the literature cited as evidence (§8)?
- Readability: in the first chapter, did you explain the background and importance of the research in the words that readers working on the problem use? Did you avoid exaggerating the importance? Did you use the terms established in the field, and give the original name at first use for concepts whose established name is in another language? Did you avoid creating new translations or coined terms (§8)?
- Strength of claims: are the claims in the abstract no stronger than the text and the evidence? Does the abstract distinguish results planned in advance from exploratory results? Does the scope of the claims stay within the scope of what was studied (tools, versions, data, models, settings, etc.)?
- Alternative explanations: could the results be explained not by the factor you claim but by ceilings or floors of the measurement, how the targets or settings were chosen, or the definitions of the tasks or conditions themselves? Are you treating results that could be predicted without experiments as findings? If conditions apply (for example, the answer becomes trivial, or the inputs of the two methods are almost the same), count the cases for each main comparison and write the counts in the abstract and the results tables.
- Numbers: do the numbers in the paper's tables, figures and text match the values regenerated from the analysis outputs?
- Remaining weaknesses: among the weaknesses found in the check, deal with those that can be dealt with within the research environment (adding samples, independent checks, adding comparison conditions, etc.) before submission if time remains. If you do not deal with one, write why. If you say it cannot be dealt with because of the constraints of the research environment, first check whether it can be dealt with using saved data or another route, and write what you checked.
This check is a self-assessment and does not replace the review.
In final_report.md, summarize the topic, what was done, the results confirmed, unverified matters, failures, the reason for ending, the list of interventions, the observable usage and unknowns, the AI API usage tally (number of calls by model and purpose, token counts, actual costs, failures, the source of the price list), and the paths of the outputs. Count numbers from the records with tools. Update it after responding to the review.
Create the SHA-256 list of the outputs with a tool and save it. You may exclude the final output list itself and caches and virtual environments used during execution, but state the scope excluded. Do not claim that hashes alone guarantee tamper-proofness or independence.

Submit the first draft in the following order.
1. Copy paper.md, claims.jsonl, VERIFY.md, final_report.md, review/self-check.md and the SHA-256 list into review/submission-1/.
2. Commit with Git and add the tag submission-1.
3. Report briefly in the conversation, as "First draft submitted", the title, research question, results, limitations, the path of VERIFY.md, the submitted commit ID and the submission time; state clearly that you are waiting for the review, and end the turn. Do not publish anything externally.

After submitting the first draft, do not change the research directory until you receive the review result. This is so that what the reviewer reads does not move.

## 11. Review round and final submission

After the first-draft submission, the human has another AI agent read the research directory (the submitted commit) and passes on its review result in a message beginning with "REVIEW-1". The human selects, instructs and runs the reviewer. Besides the correctness and verifiability of the claims, the reviewer also assesses whether the content changes the intended readers' understanding or judgment. Do not contact the reviewer, and do not call the reviewer or other AIs (the rules of §3 do not change). There is only one review.

When you receive the review result, do the following.
1. Obtain the time with a tool, and record the review-response deadline (§3) in manifest.json and events.jsonl.
2. Save the original text of the review result as it is to review/review-1.md. Do not treat a summary as the original text.
3. Record it in interventions.jsonl as type: peer_review. Record the reviewer's model name and the like only as far as the human tells you, and state that it cannot be observed directly. If research advice other than the review is included in the same message, distinguish it as scientific_feedback, as before.

Responding to the points:
- You decide whether to follow each point. You may decline with reasons. Do not agree without evidence or strengthen claims to please the reviewer.
- If a point is correct and a claim is no longer supported, weaken or withdraw the claim.
- Rebut factual errors of the reviewer by showing records or re-run results.
- Do additional experiments and analyses within the review-response period and within the resource limits of §3. Revise the plan before running them, record that they were added after the review, and distinguish them from analyses based on the prior plan.
- Even if the reviewer asks for operations outside the permitted scope (paid APIs, calling other AIs, external publication, etc.), do not do them without a request under §5 and permission.
- In review/response-1.md, write for each point: the point ID (if the review result has no numbers, assign them yourself and quote the relevant part of the original), the decision (adopted / partly adopted / not adopted / cannot be addressed), the reason, the changes made (file, section, claim_id, commit ID), and the experiments added.

Final submission:
- Revise paper.md, and append at its end a summary of the changes from the first draft (revision history). You may update claims.jsonl to the revised state (the first-draft version remains in review/submission-1/). For claims whose status changed, write the reason for the change and the relevant part of response-1.md.
- Update VERIFY.md, and do the end-to-end run of §9 again.
- Add to final_report.md a tally of the review response (number of points, number by decision, claims changed or withdrawn, experiments added). Count the numbers with tools.
- Recreate the SHA-256 list, commit with Git, and add the tag final.
- In the final reply, report briefly the title, research question, results, limitations, a summary of the review response, the main files, the end state, and the session IDs that need to be preserved. Do not publish anything externally.

If you reach the review-response deadline, do not start new experiments; mark the points not yet addressed as "not addressed" in response-1.md and make the final submission. If the human says there will be no review round, make the first draft the final version, record that, and send the final reply.

## 12. When the study involves security, privacy, dual use or social data

If the topic involves vulnerabilities, attacks, misuse, privacy or AI safety (prompt injection, jailbreaks, misuse of models, AI evading human oversight, manipulating or deceiving humans, etc.), observe the following. These take precedence over the value of the research.

12.1 Scope of what you do
- Toward third-party systems, services and AIs, limit yourself to passive viewing and use equivalent to an ordinary user. Do not exploit vulnerabilities, demonstrate exploitability, bypass authentication, brute-force, fuzz, scan actively, run load tests, or submit crafted input to forms.
- Test attack techniques only in a mock environment or local models that you built yourself inside the research directory.
- Do not attempt prompt injection or jailbreaks against third-party AI services.
- Do not collect personal information. If you obtain it incidentally, do not keep more than the research needs, and record that you obtained it.
- When dealing with the relationship between humans and AI, frame questions in the direction of AI supporting humans better and humans being able to oversee AI appropriately. Do not aim to create or improve ways to evade human oversight or to manipulate or deceive humans.

12.2 Concealment in the outputs
- In the paper, the final report and figures, do not include the names, domains, URLs or IP addresses of the individual affected organizations, nor clues that make the targets searchable or identifiable (distinctive file paths, file names, hash values, HTML fragments, combinations of product versions, etc.). Limit yourself to aggregate values and generalized descriptions.
- Do not create procedures, example inputs or proof-of-concept code directly usable for misuse, either in the research directory or in the outputs.
- Put raw data that can identify individual targets under restricted/, or list where they are, and state clearly in README.md "not to be shared externally".

12.3 Preparing disclosure (do not make contact)
- The AI does not itself contact, report to or post to organizations, vendors, coordination bodies, the press, etc. Humans make and carry out disclosure decisions.
- If the affected targets are thought to actually exist, create the following in disclosure/.
  - Summary (what was found, to what extent, with what certainty; the distinction between confirmed facts and guesses; that exploitability was not tested)
  - The list of affected targets (references to the relevant files in restricted/)
  - Evidence (time obtained, method, procedure for re-checking)
  - Candidate disclosure routes (for example, the vulnerability reporting or coordination body of the country concerned, such as IPA's vulnerability reporting [web applications / software products] or JPCERT/CC in Japan, or CISA or CERT/CC in the United States; the product vendor; the competent ministry or the sector's information-sharing body), and why each is suitable. State that the current acceptance conditions of each contact point need to be confirmed from official information.
  - A proposal for the timing of publication (such as withholding publication of the paper until fixes and coordination are complete), and the procedure for confirming the current state by re-measurement before publication
  - Results of the comparison against known-exploitation information (e.g., CISA KEV), if such a comparison was made
- In the first-draft submission and the final reply, state at the beginning that there are matters requiring a disclosure decision.

12.4 When in doubt
- If you are in doubt about any of the scope, concealment or disclosure, make the more conservative choice and record the decision. If an action needed to continue the research is still outside the permitted scope, request permission in the format of §5 and stop.

12.5 When handling social data and social problems
Even if the topic does not involve vulnerabilities and the like, observe the following when handling social data (statistics, administrative data, public information on the web, etc.) or social problems.
- Use data whose reuse is permitted. Check the licence and terms of use, and record the date checked.
- Do not analyse or publish in a form that can identify individuals or a small number of households or businesses. Do not re-identify individuals by linking multiple datasets. Handle personal information according to §12.1.
- Limit retrieval from third-party sites to the range of ordinary browsing (follow robots.txt and the terms of use, and do not impose load) (§12.1).
- Do not make claims in a form that names and blames particular organizations or individuals. When showing comparisons of regions or organizations, state the limitations of the data (differences in definitions, missing values, timing) alongside, and avoid asserting rankings.
- Write value judgments about the merits of policies or institutions separately from what the data can say.

Now initialize the records and carry out one free research study. You do not need to ask the human for a topic.
