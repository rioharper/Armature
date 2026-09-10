# Changelog

## Unreleased

- Datasheet index: rows gain a **Clauses read** cell — the sections, tables, or pages actually verified — so a review probes what a row leaves open instead of re-asking what it already answers. The `File` cell now names the source kind: a cached PDF, a hand-written HTML snapshot, or an image plus the transcript beside it (many vendors publish no PDF); a source with nothing saveable points at the run's own record. `armature-librarian` opens one ledger per run under a single naming rule — a named-part run stages at `docs/datasheets/staging/<task>-<subject>.md` and is deleted at merge, a **survey** run writes `docs/datasheets/<task>-<subject>-<slice>.md`, which is permanent, so a survey that correctly confirms nothing and writes no index row still leaves its findings. A CANDIDATE row carries no decision until the user confirms it, in `init`'s standing rules, `armature-spec` Phase 4, and the red-team checklist — which, with the red-team's inputs, now reads the survey records too. `CONTEXT.md` gains **Survey file**.
- `armature-librarian`: gains Bash. Every run opens a staging file (`docs/datasheets/staging/<task>-<subject>.md`) before its first fetch and ledgers each row and cached file as found, so a stalled or rate-limited run leaves partial results; the file is the run's only report. A pre-confirmed P/N is cached in the run — the PDF fetched by `curl`, the index row shell-appended, never read-modify-written — while a candidate waits in staging for the user's confirmation and the agent's Merge step, which deletes the file once every row is merged. Dispatch paragraphs in spec, derive, and cad point at the contract. `CONTEXT.md` gains **Staging file**.
- `armature-plan`: the task unit is the session (roughly 100k tokens, one commit); parent tasks group lettered leaves; a review and its rework, a report, and a change of executor are cuts. Tasks are cut at every third-party wait so the agent-doable half has its own `Done when`. Estimates are sessions plus wall-clock, from an executor-aware starting table, with `Actual:` on closed leaves and a same-kind re-cut at each phase gate. `CONTEXT.md` gains **Session** and **Leaf**.

## 1.2.1 — 2026-09-08

`init` hardening:

- The scaffolded `CLAUDE.md`'s Stage comment now maps each stage to the skill that works it (`concept (armature-pitch) → … → build (armature-bringup, armature-test)`), so a fresh session routes without the plugin README.
- A pre-existing non-Armature `CLAUDE.md` triggers a merge-or-replace question instead of being overwritten.
- The scaffold commit stages only the files init created or changed, keeping unrelated untracked files out in pre-existing repos.
- Standing rules annotate `docs/01-spec/budgets.md` as created by `armature-spec`; the CAD-package question mentions the bundled SolidWorks MCP server when the answer is SOLIDWORKS.

## 1.2.0 — 2026-08-30

Absorbs and adapts material from [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT, see `NOTICE.md`) and brings every agent-facing doc to one writing standard.

### New skills

- `armature-wayfind` — multi-session efforts charted as a map of decision tickets on the project's issue tracker (GitHub Issues or local markdown, auto-detected), resolved one ticket per session by the stage skills and agents.
- `armature-test` — test-driven development for robot software, default-on in Armature projects: red → green at unit and simulation level, bench seams handed to `docs/testing/bench-seams.md`.
- `armature-debug` — user-invoked bench debugging: a red-capable feedback loop before any hypothesis, then one variable at a time. Ships `scripts/human-loop.template.sh`, the shared step/confirm/capture primitive.
- `armature-bringup` — a plan's bring-up or verification test as an executable bash procedure, measurements recorded into its `docs/testing/` report.

### Renames

- `armature-concept` → `armature-pitch`, `armature-math` → `armature-derive`, `armature-teacher` → `armature-teach`. Every skill name now reads as a verb; agents keep their noun personas. Artifact paths (`docs/00-concept/`, `analysis/`) are unchanged.

### Changed

- Pitch, spec, and plan interviews run in frontier rounds via `AskUserQuestion` (recommended answer first), checkpoint each round, and send lookups to `armature-librarian` mid-interview.
- Project glossaries move from `docs/02-plan/` to the user project's `CONTEXT.md`; `init`'s `CLAUDE.md` template carries the inline-challenge rule and a three-gate ADR tier over `docs/decisions.md`.
- `armature-spec` and `armature-cad` draft questionnaires (`references/questionnaire.template.md`) for unknowns a third party holds.
- `armature-derive` gains `references/phase-boundaries.md`, the five-option context-boundary tree.
- Every `SKILL.md`, agent, and reference rewritten to the writing standard: duplicated rules single-sourced, one trigger per description branch, checkable done-conditions, hand-offs as Skill-tool calls. Agent descriptions carry their dispatch contracts.
- Repo-level `CLAUDE.md`, `docs/agents/issue-tracker.md`, and `docs/agents/domain.md` formalize the GitHub tracker and single-context domain docs.
- README gains a routing table and credits; `NOTICE.md` carries the MIT attribution.

## 1.1.0

- `armature-cad` executable build recipes (build123d): part definitions run as programs that check realized mass, COM, and inertia against `analysis/model/params.py`, self-validate features, render projected views, and sweep link envelopes for interference.
- SolidWorks MCP server (`mcp/solidworks/`): nine verification tools attached to a running session.

## 1.0.0

- First plugin release: `/armature:init`, the concept → spec → plan → math → CAD pipeline, the teacher skill, and the red-team, inventor, and librarian agents.
