# AI Development Framework: Standard Operating Procedure

<!--
  This file is a TEMPLATE. When /init-project runs, it overwrites this file
  with a project-specific version where all placeholder sections are filled
  in with concrete values (tracker names, secret names, MCP setup commands).
  The framework overview and command reference sections are kept as-is.
-->

This document describes the full development workflow for this project, running on **Claude Code**. For a quick overview and how to run the application, see the [README](../README.md).

> **The loop, at a glance.** `/init-project` once to set up, then per work item:
>
> `/plan-feature {ID}` → review the plan PR → mark **Ready for Build** → `/build-feature {ID}` → review the implementation PR → **merge** (CI marks it Done).
>
> `/revise-feature {ID}` applies PR review feedback at either checkpoint; `/fix {ID}` is the condensed single-item path; `/diagnose {scope}` seeds work items from existing code. Everything below is the detail behind this loop.

---

## Prerequisites

### 1. MCP connections (mandatory)

This framework uses two MCP (Model Context Protocol) connections: an **issue tracker** and a **Git provider**. With the default `Work Item Source: tracker`, both are needed. With `local` source the issue tracker MCP is not required, and the Git provider MCP degrades to the `gh` CLI for branch and PR operations, including the PR review comments that `/revise-feature` and re-planning read; if neither the MCP nor `gh` is available, paste the feedback into the task prompt instead. If you rely on the `gh` fallback (common with `local` source), install the GitHub CLI and run `gh auth login` once so it can open PRs and read review comments. They are defined in `.mcp.json` at the repo root (project scope, committed to git so the whole team shares them).

#### How `claude mcp add` works

There is no single `<server-spec>` value. The command takes one of two forms, depending on how the MCP server runs:

1. **Local server (stdio).** Claude starts the server process on your machine, almost always via `npx`. Credentials are passed with `--env`, and `--` separates Claude's own flags from the launch command:

   ```bash
   claude mcp add --scope project <name> --env KEY=value -- npx -y <package>
   ```

2. **Remote server (HTTP).** Claude connects to a hosted URL with an `Authorization` header:

   ```bash
   claude mcp add --scope project --transport http <name> <url> --header "Authorization: Bearer <token>"
   ```

`<name>` is any label you choose; it becomes the key under `mcpServers` in `.mcp.json`. `--scope project` is what writes the entry to the committed `.mcp.json` (omit it and the entry lands in your personal `~/.claude.json` instead).

#### Issue tracker MCP, worked example: ClickUp

ClickUp publishes an **official, first-party MCP server**: a remote (HTTP) server at `https://mcp.clickup.com/mcp`, OAuth-authenticated, currently in public beta. Prefer it over community `npx` packages.

```bash
claude mcp add --scope project --transport http clickup https://mcp.clickup.com/mcp
```

Because it uses OAuth, there is no token or team ID to paste or store: run `/mcp` inside a session and approve ClickUp in the browser (you choose the workspace there). The resulting `.mcp.json` entry holds only the URL:

```json
{
  "mcpServers": {
    "clickup": {
      "type": "http",
      "url": "https://mcp.clickup.com/mcp"
    }
  }
}
```

(Linear and Jira also publish official MCP servers, added the same way. If you instead use a community server that authenticates with an API key, see "Keeping token-based secrets out of git" below.)

#### Git provider MCP, worked example: GitHub

GitHub publishes an official remote MCP server at `https://api.githubcopilot.com/mcp/`. **Authenticate it with a Personal Access Token, not OAuth.** Claude Code's OAuth flow requires Dynamic Client Registration (RFC 7591), which this endpoint does not support, so the interactive "Authenticate" path fails with *"Incompatible auth server: does not support dynamic client registration."*

Create a PAT with the scopes the agents need. Classic: `repo` (add `workflow` if features touch `.github/workflows`); fine-grained: Contents, Pull requests, and Issues read/write plus Metadata read. Keep the token in your environment, never in `.mcp.json`:

```bash
export GITHUB_PAT=ghp_your_real_token
claude mcp add --scope project --transport http github \
  https://api.githubcopilot.com/mcp/ \
  --header 'Authorization: Bearer ${GITHUB_PAT}'
```

The single quotes stop your shell expanding `${GITHUB_PAT}` during `claude mcp add`, so `.mcp.json` stores only the variable name; Claude Code expands it at runtime. Run `/mcp` to confirm the connection.

> GitLab and Bitbucket publish their own MCP servers. If their auth server supports OAuth Dynamic Client Registration, the OAuth flow works; otherwise use the same PAT-in-header pattern.

#### Keeping token-based secrets out of git

`.mcp.json` is committed, so never put a raw token in it. When a server needs a static token, reference an environment variable instead: write `'${GITHUB_PAT}'` (the single quotes stop your shell expanding it during `claude mcp add`), so `.mcp.json` stores only the variable name. Set the real value in your shell (or CI secrets), and Claude Code expands `${...}` at runtime:

```bash
export GITHUB_PAT=ghp_your_real_token
```

OAuth servers (such as the official ClickUp one above) avoid this entirely, since there is no token to store. GitHub, authenticated by PAT here, follows the variable-reference pattern.

