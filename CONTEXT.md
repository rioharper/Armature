# Context

Glossary for the Armature plugin itself (not for user projects — their glossary lives in their own `CONTEXT.md`, alongside `docs/adr/`).

## Terms

- **Stage**: one step of the per-project pipeline (pitch → spec → plan → derive → CAD → build), recorded as the `Stage:` line in a user project's `CLAUDE.md`. A stage spans as many sessions as its plan's leaves need; each session resumes from the repo alone.
- **Session**: one agent context, roughly 100k tokens before output degrades. The unit of a plan's leaf task and of a wayfinder ticket; one session ends in one commit.
- **Leaf**: a plan task sized to one session. A parent task groups leaves and keeps the number that dependencies cite; a dependency on a parent means its last leaf. _Avoid_: subtask, step.
- **Effort**: a unit of work too big for one agent session, coordinated across sessions by a wayfinder map. An effort overlays the pipeline; it is not a stage and never moves the `Stage:` line.
- **Map**: the canonical artifact of an effort — destination, notes, decisions index, and fog — with decision tickets as children. Lives on the project's issue tracker.
- **Overlay**: the relationship between wayfinding and the pipeline: stages stay intact and become the means of resolving a map's tickets, rather than being absorbed or wrapped.
- **Executor**: who resolves a ticket or task — a stage skill, an agent (inventor / librarian / red-team), or the user. Ticket *types* (research / prototype / grilling / task) say what kind of question it is; the executor says who works it. Agents are executors, never ticket types.
