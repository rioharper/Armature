---
name: init
description: Scaffold a standardized Armature robotics project in the current folder (docs/analysis/cad tree, git repo, project CLAUDE.md), then start the pitch interview.
disable-model-invocation: true
---

# Armature Init

The current folder is the project root.

## 1. Guard

If `CLAUDE.md` here already carries a `**Stage:**` line, this is an Armature project: report its stage and stop. A `CLAUDE.md` without one is somebody else's file: ask through AskUserQuestion whether to merge the template into it or replace it, and carry that answer into step 3.

## 2. Setup interview

Ask through the AskUserQuestion tool:

1. Project name and a one-line description.
2. CAD package: SOLIDWORKS / Fusion 360 / Onshape / undecided. On
   SOLIDWORKS, mention the bundled SolidWorks MCP server (`mcp/solidworks/`;
   Windows, a running SolidWorks session, and `uv` on PATH) that lets
   armature-cad's checks run against the live model.
3. Builder profile: solo or team; fabrication access (printer, machining, hand tools); experience level.

Done when every placeholder in the template below has a value.

## 3. Scaffold

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
- `cad/ots-parts/index.md`: header + empty table
  `| File | P/N | Datasheet row | Source URL | Retrieved |`.
- `.gitkeep` in every scaffolded directory the seeds above leave empty (git
  drops empty directories).
- `.gitignore`:

```
__pycache__/
.pytest_cache/
~$*
*.bak
```

- `CLAUDE.md` from the template below, with the setup answers filled in.
  If step 1 chose merge, append the template's sections to the existing
  file, keeping its content above them.

Then `git init` (if not already a repo), stage only the files this scaffold
created or changed, and commit as `Initialize Armature project scaffold`.
Done when `git ls-files` lists every scaffolded directory.

## 4. CLAUDE.md template

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
- Every artifact write ends in a git commit.

## Builder profile

- CAD package: <answer>
- Fabrication: <answer>
- Team: <answer>
- Experience: <answer>
```

## 5. Hand off

Report the scaffold commit, then call the Skill tool with "armature-pitch"
and begin the interview in this session.
