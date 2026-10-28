# Exploratory pool and window influence diagnostic

Fixed after inspecting aggregate risks and the primary per-window pool counts,
before computing the diagnostics below. One small window has few nontrivial
matchable pools, so the global nontrivial count alone does not resolve its
influence on an equal-window average. This does not revise primary metrics,
remove windows from the study or identify field hydrological equivalence.

For every completed empirical `*-summary` condition, use its saved decisions
and the existing half-coverage hydrological pair/category query screens.
Condition each screen on the previously defined `nontrivial_matchable` flag:
at least two candidate categories and at least one matching category. Do not
rescreen, replace queries or change candidate references. Evaluate all methods
on that same conditional query set; report retained counts and contributing
window counts. Compute window-macro and pooled mismatch and paired differences
from the corresponding selector. Use the existing10000-window-bootstrap rule
and seed18018 on the common contributing windows. If no conditional queries
exist, leave the result missing and record zero denominators.

Separately, for each archived own-screen augmentation-versus-physical contrast,
omit each contributing window in turn and average the remaining paired window
differences. Report every omission, the range, and counts whose signs and
two-percentage-point descriptive benchmark differ from the full-panel value.
This is influence analysis, not a new population estimate or independent
repetition. Do not select an omission as a replacement headline result.

Keep all conditions, denominators, input hashes and raw diagnostic rows.
These label-conditional checks are retrospective and exploratory; they do not
define an operational query acceptance rule. Run in a free bounded local
slot, without network or AI calls. Add the procedure to offline verification.
