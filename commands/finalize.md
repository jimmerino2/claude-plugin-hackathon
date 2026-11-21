---
description: Build or refresh OVERVIEW.md, version it (commit + tag), and ask whether the designs are confirmed. No loops back to /hack:amend; Yes generates the handoffs and marks the project complete.
---

# /hack:finalize: overview, version, confirm

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md`, including its preflight.

**Reads:** everything · **Writes:** `OVERVIEW.md`, `state.json`, git commit + tags; on confirmation, everything `/hack:handoff` writes

## Step 1: preconditions
`chosen-idea.md`, `design/architecture.md`, `design/ui.md`, `design/contracts.md`, `design/demo.md`, and `pitch.md` must exist. If any is missing, say "Run `/hack:design` first" and stop.
If `changelog.md` lists stale files (`(stale: …)`) newer than the last `design generated` line, warn that those files are out of date and recommend `/hack:design` first. Ask before continuing.

## Step 2: build OVERVIEW.md
Set the phase to `finalizing`. Build `OVERVIEW.md` in the project root from `${CLAUDE_PLUGIN_ROOT}/templates/OVERVIEW.md`, filling every section from the files (never from chat memory):
- Header: hackathon, track (short), focus and weights, version = the version this commit will get (`state.version + 1`), status
- One-liner, problem & SDG, solution: from `chosen-idea.md` and `sdgs.json`
- Rubric mapping: **every** criterion in `rubric.json`, with its weight and a concrete feature
- Differentiation: from the competitor table
- MVP and stretch: from `chosen-idea.md`
- Tech stack: only the ticked items in `design/elements.md`
- Repo structure: copy the `repo-structure` block from `architecture.md`
- Demo flow (short), risks: from `demo.md` / `chosen-idea.md`
- Design file links, the team handoffs table (keep existing rows if present), and the latest 5 changelog lines

## Step 3: version
Increment `state.version`. Commit `v<N>: overview — <one-line summary>` and tag `v<N>` (see the tag rule in the conventions).

## Step 4: confirm
Show a 5-line summary of the design, then ask with `AskUserQuestion`: **"Are the designs confirmed?"**
- **Yes, confirmed: generate handoffs**
- **No, keep amending**

### No
Set the phase to `amending` and `designs_confirmed: false`. Append `- <ts> — v<N> reviewed, not confirmed` to the changelog and commit. Say: "Run `/hack:amend` to make changes, then `/hack:design` and `/hack:finalize` again."

### Yes
1. Set `designs_confirmed: true` and update `contracts.md`'s status line to `FROZEN at v<N>`.
2. Run the `/hack:handoff` procedure: read `${CLAUDE_PLUGIN_ROOT}/commands/handoff.md` and do its steps (skip its "not confirmed" warning). If its validation doesn't pass, stop here, report it, and leave the phase as `handoff`.
3. Set the phase to `complete`. Update OVERVIEW's status to `complete`. Append `- <ts> — designs confirmed; project complete` to the changelog.
4. Increment the version, commit `v<N>: complete`, and tag `final`.
5. Print a summary of all files: OVERVIEW.md, every design file, pitch.md, OWNERSHIP.md, and each HANDOFF file with its teammate. Then print the per-teammate start instructions from the handoff step.
