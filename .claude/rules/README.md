# .claude/rules/ (materialized, do not hand-edit)

This directory holds the framework's **always-on** engineering standards. They are **not authored or committed here**. The single source of truth is the `claude-dev` plugin's `rules/` directory.

`/init-project` materializes the six always-on standards into this folder (Section R of the init-project skill), in both greenfield and existing modes, because `CLAUDE.md` `@`-imports them and Claude Code cannot inject always-on memory from a plugin:

- `coding_standards.md`
- `user_story_alignment.md`
- `workflow_triggers.md`
- `mcp_integration.md`
- `existing_codebase.md`
- `work_items.md`

The four phase-specific standards (`testing_standards.md`, `refactoring_standards.md`, `review_standards.md`, `security_standards.md`) are **not** materialized here. The skills and subagents read those on demand straight from the plugin via `${CLAUDE_PLUGIN_ROOT}/rules/`.

So this folder is empty in a fresh clone of the template, and holds only the six always-on files after you run `/init-project`.

## Editing a standard

Do not edit the files that land here: they are overwritten on every `/init-project` run. To change any standard (always-on or phase-specific):

1. Edit it in the plugin repo (`claude-dev-plugin/rules/`).
2. Cut a new plugin version. If the marketplace pins a tag, bump its `source.ref`; by default it floats on `main`, so `claude plugin marketplace update bemayker` is enough.
3. Re-run `/init-project` in the consuming repo to re-materialize the always-on ones.

This keeps the plugin and every consuming project from drifting, which is exactly what used to happen when a second copy lived in the template.
