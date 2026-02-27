---
description: Run a structured PR review against the current branch
---

## Steps

1. Retrieve the `git diff` against the target branch (usually `beta`).
   - Identify the core purpose of the changes based on the diff and any recent commit messages.

2. Run the project's lint and type-check tooling to surface mechanical issues:
   - `poetry run ruff check .`
   - `poetry run isort --check-only --diff .`
   - `poetry run pyright`

3. Evaluate the diff against these criteria:
   - **Type Safety:** Flag any issues surfaced by Pyright. Flag overly broad types (like `Any`) where a specific type could be inferred.
   - **Docstrings:** Ensure new public functions/classes have docstrings consistent with the existing style.
   - **Test Coverage:** Check if new logic is covered by tests. Flag missing unit tests.
   - **Performance:** Identify obvious bottlenecks, inefficient loops, or unnecessary allocations.
   - **Architecture:** Ensure the code follows modular design and doesn't introduce circular dependencies.
   - **Security:** Flag hardcoded secrets, injection vulnerabilities, or unsafe deserialization.
   - **Breaking Changes:** Flag any removed or renamed public API exports.

4. Present the review in this format:

   **1. 📝 Summary of Changes**
   *(A 2-3 sentence summary of what this PR actually does)*

   **2. 🔴 Critical Issues (Must Fix)**
   *(List any bugs, security flaws, missing type hints, or broken tests. Reference specific files and lines, e.g., `card.py:146`. If none, state "None found".)*

   **3. 🟡 Suggested Improvements (Nitpicks & Refactors)**
   *(List code style suggestions, minor performance tweaks, or readability improvements. Reference specific files and lines.)*

   **4. 🟢 Testing Status**
   *(A brief assessment of whether the new code appears adequately tested)*

5. After providing the review, ask the user: "Would you like me to fix any of the Critical Issues, or is this ready for you to open a PR?"