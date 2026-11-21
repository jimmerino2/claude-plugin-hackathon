---
description: Recommend SDGs, generate 5 researched ideas per selected SDG (parallel subagents), and rank them against the rubric and focus.
argument-hint: "[sdg numbers, e.g. 11 13]"
---

# /hack:ideas: ideation

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md`, including its preflight.

**Reads:** `.hackathon/track.md`, `rubric.json`, `config.json` · **Writes:** `.hackathon/sdgs.json`, `.hackathon/ideas/sdg-<n>.md`, `.hackathon/ideas/ranking.md`

Arguments: `$ARGUMENTS`

## Step 1: read
Read `.hackathon/track.md`, `.hackathon/rubric.json`, `.hackathon/config.json`, and `${CLAUDE_PLUGIN_ROOT}/reference/sdgs.md`.
If `.hackathon/ideas/` already has files, warn that re-running replaces them (and makes any `chosen-idea.md` refer to old IDs), and ask before continuing.

## Step 2: recommend and select SDGs (up to 3)
1. Recommend **3–6** SDGs that fit the track, each with a one-line reason tied to the track text. Show them as a table: `# | SDG | why`.
2. If the arguments already name SDG numbers (at most 3), use them and skip the question.
3. Otherwise ask with `AskUserQuestion` (`multiSelect: true`): options = your top 4 recommendations (the tool's "Other" lets the user type any SDG numbers). Ask them to pick **at most 3**.
4. If more than 3 are chosen, ask them to drop down to 3. If none are chosen, ask again.
5. Write `.hackathon/sdgs.json`:
   ```json
   { "recommended": [ { "sdg": 11, "name": "Sustainable Cities and Communities", "why": "..." } ], "selected": [11, 13] }
   ```

## Step 3: parallel ideation
Launch **one `hack:sdg-ideator` subagent per selected SDG, all in the same message** so they run in parallel. Prompt for each:
```
SDG: <n>, <name>
Why it fits: <why>
Project root (absolute): <abs path>
Plugin root (absolute): ${CLAUDE_PLUGIN_ROOT}
Write exactly 5 ideas to <abs path>/.hackathon/ideas/sdg-<n>.md following templates/idea.md.
Other SDGs being ideated in parallel: <list>. Avoid duplicating their obvious ideas.
```
Wait for all of them. If one fails or writes fewer than 5 ideas, re-run only that SDG.

## Step 4: verify links
Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_links.py" "<project root>"`.
- For links reported **dead** (DNS failure, 404, 410): launch `hack:competitor-scout` for that idea (title + description). Replace the competitor table and similarity score with what it returns. If it finds nothing, use the `none found` row. Run the scores of the affected idea back through the ranking.
- Links reported **blocked** (401/403/429/timeouts) are common for app stores and Product Hunt. Leave them, but list them in your summary as "could not be auto-verified".

## Step 5: rank and enforce the constraint
1. Launch `hack:idea-ranker` with the project root and plugin root.
2. If it reports **schema problems**, re-run the affected `hack:sdg-ideator` with: "Fix these problems in your file: <list>". Then re-rank.
3. If the **constraint** is missing (no idea with feasibility ≥ 8, or none with creativity ≥ 8), re-run the `hack:sdg-ideator` for the SDG the ranker recommended with: "Replace idea <ID> with a new idea that genuinely scores <feasibility|creativity> ≥ 8. Keep the other four unchanged." Then re-rank. Repeat at most twice, then report honestly if it's still unmet.

## Step 6: present
Show the user the ranking table (from `ranking.md`) and the three labelled picks: **Best overall**, **Most realistic**, **Most creative**, plus any unverified links.
Update `state.json`: phase `ideation`. Commit `v<version>: ideas` (this is v1 on a fresh project). Finish with: "Next: `/hack:pick` (pick an ID, or merge two)".
