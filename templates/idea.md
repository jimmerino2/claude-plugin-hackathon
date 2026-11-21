<!--
Idea block format. Each ideas/sdg-<n>.md file starts with a header, then has EXACTLY 5 blocks like this.
The header line must be exactly "## [SDG<n>-<k>] <Title>" (k = 1..5); rank.py parses it.
Keep every field label exactly as written. Scores are numbers 0-10 (decimals are allowed).
-->
# SDG <n>: <SDG name>
> Why this SDG fits the track: <one line>

## [SDG<n>-<k>] <Title>
- **Type:** <free text, any software-engineering project type, e.g. agentic assistant, browser extension, data pipeline, IoT-software system, mobile app, game, developer tool…>
- **Description:** <2–3 sentences>
- **Target user & problem:** <who, and what pain>
- **Competitor analysis:**

  | Existing project | Link | Overlap | Our differentiator |
  |---|---|---|---|
  | <name> | <real URL you opened or saw in search results> | <what is the same> | <what we do differently> |

  <If nothing similar was found, write a single row: | none found | — | — | — |>
- **Scores (0–10, each with a one-line reason):**
  - Similarity: <x> — <reason> (higher = more similar to existing work = worse)
  - Feasibility: <x> — <reason> (buildable by this team in the timeframe)
  - Creativity: <x> — <reason>
  - UI impact: <x> — <reason> (how much visual and demo "wow" the UI can carry)
  - Rubric fit: <x> — <one-line reason>
  - Rubric breakdown: <Criterion A> <score> · <Criterion B> <score> · … (rubric fit = weighted sum using rubric.json weights)
- **Demo workflow:**
  1. <what judges see first>
  2. <…>
  3. <…>
