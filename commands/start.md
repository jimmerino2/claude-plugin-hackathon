---
description: Start a hackathon project. Intake goes through a start.md template; then rubric.json, config.json, and state.json are written.
argument-hint: "[resume|restart]"
---

# /hack:start: intake

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md` (skip its preflight; this command creates the project).

**Reads:** `start.md` (user-filled) · **Writes:** `start.md` (template, if absent), `.hackathon/track.md`, `.hackathon/rubric.json`, `.hackathon/config.json`, `.hackathon/state.json`, `CLAUDE.md`

Arguments: `$ARGUMENTS`

## Step 1: existing project?
If `.hackathon/state.json` exists:
- Read it and say: "A hackathon project already exists here (phase `<phase>`, v`<version>`)."
- Unless the argument is `restart`, ask: **Resume** (Recommended: run the `/hack:status` logic and stop) or **Restart intake** (re-run steps 2–8 and overwrite intake files; later-phase files stay, and you warn they may now be stale).

## Step 2: the intake template
Intake works through a file, not an interrogation. **Never ask for intake information in chat before the template has been offered.**
- **`start.md` exists in the project root:** ask "Found `start.md`. Read it now?" If yes, go to step 4. If no, stop.
- **`start.md` does not exist:** copy `${CLAUDE_PLUGIN_ROOT}/templates/start.md` to `./start.md` unchanged. Then say:
  > I created `start.md`. Fill it in (the required items are marked), save it, then tell me "filled in".

  **Stop and end your turn.** Don't ask any other question.

## Step 3: wait
When the user says it's filled in ("done", "filled in", "ready", …), go to step 4. If they paste the info into chat instead, write it into `start.md` for them, then go to step 4.

## Step 4: read and check the required items
Read `start.md`. Parse:
| Item | Required | Parsing notes |
|---|---|---|
| Hackathon name | yes | |
| Track / theme | yes | Keep it verbatim. |
| Rubric | yes | Keep it verbatim in `rubric.json.source`. Extract criteria. Weights may be %, points, or fractions: normalize to fractions that sum to 1.0 (round to 2 decimals and fix the rounding on the largest criterion). |
| Team names | yes, ≥1 | Lines like `- Alice (skills: react, ml)`. Ignore empty `Name:` lines. Skills are optional. |
| Focus or weights | yes | One `[x]` box, or custom `ui = a, feasibility = b`. |
| Time, pitch length, tech preferences, notes | no | Use them if present. Never ask about them. |

**Focus and weights rules:**
- Presets: `wow` → 0.7 / 0.3 · `realistic` → 0.3 / 0.7 · `balanced` → 0.5 / 0.5 (ui / feasibility).
- Only a focus is given → apply its preset.
- Only weights are given → they must sum to 1.0, otherwise that's ambiguous. Derive the focus: ui > feasibility → `wow`; ui < feasibility → `realistic`; equal → `balanced`.
- Both are given and they agree (for example `wow` with ui 0.8 / 0.2) → keep the custom weights and the focus.
- Both are given and they **contradict** (for example `realistic` with ui 0.7) → ambiguous: ask which one they meant.
- More than one box is ticked → ambiguous.
- **No fixed default.** Neither a focus nor weights → missing: ask.

## Step 5: ask only about what is missing or ambiguous
Collect every problem first, then ask **once** with one batched `AskUserQuestion` call (≤4 questions; if there are more, do the most important first and the rest in a second call). Examples:
- Missing name, track, or rubric → ask for it (the user answers via "Other" free text), or suggest they edit `start.md`.
- Rubric has no weights → propose weights (equal, or reasoned from the rubric wording) as the recommended option, with "equal weights" as the alternative.
- Contradictory focus and weights → options: "Use focus `<x>` preset (a/b)", "Use custom weights (c/d), focus `<derived>`".
- A team entry that is only a placeholder (`Name`, `TBD`, `Person 1`) → ask for the real names. Placeholders are allowed only if the user confirms them.

**Do not ask about optional items** (timeframe, pitch length, tech, notes). **Never ask about or mention skills.**
If nothing is missing or ambiguous, ask nothing and go straight to step 6.

## Step 6: write the project files
Get a timestamp with `date -u +"%Y-%m-%dT%H:%M:%SZ"`. Create `.hackathon/` and write:
1. `.hackathon/track.md`:
   ```markdown
   # <Hackathon name>
   ## Track (verbatim)
   <track text>
   ## Constraints & preferences
   - Timeframe: <or "not given">
   - Pitch length: <n> min
   - Tech preferences: <or "none given">
   - Notes: <or "none">
   ```
2. `.hackathon/rubric.json`: shape of `${CLAUDE_PLUGIN_ROOT}/templates/rubric.json`. Weights must sum to 1.0. Record any derivation in `notes`.
3. `.hackathon/config.json`: shape of `${CLAUDE_PLUGIN_ROOT}/templates/config.json`:
   - `ui_weight + feasibility_weight` must equal 1.0 (check it).
   - `pitch_minutes`: from start.md, otherwise 3. `timeframe` and `tech_preferences`: from start.md, otherwise `""`.
   - `team`: `[{ "name": "...", "skills": [...] }]`. Use `"skills": []` when none are listed.
   - Copy `ranking_mix` from the template unchanged.
4. `.hackathon/state.json`: `{ "hackathon": "<name>", "phase": "intake", "version": 0, "designs_confirmed": false, "updated_at": "<ts>" }`
5. `.hackathon/changelog.md`: `# Changelog` followed by `- <ts> — v0 intake: project created`.
6. `CLAUDE.md`: copy `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md` to the project root. If a `CLAUDE.md` already exists and doesn't already contain `# Hackathon project rules`, **append** the rules to it instead of overwriting.

## Step 7: summary and confirmation
Print a short summary:
```
Hackathon: <name>
Focus: <focus> (UI <ui_weight> / feasibility <feasibility_weight>)
Team (N=<n>): <names>   ← N decides how many HANDOFF files get produced
Rubric: <criterion> <weight> · …
Pitch: <n> min · Timeframe: <…>
```
Then ask: "Does this look right?" (options: **Looks right** (Recommended) / **Change something**). If the user wants changes, apply them to the files (and to `start.md`, so the two agree) and show the summary again.

## Step 8: commit
If the folder isn't a git repo, run `git init`. Commit `v0: intake` as described in the conventions (version stays 0 for intake). Finish with: "Next: `/hack:ideas`".
