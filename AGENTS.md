# Agent Guidelines

This document provides comprehensive instructions for AI agents operating within the this repository. Follow these guidelines strictly to ensure code quality, consistency, and stability.

## Environment & Toolchain

This project expects the host system to provide certain tools.
If these aren't present inform the user and provide instructions for them to properly install the required tools in their environment.

### Core Environment Tools
| Tool | Check Command | Initialization Command | Description |
|--------|---------|-------------|----------------|
| **UV** | `uv --version` | `uv init` | A modern python package manager. |
| **Beads** | `bd --version` | `bd init` | An AI native issue tracker. |
| **OpenCode** | `opencode --version` | `/init` (within the OpenCode TUI) | An open source AI Agent. |


This project relies on a suite of project tools to maintain quality.  If these tools aren't present add them to the project's dev dependencies.

### Core Project Tools
| Tool | Install Command | Description |
|--------|---------|-------------|
| **Python** | `uv python install 3.12` | A modern python interpreter (version 3.12 or above). |
| **Pytest** | `uv add pytest --dev` | Unit test runner. |
| **Pytest Coverage** | `uv add pytest-cov --dev` | Unit test code coverage. |
| **Behave** | `uv add behave --dev` | Behavior-driven development automated acceptance testing. |
| **Ruff** | `uv add ruff --dev` | Linting and formatting. |
| **Pyright** | `uv add pyright --dev` | Type checking. |
| **MkDocs** | `uv add mkdocs --dev` | Static site generator. |
| **MkDocs Material UI** | `uv add mkdocs-material --dev` | Material UI components for MkDocs. |

The project uses **uv** for dependency management and task execution. All commands should be executed via `uv run`.

### Core Commands
| Action | Command | Description |
|--------|---------|-------------|
| **Unit Tests** | `uv run pytest` | Run all unit tests with coverage |
| **BDD Tests** | `uv run behave` | Run acceptance tests (feature files) |
| **Linting** | `uv run ruff check .` | Check for linting errors |
| **Formatting** | `uv run ruff format .` | Auto-format code |
| **Type Check** | `uv run pyright` | Run static type checking |
| **Build** | `uv run python -m build` | Build the package |
| **Docs** | `uv run mkdocs build` | Build documentation site |

### Running Specific Tests
*   **Single Test File:** `uv run pytest tests/<package>/test_thing.py`
*   **Single Test Function:** `uv run pytest tests/<package>/test_<thing>.py::test_<function_name>`
*   **Specific BDD Feature:** `uv run behave features/<package>/<use_case>.feature`

## Issue Tracking

This project is adamant about ensuring we make our work visible.  Any work you are assigned must be documented appropriately as epics, features, tasks, or bugs in bd (beads).  This includes writing descriptions for issues and updating status as work is performed.

This project uses **bd (beads)** for issue tracking.
Run `bd prime` for workflow context, or install hooks (`bd hooks install`) for auto-injection.

**Quick reference:**
- `bd ready` - Find unblocked work
- `bd create "Title" --type task --priority 2` - Create issue
- `bd close <id>` - Complete work
- `bd sync` - Sync with git (run at session end)

For full workflow details: `bd prime`

## Standard Process

When asked to do work adhere to the following process:
1. Write a feature or bug in bd (beads) that defines the work and expected outcome.  Ensure to include detailed feature / task / bug descriptions to avoid ambiguity and support human review.
2. Decompose the feature or bug into tasks in bd (beads).  Ensure the last step checks all test and quality concerns by running 'uv run ruff check .', 'uv run ruff format .', 'uv run pytest', 'uv run pyright', and 'uv run behave' ensuring everything passes or fixing any reported errors.
3. Execute the work based on the plan you've created in bd (beads).  Ensure any new code you write has corresponging unit tests.  In general, if adding a new feature also write a BDD acceptance test.
4. Track your work in bd (beads) as you work.  When completing a feature, commit the changes and push changes in git.

## Code Style & Conventions

### Python Standards
*   **Style Guide:** Adhere strictly to **PEP 8**.
*   **Formatter:** We use `ruff`. Always run `uv run ruff format` before submitting changes.
*   **Imports:**
    *   Sort imports using `ruff` (automated).
    *   Use absolute imports for internal modules (e.g., `from <module> import <function / class>` instead of `from <path> import <function / class>`).
    *   Group standard library, third-party, and local imports separately.

### Type Safety
*   **Strong Typing:** All new code **must** include type hints.
*   **Validation:** Use `pydantic` for data validation and schema definitions where appropriate.
*   **Check:** Verify types with `uv run pyright`.
*   **Generics:** Use modern generic syntax (e.g., `list[str]` instead of `List[str]`) where supported by Python 3.12+.

### Naming Conventions
*   **Variables/Functions:** `snake_case` (e.g., `validate_schema`, `user_input`)
*   **Classes:** `PascalCase` (e.g., `SchemaValidator`, `QueryEngine`)
*   **Constants:** `UPPER_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_CONFIG`)
*   **Private Members:** Prefix with `_` (e.g., `_internal_cache`)

### Error Handling
*   **Exceptions:** Use specific, custom exception classes (inherit from `Exception` or base project exceptions) rather than generic `Exception`.
*   **Context:** Catch exceptions narrowly and provide context when re-raising.
*   **Fail Fast:** Validate inputs early.

## Project Structure

The project is modularized by functionality:
*   `docs/`:  Documentation for the application or library.
*   `src/`:  Source code for the application or library.  Modules are in subdirectories.
*   `tests/`: Unit tests mirroring the `src` structure.
*   `features/`: Gherkin feature files for BDD.

## Testing Guidelines

*   **TDD/BDD:** Adopt a Test-Driven or Behavior-Driven approach. Write the test or feature file *before* implementing the logic.
*   **Coverage:** Maintain high test coverage (fail under 75% is configured).
*   **Mocking:** Use `unittest.mock` or `pytest-mock` to isolate external dependencies (filesystem, network).
*   **Fixtures:** Use `pytest` fixtures for setup/teardown and reusable test data.

## Documentation & Comments

*   **Docstrings:** Use Google-style docstrings for public modules, classes, and methods.
*   **Why vs. What:** Comments should explain *why* a complex piece of logic exists, not *what* the code is doing (the code should be self-documenting).
*   **No Chat:** Do not add conversational comments or signature blocks.

## Workflow Checklist for Agents

1.  **Analyze:** Read related files and `AGENTS.md` before starting.
2.  **Safety:** If modifying filesystem/running shell commands, explain the impact first.
3.  **Plan:** Formulate a plan involving necessary changes and test coverage.
4.  **Implement:** Write code, following the conventions above.
5.  **Verify:**
    *   Run format: `uv run ruff format .`
    *   Run lint: `uv run ruff check .`
    *   Run type check: `uv run pyright`
    *   Run tests: `uv run pytest` (and `uv run behave` if applicable)
    *   Run docs: `uv run mkdocs build`
6.  **Refine:** Fix any issues found during verification.

## Copilot/AI Specifics

*   **Context:** Consider the surrounding code and project structure.
*   **Dependencies:** Do not introduce new dependencies without explicit instruction. Use existing libraries.
*   **Hallucinations:** Verify library APIs before generating code.
