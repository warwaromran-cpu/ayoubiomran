# Project record conventions

Records are scoped by project, kind, and ID. Existing project IDs must be checked
before creation. Use IDs consistently across drawings and schedules; a label is
not evidence of verification or approval.

## Record types

| Kind | Purpose |
|---|---|
| source | File, revision, and SHA-256 fingerprint; registration checks the actual file |
| item | Stable joinery item, scope, description, and required function |
| dimension | Item and measurement key, positive value in mm, evidence classification, source, criticality |
| material | Material or finish specification with its evidence and approval status |
| hardware | Product selection and manufacturer specification references |
| part | Item, quantity, material reference, finished/cutting sizes, machining, grain, and edging |
| deliverable | File reference, purpose, revision, dependencies, and part quantity mapping |
| issue | Missing fact or discrepancy, status, affected outputs, and resolution evidence |
| decision | Proposed or confirmed choice, basis, responsible person, date, and consequences |
| approval | Explicit approval evidence and its precise scope; a record is not authentication |
| check | Actual review result, reviewer, and evidence |
| progress | Current stage, completed outputs, pending decisions, and next action |

Use `depends_on` references in the form `kind:id`, always within the same project.
Register inputs before their dependents. Do not conceal an unknown dimension using
a fabricated positive value: record an open issue until the fact is available.

## Evidence

Dimension evidence categories are `site_verified`, `manufacturer`, `design`,
`photo_estimate`, and `assumed`. A source record alone does not prove its contents:
the agent must inspect the source and record its page, drawing/detail, measurement
method, date, and verifier where applicable. Critical site dimensions need actual
site evidence, not a manufacturer specification for an unrelated product.

Design requirements and site dimensions may both be valid but describe different
things. Give them precise distinct keys and reconcile them explicitly. Do not erase
contradictory evidence simply to make the automatic conflict check pass.

Part sizes use `finished` and `cutting` objects, each with `length`, `width`, and
`thickness` in mm. Record grain, edging, machining, and allowance explanations in
additional fields. Review actual calculations and allowances; numerical positivity
does not verify their engineering correctness.

Manufacturing deliverables use `purpose: "manufacturing"`, actual file path and
SHA-256, dependencies, and `parts` as an ID-to-quantity mapping. Quantity is the full
project quantity of that part represented by that schedule; use unique part IDs
for separate variants. Do not use this mapping as an unexplained subtotal.

## Reviews

Required review IDs are `geometry`, `hardware`, `site_fit`, `manufacturability`, and
`rendering`. Each requires `pass: true`, a reviewer, and meaningful evidence of the
actual check. A check that does not apply must explain why, not silently disappear.
Text such as “checked” without supporting observations is insufficient operational
evidence, even if a text field accepts it.

Engineering changes invalidate prior checks. An unchanged output may be accepted
after a real recheck against changed inputs; it must not become current merely by
resaving the same values. Follow the backend's revalidation requirements.

To revalidate a stale engineering record, first revise its stale dependencies, then
submit updated record content with `revalidation: {"reviewer": "name or role",
"evidence": "what was checked against which revised inputs"}` and a new request ID.
If dimensions remain correct, the changed revalidation evidence must explain why.
Simply replaying an old operation returns that operation's historical receipt; use
`get` or `check` to read the current state afterward.

## Progress and owner decisions

Use one progress record with ID `current`. Keep its stage consistent with the
existing states: Draft, Awaiting information, Awaiting review, Approved, or Released
for manufacture. A stage string records workflow information; it cannot grant release.

For an owner decision, record the question, recommendation, consequence, affected
deliverables, and evidence already consulted. Batch related decisions. Continue
unaffected work while the decision is pending. Record failures and recovery actions
as issues/progress rather than retrying blindly.

## Limitations

The backend strictly validates certain fields and references; other descriptive
fields remain structured notes reviewed by the agent. It is not a complete CAD
schema, product catalogue, approval identity service, or substitute for site checks.
See `README.md` for operational boundaries and `VERIFICATION.md` for tested behavior.

## Superseded records

Use exact `status: "superseded"` to retire a record while preserving its data and history. Retirement excludes it from current checks and implicit dimension dependencies; it still invalidates active dependents. Active records cannot depend on retired inputs. Retirement does not clear prior stale flags or authenticate a replacement. Revisions must be redrafted and rechecked against new evidence; reactivation requires recorded revalidation.
