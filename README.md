# ADIBUILD Shared Agents

This folder contains reusable operating instructions, prompts, a clean recipient-local agent registry template, business-wide workshop standards, and a distilled Marketing Agent knowledge pack. It is designed for another Codex user to create independent conversations in their own account.

## Use in your own Codex account
1. Copy or clone this folder into your own workspace and open that folder in Codex.
2. Read `AGENTS.md`, then `WORKSHOP-PROFILE.md`. For project work, read `repository/AGENTS.md` and any project-specific instructions created for that project.
3. Create a separate Codex conversation for the CEO and each specialist: Design, Costing and Invoicing, GitHub, Software Maintenance, and Marketing. Start each conversation with the matching file in `setup/`.
4. Only after creating those conversations, populate `coordination/agents.json` with the new account's own local conversation routes. Never import another person's thread IDs. This local file is excluded by `.gitignore`; do not commit it.
5. Check current tool permissions, project sources, the live price library, and website/social account access in your account. No credential or account connection is transferred by these files.
6. Test one authorized handoff and acknowledgment before relying on the team bridge. Prompts do not create chats, activate automations, or grant access by themselves.
7. Update the workshop profile only with owner-confirmed business-wide facts. Keep client and project records in separate project folders. Use a fresh local database if enabling the optional backend.
8. Keep work Draft — Awaiting review until the owner authorizes external publication, customer contact, spending, deployment, or manufacturing release.

## Included
- CEO and specialist operating instructions, communication workflow, independent-account setup prompts, and six-role template.
- Generic repository workflow and blank project-register template.
- Optional local structured-record backend source and documentation; no database is included.
- Marketing Agent instructions, a distilled brand guide, design practice notes, and the existing digital marketing research playbook. Account routing, campaign plans, and outputs are omitted.

## Excluded for privacy and portability
No private chat transcripts, conversation IDs, memory databases, credentials, API keys, account configuration, collaborator authorizations, client records, project specifications, source drawings, project outputs, issued quotations/invoices, or live project database are included. The live `coordination/agents.json` stays recipient-local and is ignored by Git.

## Known missing brand assets
The current approved logo master, official licensed font files, and confirmed brand color specifications were not available as a verified asset kit. The accessible local gold logo candidate conflicts with the later burgundy/cream logo reference and was excluded. Supply approved assets before producing artwork requiring exact logo or font reproduction.

The live ADIBUILD price library and social account access must be connected separately using the recipient's own authorized account. Price values in `WORKSHOP-PROFILE.md` are a dated internal reference snapshot, not confirmation of current live prices.
