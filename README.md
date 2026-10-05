# project-template

A [Copier](https://copier.readthedocs.io/) template for a low-friction, single-operator
project, carrying the working system extracted from
[library-context](https://github.com/paul-heyse/library-context), with the shared agent workflows
and bounded-review and execution-fit policy aligned on 2026-10-05.

Every generated project gets the **core**:

- `AGENTS.md` and `CLAUDE.md`: agent instructions, reporting vocabulary
  (`passed`/`failed`/`blocked`/`not_run`), Git rules and working agreements;
- `STATUS.md` and the `handoff` skill: the current checkpoint;
- `docs/adr/` with `scripts/adr.py` (`just adr new|supersede|index|lint|revisit`) and seed
  ADR-0001 (light process, current working set, end-of-turn bundles) and ADR-0002 (design review);
- `docs/design/`: an architecture map and a DESIGN skeleton with stable § IDs and
  `> Decision:` lines;
- `docs/design_review/`: the layered design standard (core 3.3) paired with
  `core/efficient-architecture-heuristics.md` (all H1–H28), a repository binding, reviews
  and evidence conventions, the `design-review` skill and the `design-reviewer` subagent;
- explicit concepts and operation contracts govern behavior, assessed through FP-04/A2 during
  bounded design reviews; ordinary implementation does not initiate a modeling exercise (ADR-0006);
- six shared worker roles with native Codex and Claude adapters, and paired skills for preparing
  and performing design reviews, plan creation and plan execution. The coordinator retains design,
  integration and acceptance. Delegation depends on task independence, context or capability needs,
  and whether its benefit justifies handoff and integration cost;
- `docs/plans/`; a dependency policy where libraries are added freely and float to the latest
  (`uv add`/`cargo add` defaults, committed lockfiles, `just upgrade` at the agent's discretion),
  with `docs/pins.md` listing only deliberate pins, each with its reason, through the `pin-check`
  skill;
- `.claude/settings.json` (permissions), `.agents/skills` for Codex, and
  `scripts/check_agents.py` (`just lint-agents`: every agent-facing path, link and recipe
  resolves);
- `.gitattributes` for Git LFS evidence, and a `justfile` whose `check`, `test-all` and `doctor`
  compose only the chosen layers.

**Layers**, chosen when you generate:

| Question | Default | Adds |
|---|---|---|
| `with_rust` | yes | `rust-toolchain.toml`, workspace lints and profiles, `.cargo/config.toml` (sccache, clang + mold), nextest, cargo-deny bans and sources, `scripts/check_pins.py` (`just deps`: declared families resolve to one version, every exact pin or git rev has a pins row), a starter crate |
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
(`_skip_if_exists` in `copier.yml`). Root README and STATUS patterns are anchored so managed
role and skill READMEs continue to receive workflow updates.

The design principles and efficient-architecture heuristics are used together in all generated
projects, independently of the optional code-intelligence profile and documentation site.
`standard.toml` declares `core.heuristics`; the site publisher includes it when present while
continuing to accept older manifests without that key. Standard versions remain unchanged.
The companion supports qualitative early judgment before physical organization, interfaces,
preparation, assurance and lifecycle choices become entrenched. It adds no checklist, cost
model or proof machinery and does not restart settled reviews during execution.

Copier continues to protect existing project DESIGN, binding and STATUS files. After updating
an existing project, manually add links to both
`docs/design_review/design_principles/core/design-principles.md` and
`docs/design_review/design_principles/core/efficient-architecture-heuristics.md` in its owned
DESIGN guidance, binding's applied-standard guidance and current STATUS checkpoint. Preserve
its current decisions, receipts and content; do not overwrite these files with fresh seeds.
Fresh projects receive these links directly. No new ADR, standard version or gate is needed
solely to adopt the companion; accepted and historical records remain immutable.

Design reviews are grounded only in the standard and the functional target (DESIGN §1.1). ADRs,
§B decisions, binding policies and other rules are current design, not criteria: every review
has the `target` purpose and lists its rule impacts (`review#RCnn`), and `create-plan` has the
operator accept or reject each before the plan depends on it. The skills carry this to existing
projects; their protected binding needs the same edits by hand (grounding bullet, `change/target`
cadence, authority scoped to execution, the RCnn route in § 4). Accepted ADRs stay immutable.

Core 3.3 and optional code-intelligence guidance 1.4 add FP-07/A4 execution fit alongside the
independent semantic gates. Reviews qualitatively assess physical work, composed libraries, locality,
reuse, assurance and lifecycle scope from relevant operations and growth/failure scenarios, explaining
material tradeoffs in plain language. This consideration requires no numerical estimates, cost models,
estimators, runtime cost accounting, execution-planning machinery, instrumentation, formal cost proofs
or additional proof artifacts; such mechanisms need a separate concrete functional or operational
requirement. Quantitative performance/capacity claims still require measurements; semantic correctness
obligations remain. Skills apply the criteria through existing review, planning and ADR routes.
Fresh projects receive ADR-0006, which carries forward bounded domain-model review criteria and
reusable roles while introducing task-sensitive delegation, concrete escalation and stronger
evidence/review defaults. Retired seeds are no longer generated. Updates exclude ADR-0004,
ADR-0005 and ADR-0006 seed paths to preserve project-owned ADR numbers and decisions. An existing
project adopting the policy records its own next available ADR and aligns its owned DESIGN and
binding summaries; accepted records are not rewritten.

The default workflow supplies shared responsibilities in `.agents/roles`, native settings in
`.codex/agents` and `.claude/agents`, and the three process-skill pairs documented in the generated
skills index. The five new planning/authoring/execution skills are tracked core files. Existing
projects should reconcile customized agent definitions and model defaults when reviewing an update.
Plan creation includes focused assessment of the foundations it will use; improvements enter the
plan before dependent work. Planning companions do not switch modes or add a durable second plan.

An existing repository that was not generated can adopt the template: run `copier copy` into its
working tree, review the diff, and commit `.copier-answers.yml`; `copier update` works from then on.

## Change the template

1. Edit files under `template/` (`.jinja` files are rendered; everything else is copied
   verbatim). Keep scripts as plain files that read convention paths or data, so they stay
   identical across projects.
2. `just test` renders the core, rust, python and full combinations from the working tree into
   `build/render/` and runs each project's own `just check`, every `just hygiene` check
   (`docs-check` only when the docs tools are installed) and `docs-test`, then `just turn-end`
   and `just ready`, and checks for a clean tree.
3. Commit, then tag a release: `git tag vX.Y.Z && git push --follow-tags`. `copier copy` and
   `copier update` use the latest tag.

Seed ADRs are updated in place here when a process decision changes. A generated project's
accepted records stay immutable: it records the change in its own superseding ADR.

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
