# Backend verification — 2026-09-29

Result: Local record backend implemented and checked. No manufacturing package is
approved or released by these results.

## Executed checks

- 23 backend unit tests passed using temporary, clearly labelled sample projects.
- 18 existing automation regression tests passed locally, with their mocked network
  and worker behavior; no real publication or model call was triggered by these tests.
- CLI integration passed: create a sample project, add a record, replay the same
  request, return exit code 1 for a blocked candidate, and summarize its state.
- Empty working database initialized at `backend/data/projects.sqlite3` with zero
  project rows; SQLite `integrity_check` returned `ok`.
- Python compilation and CLI help succeeded using the bundled Python runtime.

## Requested scenarios

| Scenario | Observed behavior |
|---|---|
| Register project and sources | Scoped records persist; actual file digest and revision recorded |
| Conflicting dimensions | Different values for the same item/key produce a blocker |
| Photo-derived estimates | Estimate classification prevents candidate readiness |
| Changed dimension | Associated parts and dependent deliverables become stale; reviews invalidated |
| Incorrect parts or quantities | Unknown references rejected; quantity mismatch blocks readiness |
| Missing critical information | Empty/incomplete project and unverified critical dimensions blocked |
| Resume without duplication | New Store instance recovers records; operation replay does not duplicate writes |
| Separate projects | Records remain scoped; cross-project references and overlapping roots rejected |

Additional cases cover non-finite numbers, changed source content, out-of-root
paths, stale resubmission, missing part specifications, transaction rollback,
automatic dimension dependencies, latest progress selection, and fresh reviews
after output revalidation. A complete synthetic candidate becomes ready for owner
review while explicitly remaining NOT RELEASED.

Recovery tests cover persistence/reopen and rolled-back failed writes. They are not
physical power-loss or disk-failure tests. Evidence/reviewer fields are recorded
attestations, not authenticated identities or proof of a geometric calculation.

## Scope and preservation

Changes for this task are limited to the WoodWork root instructions/start guide and
the new backend directory. No existing project design file or automation code was
edited by this task. No Git metadata exists in the local repository snapshot, so
no branch/commit/PR was created.

A content comparison against the initial 26-file repository baseline found 25
unchanged files and one changed file:
`repository/management/AUTOMATION-TEST-RESULTS.md`. This task did not write that
file; it changed concurrently and was left intact. Do not interpret this comparison
as a clean Git worktree claim.

## Remaining practical limits

- No CAD engine, OCR pipeline, nesting optimizer, or autonomous production worker
  is added. The agent must use available tools and record actual evidence.
- Review correctness, dimension-chain calculations, joinery suitability, hardware
  function, fit, and output rendering require actual technical/visual review.
- Field completeness does not prove material, edging, machining, or finish choices
  are correct. File hashes check consistency, not engineering adequacy.
- Existing projects are not automatically migrated. Nested/shared legacy roots
  require a deliberate routing plan; their current records remain authoritative.
- No off-device backup, external publishing, schedule, purchase, or manufacturing
  release was activated.

Submit the next project's client/name, design files or photographs, known dimensions,
and required outcome. The agent can then register its verified inputs and use this
backend during supervised work.
