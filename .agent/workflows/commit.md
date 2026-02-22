---
description: Generate a commit message from staged changes and optionally commit
---

## Steps

1. **Review Changes**
   - Run `git diff --staged` and `git status --short` to review staged changes.
   - If nothing is staged: Inform the user and stop.
   - If there are unstaged changes: Confirm with the user that these should remain unstaged before proceeding.

2. **Generate Commit Message**
   - **Format:**
     ```
     type: short lowercase description

     - Bullet point explaining a specific change or rationale.
     - Another bullet point for a separate change.
     - Wrap lines at ~72 characters.
     ```
   - **Allowed Types:** `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`.
   - **Constraint Rules:**
     - **Summary Line:** Lowercase, imperative mood, no trailing period, and ideally under 50 characters.
     - **Content:** Explain *what* and *why*, not just a restatement of the diff.
     - **Paths:** Use relative paths for files/classes; never include absolute paths (e.g., `/Users/...`).
     - **Formatting:** Use backslash-escaped backticks (\`code\`) for code references.
     - **Scope:** Typically 3–6 bullets. If it isn't in the diff, it doesn't belong in the message (no internal reasoning that didn't make the final commit).

3. **User Approval**
   - Present the final draft to the user for explicit approval.

4. **Execution**
   - Once approved, run the commit. 
   - *Note:* To handle multiline messages reliably, use standard input: 
     `echo "<message>" | git commit -F -`