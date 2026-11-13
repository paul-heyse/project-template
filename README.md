# project-template

A [Copier](https://copier.readthedocs.io/) template for a pinned, low-friction, single-operator
project, carrying the working system extracted from
[library-context](https://github.com/paul-heyse/library-context), with the shared agent workflows
and bounded-review and execution-fit policy aligned on 2026-10-20.

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
- six shared worker roles with native Codex adapters, and paired skills for preparing
  and performing design reviews, plan creation and plan execution. The coordinator retains design,
  integration and acceptance. Contributions follow useful outcomes, shared decisions and readiness
  for the requested result. Delegation can provide progress, earlier learning or independent judgment,
  including serial work. Shared principles guide decomposition; local operating rules govern effects;
- `docs/plans/`; a dependency policy where every declared dependency is pinned exactly
  (`uv add` writes `==` through `add-bounds = "exact"`, `cargo add name@=x.y.z`), committed
  lockfiles hold the rest, versions change deliberately on the agent's judgment, and
  `docs/pins.md` lists only holds, each with its reason, through the `pin-check` skill;
- library-led discovery and three assessment skills, with `docs/library_leverage/` holding
  contextual briefings, codebase opportunities, library applicability with reusable types and
  comparative option reviews. The collection folders exist with unassessed entry pages;
- `.claude/settings.json` (permissions), `.agents/skills` for Codex, and
  `scripts/check_agents.py` (`just lint-agents`: every agent-facing path, link and recipe
  resolves);
- `.gitattributes` for Git LFS evidence, and a `justfile` whose `check`, `test-all` and `doctor`
  compose only the chosen layers.

**Layers**, chosen when you generate:

| Question | Default | Adds |
|---|---|---|
| `with_rust` | yes | `rust-toolchain.toml`, workspace lints and profiles, `.cargo/config.toml` (sccache, clang + mold), nextest, cargo-deny bans and sources, `scripts/check_pins.py` (`just deps`: every registry dependency pinned exactly and every git one by its rev; declared families resolve to one version), a starter crate |
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
architecture map, the ADRs and their index, pins, the binding and the evidence index, living diagnostic audit and library-overview index
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
Fresh projects receive ADR-0006 for task-sensitive coordination and ADR-0007 for the audit-led
workflow, Codex-only role routing and library-skill retirement. New seed paths are excluded on
updates so existing projects allocate their own next ADR; accepted decisions stay immutable.

The default workflow uses shared responsibilities in `.agents/roles`, Codex settings in
`.codex/agents`, and tracked process skills in `.claude/skills` exposed through `.agents/skills`.
A broad persisted principle audit precedes a diagnostic review of production or broad system scope. The operator selects
holistic, library-targeted, principle-focused or combined focus; reviewers choose methods and depth.
Requested recommendation audits publish net changes and revise the principal review with attribution
and recoverable input. Requested completion audits correct the same owning plan. Neither becomes
automatic per-slice review. Existing plans and reviews are not migrated by this template change.

Test-only diagnostic engagements use `design-principle-audit-tests` and the separate living
account at `docs/design_review/test-audit/`. Mixed scope identifies applicable accounts under
the project binding; each retains its own baseline and findings one primary home. The
`core/test-assessment.md` companion interprets the same Core 3.3 foundations for test evidence,
reuse and shared support without new gates or an automatic test campaign. `standard.toml`
selects it through `core.test_assessment`; docs-enabled projects publish it as active guidance.
The companion is available in every layer combination, independently of optional profiles.

Test-only review does not initiate a broad production audit. Both collections begin as explicitly
unperformed scaffolds; installing them establishes no suite quality or product qualification.

Existing projects adopt the new skill, companion and manifest selection as managed guidance,
then reconcile their protected binding, DESIGN and checkpoint with the test-scope route and
clarified validator/oracle distinction. Allocate a local ADR for this additive process change;
do not copy the template seed over accepted project decisions. Copier preserves the complete
test-audit subtree once authored, including nested topic pages, while managed skill and companion
updates continue. The focused `just test-env` exercises discovery, publication selection and
update preservation without product builds or health suites.

Functional enhancement uses `plan-functional-extension-review` / `functional-extension-review`
to explore useful product, developer, operator or research capabilities within an operator-selected
outcome, workflow, subsystem or ecosystem. No diagnostic audit, principle violation or existing
caller is required. Design principles shape realizations; concrete enabling mechanisms and sources
remain with opportunities. `docs/functional_reviews/` holds principal reviews and audit companions.
Recommendation auditing preserves the functional-value lens; selected opportunities enter existing
plans with stable source references, and completion auditing assesses the delivered workflow.

Plan improvement uses `plan-improvement-review` to examine the remaining change footprint of
an implementation plan or coordinated series. It actively seeks design-principle alignment,
general enhancements and execution improvements across materially affected components, including
supporting code whose value extends beyond the functional target. Recommendations are judged
for coherent integration and total burden. `docs/plan_improvement_reviews/` holds standalone
assessments; updating a plan from one is separately instructed, using the existing planning and
decision routes. There is no separate update skill or broad audit prerequisite, and formal
review cadence remains unchanged. Every layer combination receives the skill and collection;
docs-enabled projects publish both. Existing projects reconcile their protected binding with
this route by hand after updating managed guidance. Authored reviews remain project-owned.

`docs/design_review/audit/` begins as an explicitly unperformed scaffold and is protected from
Copier updates once authored. `docs/design_review/reviews/audits/` holds companion conventions.
`docs/libraries/` supplies a repository-agnostic capability-overview guide and project-owned index.
Optional overviews orient capability discovery; AGENTS.md guides source selection by the question
and uncertainty being resolved; active central library-skill
selection and synchronization are removed. Existing indexes can retain inactive historical links.

Existing projects must reconcile owned bindings, DESIGN and checkpoints with these workflow
owners and research routes, preserving local criteria, profiles, accepted scope and historical
receipts. Copier's protection is intentional; it does not silently upgrade those project-owned
documents. Shared skills and role guidance update without overwriting them.

Library leverage is available in every layer combination. `leverage-library-discovery` relates
a library family's capabilities to local usage and proposes research priorities without requiring
a concrete opportunity. Its shared evidence guide supplies portable Rust and Python inspection
examples; agents use the relevant language sections and receiving project conventions. Discovery
may use one complete briefing or a summary with focused briefings under `briefings/`; agents choose
organization and sufficient detail. No brevity requirement or fixed segmentation scheme applies.
`leverage-codebase-audit` identifies
concrete opportunities; `leverage-library-assessment` researches focused capabilities and their
contextual fit; `leverage-opportunity-review` compares complete options and bounded targets.
All stages use the base patterns and useful additional patterns authored in output
`docs/library_leverage/assessment-patterns.md`; promotion into base guidance is manual.
Reusable library types and additional patterns survive retirement of their current matches.
Installation performs no discovery or opportunity audit and establishes no library qualification.

Copier protects the project's leverage index and framework binding, all three assessment subtrees
and its additional-pattern output, including authored topics that collide with later template
content, including authored summaries and nested focused discovery briefings. Skill instructions,
the discovery/evidence guide, shared writing guidance and base pattern guidance remain managed.
After updating an existing project, manually reconcile protected leverage indexes and the framework
with the optional discovery entry; Copier intentionally preserves their authored content. Accepted
project decisions remain unchanged. No native analysis host or executable discovery helper is installed.
Fresh projects receive ADR-0008; updates exclude that seed so existing projects allocate a local
decision and reconcile protected DESIGN, binding and STATUS themselves. `just test-env` exercises
skill discovery, real output folders, docs publication and update preservation across layers
without product builds.

An existing repository that was not generated can adopt the template: run `copier copy` into its
working tree, review the diff, and commit `.copier-answers.yml`; `copier update` works from then on.

## Validation and design-stage guidance

The v0.6.1 guidance favors engineering judgment for expected improvements and coherent target
designs during development. Benchmarking and profiling address serious regression concerns;
expected gains need no routine measurement task or deferred obligation. Functional and numerical
correctness checks retain their purpose. Completed replacements include affected consumers and
removal of superseded machinery, preserving required behavior and useful independent verification.

Fresh projects receive these defaults in AGENTS.md, skills, shared roles and the layered design
standard. Existing projects receive managed guidance through Copier; reconcile project-owned
bindings, DESIGN and checkpoints locally. Keep their accepted decisions, authored content and
historical evidence intact. Core 3.3, code-intelligence 1.4 and Copier's preservation rules remain
unchanged. This release also includes the library-reference selection guidance and the existing
Codex environment-settings update.

## Library implementation guidance

The v0.6.2 guidance presents Context7 as an optional way to discover implementation approaches,
examples, related APIs and useful options, including when a workable approach is already familiar.
AGENTS.md describes useful situations, query framing and version checks; it adds no mandatory
lookup sequence or research artifact. Direct primary documentation remains an equally appropriate
route. The guidance applies to every generated layer combination and reaches existing projects
through Copier's managed AGENTS.md update.

This revision also includes the portable library-discovery guide and its existing runnable examples.

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

Generated projects include `.envrc` and `scripts/setup-env`. After scaffold lock creation,
`bash scripts/setup-env` prepares the enabled Python layer.
Directory activation remains separate: review `.envrc`, then `direnv allow` in each checkout.
It removes foreign Python environment paths and performs no installation or native build.
Personal overrides use ignored `.envrc.local`. Generated `.codex/config.toml` keeps the shared
daemon, disables login shells and shell snapshots, sets `UV_LOCKED=1`, and selects the existing
workstation direnv bridge using `BASH_ENV = "${HOME}/.config/codex/bash-env.bash"`. Bash expands
`HOME` when loading that file; no operator or checkout path is embedded in generated settings.
The bridge refreshes approved settings for the actual command directory, including commands
launched through a daemon that inherited another project's environment.

Machine setup must already provide `~/.config/codex/bash-env.bash` and its machine-environment
helper, plus `direnv`. Check that the bridge is readable with
`test -r "$HOME/.config/codex/bash-env.bash"` before using Codex; Bash silently ignores a missing
`BASH_ENV` file. The template selects the existing bridge rather than maintaining a second copy
of workstation initialization. After applying these settings to an existing repository, exit
and resume its Codex session; the daemon and other sessions can remain running.
The installed Rust toolchain follows the generated pin file.
`just test-env` checks environment/workflow generation for all four layer combinations, including
store-free setup, skill and ADR validation, and preservation of project-owned audit/index content
during a scratch Copier update, without installing product dependencies or building native code.

| Step | Command |
|---|---|
| Copier | `uv tool install copier` (9.18.2 verified 2026-09-26) |
| `new-project` on `PATH` | `ln -s ~/project-template/tools/new-project ~/.local/bin/new-project` |
| `gh new` | `gh alias set --shell new 'new-project "$@"'` |
| Default branch | `git config --global init.defaultBranch main` |

Generated projects also expect `just`, `uv` and Git LFS, and per layer the Rust tools
(cargo-nextest, cargo-deny, sccache, clang, mold) and ast-grep; `just doctor` lists them.
