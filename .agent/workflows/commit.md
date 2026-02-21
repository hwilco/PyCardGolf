---
description: Generate a commit message from staged changes and optionally commit
---

## Steps

1. Run `git diff --staged; git status --short` to review the staged changes.
   - If nothing is staged, inform the user and stop. 
   - If there are unstaged changes, confirm with the user that they intend for those to remain unstaged.

2. Generate a commit message in this format:

   ```
   type: short lowercase description

   - Bullet point explaining a specific change or rationale.
   - Another bullet point for a separate change.
   - Wrap lines at ~72 characters.
   ```

   **Type** must be one of:
   | Type | When to use |
   |------|-------------|
   | `feat` | New feature or capability |
   | `fix` | Bug fix |
   | `refactor` | Code restructuring with no behavior change |
   | `chore` | Tooling, deps, CI, config changes |
   | `docs` | Documentation only |
   | `test` | Adding or updating tests only |
   | `style` | Formatting, whitespace, import sorting |

   **Rules:**
   - The summary line must be lowercase, imperative mood, no period.
   - Bullet points should explain *what* and *why*, not just restate the diff.
   - Reference specific files/classes with backticks when helpful.
   - Keep the full message concise — typically 3–6 bullet points, though don't leave out necessary details. When in doubt, check with the user.
   - If it's not in the diff, it doesn't belong in the message. (Purpose - avoid explaining internal decisions that don't impact the commit in its final form)

3. Present the commit message to the user for approval.

// turbo
4. Once approved, run `git commit -m "<message>"` with the approved message.