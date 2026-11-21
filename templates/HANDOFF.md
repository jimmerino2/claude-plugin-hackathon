# HANDOFF <n>/<N>: <Name>: <slice title>

> **To Claude Code:** You are building ONE slice of a larger project with a team working in parallel.
> Read OVERVIEW.md and .hackathon/design/contracts.md first, then this file.
> Only touch files you own (below). Never edit the contracts. Build against mocks of other slices.

<!-- Machine-checked format (validate_handoff.py). Keep these exact shapes:
     - Role lines: "- **Integration owner:** yes|no" and "- **Demo & pitch owner:** yes|no"
     - OWN list: "- `path` : purpose" (directories end with "/")
     - Interface tables: the 2nd column holds a contract ID like C-01
     - Tasks: "- [ ] T<k> ..." followed by "  - Files: `a`, `b`" and "  - Acceptance: ..." -->

## Role
**Slice:** <slice title>
<one-paragraph goal>
- **Integration owner:** no
- **Demo & pitch owner:** no

## Context (short)
- **One-liner:** <from OVERVIEW>
- **For:** <target user>
- **Stack:** <copied from OVERVIEW tech stack>
- **Where your slice fits:** <1–2 sentences, which slices you talk to and how>

## Git
- Branch: `feat/<n>-<slice-name>`
- Commit only inside your owned paths. Rebase on `main` before opening a PR.

## Files you OWN (exclusive: only you edit these)
- `<path/or/dir/>` : <purpose>

## Files you may READ but must not edit
- `.hackathon/design/contracts.md`, `.hackathon/design/ui.md`, `OVERVIEW.md`
- Other slices' directories: <list>

## Shared files (edit only via the integration owner)
- <root manifest, lockfile, CI, env example, README, root config: list the real paths>
- Need a new dependency or env var? Add it to the "Requests" section at the bottom and tell the integration owner. Don't touch the shared file yourself, unless you ARE the integration owner.

## Interfaces
### You PROVIDE (others depend on these; they must match contracts.md exactly)
| Interface | Contract ref | Consumers |
|---|---|---|
| <name> | C-01 | <Name (slice)> |

### You CONSUME (build against the mock until the real one lands)
| Interface | Contract ref | Provider | Mock to use |
|---|---|---|---|
| <name> | C-02 | <Name (slice)> | <fixture/stub, created inside YOUR owned paths, e.g. `web/src/mocks/c02.json`> |

## Tasks (ordered)
- [ ] T1 <description>
  - Files: `<path inside your owned paths>`
  - Acceptance: <checkable criterion: a command, a URL, an observable behavior>
- [ ] T2 …
  - Files: …
  - Acceptance: …
- [ ] T<k> (stretch) …
  - Files: …
  - Acceptance: …

## Definition of done
- Every MVP task's acceptance criteria pass
- Tests or a runnable check for your slice pass on their own, against mocks: `<command>`
- You provide each "PROVIDE" interface exactly as specified in the contracts

## Integration checkpoints
- **CP1 (T+25%):** providers up as mocks. **CP2 (T+60%):** real providers swapped in. **CP3 (T+85%):** full demo run. Ask the integration owner to merge when each is ready.
- Your deliverable at each checkpoint: CP1 <…> · CP2 <…> · CP3 <…>

## Demo & pitch duties (only if you own them)
<Rehearsal and demo-run steps from .hackathon/design/demo.md and .hackathon/pitch.md, or "None.">

## Contract change requests / dependency requests
(Append here instead of editing shared files. The integration owner collects these and updates the contracts.)
| # | Type (contract / dependency / env var) | Request | Reason | Status |
|---|---|---|---|---|

## Notes
- **Risks:** …
- **Fallback behavior:** …
