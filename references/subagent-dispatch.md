# Dispatching subagents — waves, not fan-out

Every dispatch site in the plugin runs under this rule: **armature-spec**'s inventors and
librarians, **armature-derive**'s Step 0 lookups, **armature-plan**'s frontier lookups,
**armature-wayfind**'s research tickets, **armature-cad**'s part lookups, and any
**armature-red-team** pass. Skills point here; they don't restate it.

## The wave

Send **two or three at a time**, and let a wave land before the next one goes out.

Each subagent spends the dispatching session's budget — its own context window, its tool
calls, and a share of the account's session limit — and spends it whether it succeeds or
dies. Five at once is not five times faster; it is five times the burn, and a run killed
mid-hunt takes its findings with it. In the armature demo, five librarians went out
together: four hit the platform's 600 s stall watchdog, and two re-dispatches then hit the
session limit.

**Name the cost before the wave.** A wave is the user's spend, so say how many agents are
going and that fan-out burns the session budget fast, then dispatch on their word. One
lookup mid-interview needs no such ceremony; it is the wave that does.

## Size each run to survive

- **One part, or one slice of a field, per run.** A prompt carrying five parts makes a run
  long enough to hit the stall watchdog, and the whole run dies together.
- **Prefer the agent that writes as it goes.** The librarian opens its ledger before its
  first fetch and appends every row and cached file the moment it exists (`Open the ledger`
  in `agents/librarian.md`), so a killed run still leaves what it found. The inventor and
  the red-team write once at the end: a dead run leaves nothing, so keep an inventor's idea
  family narrow and re-run rather than resume it.
- **Read the wreckage before re-hunting.** A file left in `docs/datasheets/staging/` is an
  unmerged run: read it, merge what stands, and re-dispatch only the gaps.

A wave is done when every part of it is merged, re-dispatched, or carried back to the user
as an open question — never when the agents simply stopped returning.
