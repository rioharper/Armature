---
name: init
description: Scaffold a standardized Armature robotics project in the current folder (docs/analysis/cad tree, git repo, project CLAUDE.md), then start the pitch interview.
disable-model-invocation: true
---

# Armature Init

The current folder is the project root.

## 1. Guard

If `CLAUDE.md` here already carries a `**Stage:**` line, this is an Armature project: report its stage and stop. A `CLAUDE.md` without one is somebody else's file: ask through AskUserQuestion whether to merge the template into it or replace it, and carry that answer into step 4.

The stop carries one repair: where `.mcp.json` names a `mcp/solidworks/server.py` path that no longer exists — a plugin update moved it — offer to rewrite that path from the current `${CLAUDE_PLUGIN_ROOT}`. Report and repair is the whole of a re-run; a project that has no `.mcp.json` wanted none.

## 2. Probe the machine

Run the plugin's environment probe and keep its output for the next two steps:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/env-probe.sh"
```

It prints `KEY=VALUE` and exits 0 whatever it finds, because an absence here is
something to plan around rather than an error. `PYTHON` is the invocation that
works on this machine — `py` and `absent` are different answers, and reading
them as the same is what put a stale "python is not on PATH" note in a project
that had python all along. Step 4 writes the result to `docs/environment.md`;
its format and rules are `references/environment-record.md`, two levels above
this skill.

## 3. Setup interview

Ask through the AskUserQuestion tool:

1. Project name and a one-line description.
2. CAD package: SOLIDWORKS / Fusion 360 / Onshape / undecided.
3. On SOLIDWORKS only: connect the SolidWorks MCP server to this project? It
   lets armature-cad's Done-when checks measure the live model instead of
   asking you to transcribe numbers. Two of its three prerequisites are
   already answered: state Windows and [uv](https://docs.astral.sh/uv/) on PATH
   from step 2's `OS_KIND` and `UV` instead of asking the user to vouch for
   them, and where either is missing, say so and recommend no — the server
   cannot start. The third — SolidWorks running while those checks run — is
   never true in advance, so it stays a question. Yes seeds
   `.mcp.json` in step 4, and Claude Code asks you to approve it on the next
   start. Every other answer leaves the project with no MCP server, which is
   why a Fusion, Onshape, or undecided project never sees one fail.
4. Builder profile: solo or team; fabrication access (printer, machining, hand tools); experience level.

Done when every placeholder in the template below has a value.

## 4. Scaffold

Create (bash):

```bash
mkdir -p docs/00-concept docs/01-spec docs/02-plan docs/testing \
         docs/reviews docs/research docs/datasheets \
         analysis/derivation analysis/model \
         cad/parts cad/assemblies cad/ots-parts
```

Seed these files:

- `docs/decisions.md`: header `# Decision log`, one column-format line
  `<!-- date · decision · why · supersedes -->`, and its first entry — the
  project init itself.
- `docs/datasheets/index.md`: header, the legend comment
  `<!-- Clauses read: the sections, tables, or pages actually verified. Price: list
  price at its quantity break, or "quote only" where the vendor publishes none;
  dated by Retrieved. File: the cached PDF, HTML snapshot, or image + transcript; a
  source with no saveable document points at its survey record,
  docs/datasheets/<task>-<subject>-<slice>.md. -->`,
  and the empty table
  `| P/N | Manufacturer | Key numbers | Clauses read | Price | Source URL | Retrieved | File |`.
- `docs/environment.md` from step 2's output, in the shape
  `references/environment-record.md` gives: one section for this machine,
  headed by hostname, OS, and today's date, closing with the gaps this project
  will actually feel — a missing SciPy blocks **armature-derive**, a missing
  `gh` blocks the issue tracker. No gap stops the scaffold.
- `cad/ots-parts/index.md`: header + empty table
  `| File | P/N | Datasheet row | Source URL | Retrieved |`.
- `.mcp.json`, only where step 3 said yes to the server:
  `{"mcpServers": {"solidworks": {"command": "uv", "args": ["run",
  "<plugin root>/mcp/solidworks/server.py"]}}}`. Write `<plugin root>` as the
  absolute path `${CLAUDE_PLUGIN_ROOT}` holds — a *project* `.mcp.json` is
  read without that substitution, so the placeholder itself would load
  verbatim and fail.
- `.gitkeep` in every scaffolded directory the seeds above leave empty (git
  drops empty directories).
- `.gitignore`:

```
__pycache__/
.pytest_cache/
~$*
*.bak
# absolute path into this machine's plugin install
.mcp.json
```

- `CLAUDE.md` from the template below, with the setup answers filled in.
  If step 1 chose merge, append the template's sections to the existing
  file, keeping its content above them.

Then `git init` (if not already a repo), stage only the files this scaffold
created or changed, and commit as `Initialize Armature project scaffold`.
Done when `git ls-files` lists every scaffolded directory.

## 5. CLAUDE.md template

```markdown
# <Project Name>

<one-line description>

**Stage:** concept
<!-- concept (armature-pitch) → spec (armature-spec) → plan (armature-plan)
     → analysis (armature-derive) → cad (armature-cad)
     → build (armature-bringup, armature-test) -->
**Latest artifacts:** none yet

## Glossary

The project glossary is `CONTEXT.md` at the repo root — frames, symbol
table, part numbering, CAD file naming, each term with an `_Avoid_:` line
naming the synonyms it displaces; armature-plan writes it. Challenge any
term, the user's or your own, that conflicts with `CONTEXT.md` the moment
it appears.

- Units: SI internally; imperial in parentheses when the shop works in it.
- Requirement numbering: RC-xxx = concept-level outcome
  (docs/00-concept/); REQ-xxx = verifiable engineering requirement with a
  verification method (docs/01-spec/).

## Standing rules

- Every datasheet number cited anywhere traces to a row in
  docs/datasheets/index.md (the armature-librarian agent maintains it). A row
  marked CANDIDATE is unconfirmed and carries no decision until the user
  confirms it.
- Red-team review (armature-red-team agent) before CAD hours or purchases.
- Any change to a mass, power draw, or cost updates
  docs/01-spec/budgets.md (created by armature-spec) in the same session. A cost
  estimate cites the index row whose Price it reads; a part priced `quote only`
  stays a guess until a human asks a vendor. Nothing debits a reserve line item
  directly — a debit elsewhere debits it, and one that drives its margin negative
  breaches the requirement it holds: fail that REQ in the row and in
  docs/01-spec/traceability.md, not in a sentence above the table.
- Every design decision gets a line in docs/decisions.md. When all three
  hold — hard to reverse, surprising without context, a real trade-off —
  it also gets a short ADR in docs/adr/ (`NNNN-slug.md`, a paragraph;
  create the directory with the first one) linked from that line.
- OTS CAD models live in cad/ots-parts/ with an index row linking
  model → P/N → datasheet.
- The machines this project is built on are recorded in
  docs/environment.md, dated, one section each. Read it before assuming a
  tool is installed; refresh it by re-running the plugin's
  scripts/env-probe.sh, never by editing the file.
- Every artifact write ends in a git commit.

## Builder profile

- CAD package: <answer>
- Fabrication: <answer>
- Team: <answer>
- Experience: <answer>
```

## 6. Hand off

Report the scaffold commit and any gap `docs/environment.md` names, then call the Skill tool with "armature-pitch"
and begin the interview in this session.
