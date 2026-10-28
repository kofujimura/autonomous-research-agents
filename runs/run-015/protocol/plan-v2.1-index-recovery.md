# Technical addendum v2.1: recover the same public index with byte ranges

Inherit the unchanged scientific v1 design, technical v2 limits, and v3/v3.1 exploratory specification when that analysis is requested. A scheduled IFS index (2026-06-23,180h) returned HTTP503 on both advertised endpoints; this was recorded in B010. No weather result or sample choice motivates this revision.

If ordinary whole-index GETs fail, permit ordinary HTTP byte-range retrieval of that SAME `.index` object on the SAME two advertised endpoints. Use64KiB pieces, at most three attempts per piece/endpoint, bounded timeouts, require206 and matching Content-Range, retain checked prefixes, read no more than8MB total, and validate all JSON-line index entries. Do not use query-string cache busting, new hosts, authentication changes or403/404 bypasses. A server ignoring Range ends that endpoint's ranged attempt. Preserve the original full-GET failures and all ranged attempts. This recovers known public metadata, not a scan or test of a third-party system.

Keep at most two acquisition INVOCATIONS per scheduled forecast unit, including the single allowed cached-data resumption, and the runner's <=1800second timeout/two-worker cap. If the second invocation still fails, retain missingness; no substitute date. Scientific metrics, hypotheses, exclusions, models, members and calendar remain unchanged.
