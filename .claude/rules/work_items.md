# Work items

## 1. Sources

A *work item* is a unit of work: a feature, bug, performance issue, or chore. Its source is set by `CLAUDE.md` Work Item Source:

- `tracker`: items live in the issue tracker (ClickUp, Linear, Jira) via MCP. This is the default and matches the original framework behaviour.
- `local`: items live as files under `docs/issues/` in the repo. No tracker MCP is required.
- `hybrid`: resolve from the tracker if the ID exists there, otherwise from `docs/issues/`.

## 2. Local work-item file

Path: `docs/issues/{ID}.md`. YAML frontmatter plus body:

```markdown
---
id: BUG-014
type: bug            # feature | bug | perf | chore
title: Cart total miscalculates with discount codes
status: todo         # todo | planning | ready_for_build | in_progress | in_review | done
severity: high       # bugs/perf only; optional otherwise
branch: feature/BUG-014-cart-discount-total
depends_on: []
---

## Description / expected behaviour
...

## Acceptance criteria
- [ ] ...
```

ID prefixes by type: `FEAT-`, `BUG-`, `PERF-`, `CHORE-`. Any `{WORK_ITEM_ID}` a command accepts may be a tracker ID or a local file ID. Throughout the skills, `{FEATURE_ID}` and `{WORK_ITEM_ID}` are interchangeable; feature is just the default type.

## 3. Resolve work item (used by every pipeline skill at Load Context)

Given `{WORK_ITEM_ID}` and Work Item Source:

- `tracker` or `hybrid`: look up `external_id` in `project_state.json`, fetch via the tracker MCP. For `hybrid`, if the ID is not in the tracker, fall back to the local file.
- `local`: read `docs/issues/{ID}.md`. Parse frontmatter (id, type, title, status, severity, branch, depends_on) and body (description, acceptance criteria).

If the item cannot be resolved from the configured source, stop with a clear message naming the ID and the source checked.

**Branch and dependencies.** For tracker features these live in `feature_map.md`; for local items they live in the work-item frontmatter. Wherever a skill reads `feature_map.md` for a work item's `branch` or `depends_on`, read the frontmatter instead when the item is local.

## 4. Status handling

- `tracker` or `hybrid` (tracker item): update status via the tracker MCP using `status_mapping` (unchanged behaviour).
- `local`: update the `status:` field in the item's frontmatter file. No MCP call.

Done on merge: for local items, a CI step (or a manual step) sets `status: done` in the file when the PR merges. No tracker REST call or secret is needed.

## 5. MCP requirement by source

- `tracker` or `hybrid`: the issue tracker MCP is required, per `mcp_integration.md`.
- `local`: the issue tracker MCP is NOT required. The Git provider MCP stays recommended for PR and review-comment operations but degrades to the `gh` CLI; if neither is present, PR-based steps fall back to a manual note in the work-item file.
