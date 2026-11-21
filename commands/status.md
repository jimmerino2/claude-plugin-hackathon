---
description: Show the hackathon project's phase, version, focus and weights, recent changes, and the next command to run.
---

# /hack:status

Read-only. **Writes nothing.**

1. If `.hackathon/state.json` doesn't exist: say "No hackathon project here. Run `/hack:start`." If `start.md` exists but `.hackathon/` doesn't, add "(start.md found: `/hack:start` will offer to read it)". Stop.
2. Read `.hackathon/state.json` and `.hackathon/config.json`, plus the last 5 lines of `.hackathon/changelog.md` that start with `- ` (if the file exists).
3. Print:
   ```
   <hackathon> · phase: <phase> · v<version> · designs confirmed: <yes/no>
   Focus: <focus> (UI <ui_weight> / feasibility <feasibility_weight>) · Team N=<n>: <names>
   Recent changes:
     - …
   Next: <command> (<why>)
   ```
4. Next step by phase:
   | Phase | Next |
   |---|---|
   | intake | `/hack:ideas` |
   | ideation | `/hack:pick` |
   | picked | `/hack:amend` (optional) or `/hack:design` |
   | amending | `/hack:design` (regenerate any stale design files), then `/hack:finalize` |
   | design | `/hack:finalize` |
   | finalizing | answer the confirmation question in `/hack:finalize` |
   | handoff | `/hack:handoff` (finish or regenerate the handoff files) |
   | complete | Share `.hackathon/handoff/HANDOFF-*.md`. Each teammate says "Read .hackathon/handoff/HANDOFF-<n>-<name>.md and build it." |
5. Also flag any inconsistency you notice, without fixing it: a file the phase should have produced is missing, or the weights don't sum to 1.0.
6. **Empty optional fields are not problems.** Never mention or suggest filling in `skills`, `timeframe`, `tech_preferences`, or any other optional item. Print only the lines above, plus any real inconsistency from point 5.
