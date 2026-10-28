# Review Instructions v1.10.3 (for Research Instructions v1.10.3)

This whole file is the start instruction for this review. What follows is addressed to the new review session that receives this message.

## 1. Request

Another AI agent, following Research Instructions v1.10.3, chose a research topic itself, carried out one study autonomously, and submitted a first draft of the paper. Review this study and paper. The review result is passed to the research side only once, through a human, and within a 2-hour review-response period the research side answers each point and revises. You will not receive the research side's answers.

Research Instructions v1.10.3 do not restrict the research field, and present themes such as discovering social problems by using information on the internet such as open data, or proposing tools that help solve social problems. The main readers of this study are assumed to be researchers working on the social problem addressed and practitioners in government, business, communities and other settings (humans and AIs). Assess the following.
- Are the claims correct? Do they follow from the evidence?
- Can the research process be verified? Was it carried out in the recorded order? Does re-running give the same values?
- Is the novelty claim valid?
- Does the content change readers' understanding or judgment between before and after reading?
- Are the background and importance of the research explained in words that readers working on the problem understand?

The purpose of the review is to raise the quality of the research and the reliability of its claims. Be neither too harsh nor too lenient, and write on the basis of observed facts. Give priority to the content of the research and the reliability of the claims over whether the record format follows the research instructions. The research side's conditions (time, resources, permitted operations) can be checked in run-017/input_prompt.md, and its topic-selection procedure in run-017/input_skills/research-question/.

In topic selection, the research side had another model (gpt-6-astra, with web search) critique its topic candidates through an API (run-017/protocol/topic-selection.md). Do not assume that the critique was valid; evaluate the chosen topic and the study independently.

Carry out the review by following the peer-review skill. Read the whole skill before starting the review: /Users/fujimura/Research/ai-free-research-en/skills/peer-review/SKILL.md.

## 2. Conditions of this review

- Review ID: review-017-1
- Target: Git tag submission-1 of /Users/fujimura/Research/ai-free-research-en/run-017
- Review directory: /Users/fujimura/Research/ai-free-research-en/review-017
- Starting point: the current time first obtained with a tool after receiving this instruction. Record it in UTC and with the time zone.
- Time limit: 3 hours of elapsed time from the starting point. This includes waiting for human replies, stops and sleep. However, it does not include stop time due to the AI usage limit (next item). Extending the time requires separate permission.
- Handling of stops due to the usage limit: If execution stops because the AI usage limit (the usage limit per 5 hours) has been reached and later resumes, the stop time runs from the last time obtained with a tool before the stop to the first time obtained with a tool after resuming; extend the deadline by that amount. Do not exclude a stop whose reason cannot be confirmed as the usage limit from the runtime's error display or the human's resume message. Compute the stop time, the basis of confirmation and the extended deadline with tools, and record them.
- As a guide, refrain from running new verifications when 30 minutes remain, and give priority to writing the review result.
- Total storage limit of the review directory: 10 GiB, including dependencies, copied data and logs.
- Concurrent processes: at most 2. Run limit of one execution: 30 minutes. Set a timeout.
- Model: the model set at the start of this session (specified by the human: Opus 5.5, reasoning effort xhigh). Do not change the model or provider on your own initiative. If the actual setting differs from the specification, or cannot be confirmed, record that.
- Do not call AI APIs. Even if an API key is set in an environment variable, do not use it, and do not display or record the key's value. Verify the results the research side obtained with AI APIs from the saved responses.
- New paid API use, adding billing routes, purchases and contracting cloud compute are prohibited.
- Calling sub-agents or another AI or CLI requires a prior permission request.

These values are the starting conditions of this review. Do not relax them later on your own; if a change is approved, record the old condition, the new condition, the time and the permission.

## 3. Permitted operations and prohibitions

Operations permitted in advance:
- Reading the research directory (run-017), including reading the Git history, tags and diffs.
- Reading the peer-review skill (/Users/fujimura/Research/ai-free-research-en/skills/peer-review/) and copying it into the review directory (§4).
- Creating the review directory and working inside it: copying the submitted commit, copying data from the research directory, installing packages into a dedicated environment (global installation is prohibited), running verifications, and creating records.
- Viewing and searching the public web and papers (to confirm that references exist and to check novelty).
- Returning to the requesting conversation permission requests, minimal progress and the review result.

Do not do the following:
- Writing to or changing the research directory, including operations that change the working tree or history such as checkout, commit, tag and stash. Run `git status` as `git --no-optional-locks status`.
- Contacting the research-side agent, or viewing the research side's session history.
- Viewing user files other than the research directory, the review directory and the peer-review skill, other trials (run-* other than run-017, other review-*), or past conversations.
- Posting, uploading, publishing or sending messages externally. Active testing of third-party systems.
- sudo, changing system or runtime settings, persistent memory or persistent Skills, circumventing terms of use or access restrictions.

If the study involves security, privacy or dual use (research instructions §12), handle data under restricted/ only to the extent needed for verification, and do not write in the review result information that identifies individual targets or procedures usable for misuse.

Only when a permission is needed, request it in the following format and stop before carrying out the action. Do not treat ambiguous replies, silence or timeouts as permission.

PERM-R001 (numbered consecutively thereafter)
- Operation needed: target, whether it reads, writes or sends, what is done
- Scope of permission: target paths, destinations, amount, number of times, period
- Review purpose: a short explanation
- Cost and risk: what has been confirmed. Mark unknowns as unknown
- If not permitted: the alternative you have chosen

## 4. Records at the start

First check the date and time with a tool, and confirm that the review directory does not exist. If it contains existing files, do not overwrite them; stop and request permission to use another directory.
Create the following in the review directory.
- input_prompt.md: the original text of this instruction. Do not treat a summary as the original text.
- input_skills/peer-review/: the peer-review skill, copied unchanged.
- manifest.json: the review ID, start time, deadline, the target tag and the commit ID it points to, model, provider and runtime versions (distinguish the model name presented in the conversation from identifiers confirmed from the execution environment), and unknowns.
- events.jsonl: append events in time order. Give each line at least event_id, observed_at_utc, type, summary and artifact_paths.

Then record the state of the target. Do the same check again at the end of the review, to show that the target did not change during the review.
- the commit ID of HEAD of the research directory, and the commit ID the tag submission-1 points to
- the result of `git --no-optional-locks status`
- the result of checking the SHA-256 list in review/submission-1/ against the actual files in the research directory (the numbers of matches, mismatches and missing files, and the paths of mismatches and missing files)

Always obtain times with a tool and record them. The research side's model name may be found in manifest.json and elsewhere, but do not use it as material for the evaluation.

## 5. Review procedure

Follow sections 1–5 of the peer-review skill (prior expectation, reading through, running the verification, checking the research process and the grounds, value to readers).

## 6. Writing the review result

Write review-1.md in the format of section 6 of the peer-review skill, following its notes on writing. The first line must be "REVIEW-1".

## 7. Ending

- When you reach the deadline, do not start new verifications; complete review-1.md with the results at that point, and state the verifications not carried out.
- Stop the processes you started, and state clearly any that remain.
- Do the check of the target's state in §4 again, and record the difference from the start. If there is a difference, write its content, and whether it was caused by your operations, in §8 of review-1.md.
- Append the end time and the excluded usage-limit stop time to manifest.json.
- In the final reply, show the full text of review-1.md as it is, and at the end add one line with the path of review-1.md and the end state (complete, or partly not carried out because time ran out, etc.). The human forwards the part beginning with "REVIEW-1" to the research side. Do not publish anything externally.

Now initialize the records and carry out the review.
