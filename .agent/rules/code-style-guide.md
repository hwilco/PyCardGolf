---
trigger: model_decision
description: Any time code is modified or if I ask for a review of code style
---

* Make sure all the code is styled with with the PEP8 style guide as a baseline, and respecting the Ruff linting I set up in pyproject.toml. Refer to https://docs.astral.sh/ruff/rules/ if needed, and ask for permission to add exceptions from Ruff
* Make sure all the code is properly commented
* Make sure typehints are used properly, including where it makes sense for instance variables
