# Uniform-contract conformance audit

**Role:** headline-support — the twin of the dependency-incompatibility analysis. **Feasibility:** NOW (static +
`bioq describe`, no cloud).

**Status:** implemented — live audit of the deployed fleet; raw manifests
committed under `data/manifests/` so every downstream number regenerates
offline. First audit (28 audited, 65 task endpoints; structural
items ~100%, metadata gaps wide). Re-audit after the fleet-wide
contract fixes landed (gateway-served static manifests + `default_kind`
semantics): **30/30** in-scope services served a manifest, **141 endpoints**
checked, **68** of them `bioq run` task endpoints. Headline: **98.5%** of
task endpoints fully conformant, **96.7%** of services at or above the 0.9
bar (median score 1.0) — `typed_params`/`file_fields`/`machine_view`/
`docs_text` now 100%, one residual gap: chembounce `scaffold_hop`'s
`input_smiles_uri` default is unannotated (see `data/stragglers.md`).

**Scope.** `ensemble` is excluded from the audit entirely: it is a legacy
`/v1`-API service generation, not built on the shared service framework, and
therefore outside the uniform contract this experiment measures — a different
kind of service, not a conformance data point. Services that did not serve a
manifest at audit time (cold start / transient unavailability) are listed as
*not audited* and excluded from every statistic — availability is an
operational concern, not a contract-conformance finding.

## Claim

The "uniform contract" is genuinely fleet-wide: across all deployed services,
endpoints expose a machine-readable manifest (typed parameters, required `--file`
fields, defaults, JSON output) — not just on a few showcase examples. Residual
gaps are enumerated, not hidden.

## Rationale

The dependency-incompatibility analysis proves the *environments* are mutually
incompatible; this one proves the *interface* is actually uniform — i.e.
contribution (i) holds beyond the exemplars. Without
it, "uniform contract" is a slogan; with it, the paper has a symmetric pair: the
tools cannot share an environment, but they do share an interface, and that is
precisely bioq's contribution. The straggler list is also actionable: it seeds the
Limitations section and the agent-drivability analysis's failure-cause feedback.

## Protocol

1. Enumerate the deployed fleet with `bioq services` (gateway registry) and fetch
   the exact machine payload a user or agent sees: `bioq describe <svc> --output
   json` per service. Raw payloads are stored verbatim under `data/manifests/`.
2. Per endpoint in each manifest, check a fixed 5-item checklist (below).
3. Compute a per-service conformance score (mean endpoint score) and a fleet
   histogram; tabulate stragglers with their exact missing items.

### The checklist (mechanical, manifest-only)

Every item is evaluated purely from the manifest JSON — the machine artifact —
never from prose or docs pages. The items split into two tiers: **structural**
contract items (the interface is machine-constructible) and **metadata**
completeness items (the interface is self-documenting):

| tier | item | passes when |
|------|------|-------------|
| structural | `typed_params` | every request field carries a concrete `type` (not empty, not `any`) |
| structural | `file_fields` | multipart endpoints declare their file inputs as file-typed fields — the `--file` surface of `bioq run` (vacuous pass for JSON endpoints) |
| structural | `machine_view` | the `--output json` view is complete: `method`, `path`, a `request_fields` list — plus `request_content_type` and a `request_schema_ref` into `/openapi.json` for body-request endpoints (bodyless GET/HEAD pass those sub-requirements vacuously) |
| metadata | `defaults` | every optional non-file parameter declares an explicit default (`default != null`; a `null` default counts as *undeclared*, the conservative reading — the manifest cannot distinguish "explicit null" from "absent") |
| metadata | `docs_text` | the endpoint carries human-readable prose (`summary` and/or `description`) |

**Scoring.** Endpoint score = fraction of the 5 items passed. Service score =
mean over its `/api/tasks/*` endpoints — the endpoints `bioq run` exposes —
with the mean over *all* manifest endpoints kept as a sensitivity column.
A service is "above the bar" at score ≥ 0.9. Items that do not apply pass
vacuously (e.g. `file_fields` on a JSON-only endpoint); applicability counts
(`n_file_fields`, `n_optional_params`, …) are recorded so vacuous passes can
never be silently inflated into evidence.

## Metrics

- % endpoints fully schema-complete (score = 1.0) — task endpoints and all.
- % services above the threshold bar (≥ 90%).
- Per-check fleet pass rates (which contract items drift, and where).
- List of non-conforming endpoints + exact missing items (→ actionable fixes),
  plus services whose manifest could not be fetched at all.

## Controls / threats to validity

- Use the machine manifest as ground truth; do not infer conformance from prose or
  docs pages.
- Report gaps honestly — they double as the Limitations section and as contract
  feedback, mirroring the agent-drivability analysis's "report failures, not just successes".
- Checklist items that are inapplicable pass vacuously; the CSV keeps the
  applicability denominators so the scoring can be re-weighted in review.
- A service that did not serve a manifest at audit time (cold start /
  transient unavailability) is listed as *not audited* and excluded from all
  conformance statistics — cold-start availability is an operational concern, not
  evidence about the contract. The audit still distinguishes
  *no response at all* from *HTTP answers but no `/api/manifest`* in the
  raw fetch log for transparency.
- Known finding: `operation_id` is unparsed fleet-wide in the manifest while the
  equivalent `request_schema_ref` pointers are populated; it is tracked as an
  informational column (`has_operation_id`), not a scored item.
- The checklist catches real declaration bugs, not just style: e.g. one endpoint
  declares a file-list input as `array[file]` without `is_file`, hiding it from
  the `--file` upload surface an agent would use.

## How to run

```bash
./run_all.sh                 # live: bioq CLI (authenticated) → collect → score → plot
./run_all.sh --offline       # regenerate everything from committed data/manifests/
BIOQ=/path/to/bioq ./run_all.sh
```

## Layout

```
contract_conformance/
├── README.md            # this file
├── analysis.md          # interpretation of the re-audit results (prose)
├── audit.py             # collects `bioq describe --output json` fleet-wide + checks the checklist
├── score.py             # per-service scores, fleet summary, straggler tables
├── plot.py              # conformance figure: endpoint-surface bars + checklist/doc-depth heatmap
├── run_all.sh           # collect → check → score → plot
├── data/
│   ├── manifests/           # raw describe payloads (ground truth, committed)
│   ├── fleet.csv            # per-service fetch status + endpoint counts
│   ├── conformance.csv      # per-endpoint checklist rows
│   ├── scores.csv           # per-service scores
│   ├── summary.json         # fleet headline numbers
│   ├── fix-suggestions.md   # the fix campaign this audit seeded (working note)
│   └── stragglers.csv/.md
└── figures/
    └── fig-conformance.{pdf,png}
```

## Outputs

- **Conformance figure:** per-service conformance bars + checklist anatomy heatmap
  (pairs visually with the dependency-incompatibility analysis (co-installability)),
  + a straggler table (`data/stragglers.md`).

## Data

`data/` (raw describe payloads, per-endpoint conformance checklist CSV, scores,
fleet summary, straggler list).