#### Figma MCP (optional)

Only if `CLAUDE.md` → Design Reference → Mode is `FIGMA_MCP`. Add the Figma MCP server the same way, then authenticate with `/mcp`.

#### Verify

```bash
claude mcp list        # both should show as connected
```

Inside a session, `/mcp` lists the servers and triggers any interactive auth flows.

> **Cloud surfaces:** In Claude Code on the web / Routines (unattended runs triggered on a schedule, webhook, or API call; see [Dispatching Sessions](#dispatching-sessions)), the same project-scoped `.mcp.json` is used. Credentials are supplied by the environment (the web session or Routine secrets), not a developer's local machine. The "MCP is mandatory, stop if absent" guard still applies; only the place you set the secrets moves.

### 2. Permissions & Autonomy

Claude Code has an explicit permission system. Unattended runs must not block on approvals, so the framework keeps a permission posture in **`.claude/settings.json`**. `/init-project` writes it from the plugin (the committed file starts with only the marketplace/plugin bootstrap that triggers auto-install), and you can tune it afterwards:

- **`permissions.defaultMode: "acceptEdits"`**: file edits proceed without prompting.
- **`permissions.allow`**: the git / package-manager / test / formatter / Docker commands and MCP tools agents routinely need.
- **`permissions.deny`**: destructive or unsafe operations (`rm -rf`, `sudo`, the common force-push flags `--force` / `-f` / `--force-with-lease`, writing `.git/`, and reading committed secret env files like `.env` / `.env.local`). Treat this as a best-effort guard, not a sandbox: an allowed interpreter or shell utility can still read a file, so keep real secrets in environment variables or CI secrets, never in committed files. The non-secret `.env.example` stays readable on purpose.
- **Hooks**: deterministic gates (see [Hooks](#hooks) below).

Tune the allow/deny lists for your stack. For Claude Code on the web, the environment can also grant tool permissions; keep `.claude/settings.json` as the committed source of truth so local and cloud runs behave the same.

> Personal overrides go in `.claude/settings.local.json` (gitignored). Never put secrets in `.claude/settings.json`.

### 3. Repository Secrets (for CI/CD)

<!--
  /init-project replaces this with exact secret names and platform-specific
  instructions for the configured tracker and Git provider.
-->

The CI pipelines require secrets to be configured in your repository settings. These enable the auto-Done pipeline to transition features in your tracker when PRs are merged.

| Secret | Purpose | Where to get it | Where to add it |
| --- | --- | --- | --- |
| `{TRACKER}_API_KEY` | Auto-transition features to Done on merge | Your issue tracker's API settings | Your Git provider's repository secrets settings |

**Platform-specific instructions:**

- **GitHub:** Repository → Settings → Secrets and variables → Actions → New repository secret
- **GitLab:** Repository → Settings → CI/CD → Variables (set as masked + protected)
- **Bitbucket:** Repository → Repository settings → Pipelines → Repository variables (set as secured)

**Optional Slack notifications.** If `/init-project` generated the PR notification pipeline (`notify-slack.yml`), it is opt-in and off by default. Enabling it takes three required steps: a `NOTIFY_SLACK` repository Variable, a `SLACK_WEBHOOK_URL` Secret, and pushing the workflow from a local CLI. See [Notes & edge cases → Slack notifications (opt-in)](#slack-notifications-opt-in) for the full setup and the reasoning behind it.

**Tracker-specific API key locations:**

- **Linear:** Linear → Settings → Account → API → Personal API keys → Create key
- **ClickUp:** ClickUp → Settings → Apps → API Token
- **Jira:** Atlassian → Account → Security → API tokens → Create API token (also requires `JIRA_EMAIL` secret)

### 4. Development Environment

> Specific requirements (Docker, Node.js, Python versions, etc.) depend on the tech stack configured in `CLAUDE.md` and will be documented here after the scaffold feature creates the project infrastructure.

---

## Framework Overview

### How It Works

This framework uses Claude Code to plan, implement, test, and deliver features autonomously. The commands you run are plan, build, and revise; the lifecycle they produce is **plan → review → build → review → revise → merge → Done**. The two reviews are human checkpoints (on the plan PR and the implementation PR), revise is the loop back when a review asks for changes, and Done is set automatically by CI on merge.

The **primary dispatch surface is Claude Code on the web** (or `claude --remote`): each session runs in an isolated, Anthropic-managed cloud VM, clones the repo, and prepares a PR. Because each invocation is its own independent session, you can fire `/plan-feature US-101`, `US-102`, `US-103` in parallel, one per feature. See [Dispatching Sessions](#dispatching-sessions).

### Key Files

| File | Purpose | Who edits it |
| --- | --- | --- |
| `CLAUDE.md` | Project configuration (tech stack, MCP config, design refs, toggles) plus always-on standard imports | Generated by `/init-project` from the plugin, then filled in by a human |
| `.mcp.json` | Live MCP server definitions (project scope); written by `claude mcp add`. The template ships `.mcp.json.example` as a sample | Human / `claude mcp add` |
| `.claude/settings.json` | Permissions and autonomy posture (hooks are wired by the plugin, not here) | Bootstrap committed; permissions written by `/init-project`, then tunable |
| commands, skills, subagents, hooks | The pipeline logic and gate scripts | Provided by the `claude-dev` plugin (not files in this repo) |
| `.claude/rules/*.md` | Engineering standards (coding/testing/review) | Materialized from the plugin by `/init-project`; do not hand-edit |
| `.claude/project_state.json` | Status mapping + feature registry (tracker source); tracker-less (Git provider + `work_item_source` only) under `local` source | Generated by `/init-project` |
| `.claude/feature_map.md` | Feature dependencies and execution waves (tracker/greenfield); flat or absent under `local` source | Generated by `/init-project`, maintained manually if features change |
| `.claude/artifacts/{ID}/` | Per-feature plans, reports, and User Acceptance Testing (UAT) scripts | Generated by agents |

### Status Flow

Features move through these statuses. The framework maps them to your tracker's actual status names during `/init-project`.

```
Todo → Planning → Plan Review → Ready for Build → In Progress → In Review → Done
                       ↑                                              |
                       |              (revision needed)               |
                       └──────────────────────────────────────────────┘
```

| Status | Who sets it | How |
| --- | --- | --- |
| Todo | Default | Initial state in tracker |
| Planning | AI agent | `/plan-feature` starts |
| Plan Review | AI agent | `/plan-feature` creates draft PR |
| Ready for Build | **Human** | You approve the plan in the tracker |
| In Progress | AI agent | `/build-feature` starts |
| In Review | AI agent | `/build-feature` creates ready PR |
| Done | **CI pipeline** | Automated on merge to main |

---

## Commands, Skills, and Subagents

The commands, skills, and subagents are provided by the `claude-dev` plugin, not files in this repo. Once the plugin is installed, each command is available as `/claude-dev:<command>`; the bare `/<command>` form (used in the examples throughout these docs) also works when no other plugin claims the same name. Each command invokes the matching **skill**, which holds the full multi-phase procedure and auto-loads (by its description) even in Claude Code on the web and Routines. Commands also pin a **model** per task (strongest for planning, cheaper for mechanical work).

### Subagents

The plan / build / review split is expressed with dedicated subagents provided by the plugin (`planner`, `builder`, `reviewer`):

| Subagent | Role | Tools / Permissions | Model |
| --- | --- | --- | --- |
| `planner` | Architect plans (`/plan-feature`) | Read-mostly; writes only plan artifacts under `.claude/artifacts/` | opus |
| `builder` | Implementation + tests (`/build-feature`, `/revise-feature`, `/fix`) | Read/write code, run tests, commit and push | sonnet |
| `reviewer` | Self-review against `review_standards.md` (`/build-feature`, `/fix`) | **Read-only** (Read, Grep, Glob); cannot edit, run, or commit | sonnet |

The reviewer is intentionally read-only so it cannot quietly fix what it is meant to critique. It reports findings; the builder applies the fixes.

### Hooks

The `claude-dev` plugin wires three deterministic hooks in its manifest (`.claude-plugin/plugin.json`). The scripts live in the plugin and are referenced via `${CLAUDE_PLUGIN_ROOT}/hooks/`; they are **not** files in this repo:

- **`branch-guard.sh`** (PreToolUse on `git commit`/`git push`): hard-enforces the branch convention. **Blocks** the command on an unrecognized branch (it allows `feature/*`, the standalone `refactor/*` and `test/*` branches that `/refactor` and `/generate-tests` create, and `main`/`master`/`develop`), so cloud surfaces that start on an auto-generated `claude/<slug>` branch cannot commit or push there. The block message is fed back to the agent, which then switches to the `feature/{FEATURE_ID}-{slug}` branch from `feature_map.md` and retries. **Fails open** when it cannot resolve a branch (detached HEAD, not a repo). This is what makes the auto-Done pipeline's feature-ID parsing reliable.
- **`test-gate.sh`** (PreToolUse on `git push`): detects the project's test runner and runs it before any push. **Fails closed** (blocks the push) if tests genuinely fail; **fails open** (allows) when no test setup exists yet, or when the runner collects no tests (pytest exit 5, e.g. a docs-only plan push), so it never blocks before the scaffold feature has built the project. It runs the full detected suite on every push, including docs-only plan pushes; if that is slow on a large repo, scope the command in the script and leave the full suite to CI.
- **`format-on-edit.sh`** (PostToolUse on Write/Edit/MultiEdit): formats the file just written (ruff/black for Python, prettier for JS/TS) if a formatter is installed. Advisory only; it never blocks.

These turn "the prompt says run tests" into an enforced gate. Both scripts are stack-agnostic; edit their detection blocks to match your toolchain.

> **Scope of the gates.** `branch-guard` and `test-gate` are `PreToolUse` hooks on `Bash`, so they act only on `git` run through the shell, which is how the skills commit and push. A commit or push made through the Git provider MCP/API (rather than the `gh`/`git` CLI) does not pass through them. In normal runs the agents use shell `git`, so the gates fire; treat them as a strong in-session guard, not an absolute one, and keep the CI checks (PR tests, auto-Done branch match) as the backstop.

### Per-Command Model Pinning

| Command | Model | Rationale |
| --- | --- | --- |
| `/init-project` | sonnet | Interactive setup and reasoning over dependencies |
| `/plan-feature` | opus | Architecture and planning, strongest model |
| `/build-feature` | sonnet | Capable implementation at lower cost |
| `/revise-feature` | sonnet | Targeted fixes |
| `/refactor` | haiku | Mechanical, low-risk cleanup |
| `/generate-tests` | haiku | Mechanical test generation |
| `/diagnose` | sonnet | Reasoning over code to find real defects |
| `/fix` | sonnet | Condensed plan+build for one work item |
| `/security-scan` | sonnet | Local Aikido scan and finding triage |

Adjust the `model:` field in the plugin's `commands/*.md` (these files live in the `claude-dev` plugin, not in this repo), then cut a new plugin version.

### `/init-project`

**Run locally, once per project.** Interactive setup wizard. Do not run in unattended surfaces (it stops for human input).

What it does:
1. Verifies MCP connections (`claude mcp list`)
2. Sets up tracker status mapping
3. Imports features from the issue tracker
4. Analyzes dependencies and assigns execution waves
5. Identifies the scaffold feature (first to be built)
6. Generates `feature_map.md`, `project_state.json`, CI pipelines, documentation

### `/plan-feature {FEATURE_ID}`

**Dispatch as an autonomous session, one per feature.** Delegates architecture to the `planner` subagent.

1. Checks dependencies (all must be Done)
2. Fetches feature details from MCP
3. Creates feature branch
4. Detects if this is the scaffold feature and includes infrastructure setup in the plan
5. Generates architect plan with file manifest, API contracts, testing strategy
6. Creates a draft PR with the plan
7. Updates tracker status to Plan Review

When re-planning (dispatched again for a feature with an existing plan): reads PR review comments via Git provider MCP and revises the plan to address the feedback.

### `/build-feature {FEATURE_ID}`

**Dispatch as an autonomous session, one per feature.** Requires an approved plan. Delegates implementation to the `builder` subagent and self-review to the read-only `reviewer` subagent.

1. Verifies feature is "Ready for Build" and plan exists
2. Scaffolds project infrastructure (if scaffold feature)
3. Implements frontend, backend, and/or API integration (as specified by the plan)
4. Generates and runs unit + integration tests
5. Generates E2E test specs (executed by CI, not the agent)
6. Self-reviews against coding and security standards
7. Runs refactor gate (if enabled)
8. Generates UAT artifacts (if enabled)
9. Updates README and DEVELOPMENT.md if infrastructure was created
10. Updates PR title and converts to ready-for-review
11. Updates tracker status to In Review

### `/revise-feature {FEATURE_ID}`

**Dispatch as an autonomous session.** For applying PR review feedback.

1. Reads PR review comments via Git provider MCP
2. Applies targeted fixes (via the `builder` subagent)
3. Re-runs affected tests
4. Pushes updates (PR auto-updates)
5. Does not change tracker status (feature stays In Review)

### `/refactor frontend|backend|{FEATURE_ID}`

**Dispatch as a session or run locally.** Standalone code quality improvement.

1. Scans target files against the refactoring checklist
2. Applies RECOMMENDED improvements
3. Verifies tests still pass
4. Creates PR with changes

### `/generate-tests {scope} [--tier unit|integration|e2e|all]`

**Dispatch as a session or run locally.** Standalone test generation.

Supported scopes: `backend`, `frontend`, a feature ID, or a file/directory path.

1. Analyzes source files to determine which test tiers are warranted
2. Generates tests following testing standards and `CLAUDE.md` Test Configuration paths
3. Runs unit + integration tests (E2E deferred to CI)
4. Creates PR with generated tests

---

## Dispatching Sessions

**Primary surface: Claude Code on the web (or `claude --remote`).** Connect the repo, then start one session per feature with the command as the prompt (e.g. `/plan-feature US-101`). Each session runs in its own isolated cloud VM, clones the repo (so it needs the committed `CLAUDE.md`, `.claude/`, and `.mcp.json`), and opens a PR. Fire several in parallel for a whole wave.

**Other surfaces (optional):**

- **Routines**: saved prompt + repo + connectors, triggered on a schedule / webhook / API call, fully unattended. The natural home for "when a feature moves to Ready for Build, auto-run `/build-feature`." Skills committed in the repo load automatically in a Routine. Do **not** run `/init-project` here (it is interactive).
- **GitHub Actions** (`anthropics/claude-code-action`): autonomous PR review/fixes on comment or cron triggers. A good home for `/revise-feature` and review edges, alongside the auto-Done pipeline.
- **Headless `claude -p`**: orchestrate dispatch from your own infrastructure.

All commands except `/init-project` are designed to run unattended. Interactive checkpoints exist only in `/init-project`.

---

## Development Workflow

### Phase 0: Project Setup (once)

1. Fill in `CLAUDE.md` with your project's configuration
2. Add the two MCP connections with `claude mcp add --scope project ...` and verify with `claude mcp list`
3. Run `/init-project` in a local interactive Claude Code session, and follow the wizard to map statuses, import features, and assign waves
4. Review generated files
5. **Commit and push everything to the repo** (cloud sessions clone these files)
6. Add required repository secrets for CI (see Prerequisites)

### Phase 1: Planning

1. Look at `feature_map.md`, identify the scaffold feature (marked ✅) and Wave 1
2. **Dispatch the scaffold feature first:** `/plan-feature {SCAFFOLD_ID}`
3. Review the scaffold plan PR; it should include infrastructure setup
4. For plans that need changes: leave PR comments, re-dispatch `/plan-feature` for that feature
5. For approved plans: move the feature to "Ready for Build" in your tracker
6. After the scaffold feature is built and merged, dispatch `/plan-feature` for remaining Wave 1 features
7. Review plan PRs, approve in tracker when ready

### Phase 2: Implementation

1. Dispatch one session per approved feature, each running `/build-feature {FEATURE_ID}`
2. Each session implements the plan, runs tests, and creates a ready-for-review PR
3. **Review implementation PRs**: standard code review
4. For PRs that need changes: leave review comments, dispatch `/revise-feature {FEATURE_ID}`
5. For approved PRs: merge to main → CI auto-transitions to Done

### Phase 3: Next Wave

1. Once all features in the current wave are Done (merged), the next wave's dependencies are satisfied
2. Return to Phase 1 for the next wave
3. Repeat until all waves are complete

### Parallel Execution

- Features within the same wave can be planned and built simultaneously by separate sessions
- Each feature runs on its own branch, with no conflicts between parallel sessions
- The `shared_risk_notes` column in `feature_map.md` flags potential file conflicts between features in the same wave
- Features from different waves should NOT run simultaneously if there are unresolved dependencies

### Adding work after initial setup

**Tracker source.** When new features are added to the tracker after `/init-project`:

1. Re-run `/init-project` locally. It detects existing features and adds new ones.
2. The dependency graph and waves are regenerated. Existing features are preserved.
3. Commit and push the updated `feature_map.md` and `project_state.json`.
4. Dispatch sessions for the new features as part of their assigned wave.

**Local or hybrid source.** No re-init is needed per item, which makes this the natural mode for a repo that accrues work incrementally. Create a `docs/issues/{ID}.md` (or let `/fix "describe it"` create one), then run `/fix {ID}` for a small change, or `/plan-feature {ID}` → `/build-feature {ID}` for a larger one. Local items carry their own `branch` and `depends_on` in frontmatter, so the pipeline resolves them without `feature_map.md`. Repeat whenever new work appears.

---

## Feature Map

`.claude/feature_map.md` is the local source of truth for:

- **Dependencies:** Which features block which other features
- **Waves:** Grouping of features that can run in parallel
- **Branch names:** Consistent naming for feature branches (prefix `feature/`)
- **Scaffold flag:** Which feature sets up project infrastructure
- **Shared risks:** Flags for potential merge conflicts within a wave

Agents read this file to check dependencies. They then verify actual status via MCP.

---

## Testing

Testing is integrated into the build pipeline at multiple layers.

| Layer | Generated in | Executed in | Blocks merge? |
| --- | --- | --- | --- |
| Unit tests | `/build-feature` | During build (+ test-gate hook on push) + CI on PR | Yes |
| Integration tests | `/build-feature` | During build + CI on PR | Yes (if enabled) |
| E2E tests | `/build-feature` | CI on PR | Depends on toggle |
| UAT Gherkin | `/build-feature` | CI on merge to main | Yes (if enabled) |
| UAT manual script | `/build-feature` | Human tester | No (reference only) |

Test directory paths and naming conventions are configured in `CLAUDE.md` → Test Configuration. Toggle configuration is in `CLAUDE.md` → Feature Toggles.

---

## CI/CD

> **GitHub is the reference implementation.** The plugin ships lint-checked workflow templates for GitHub only (`pr-tests.yml`, `auto-done.yml`, `notify-slack.yml`, and the optional `security-scan.yml`) that `/init-project` copies in and adapts. For GitLab and Bitbucket there is no shipped template: `/init-project` generates `.gitlab-ci.yml` / `bitbucket-pipelines.yml` (including the security-scan job) from the GitHub templates as the reference to port. The pipeline behaviour described below is identical across providers; only GitHub has a canonical file to diff against today.

### PR Pipeline

Triggers on PR open and push:
- Runs unit tests
- Runs integration tests (if enabled)
- Runs E2E tests (if enabled)
- Reports results as PR status checks

### Merge Pipeline

Triggers when PR is merged to main:
- Extracts feature ID from branch name (`feature/{FEATURE_ID}-*`)
- Reads `.claude/project_state.json` for the feature's `external_id` and the `done` status name
- Calls the tracker's REST API to transition the feature to Done (using the repository secret)
- Validates UAT Gherkin scenarios are well-formed (if enabled)

> **Local work-item source:** with `Work Item Source: local`, the merge pipeline does not call a tracker API. It sets `status: done` in `docs/issues/{ID}.md` and commits that back to the default branch (a `[skip ci]` commit), so no tracker API key or secret is needed. See `.claude/rules/work_items.md`.

> **UAT step:** validates that each `e2e/uat/scenarios/*.feature` file is well-formed Gherkin; it does not run them as browser tests, and is a clean no-op when UAT is off. See [Notes & edge cases → Why UAT is validated, not executed](#why-uat-is-validated-not-executed).

> **Branch prefix:** the auto-Done pipeline matches the `feature/{FEATURE_ID}-{slug}` branch name, which `branch-guard.sh` hard-enforces in-session. See [Notes & edge cases → Branch prefix and auto-Done](#branch-prefix-and-auto-done) if you dispatch with a different prefix.

### Required Secrets

> See Prerequisites → Repository Secrets above for exact names and setup instructions.

### Security scanning (Aikido)

Security scanning is optional, controlled by the **Security Scanning** toggle in `CLAUDE.md` → Feature Toggles (`ENABLED` blocks on findings, `OPTIONAL` reports without blocking, `DISABLED` skips it). It uses [Aikido](https://www.aikido.dev/), which scans for vulnerable dependencies (SCA), exposed secrets, IaC issues, SAST, malware, and license risks. There are three approaches:

- **Native PR gating (recommended):** enable it from the Aikido dashboard. Aikido scans the PR diff on its own infrastructure and posts a check, with no workflow file and no CI minutes.
- **CI release gate:** the `security-scan.yml` workflow `/init-project` adds, which runs the Aikido local scanner on the default branch (needs the `AIKIDO_API_KEY` repository secret).
- **Local, no repo or CI required:** run `/security-scan` to scan the working directory with the same local scanner.

The default policy blocks on newly introduced findings at or above High severity; because Aikido compares the branch diff, a pre-existing backlog does not block new work.

**Full setup (creating the Aikido account, retrieving the token, the dashboard click-paths, and branch protection) is in the plugin's [security scanning guide](https://github.com/bemayker/claude-dev-plugin/blob/main/docs/security-scanning.md).** Policy and triage live in the plugin's `security_standards.md`; act on a finding with `/fix {ID}`.

---

## Configuring the Framework

### For a New Project

1. Create a repo from `claude-dev-template` and open it in Claude Code. It prompts you to install the `claude-dev` plugin (the template commits the marketplace bootstrap), so approve that once.
2. Add MCP connections (`claude mcp add --scope project ...`); skip the tracker if Work Item Source is `local`.
3. Run `/init-project`. It generates `CLAUDE.md` and the `.claude/settings.json` permissions from the plugin, then stops so you can fill in `CLAUDE.md` (project description, tech stack, test config, MCP names). The generated file defaults to `Source: tracker`; if you want `local` work items, set `Source: local` now, before the re-run.
4. Re-run `/init-project` to finish: for `tracker` source it maps statuses, imports work items, assigns waves, and generates CI and docs. For `local` source there is no tracker import, so you manage work as files under `docs/issues/` (the incremental flow); CI and the auto-Done file-flip are still generated.
5. Commit and push all generated files.
6. Add repository secrets (see Prerequisites).
7. Build and merge the scaffold feature first, then dispatch the rest of the wave.

### What NOT to Edit

The commands, skills, subagents, and hooks are provided by the `claude-dev` plugin, not files in this repo, so there is nothing to edit here. `.claude/rules/*.md` is materialized from the plugin by `/init-project` and is overwritten on every run, so do not hand-edit it: change a standard in the plugin and re-materialize.

`.claude/settings.json` is generated by `/init-project` from the plugin, but its allow/deny lists and autonomy posture are then yours to tune. To change pipeline behaviour, a gate script, or a standard, edit the plugin rather than editing files in this repo.

## Framework distribution and modes

### Distribution

The framework ships as the `claude-dev` plugin (private `bemayker` marketplace). The plugin owns commands, skills, agents, hooks, and the rule standards; this repo owns configuration only. Update with `claude plugin update claude-dev@bemayker`.

### Updating the framework in this repo

The plugin updates independently of your project, but the always-on standards under `.claude/rules/` are *materialized copies*, so a plugin update does not refresh them on its own. To pull a new plugin version into this repo:

1. `claude plugin update claude-dev@bemayker` (run `claude plugin marketplace update bemayker` first if the marketplace floats on `main`).
2. Re-run `/init-project` locally. It re-materializes the six always-on rules into `.claude/rules/` and regenerates `.claude/project_state.json`, without overwriting your `CLAUDE.md` or a customized `.claude/settings.json`.
3. Review the diff in `.claude/rules/` (and any regenerated docs), then commit and push so cloud sessions pick up the new standards.

Skipping step 2 leaves this repo on the old standards even after the plugin updates. Never hand-edit `.claude/rules/*.md`: those copies are overwritten on every `/init-project` run.

### Project mode

- `greenfield`: the original flow. `init-project` imports the backlog, assigns waves, recommends a scaffold feature, and generates CI.
- `existing`: `init-project` discovers the codebase (stack, layout, test setup, conventions) into `CLAUDE.md`, skips scaffolding and CI generation, and never overwrites host config. Plan, build, and refactor follow `existing_codebase.md`: match existing patterns, scope review and coverage to the diff, and never restructure existing code as part of a change.

### Work item source

- `tracker`: features and status live in the issue tracker via MCP (default).
- `local`: work items are markdown files under `docs/issues/` (schema in `work_items.md`). No tracker MCP required; status lives in each file's frontmatter and is set to done when the PR merges.
- `hybrid`: tracker items resolve from the tracker, everything else from `docs/issues/`.

### Investigative commands

- `/diagnose {scope}`: scans existing code for bugs, performance issues, and risky patterns, writing each finding as a local work item under `docs/issues/`. Analysis only.
- `/fix {ID | description}`: a condensed plan+build for one work item that keeps the self-review, test, and refactor gates but skips the separate plan-review PR. It promotes to `/plan-feature` if the change turns out large or architectural.
- `/security-scan {scope}`: runs an Aikido scan locally (no git repo or CI required) and reports findings, optionally writing them as `docs/issues/` items for `/fix`. Analysis only. See [Security scanning (Aikido)](#security-scanning-aikido) under CI/CD.

---

## Troubleshooting

Common first-run problems and the fix. Deeper, rarer edge cases are in [Notes & edge cases](#notes--edge-cases).

**The plugin did not install when I opened the repo.** The auto-install prompt comes from the committed `.claude/settings.json` (`extraKnownMarketplaces` + `enabledPlugins`). If it did not appear, install by hand: `claude plugin marketplace add bemayker/claude-marketplace` then `claude plugin install claude-dev@bemayker`. Both repos are private, so you need GitHub read access first.

**The plugin clone asks for credentials or fails to authenticate.** The plugin is fetched over HTTPS through your git credential helper. Run `gh auth login` (or cache a PAT in your credential helper) and retry. No SSH key is needed.

**The GitHub MCP fails to authenticate, or reports "does not support dynamic client registration".** GitHub's MCP endpoint does not support the OAuth flow Claude Code uses. Authenticate with a Personal Access Token in a header instead (see [MCP connections](#1-mcp-connections-mandatory)); do not use the interactive "Authenticate" path for GitHub.

**The issue-tracker MCP shows connected but agents cannot read items.** OAuth trackers (ClickUp, Linear, Jira) need a browser approval: run `/mcp` in a session and complete it, choosing the right workspace. `claude mcp list` showing "connected" means the server is reachable, not that you have authorized it.

**`/init-project` "did nothing", it just told me to fill in `CLAUDE.md`.** That is the expected first pass: it generates `CLAUDE.md` and stops so you can fill in project details, then you re-run it to finish. It is the only interactive command; do not run it in a cloud or unattended surface.

**A pipeline command stops with "Run /init-project first".** `.claude/project_state.json` is missing or was never committed. Run `/init-project` locally, then commit and push the generated `.claude/` files: cloud sessions clone the repo and need them present. (`/diagnose` and `/fix` are the only commands that do not require `project_state.json`.)

**A cloud session committed on a `claude/...` branch and auto-Done never fired.** The `branch-guard` hook blocks commits on unrecognized branches (such as `claude/*`) in-session, but a branch pushed another way can slip through. Ensure work lands on `feature/{ID}-{slug}`; for recovery see [When auto-Done fails after a merge](#when-auto-done-fails-after-a-merge).

**A cloud run stopped to ask for a permission.** The allow-list in `.claude/settings.json` is missing a tool the run needed, often an `mcp__<server>__*` entry. `/init-project` syncs the MCP allow-list to your `.mcp.json`; if you added a server later, re-run it (or add the entry by hand). Never store secrets in `.claude/settings.json`.

---

## Notes & edge cases

Deeper rationale and edge cases pulled out of the happy path above. You do not need these for a normal run.

### Slack notifications (opt-in)

If `/init-project` generated the PR notification pipeline (`notify-slack.yml`, section 6.3 of that skill), it is opt-in and off by default. It runs in CI, so it fires reliably where an in-session Stop hook would be killed first. Enabling it takes three steps, all required: (1) add a repository **Variable** `NOTIFY_SLACK` = `true` (Variables tab, not Secrets); (2) add a repository **Secret** `SLACK_WEBHOOK_URL` with a Slack Incoming Webhook URL (Secrets tab; the Incoming Webhooks app must be permitted in your workspace); (3) push the workflow file from a **local** CLI, since workflow files need a token with the `workflow` scope that cloud-session tokens lack. Verify without a PR via the Actions tab -> "Notify Slack on PR" -> "Run workflow" (the `workflow_dispatch` trigger posts a test message). The job always runs and its log states why it did or did not post; a missing toggle or secret is reported as a notice/warning, **not** a failed check, so a half-finished setup never shows as a red X.

### Why UAT is validated, not executed

The `.feature` files under `e2e/uat/scenarios/` are acceptance-criteria artifacts and have no Cucumber/BDD step definitions, so they are not executable by `playwright test` (the executable browser checks are the `*.spec.ts` E2E specs, run by the PR Test pipeline). The merge pipeline therefore **validates** that each scenario is well-formed Gherkin rather than driving a browser. Do not point `npx playwright test` at `e2e/uat`: Playwright's `testDir` is the E2E spec directory, finds no tests there, and exits 1 ("No tests found"). The step is guarded on the presence of `e2e/uat/scenarios/*.feature`, so it is a clean no-op when UAT generation is off. Want truly executable UAT? Add a BDD runner (e.g. `playwright-bdd`) and generate step definitions next to the `.feature` files.

### Branch prefix and auto-Done

The auto-Done pipeline runs in CI, not in Claude Code, so it uses the tracker REST API (not MCP). It matches the `feature/{FEATURE_ID}-{slug}` branch name. The `/plan-feature` and `/build-feature` skills set this branch name, and the `branch-guard.sh` hook hard-enforces it in-session by blocking commits/pushes on an unrecognized branch (it allows `feature/*` plus the `refactor/*` and `test/*` prefixes the standalone commands use, and the base branches), even when the dispatch surface starts the session on an auto-generated `claude/<slug>` branch (Claude Code on the web and Routines). If you intentionally dispatch with a different prefix, adjust `branch-guard.sh` and align the branch regex in the auto-Done pipeline accordingly.

### When auto-Done fails after a merge

The merge to main is the source of truth, not the tracker transition. If the PR merges but the auto-Done step fails (an expired or missing tracker API key, a tracker outage, or a branch name the regex could not parse), the code is safely on main but the work item is stranded in its previous status (usually In Review). The merge is **not** rolled back and nothing is lost; only the status label is stale. To recover:

1. **Read the failed job log** (Actions tab on GitHub, Pipelines on GitLab/Bitbucket). It states which step failed and why, the same precheck pattern the Slack job uses.
2. **If it was a transient failure or a fixed secret:** re-run the job. On GitHub, Actions -> the failed run -> "Re-run jobs". The transition is idempotent (it sets a status, it does not toggle), so re-running is safe.
3. **If the branch name did not match:** the feature ID could not be parsed from the branch. Set the item to Done by hand in the tracker this once, then ensure future branches use `feature/{FEATURE_ID}-{slug}` (the `branch-guard.sh` hook enforces this in-session; a manually pushed branch can still bypass it).
4. **Local work-item source:** the equivalent failure is the file-flip commit not landing, most often because the default branch is protected and the CI bot is not allowed to push to it. Allow the `github-actions` bot to bypass the branch protection (GitLab/Bitbucket: grant the CI user push access to the protected branch), then re-run the job; or set `status: done` in `docs/issues/{ID}.md` by hand and commit it with `[skip ci]`.

A stale status never blocks merging or building; dependency checks read the tracker (or the local file) live, so once the status is corrected the next wave proceeds normally.

### Hotfixes and rollbacks

The lifecycle (plan → review → build → review → revise → merge → Done) is forward-only by design, but production fixes still fit it without a special mode:

- **Hotfix:** treat it as a normal small work item. Create a `docs/issues/{ID}.md` (or a tracker item), then run `/fix {ID}` on its `feature/{ID}-{slug}` branch. All the build-time gates (self-review, test gate, refactor gate) and the auto-Done flip still apply, so a hotfix is just a fast trip through the same pipeline. If the fix turns out larger than expected, `/fix` will stop and recommend `/plan-feature`.
- **Reverting a merged feature:** open a normal revert PR (`git revert <merge-commit>` on a `feature/{ID}-revert-{slug}` branch, or your provider's "Revert" button followed by renaming the branch to the `feature/` prefix so auto-Done and the gates apply). Record it as its own work item so the revert is tracked and reviewed like any other change rather than force-pushed onto main.
- **What not to do:** do not force-push to main or rewrite merged history (the deny-list in `.claude/settings.json` blocks the common force-push flags for agents: `--force`, `-f`, and `--force-with-lease`; the same discipline applies to humans). Roll forward with a revert or a hotfix instead.

### Same-wave merge conflicts

Features in the same wave run on independent `feature/` branches and merge one at a time, so a later branch can fall behind `main` and conflict with what already merged. `build-feature` deliberately does **not** auto-rebase (see Branch Setup: it fetches `main` for reference but never rebases on its own); reconciling against a moved `main` is a human-triggered step. When a feature's PR shows conflicts, or its CI fails only because `main` advanced:

1. **Locally:** `git checkout {branch}`, `git fetch origin main`, then `git rebase origin/main` (or `git merge origin/main` if you prefer a merge commit), resolve conflicts, and push. The branch keeps its `feature/` prefix, so `branch-guard` and `test-gate` still apply and the push re-runs the suite.
2. **Or via the pipeline:** merge `main` into the branch, then dispatch `/revise-feature {ID}` to let the `builder` reconcile the change against what merged.

Use the `shared_risk_notes` column in `feature_map.md` to spot the file overlaps most likely to conflict: review those features' PRs together and merge the lower-risk one first. If two same-wave features touch the same files heavily, sequence them (merge one, rebase the other) rather than building both blindly in parallel.
