# Ownership map
> One owner per path. A directory entry (ending in "/") covers everything under it.
> Machine-checked by validate_handoff.py: keep the path in backticks in the first column and the owner's exact team name in the second.
> The table lists EVERY owned path, including the shared files (owned by the integration owner). It must match each HANDOFF's "Files you OWN" list.

## Paths
| Path | Owner | Purpose |
|---|---|---|
| `<dir/>` | <Name> | <purpose> |

## Shared files (integration owner: <Name>)
Only the integration owner edits these. Everyone else files a request in their HANDOFF.
- `<package.json or equivalent>`
- `<lockfile>`
- `<CI config>`
- `<.env.example>`
- `<README.md>`

## Roles
- **Integration owner:** <Name>
- **Demo & pitch owner:** <Name>

## Merge order
1. <integration owner's scaffold: root config + empty owned directories, merged to main first>
2. <providers before consumers>
3. …

## Integration checkpoints
- **CP1 (T+25%):** every provider serves its contract as a mock. Merge order above.
- **CP2 (T+60%):** real providers swapped in. Consumers switch off mocks.
- **CP3 (T+85%):** full demo run from `.hackathon/design/demo.md` on the merged `main`.
