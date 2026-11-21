---
description: Suggest UI elements and libraries with reasoning, let the user pick, then write architecture, UI, frozen contracts, demo script, and pitch.
---

# /hack:design: design artifacts + pitch

Follow `${CLAUDE_PLUGIN_ROOT}/reference/conventions.md`, including its preflight.

**Reads:** `.hackathon/chosen-idea.md`, `rubric.json`, `config.json` · **Writes:** `.hackathon/design/{elements,questions,architecture,ui,contracts,demo}.md`, `.hackathon/pitch.md`

## Step 1: suggestions
1. If `chosen-idea.md` doesn't exist, say "Run `/hack:pick` first" and stop.
2. If `design/elements.md` already has ticked items (a re-run after `/hack:amend`), show the current selection and the stale list from `changelog.md`, then ask: **Keep selections, regenerate stale files** (Recommended) / **Re-suggest elements**. If they keep the selections, skip to step 3.
3. Otherwise launch `hack:design-advisor` with: `Mode: suggest`, the project root, and the plugin root (absolute paths).

## Step 2: question loop (the user picks the design elements)
1. Read `design/elements.md` and `design/questions.md`.
2. Ask with `AskUserQuestion`: one question per category, up to 4 per call. Use `multiSelect: true` for "Key UI elements" and similar multi-pick categories, single-select for frameworks and libraries. Options = the checklist items (recommended first). Put each item's reasoning in the option description. Include the open questions from `questions.md` in the same calls.
3. Write the answers back: tick `[x]` the chosen items in `elements.md` (and add any "Other" answers as ticked items, with the user's reason). Fill the `Answer` column in `questions.md`.
4. Repeat until every category has at least one ticked item and no question is `(open)`. If an answer creates a new question (for example "Supabase" → "auth needed?"), add it and ask it.

## Step 3: write the design
Launch `hack:design-advisor` with `Mode: write`, the project root, and the plugin root. If it reports a missing element or a new question, ask the user (back to step 2), then run `write` again.

## Step 4: check
Check that these exist and are non-empty: `design/architecture.md` (with a `repo-structure` block), `design/ui.md`, `design/contracts.md` (interface IDs `C-01…`, each with a **Mock** line), `design/demo.md` (with a fallback plan), and `pitch.md` (sections mapped to rubric criteria, 5 Q&As). Also spot-check that no technology appears in architecture.md that isn't ticked in elements.md. Fix problems by re-running `write`.

## Step 5: record and commit
- Append to `changelog.md`: `- <ts> — design generated (elements: <short list>)`. If this re-run cleared stale files, add `(stale cleared: …)`.
- Update `state.json`: phase `design`. Commit `v<version>: design`.
- Show a summary: the stack, the screens, the contract IDs, and the demo outline. Finish with: "Next: `/hack:finalize` to build OVERVIEW.md and confirm the designs".
