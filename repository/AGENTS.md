# Repository Instructions

These instructions apply to the shared repository. Nested `AGENTS.md` files may add package-specific rules but may not weaken approval, privacy, or manufacturing safeguards.

## Roles and routing
- The CEO identifies the client/project/work package, coordinates review, and owns shared management registers.
- Specialists work only in their assigned scope. Give each owner explicit paths and acceptance criteria. Use real agents only when actually available.
- Keep client and project packages separate. Do not transfer measurements, materials, hardware, or decisions between projects without verified evidence.
- For new work, use `management/templates/NEW-PROJECT.md`; do not reuse project-specific values.

## Authoritative records and Git workflow
1. Read this file, applicable nested instructions, the project register, and relevant source/revision history before choosing the authoritative version.
2. Preserve uncommitted and unrelated work. Use one scoped branch per coherent change.
3. Before a commit or pull request, inspect the diff, verify affected and unaffected paths, record checks and unresolved issues, and open a draft for review when authorized.
4. Do not merge, force-push, delete branches, bypass protections, publish, or deploy without explicit owner authorization.
5. Keep shared management registers concise and link to the authoritative package sources rather than duplicating specifications.

## Evidence, change control, and release
Classify information as architect/client requirement, confirmed site measurement, supplier/manufacturer specification, CAD-measured value, proposed construction assumption, or unresolved confirmation. Preserve design intent. Do not invent dimensions, capacities, machining templates, fixing details, or quantities.

Check drawings, dimension chains, cutting lists, and hardware schedules against one another. Distinguish finished dimensions from cutting dimensions and account for material thickness, edging, and operating clearances. Use exactly these workflow states: Draft; Awaiting information; Awaiting review; Approved; Released for manufacture. Approval, a commit, or a merged pull request does not itself authorize fabrication.

Do not buy, contact external parties, publish, contract, issue commercial documents, or release for manufacture without explicit authorization. Keep editable sources alongside deliverables when practical. Verify generated PDFs and exports before claiming they are ready.
