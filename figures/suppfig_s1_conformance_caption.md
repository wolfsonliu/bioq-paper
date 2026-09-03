**Figure S1.** Fleet-wide audit of the uniform, self-describing contract. A
manifest-only audit of the 30 deployed services (141 endpoints, 68 of them
`bioq run` task endpoints) scores every endpoint against a five-item checklist —
the structural items `typed_params`, `file_fields`, and `machine_view`, and the
metadata items `defaults` and `docs_text`. 98.5% of task endpoints are fully
conformant and 96.7% of services sit at or above a 0.9 score (median 1.0); the
single residual gap is one unannotated `input_smiles_uri` default on `chembounce`
`scaffold_hop`, which falls below the bar (amber).

- **(a)** Endpoint surface, per service. Each vertical bar is a service's
  total endpoint count --- a dark base for task (async job interface)
  endpoints and a light top for non-task (sync job and status
  interface) endpoints. Teal marks services at or above the 0.9 bar;
  amber marks those below it.
- **(b)** Conformance checklist x documentation depth.
  One column per service and one row per contract item.
  The five scored rows report the fraction of task endpoints
  passing each checklist item; the final \texttt{field\_desc} row
  (non-scored) reports the mean fraction of request fields carrying a
  description.
