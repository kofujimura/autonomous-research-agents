# Technical v2.4: reuse validated regular-grid point indices

This changes extraction implementation only. The v4/v4.1/v4.2 scientific
calendar, locations, endpoints, members, matching and stopping rules remain
unchanged. The original exhausted v1 unit is never requested again. Network
hosts, range sizes, strict response validation, retry limits and two unit
acquisition invocations remain unchanged; no parallel HTTP requests are added.

Whole-second existing transfer/measurement logs for one completed IFS v4 field
show about 2.5 seconds after download per member, compared with about 4.6
seconds total. This uncontrolled diagnostic motivates avoiding repeated nearest
searches, not a claim about provider speed or a scientific performance result.

For GRIB2 regular_ll fields, compute the SHA-256 of the exact grid-definition
section3 bytes. For the first newly decoded member of each raw unit, run the
existing ecCodes nearest-point routine and check its values exactly against the
full decoded values array at the returned zero-based indices. Reuse indices
only while every later message has byte-identical grid definition and the same
decoded point count. Independently repeat the nearest-point/value comparison
for member50. Stop on disagreement. Coordinates/distances/indices remain those
returned by the original nearest routine. Every member's existing parameter,
unit/date/step/member, GRIB-length, finite-temperature and coordinate checks stay.

Before network use, compare both extraction paths on the bundled IFS land-mask
field using the fixed city/regular points. Retain first/last temperature messages
from the next two planned horizons, one per product, solely as offline decoder
validation fixtures. This is at most16messages of under2MB each and makes no
additional requests. Other global temperature fields remain unretained. Outside
site values in these few fixtures are not scientific analysis variables. Save
hashes, parameter metadata, source ranges and the expected selected-vector path.
Re-run the offline fixture comparisons during final verification. Do not claim
an actual speed improvement without a controlled benchmark, and do not create
a third original acquisition or reset any attempt ledger.

Official ecCodes C nearest documentation identifies returned indexes as indexes
in the values array; Python documentation identifies codes_get_values as that
decoded array. Their relevant full API descriptions were checked26October2026
UTC and are recorded in sources.jsonl.

Fixed at 2026-10-26T06:09:44Z.
