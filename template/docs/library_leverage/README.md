# Library leverage

**Implemented template guidance.** Three distinct assessment stages with an optional library-led
discovery entry and evergreen collections. Benefits to discovery and design quality
remain Proposed; installation does not establish an assessed codebase or qualified library fit.

Start with the [framework](library-leverage-framework.md) for responsibilities, handoffs, collection
paths and retention. Read the [base opportunity patterns](patterns.md) with additional patterns
from `assessment-patterns.md` when that output exists. All stages use relevant additions on the
same footing; promotion into base guidance is a manual operator decision.

| Skill | Question it answers | Collection it maintains |
| --- | --- | --- |
| [leverage-library-discovery](../../.claude/skills/leverage-library-discovery/SKILL.md) | What can this library family do, what do we use, and what warrants investigation? | [Library-led briefings](libraries/README.md#library-led-briefings) |
| [leverage-codebase-audit](../../.claude/skills/leverage-codebase-audit/SKILL.md) | Which concrete responsibilities and operations deserve investigation? | [Codebase opportunities](codebase/README.md) |
| [leverage-library-assessment](../../.claude/skills/leverage-library-assessment/SKILL.md) | Which focused library capabilities could address those opportunities, under what conditions? | [Library assessments](libraries/README.md) |
| [leverage-opportunity-review](../../.claude/skills/leverage-opportunity-review/SKILL.md) | Which complete option best addresses each opportunity, and why? | [Comparative reviews](reviews/README.md) |

## Use the workflow

Invoke the relevant skill with the intended scope, for example:

- `$leverage-library-discovery` — discover a library family's capabilities, current usage and
  research priorities, without a prior codebase opportunity.
- `$leverage-codebase-audit` — identify library-leverage opportunities in a selected operation,
  subsystem or the codebase.
- `$leverage-library-assessment` — assess selected opportunities against relevant capabilities,
  using the opportunity IDs and existing library analysis.
- `$leverage-opportunity-review` — compare complete options for those opportunities and recommend
  bounded target designs.

An end-to-end request can authorize discovery and the three assessment stages. Coordinate their substantive handoffs and
iterate where new evidence changes a premise. A focused inquiry needs only the relevant scope;
ordinary implementation and API questions do not initiate this workflow.

## Current accounts

No discovery, opportunity audit, library applicability assessment or comparative review has been run by
installing the workflow. The three collection folders and their README entry points exist and
explicitly identify their unassessed state. Author topic documents and record inspected baselines
when the first real assessment supplies content. Create `assessment-patterns.md` with its first useful
addition; do not invent patterns to populate a scaffold. Record inspected baselines and limits
rather than treating empty collections as assessed.

The [discovery and evidence guide](references/discovery-and-evidence.md) covers portable Rust
and Python inspection and briefing organization. The shared [vocabulary](references/shared-language.md)
and [collection-writing guidance](references/collection-writing.md) support the assessment stages. Keep
reusable library types and useful additional patterns when their originating matches retire.
The library collection is distinct from the broad [capability overviews](../libraries/README.md):
it holds contextual discovery briefings alongside focused capability knowledge and applicability.

The tracked skill source is `.claude/skills`, exposed to Codex through the existing `.agents/skills`
symlink and loaded directly by Claude Code. Discovery follows the repository's existing arrangement;
[official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
describes repository skills and symlink support. Existing formal review, planning and implementation
routes retain their scope and authority under the [framework binding](library-leverage-framework.md#repository-binding-and-downstream-use).
