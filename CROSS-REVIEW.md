# Claude Code and Codex cross-review workflow

Claude Code and Codex work on this project side by side, in two separate terminal windows. Both follow the same rules: Codex reads `AGENTS.md`, and Claude Code reads `CLAUDE.md`, which imports `AGENTS.md`. Edit `AGENTS.md` only; never copy its rules into `CLAUDE.md`.

## Permissions

- **Claude Code** uses `.claude/settings.json` (default mode). It asks before editing files or running commands.
- **Codex** uses `.codex/config.toml` (approval policy `untrusted`, sandbox `workspace-write`, no network). It may edit only inside this folder and asks before running commands. Mark the project as trusted in Codex so it loads this file.

## Workflow

1. **Build with Claude Code.** In the project folder, run `claude` and ask it to draft the change or the architecture plan. Do not commit yet.
2. **Review with Codex.** In a second terminal in the same folder, run `codex`, then `/review` and choose the uncommitted changes. Codex starts with no memory of Claude's session, so it reviews the raw `git diff` without bias.
3. **Fix.** Give Codex's findings back to Claude Code, or fix them directly. Repeat step 2 until the review is clean.
4. **Commit.** Commit only after the review passes. Owner approval rules in `AGENTS.md` still apply.

Do not let both agents edit files at the same time. One builds, then the other reviews.
