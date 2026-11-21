# Interface contracts
**Status:** FROZEN at v<N> · Changes go through a contract change request in a HANDOFF file, and the integration owner applies them.

> Every teammate builds against these contracts and mocks everyone else's side.
> Each interface has an ID `C-<nn>`. HANDOFF files refer to interfaces by these IDs only.
> Use the project's real language for types (TypeScript, Python, etc.), not pseudo-code.

## Shared data models
```<language>
// Types used by more than one slice
```

## Interfaces

### C-01 · <METHOD> <path> (<short name>)
- **Provider:** <slice / directory>
- **Consumers:** <slices>
- **Request:**
  ```json
  {}
  ```
- **Response 200:**
  ```json
  {}
  ```
- **Errors:** `{ "error": { "code": "<CODE>", "message": "<text>" } }` with status <4xx/5xx> when <condition>
- **Mock:** <how a consumer fakes it: fixture JSON (inline above), stub function signature, or mock server command>

### C-02 · event `<event.name>` (<short name>)
- **Provider:** …
- **Consumers:** …
- **Payload:**
  ```json
  {}
  ```
- **Mock:** …

## Environment variables and config keys
| Key | Example | Used by | Provided by |
|---|---|---|---|
| `<KEY>` | `<example>` | <slice> | <integration owner / service> |

## Mock strategy (summary)
| Interface | Consumer fakes it with |
|---|---|
| C-01 | <fixture / stub / mock server> |

## Change log
| Version | Change | Requested by | Applied by |
|---|---|---|---|
