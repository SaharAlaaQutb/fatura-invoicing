# AGENTS.md — fatura-invoicing

## Repo status

The repo is in the **planning / scaffolding stage**. There is **no runnable code yet**: no `pyproject.toml`, `package.json`, `docker-compose.yml`, source tree, or CI workflows exist.

Do not invent test/lint/build/typecheck commands — none are executable until the scaffold described in the docs lands.

## High-signal facts (repo-specific)

- **`README.md`** (tracked) is the public-facing project, architecture, and usage doc.
- **`local-docs/`** (gitignored via `.gitignore`) holds planning documents:
  - `IMPLEMENTATION_PLAN.md` — SOLID / clean-architecture plan, API, DB design, roadmap.
  - `03-fatura-invoicing-inventory.md` — original project specification.
- **Do not commit anything under `local-docs/`**. It is gitignored and local-only.
- **`.idea/` is gitignored.**
- When code lands, the intended layout is `backend/` + `frontend/` under repo root (see README and implementation plan). Nothing under those paths exists yet.

## Working rules (always apply)

- Stick to the two plans in `local-docs/`: `IMPLEMENTATION_PLAN.md` and `03-fatura-invoicing-inventory.md`. They are the source of truth; do not implement from memory or invent scope.
- Always apply SOLID principles and design patterns when implementing.
- Always keep code clean and well documented.
- For every subtask: write a **code proposal** first (what will be created/changed, why, and how to verify), wait for user approval, then implement.
- Always checkout a new branch for each new feature before starting work.
- Never commit or push unless CI/CD tests are fully passing. (No CI/CD exists yet in the scaffold stage; this rule applies once pipelines land.)
- Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.) with a brief description in every commit.

## What to do before making changes

1. Read `README.md` first.
2. Read `local-docs/IMPLEMENTATION_PLAN.md` for architecture, layers, SOLID mapping, and the phased roadmap.
3. Read `local-docs/03-fatura-invoicing-inventory.md` for the source-of-truth specification.
4. Confirm actual config/scripts exist (root manifests, backend `pyproject.toml`, frontend `package.json`, `.github/workflows/`) before running any lint/type/test commands — docs describe targets that do not exist yet.
