---
description: Split the confirmed design into N disjoint slices and write one HANDOFF file per teammate plus OWNERSHIP.md. Runs automatically after /hack:finalize confirmation; re-run it after the team changes.
---

# /hack:handoff: split + export

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md`, including its preflight.

**Reads:** `OVERVIEW.md`, `.hackathon/design/*`, `.hackathon/config.json` · **Writes:** `.hackathon/handoff/HANDOFF-<n>-<name>.md` × N, `.hackathon/handoff/OWNERSHIP.md`

## Step 1: preconditions
1. `OVERVIEW.md`, `design/architecture.md` (with a `repo-structure` block), and `design/contracts.md` must exist. If any is missing, name the command that creates it and stop.
2. If `state.designs_confirmed` is false and this was run directly (not from `/hack:finalize`), warn: "Designs aren't confirmed yet. Handoffs may go stale." Ask: **Run `/hack:finalize` instead** (Recommended) / **Generate anyway**.
3. N = `config.team.length`. If the team has changed since the last handoff (compare with the existing files in `.hackathon/handoff/`), say who was added or removed.
4. Set `state.json` phase to `handoff`.

## Step 2: split
Launch `hack:work-splitter` with the project root and plugin root (absolute paths).

## Step 3: validate (the §9 checks)
Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/validate_handoff.py" "<project root>"`. It checks:
- exactly N HANDOFF files, one per teammate
- no path in two owners' OWN lists (no overlapping or nested directories across owners)
- every repo-structure path has an owner in OWNERSHIP.md
- every CONSUME row has a matching PROVIDE row in another file, and a mock
- exactly one integration owner and one demo & pitch owner
- every task lists only files inside its owner's paths
- every referenced interface exists in contracts.md

If it fails, re-launch `hack:work-splitter` with the failure list ("Fix these validation failures: …"). Repeat up to 3 times. If it still fails, report the remaining failures honestly and **don't** mark the handoff as done.

## Step 4: update OVERVIEW and commit
1. Fill the "Team handoffs" table in `OVERVIEW.md`: `| <n> | <name> | <slice> | [HANDOFF-<n>-<slug>.md](.hackathon/handoff/HANDOFF-<n>-<slug>.md) |`.
2. Append to `changelog.md`: `- <ts> — handoff generated for N=<n> (<names>)`.
3. Commit `v<version>: handoff`. Stage `.hackathon/handoff` so deleted files are recorded too (`git add -A .hackathon/handoff`).

## Step 5: tell each teammate
Print:
```
Integration owner: <name> (merges at CP1/CP2/CP3; scaffolds the repo first)
Demo & pitch owner: <name>

<name> → .hackathon/handoff/HANDOFF-<n>-<slug>.md   (branch feat/<n>-<slice>)
...

How to start (every teammate, at the same time, after the integration owner's scaffold is on main):
  git pull origin main
  claude
  > Read .hackathon/handoff/HANDOFF-<n>-<slug>.md and build it.
```
If the repo has no remote, say that it needs one (for example a GitHub repo) before teammates can pull. Don't create or push to a remote yourself unless the user asks.
