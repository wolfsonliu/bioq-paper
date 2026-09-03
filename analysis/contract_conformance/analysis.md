# Analysis of the uniform-contract conformance results

This note interprets the output of the re-audit in
`data/summary.json` / `data/scores.csv` / `data/conformance.csv`, after the
fleet-wide contract fixes documented in `data/fix-suggestions.md` had landed.
Numbers here are drawn from those committed artifacts and regenerate offline
with `./run_all.sh --offline`.

## What this analysis actually measures

This analysis is the twin of the dependency-incompatibility analysis. That
analysis shows the **environments** of the AI drug-discovery zoo are mutually
incompatible and expensive to reconcile. This one shows the
**interface** is, in contrast, genuinely uniform: when a human or an agent runs
`bioq describe <svc> --output json`, every deployed service emits a
machine-readable manifest that the same client can construct request shells
from. The audit is entirely manifest-based — a five-item checklist applied to
every endpoint, never inferred from prose or docs pages — so "uniform contract"
is verified against the exact machine artifact a consumer receives, not against
the project's own documentation.

## Headline result

- **30 / 30** in-scope services served a manifest at audit time (vs. 28/28 at
  the first pass, with `esmfold2` and `promera` now reachable).
- **141 endpoints** checked, of which **68** are `bioq run` task endpoints.
- **98.5%** of task endpoints are fully conformant (score = 1.0) — **67 / 68**.
- **98.6%** of all endpoints are fully conformant (**139 / 141**).
- **96.7%** of services sit at or above the 0.90 bar (**29 / 30**); the median
  service score is **1.0**, the mean **0.9933**.

The structural contract items — `typed_params`, `file_fields`, `machine_view` —
pass at **100%** on both task and all-endpoint denominators, and `docs_text`
has climbed from 61.5% to **100%**. The only scored item below 100% is
`defaults` (98.53% on task endpoints), and it is off by a single field.

## Interpretation

**The contract is fleet-wide, not exemplary.** The result is not "our showcase
tools conform" but "all 30 deployed services conform at the median score of
1.0." The distribution is a spike at the top: 29 services score 1.0, and one
service (`chembounce`) scores 0.8 because two mirror endpoints
(`/api/scaffold_hop` and `/api/tasks/scaffold_hop`) leak one unannotated
default. This is the symmetric counterpart to the dependency-incompatibility analysis's long tail of incompatibility,
and it is what lets the paper claim the interface — unlike the environment — is
the single place the zoo becomes one tool.

**The before/after shows the straggler list was a real mechanism, not theater.**
The first audit found structural items already ~100% but two wide
metadata gaps: `docs_text` at 61.5% and `defaults` at 16.9%. The fix campaign
that followed (framework `summary` passthrough, per-endpoint summaries, file-
array recognition in `_is_file_schema`, and the `defaults` sweep) moved
`docs_text` to 100% and `defaults` to 98.5%, lifting the service ≥0.9 bar from
3/28 (11%) to 29/30 (96.7%). The conformance audit did double duty: it produced
the evidence *and* it was the tool that enumerated the exact missing items that
made the fixes actionable.

**The one residual gap is honestly attributable.** `chembounce scaffold_hop`'s
`input_smiles_uri` carries no `default` key in the manifest, so the audit's
conservative rule ("`null` default = undeclared") flags it. The consequence is
narrow — one optional parameter on one endpoint whose default is not machine-
readable — but it is kept as the single below-bar data point rather than rounded
away. It also seeds the Limitations section and mirrors the agent-drivability analysis's "report failures,
not just successes" stance.

## Nuances carried into the paper

These are non-scored observations the results surfaces, and they should temper
the headline rather than be silently dropped.

1. **`defaults` remains the honest weak point.** Even at 98.5%, `defaults` is
   the lowest pass rate because `Optional[X] = None` parameters — the common
   case where the true default lives *inside the upstream tool* — cannot be
   mechanically distinguished from "no default at all" from the manifest alone.
   Fix B1/B2 (declare a concrete default, or document "unset") washed most of
   this out; the residual requires either annotating the remaining field or the
   framework-level explicit-null distinction proposed as B3. The paper should
   not present "defaults are solved"; it should present "defaults are *near-*
   solved, with one known field and a systematic None-vs-undeclared ambiguity
   acknowledged."
2. **Field-level descriptions lag endpoint-level docs.** `docs_text` (endpoint
   `summary`/`description`) is now 100%, but `field_desc_frac` in
   `conformance.csv` — the fraction of *request fields* carrying their own
   `description` — is highly uneven: 0.0 for `alphafold`, `esmfold2`, `promera`,
   and the `rfantibody` task endpoints, versus 1.0 for `flowmol`, `megalodon`,
   `rfdiffusion`, `rfdiffusion2`, `semlaflow`. This is not scored, but it is a
   real aide-ability gradient an agent will feel when it has to reason about a
   bare field name. It is a natural next tranche of work, not a conformance
   failure today.
3. **`operation_id` is unparsed fleet-wide.** Every manifest endpoint carries a
   populated `request_schema_ref` but `has_operation_id` is 0 across all 141
   endpoints. It is tracked as an informational column, not a scored item, but
   it is a known framework gap (`manifest.py::_service_endpoints`) worth one
   sentence in Limitations so a reviewer does not rediscover it as a hole.
4. **Vacuous passes are guarded against inflation.** `file_fields` on JSON-only
   endpoints and `defaults` on endpoints without optional parameters pass
   vacuously by design; `conformance.csv` keeps the applicability denominators
   (`n_file_fields`, `n_optional_params`, `content_type`) so re-weighting in
   review cannot be accused of hiding vacuous counts. The "all endpoints" score
   (98.6%) is reported alongside the task-endpoint score (98.5%) as a
   sensitivity check — the two agree, so the headline does not depend on the
   task-vs-legacy split.
5. **Scope boundaries are explicit.** `ensemble` is excluded as a legacy `/v1`
   generation built outside the shared framework, and services that did not
   serve a manifest at audit time are listed as *not audited* rather than scored
   (availability is an operational concern, not a contract finding). This re-audit had
   zero such services; the first audit's two (`esmfold2`, `promera`) recovered
   once redeployed, which is an operational recovery, not a conformance change.

## What this buys the paper

This analysis closes the loop on contribution (i): "uniform contract" is no longer a
slogan attached to a few demo services, but a measured property of the whole
deployed fleet — 30 services, 141 endpoints, median 1.0 — with the residual
gaps enumerated to the exact field. Together the dependency-incompatibility
analysis and this one make the symmetric argument the manuscript's framing rests
on: the tools *cannot* share an environment, yet they *do* share an interface,
and that shared interface is precisely what bioq contributes and what an
autonomous agent can drive unattended.

## Remaining action items

- Annotate `chembounce scaffold_hop.input_smiles_uri` with its actual default
  (or an explicit "unset" convention) to reach 100% task-endpoint conformance.
- Decide whether to adopt the B3 framework-level `default_declared` distinction
  so "explicit null" and "absent" stop being conflated in the `defaults` check.
- Optionally promote `field_desc_frac` into the scored checklist (or a
  second-tier "self-documentation depth" score) once the field-description
  gradient is deemed material.
- Track `operation_id` population as a framework follow-up and cite it in
  Limitations.