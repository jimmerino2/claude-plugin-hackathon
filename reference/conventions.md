# Shared conventions for every `/hack:*` command

Every command in this plugin follows these rules. Each command file says what is specific to it.

## Paths
- **Project root** = the current working directory. State lives in `.hackathon/` under it.
- **Plugin root** = `${CLAUDE_PLUGIN_ROOT}`. Templates are in `${CLAUDE_PLUGIN_ROOT}/templates/`, helper scripts in `${CLAUDE_PLUGIN_ROOT}/scripts/`, reference data in `${CLAUDE_PLUGIN_ROOT}/reference/`.
- In prompts to subagents, always pass **absolute paths** for both the project root and the plugin root.

## Files are memory
- Never rely on chat history for project facts. Before acting, read the files the command lists under "Reads".
- If chat and `OVERVIEW.md` (or any `.hackathon/` file) disagree, the file wins. Update the file instead of remembering the change.

## Preflight (every command except `/hack:start`)
1. If `.hackathon/state.json` does not exist, say "No hackathon project here. Run `/hack:start` first." and stop.
2. Read `.hackathon/state.json`, `.hackathon/config.json`, and `.hackathon/rubric.json`.
3. If a file the command needs is missing (for example `chosen-idea.md` for `/hack:design`), name the command that creates it and stop. Don't fabricate the missing input.

## Phases
`intake → ideation → picked → amending → design → finalizing → handoff → complete`

A command may be re-run (for example `/hack:ideas` again to regenerate ideas). When a re-run would overwrite later-phase work, say what will be overwritten and ask before continuing.

## Updating `state.json`
Read, modify, and write the whole JSON object. Always set `updated_at` to the current UTC time:
```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
```
Use the same command for timestamps in `config.json` and `changelog.md`.

## Versioned commits
Every phase ends with a git commit.
1. `state.version` counts phase commits. `/hack:start` commits `v0`. Every later phase commit first increments `state.version` by 1, writes `state.json`, then commits with message `v<version>: <summary>`.
2. Stage only plugin-managed paths: `git add .hackathon CLAUDE.md OVERVIEW.md start.md` (skip paths that don't exist). Never stage `.env` files or secrets.
3. If `git commit` fails because no git identity is configured, tell the user and ask whether to set a repo-local identity (`git config user.name` / `user.email`) with values they give. Don't invent an identity.
4. If there is nothing to commit, say so and continue. Don't create an empty commit.
5. Tags are created only by `/hack:finalize` (`v<N>` and `final`). If a tag already exists, use `git tag -f` only after telling the user.

## Asking the user
- Use `AskUserQuestion` for decisions: at most 4 questions per call, 2–4 options each (the tool adds "Other" for free text). Put the recommended option first and label it "(Recommended)".
- Batch related questions into one call. Don't ask one question per turn when several are known.
- If `AskUserQuestion` is unavailable (for example in a headless run), ask the same questions as a numbered plain-text list, then **end your turn and wait**.
- Never ask about optional information. In particular, **if `config.team[].skills` is empty or missing, never ask about skills and never mention them.**

## Honesty rules
- Never invent competitor projects, links, user numbers, or library facts. If something can't be verified, write "none found" or "unverified".
- Scores must be honest. Never raise a score just to satisfy a constraint. Change the idea instead.
- Report failures (a failed validation, a failed commit) as failures.

## Scope rule
Every idea and design must be buildable by **software engineers** in the hackathon timeframe. Hardware may appear only as a thin input or output layer around software (for example an off-the-shelf sensor feeding a software system). It is never the core difficulty, and the demo must work with simulated hardware data.

## Helper scripts (Python 3, standard library only)
- `python "${CLAUDE_PLUGIN_ROOT}/scripts/rank.py" <project-root>`: parses the ideas, checks the idea schema, computes the ranking, and checks the feasibility/creativity constraint.
- `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_links.py" <project-root>`: checks that every competitor link responds.
- `python "${CLAUDE_PLUGIN_ROOT}/scripts/validate_handoff.py" <project-root>`: runs the §9 handoff validation checks.

If `python` isn't available, try `python3` and then `py -3`. If none work, do the same checks by hand and say they were done by hand.
