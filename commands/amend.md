---
description: Free-form loop for changing the chosen project through chat. Every change goes to chosen-idea.md and changelog.md, and affected design files get flagged as stale.
argument-hint: "[the change you want]"
---

# /hack:amend: amend loop

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md`, including its preflight.

**Reads:** everything in `.hackathon/` and `OVERVIEW.md` · **Writes:** `.hackathon/chosen-idea.md`, `.hackathon/changelog.md`

Arguments (first change, optional): `$ARGUMENTS`

## Entering the loop
1. If `.hackathon/chosen-idea.md` doesn't exist, say "Run `/hack:pick` first" and stop.
2. Set `state.json` phase to `amending`.
3. If the phase was `complete` or `handoff` (designs already confirmed), warn: "Designs were already confirmed and handoffs exist. Amending will set `designs_confirmed` to false, and you'll need `/hack:design` + `/hack:finalize` to regenerate the handoffs." Ask before continuing. If the user continues, set `designs_confirmed: false`.
4. Say: "Amend mode. Describe changes one at a time or all at once. Say **done** when finished."
5. If the arguments contain a change, handle it right away.

## For every change the user describes (this loop spans multiple turns)
1. If the change is ambiguous, ask **one** clarifying question (batched if there are several).
2. Apply it to `.hackathon/chosen-idea.md` (idea text, scope, tech assumptions, risks; keep the structure).
3. If the change affects scoring (scope, type, or a major feature), re-check the idea's feasibility, creativity, and UI-impact reasoning, and update the scores in `chosen-idea.md` honestly with a short note.
4. Append to `.hackathon/changelog.md`: `- <ts> — <one-line change>` and `(stale: <files>)` if any.
5. **Stale check.** If design files exist, decide which are affected and list them:
   - feature or scope change → `design/architecture.md`, `design/ui.md`, `design/demo.md`, `pitch.md`
   - data or API change → `design/contracts.md`, `design/architecture.md`
   - stack change → `design/elements.md` plus everything above
   - story or positioning change → `pitch.md`
   Tell the user "Now stale: …".
6. Briefly confirm what changed, then wait for the next change.

## Leaving the loop
When the user says **done** (or similar):
- Summarize the changes made in this session and the full stale-file list.
- Commit `v<version>: amend: <short summary>`. The phase stays `amending`.
- Suggest: "Next: `/hack:design` (regenerates the design files; stale ones: …)".
