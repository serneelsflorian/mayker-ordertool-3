<!--
  Universal standard. Imported into CLAUDE.md (always on). Do not edit per project.
  Slash-command mapping, operational behaviour, git conventions.
-->

# Workflow Triggers & Operational Behaviour

## 1. Command Reference

The commands and skills are provided by the `claude-dev` plugin; they are not files in this repo. Once the plugin is installed, commands are available namespaced as `/claude-dev:<command>`, and each invokes the matching skill of the same name. The skill holds the full multi-phase procedure and also auto-loads by its description (including in Claude Code on the web and Routines).

| Command | Skill | Purpose |
| --- | --- | --- |
| `/claude-dev:init-project` | init-project | One-time project setup (local, interactive) |
| `/claude-dev:plan-feature {ID}` | plan-feature | Generate an architect plan for one work item |
| `/claude-dev:build-feature {ID}` | build-feature | Implement one work item from an approved plan |
| `/claude-dev:revise-feature {ID}` | revise-feature | Apply a revision based on PR review comments |
| `/claude-dev:refactor frontend\|backend\|{ID}` | refactor | Standalone code-quality scan and refactoring |
| `/claude-dev:generate-tests {scope} [--tier]` | generate-tests | Generate tests for a work item, module, or scope |
| `/claude-dev:diagnose {scope}` | diagnose | Scan existing code for bugs, perf, and risks; write local work items |
| `/claude-dev:fix {ID \| description}` | fix | Condensed plan+build for one work item, keeping the gates |

Follow the invoked skill's instructions exactly.

## 2. Subagents

The plan / build / review split is expressed with dedicated subagents provided by the plugin (`planner`, `builder`, `reviewer`). The skills delegate to them by name:

| Subagent | Role | Permissions |
| --- | --- | --- |
| `planner` | Architect plans (used by `/plan-feature`) | Read-mostly; writes only plan artifacts under `.claude/artifacts/` |
| `builder` | Implementation + tests (used by `/build-feature`) | Read/write code, run tests, commit and push |
| `reviewer` | Self-review against `review_standards.md` | Read-only; cannot edit, run, or commit |

The reviewer is intentionally read-only so it cannot quietly fix what it is meant to critique. It reports findings back; the builder applies the fixes.

## 3. Operational Behaviour

- **No TODO placeholders:** Do not generate code with "TODO: Implement logic" or similar. Write the full implementation.
- **Response format:** Be concise. Use Markdown for all code blocks.
- **MCP:** The issue tracker MCP is required only when Work Item Source is `tracker` or `hybrid`; `local` source needs no tracker (see `work_items.md` and `mcp_integration.md`). The Git provider MCP is used for PRs and degrades to the `gh` CLI. Each skill verifies what it needs at startup.
- **Config required:** All commands (except `/init-project`) require `.claude/project_state.json` to exist. If missing, stop: "Run /init-project first to generate MCP configuration."
- **Autonomy compatible:** All commands except `/init-project` are designed to run autonomously without human interaction during execution. Checkpoints that require human input exist only in `/init-project` (which is run in a local, interactive Claude Code session). Fully unattended surfaces (Routines, GitHub Actions, headless `claude -p`) cannot answer interactive prompts, do not run `/init-project` there.
- **Permissions:** Autonomous runs rely on the permission posture in `.claude/settings.json` so agents do not block on approvals. See `docs/DEVELOPMENT.md` → Permissions & Autonomy.

## 4. Git Conventions

- **Branching:** One branch per work item, prefix `feature/`. The branch name is defined in `feature_map.md` (tracker features) or in the work item's frontmatter (local `docs/issues/` items).
- **Commits:** Use semantic commit messages:
  - `feat({FEATURE_ID}): ...` for new features
  - `fix({FEATURE_ID}): ...` for bug fixes
  - `refactor({FEATURE_ID}): ...` for code-quality improvements
  - `test({FEATURE_ID}): ...` for test additions
  - `plan({FEATURE_ID}): ...` for architect plans
  - `chore: ...` for maintenance
- **Source of truth:** Git is the master record. Never rely on local IDE history as the final state.
