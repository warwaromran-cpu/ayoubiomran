# Agent communication contract

## Authority and identity
The business owner retains final authority. The CEO coordinates work and keeps the team aligned; specialists keep their own roles. This document defines a workflow, not a grant of platform permissions or authority to contact outside parties, publish, spend, deploy, or release manufacture.

## Recipient-local routes
Use only the recipient's own Codex conversations and routes in `coordination/agents.json`. Initialize that file from `setup/agents-template.json`; register only newly created conversations belonging to that recipient. Never copy another account's thread identifiers or rely on access to its chats. Keep the live routing file local and uncommitted.

Before sending a cross-agent message, check the tool's current authorization requirements. A sent message is not proof of receipt or completion; verify acknowledgment when supported. If messaging is unavailable, write a scoped handoff in the recipient's project records and have the CEO relay it. A file does not wake an idle agent.

## Handoffs and reports
Each assignment identifies project, task, sender, recipient, purpose, scope, sources/revisions, output location, acceptance checks, dependencies, and authority limits. Reuse a stable request ID for retries. A report records work completed, deliverables, checks actually performed, assumptions, blockers, and next action.

Route owner decisions through the CEO. Record consequential decisions in the authoritative project record. Keep client specifications in their project package; do not duplicate them in this communication directory. Assign one writer per artifact and avoid concurrent edits.

## Setup and checkpoints
Create separate Codex conversations for the CEO and each specialist. Register their new local routes only after creation. Test a simple, authorized handoff before claiming the bridge works. Use the smallest team that can complete the work. Do not create background automations or claim persistent memory unless they are actually configured and authorized.
