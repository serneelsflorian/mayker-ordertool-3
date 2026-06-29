# Existing-codebase mode

## 1. When this applies

This rule governs behaviour when `CLAUDE.md` Project Mode is set to `existing`: an established codebase the framework was added to, rather than a greenfield project it scaffolds from nothing. In `greenfield` mode this rule is inert and the standards apply as written.

## 2. Precedence: follow existing patterns first

In existing mode, the conventions already present in the code you touch take precedence over the framework's prescriptive standards. The standards in `coding_standards.md`, `testing_standards.md`, and the others are the fallback for net-new code that has no local precedent. Concretely:

- Match the architecture, layering, naming, file structure, and test layout of the surrounding code and sibling modules.
- Apply framework defaults (for example Router to Service to Repository, atomic design, utility-first CSS) only when introducing code in an area that has no established pattern.
- Never restructure, rename, or re-architect existing code as part of a feature or fix. Behaviour-preserving cleanup is the job of `/refactor`, run with an explicit scope.

## 3. Diff-scoped review and refactor

In existing mode, review and refactor checks apply to the lines and files this change adds or modifies, not the whole repository. A pre-existing pattern in untouched code is not a finding. When the surrounding code already does something the standards discourage, matching it for local consistency is preferred over diverging: note the deviation rather than "fixing" it inside an unrelated change.

## 4. Coverage on changed code

Coverage targets apply to the code this change introduces or modifies, not the entire existing codebase. Do not block on global coverage of legacy code.

## 5. No scaffolding, no overwrites

Existing mode never runs the scaffold phase, never generates project structure, and never overwrites the host repo's README, CI configuration, or tooling config. `init-project` discovers the existing setup instead of creating one (see the init-project skill).
