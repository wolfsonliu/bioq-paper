**Figure 1.** bioq unifies a three-tier service architecture behind a common interface for researchers and coding agents.
- **(a)** The thin bioq client communicates with a control-plane gateway,
  which dispatches jobs to more than 38 serverless GPU and CPU
  services. Large inputs are transferred through content-addressed
  storage and bypass the request path
- **(b)** Coding agents use the same describe/run contract to form a closed loop of
  tool discovery, invocation, result collection, inspection, and chaining.
- **(c)** Modality coverage by discovery stage, with one stacked horizontal bar per stage.
