# Technical v2.5: optional priority of the existing official mirror

The previous transport plans already authorize the anonymous ECMWF S3 endpoint
and its documented CloudFront mirror. Add a flag to try CloudFront first for
future already scheduled fields, falling back to S3 under the identical request,
retry, range-subdivision and validation rules. Do not add an endpoint, request,
parallel connection, billing route or third original acquisition. Existing
running processes keep their original order. All scientific designs and input
selection stay fixed.

Motivation: whole-second logs for a completed later AIFS field show an average
3.98seconds to completed download and0.14seconds after download over50members.
This uncontrolled diagnostic only locates elapsed time; it does not establish
provider slowness or a speed benefit from the alternative mirror. Preserve all
actual endpoint/range/byte/hash records and re-extraction comparisons. A mirror
priority can be retained or reverted based on operational success, never on
weather outcomes. The maximum two invocations per incomplete unit is unchanged.

Fixed at 2026-10-26T08:29:44Z. No request using the new priority has been made.
