# hack: hackathon ideation → team handoff plugin for Claude Code

Takes a team from "we received the hackathon track" to a confirmed project plus **one HANDOFF file per teammate**, so every teammate can run their own Claude Code on their own slice at the same time, with minimal merge conflicts.

- **Files are memory.** Every phase reads and writes `.hackathon/`. Nothing depends on chat history.
- **The rubric and config drive everything.** Scores, rankings, and design choices cite `rubric.json` and `config.json`.
- **Human in the loop** for picking SDGs, the idea, design elements, and confirming the designs.
- **Parallel research** (one subagent per SDG) and **parallel build** (N disjoint slices with frozen contracts).
- **Software-engineering scope.** Hardware only as a thin layer around software.

## Install

This repo is both the plugin (`hack`) and a one-plugin Claude Code marketplace (`hackathon-tools`). Inside Claude Code:

```text
/plugin marketplace add jimmerino2/claude-plugin-hackathon
/plugin install hack@hackathon-tools
```
Then run `/reload-plugins` (or restart Claude Code). The commands appear as `/hack:start`, `/hack:ideas`, and so on.

If the repo is private, you need read access and git authenticated with GitHub (`gh auth login` or an SSH key).

To try it for a single session without installing, clone the repo and point Claude Code at it:
```bash
git clone https://github.com/jimmerino2/claude-plugin-hackathon.git
claude --plugin-dir ./claude-plugin-hackathon
```
Requirements: git. Python 3 (stdlib only) for the helper scripts; without it, the commands do the same checks by hand.

## Workflow

```
/hack:start     fill in start.md → rubric.json + config.json (focus + weights) → v0
/hack:ideas     pick ≤3 SDGs → 5 researched ideas per SDG (parallel) → ranking → v1
/hack:pick      choose an ID (or merge two) → chosen-idea.md
/hack:amend     ┐ change the idea through chat (logs to changelog, flags stale design files)
/hack:design    │ suggest elements → you tick them → architecture, ui, frozen contracts, demo, pitch
/hack:finalize  ┘ OVERVIEW.md + tag v<N> → "Designs confirmed?"  No → back to /hack:amend
                                                                Yes → /hack:handoff → tag final
/hack:handoff   N slices → OWNERSHIP.md + HANDOFF-<n>-<name>.md × N (validated)
/hack:status    phase, version, focus, recent changes, next command
```

## Commands

| Command | Phase | Reads | Writes |
|---|---|---|---|
| `/hack:start` | Intake | `start.md` | `start.md` (template), `track.md`, `rubric.json`, `config.json`, `state.json`, `CLAUDE.md` |
| `/hack:ideas` | Ideation | `track.md`, `rubric.json`, `config.json` | `sdgs.json`, `ideas/sdg-<n>.md`, `ideas/ranking.md` |
| `/hack:pick` | Finalize idea | `ideas/` | `chosen-idea.md` |
| `/hack:amend` | Amend loop | everything | `chosen-idea.md`, `changelog.md` |
| `/hack:design` | Design + pitch | `chosen-idea.md`, `rubric.json`, `config.json` | `design/*.md`, `pitch.md` |
| `/hack:finalize` | Overview, version, confirm | everything | `OVERVIEW.md`, commit + tag, `state.json` (+ handoff on Yes) |
| `/hack:handoff` | Split + export | `OVERVIEW.md`, `design/*`, `config.json` | `handoff/HANDOFF-<n>-<name>.md` × N, `handoff/OWNERSHIP.md` |
| `/hack:status` | Any | `state.json` | nothing |

## Focus and weights

`config.focus` says what the project is aimed at. `ui_weight + feasibility_weight = 1.0`:

| focus | UI | feasibility |
|---|---|---|
| `wow` | 0.7 | 0.3 |
| `realistic` | 0.3 | 0.7 |
| `balanced` | 0.5 | 0.5 |

There's no default. If neither is given, `/hack:start` asks. Contradicting values (`realistic` + UI 0.7) also trigger a question.

Ranking (shown with the numbers in `ranking.md`):
```
wow     = avg(creativity, ui_impact)
balance = ui_weight * wow + feasibility_weight * feasibility
final   = 0.5 * rubric_fit + 0.5 * balance - 0.3 * max(0, similarity - 5)
```
The mix values can be changed in `config.json → ranking_mix`. Constraint: at least one idea with feasibility ≥ 8 and one with creativity ≥ 8.

## Project files

```
<project>/
├── CLAUDE.md  OVERVIEW.md  start.md
└── .hackathon/
    ├── state.json  track.md  rubric.json  config.json  sdgs.json  chosen-idea.md  changelog.md  pitch.md
    ├── ideas/      sdg-<n>.md (×≤3), ranking.md
    ├── design/     elements.md questions.md architecture.md ui.md contracts.md demo.md
    └── handoff/    OWNERSHIP.md, HANDOFF-<n>-<name>.md (×N)
```

## How a teammate uses their HANDOFF file

1. The **integration owner** does their T1 first: scaffold every directory plus the root config and dependencies, and push to `main`.
2. Everyone else: `git pull origin main`, `git checkout -b feat/<n>-<slice>`, `claude`, then:
   > Read .hackathon/handoff/HANDOFF-<n>-<name>.md and build it.
3. Everyone builds against mocks of the other slices (from `design/contracts.md`). Nobody edits contracts or shared files; they append requests to their HANDOFF instead.
4. The integration owner merges at **CP1** (T+25%, mocks up), **CP2** (T+60%, real providers), and **CP3** (T+85%, full demo run).

After a teammate joins or leaves: edit `config.json → team`, then run `/hack:handoff`.

## Plugin layout

```
claude-plugin-hackathon/
├── .claude-plugin/marketplace.json   (makes the repo installable via /plugin marketplace add)
├── .claude-plugin/plugin.json
├── commands/   start ideas pick amend design finalize handoff status
├── agents/     sdg-ideator competitor-scout idea-ranker design-advisor work-splitter
├── templates/  start.md rubric.json config.json idea.md OVERVIEW.md pitch.md contracts.md HANDOFF.md OWNERSHIP.md
├── reference/  conventions.md (shared rules for all commands), sdgs.md
├── scripts/    rank.py check_links.py validate_handoff.py
├── CLAUDE.md   (copied into each hackathon project)
└── README.md
```

### Helper scripts
| Script | Purpose |
|---|---|
| `scripts/rank.py <project> [--format md\|json]` | Parse ideas, check the schema (≤3 files, exactly 5 ideas each, every field, 3–6 demo steps), rank them, check the constraint |
| `scripts/check_links.py <project>` | Request every competitor link: `ok` / `dead` / `blocked` (the site refuses bots) |
| `scripts/validate_handoff.py <project>` | The 7 handoff validation checks (N files, disjoint ownership, coverage, PROVIDE/CONSUME + mocks, roles, task paths, contract refs) |

## Notes
- Subagents can't spawn subagents, so `sdg-ideator` follows the `competitor-scout` procedure itself. The main thread uses `competitor-scout` directly to re-research dead links and merged ideas.
- `idea-ranker` has `Bash` (beyond the spec's Read/Write) so it can run `rank.py`.
