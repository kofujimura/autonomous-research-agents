# Changes

## v1.10 (2026-10-25; used in the pilot run-014, then frozen on 2026-10-26)

Later runs of the same text use patch versions (v1.10.1, v1.10.2, …). Their filled instructions differ from v1.10 only in the version number and the run number.

From v1.9.1, the last Japanese version.

**Translation and structure**
- Translated into English: the research instructions, the review instructions and the critique request.
- Split into two skills, without adding steps:
  - `skills/research-question/` holds the topic-selection procedure (formerly §2.1 of the research instructions, with the critique request).
  - `skills/peer-review/` holds the review procedure and report format (formerly §5–§6 of the review instructions).
- The instructions keep their section numbers. §2.1 of the research instructions and §5–§6 of the review instructions now point to the skills.
- The instructions name the skill files, and each session reads them by path. Each session copies its skill unchanged into its own directory (`input_skills/`). Reading the skill is added to the permitted operations, since the skills sit outside the run directory.
- `operator/prepare_run.py` fills the per-run fields and deploys the files. `operator/OPERATIONS.md` gives the fixed operator messages (now in English) and the session settings.

**Changes in content**
- **Step 2-1, technologies to start from:** "new technologies that came into practical use roughly in 2024 or later" became "technologies with capabilities that first became possible roughly in 2024 or later (excluding new versions of an existing kind of technology)". The aim is to start from genuinely new capabilities rather than from new versions of familiar ones.
- **Step 2-6, second check:** "is it a study that applies existing measurement or evaluation methods to a different target only?" became "is there already a study that applied that technology, or existing measurement or evaluation methods, to the same problem in that field?". Applying a method to a new target is now allowed. Prior use of the same technology on the same problem is now what disqualifies a candidate.

**Changes forced by the language**
- The paper is written in English (formerly Japanese).
- The terminology rule (formerly about Japanese and English terms) became: use the terms established in the field. For a concept whose established name is in another language, give the original name at its first use. Do not coin new terms or translations. The self-check item on readability follows the same rule.
- Candidate disclosure routes (§12.3) now name examples from more than one country: IPA and JPCERT/CC in Japan, CISA and CERT/CC in the United States.
- The verdict and severity labels of the review are in English:
  - verdict: Accept / Minor revision / Major revision / Reject;
  - severity: Critical / Moderate / Minor.
- Permission answers and resume messages are in English.
