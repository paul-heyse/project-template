# project-template

A [Copier](https://copier.readthedocs.io/) template for a pinned, low-friction, single-operator
project, carrying the working system extracted from
[library-context](https://github.com/paul-heyse/library-context) (at `efa01f3`, 2026-09-26).

Every generated project gets the **core**:

- `AGENTS.md` and `CLAUDE.md`: agent instructions, reporting vocabulary
  (`passed`/`failed`/`blocked`/`not_run`), Git rules and working agreements;
- `STATUS.md` and the `handoff` skill: the current checkpoint;
- `docs/adr/` with `scripts/adr.py` (`just adr new|supersede|index|lint|revisit`) and seed
  ADR-0001 (light process, current working set) and ADR-0002 (design review);
- `docs/design/`: an architecture map and a DESIGN skeleton with stable § IDs and
  `> Decision:` lines;
- `docs/design_review/`: the layered design standard (core 3.1), a repository binding, reviews
  and evidence conventions, the `design-review` skill and the `design-reviewer` subagent;
- semantic-model-first domain design as a MUST: explicit concepts and operation contracts
  govern behavior, assessed through FP-04/A2 alongside the other five foundations (ADR-0004);
- `docs/plans/`, `docs/pins.md` and the `pin-check` skill;
- `.claude/settings.json` (permissions), `.agents/skills` for Codex, and
  `scripts/check_agents.py` (`just lint-agents`: every agent-facing path, link and recipe
  resolves);
- `.gitattributes` for Git LFS evidence, and a `justfile` whose `check`, `test-all` and `doctor`
  compose only the chosen layers.

**Layers**, chosen when you generate:

| Question | Default | Adds |
|---|---|---|
| `with_rust` | yes | `rust-toolchain.toml`, workspace lints and profiles, `.cargo/config.toml` (sccache, clang + mold), nextest, cargo-deny, `scripts/check_pins.py` (`just deps`), a starter crate |
| `with_python` | yes | `pyproject.toml` with ruff, pyrefly, pytest and Hypothesis; `just py-test`, `ruff`, `types` |
| `with_ast_grep` | yes | `sgconfig.yml`, empty `rules/` and `rule-tests/`, `just rules-scan` / `rules-test` |
| `with_docs_site` | no | mdBook + Pagefind + lychee via `scripts/docs.py`, a docs-only CI workflow, ADR-0003 |
| `with_ci_profile` | no | The code-intelligence design-review profile and skill |

## Create a project

```sh
gh new my-project            # private GitHub repo; add --public, --local-only, --dir PATH
```

`gh new` is an alias for [`tools/new-project`](tools/new-project). It runs `copier copy`, commits
the scaffold with its lockfiles, runs `just check`, and creates and pushes the GitHub repository.
Without the alias: `copier copy gh:paul-heyse/project-template <dir>`.

For a repository created on the GitHub website, create it empty, clone it, then run
`copier copy gh:paul-heyse/project-template .` inside the clone. This repository is deliberately
**not** a GitHub "template repository": its files are unrendered Jinja.

## Update a generated project

```sh
copier update --defaults     # reuse the recorded answers; add --vcs-ref TAG to pick a version
git diff                     # resolve any conflict markers, then:
just check && git commit -am "Template update to <tag> (just check passed)"
```

Seeds the project owns after generation are never touched by updates: README, STATUS, DESIGN, the
architecture map, the ADRs and their index, pins, the binding and the evidence index
(`_skip_if_exists` in `copier.yml`).

Core 3.1 also updates the review template and agent guidance. New projects receive ADR-0004
for this policy; updates exclude that seed to avoid colliding with project-owned ADR numbers.
An existing project adopting it records the decision under its next available ID and aligns
its owned DESIGN and binding summaries. Do not rewrite an accepted seed record.

An existing repository that was not generated can adopt the template: run `copier copy` into its
working tree, review the diff, and commit `.copier-answers.yml`; `copier update` works from then on.

## Change the template

1. Edit files under `template/` (`.jinja` files are rendered; everything else is copied
   verbatim). Keep scripts as plain files that read convention paths or data, so they stay
   identical across projects.
2. `just test` renders the core, rust, python and full combinations from the working tree into
   `build/render/` and runs each project's own `just check`, every `just hygiene` check
   (`docs-check` only when the docs tools are installed) and `docs-test`, then an end-of-turn
   smoke test: `scripts/after_turn.py stop` with the fixer off, the prompt barrier, a complete
   report and a clean tree.
3. Commit, then tag a release: `git tag vX.Y.Z && git push --follow-tags`. `copier copy` and
   `copier update` use the latest tag.

Do not change the seed ADRs' decisions in place once released: a generated project's accepted
records are immutable. Put a changed process decision in a new ADR seed instead.

Improvements made in a generated project, or in library-context, come back here by hand.

## Machine setup

| Step | Command |
|---|---|
| Copier | `uv tool install copier` (9.18.2 verified 2026-09-26) |
| `new-project` on `PATH` | `ln -s ~/project-template/tools/new-project ~/.local/bin/new-project` |
| `gh new` | `gh alias set --shell new 'new-project "$@"'` |
| Default branch | `git config --global init.defaultBranch main` |

Generated projects also expect `just`, `uv` and Git LFS, and per layer the Rust tools
(cargo-nextest, cargo-deny, sccache, clang, mold) and ast-grep; `just doctor` lists them.
