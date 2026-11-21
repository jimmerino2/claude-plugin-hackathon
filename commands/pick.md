---
description: Choose the idea to take forward (by ID, or merge two) and write chosen-idea.md with MVP vs. stretch scope, tech assumptions, and risks.
argument-hint: "[idea ID, or ID+ID to merge]"
---

# /hack:pick: finalize the idea

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md`, including its preflight.

**Reads:** `.hackathon/ideas/*` · **Writes:** `.hackathon/chosen-idea.md`

Arguments: `$ARGUMENTS`

## Step 1: choose
1. Read `.hackathon/ideas/ranking.md` and the `sdg-*.md` files. If there's no ranking, say "Run `/hack:ideas` first" and stop.
2. If the arguments give a valid ID (`SDG11-3`) or a merge (`SDG11-3+SDG13-1`), use that.
3. Otherwise ask with `AskUserQuestion`. Options: the Best overall (Recommended), Most realistic, and Most creative picks (labelled with ID, title, and final score; de-duplicate if one idea holds two labels). "Other" accepts any ID or `ID+ID` to merge.
4. If `chosen-idea.md` already exists, warn that it will be replaced and ask first.

## Step 2: merge (only if two IDs)
Combine the strongest parts of both into one coherent idea. Ask one question if it's unclear which core the merged idea keeps. A merged idea needs fresh competitor research: launch `hack:competitor-scout` with the merged title and description, and use its table and similarity score.

## Step 3: write `.hackathon/chosen-idea.md`
```markdown
# Chosen idea: <title>
**ID:** <ID or ID+ID> · **SDG:** <n> <name> · **Type:** <type> · **Picked:** <ts>

## Idea
<the full idea block: description, target user & problem, competitor table, scores, demo workflow>

## Scope
### MVP (must work in the live demo)
- <3–6 bullets, sized to config.timeframe and team size N>
### Stretch
- <ordered by value/effort>

## Tech assumptions
- <stack assumptions, data sources, APIs (free tier? key needed?), and simulated data needed for the demo>

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
```
Keep the scope within the software-engineering rule (the conventions' scope rule).

## Step 4: record and commit
- Append to `.hackathon/changelog.md`: `- <ts> — picked <ID>: <title>`.
- Update `state.json`: phase `picked`. Commit `v<version>: pick <ID>`.
- Show the MVP list and finish with: "Next: `/hack:amend` to change anything, or `/hack:design`."
