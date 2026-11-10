# Discovery and evidence

## Select the scope

Start with the library family, the repository objective, and the architectural owner and
representative consumers that make it relevant. Record the date, inspected Git revision,
relevant worktree changes and selected project, toolchain or interpreter, platform, features and
dependency groups.
Scope source reads to the question. Distinguish application and operator paths from tests and
experiments. Inspect independently locked projects separately. Use the Rust or Python sections
below as relevant, following the receiving repository's environment and command conventions.
The examples inspect prepared local inputs; missing tools or artifacts remain explicit gaps,
not instructions to install tools, acquire APIs or prepare analysis providers implicitly.

## Read evidence at the level it supports

| Question | Evidence and limits |
| --- | --- |
| What does the release offer? | Use broad overviews for orientation and release-matched primary docs or source for significant capability claims. Look for configuration, native components, extension points and companion packages. Distinguish capabilities available in the selected release from ones requiring configuration, another platform or an upgrade. |
| What did the project select? | Read the owning manifest for requested versions, features, extras and groups, and the locked tree for the dependency paths in the selected context. A resolved edge establishes dependency selection in that context. |
| What is installed? | Read the prepared interpreter's distribution metadata for versions, advertised extras and entry points. Keep distribution names distinct from Python import names. A namespace can have several providers and an editable install can lack a mapping. Preserve unresolved correspondences. |
| What does source show? | Start with `rg` and read the actual configuration, wrappers and consumers. Structural matches locate written syntax. Read the surrounding code before describing what is wired, conditional or delegated. Aliases, rebinding, dynamic imports, re-exports and plugin loading can leave attribution unresolved. |
| What ran? | Use existing records to establish execution in their recorded scope. A selected extra, an import or a configured path alone gives no runtime observation. |

Record a scoped no-hit separately from unavailable metadata, excluded paths, parse failures,
truncated output and unresolved joins. A briefing can proceed with representative source reads and
release-matched references alone. State which questions still need the missing evidence.

## Rust evidence

Inspect the selected Cargo workspace with its configured toolchain. Record `rustc --version`
and the package, feature and target selection when those conditions inform a claim. From the
project root, these commands inspect the locked dependency graph without fetching missing inputs:

```sh
cargo metadata --locked --offline --format-version 1
cargo tree --locked --offline --edges features --invert example-crate@1.0.0
```

Substitute a selected package name and version for the illustrative package. Explicitly select
features, default-feature policy and target when the question needs a different context. Cargo
metadata includes package IDs, sources, manifest paths, dependency renames and resolution edges;
keep defining package identity separate from aliases and facade paths. Metadata resolution and
feature trees do not establish every compiler-unit context or prove that code executes. A lockfile
records resolution, not every available optional capability or local installation condition.

Read representative consumers, wrappers and configuration. A text match for an import or method
is a lead, not a resolved semantic reference. Re-exports, trait methods, macros, conditional
compilation and build-script output can require deeper inspection. Use release-matched API
documentation or upstream source to investigate contracts and useful capabilities beyond the
observed entry points. An API's absence from local uses is not evidence of its absence from the
library or of its value here.

If the receiving repository provides prepared semantic-reference or rustdoc exports, use their
own documented commands and inspect coverage before interpreting them. Preserve package identity,
source revision, feature/target selection and acquisition context. Rustdoc IDs are artifact-local;
documentation configuration can differ from compilation. Resolved written references still do not
prove execution. Failed acquisition, missing macro expansion, excluded configurations and
unresolved joins remain gaps. Generated inventories broaden discovery; they do not rank it.

[Cargo metadata](https://doc.rust-lang.org/cargo/commands/cargo-metadata.html) ·
[Cargo tree](https://doc.rust-lang.org/cargo/commands/cargo-tree.html)

## Python evidence

### Inspect dependency selection and installation

From the selected project root, substitute a distribution name for the illustrative name below.
The tree uses the default groups and discovered interpreter platform unless flags select another
context. Use `--no-dev` to inspect the tree without the development group or `--universal` to
examine the lock across platforms. State the context with the result. uv's tree JSON is a preview
format suitable for ad hoc inspection.

```sh
uv tree --locked --offline --no-python-downloads --invert --package example-dist
```

In a prepared uv environment, pass the distribution and its suspected top-level import name
separately. The metadata query reads the installed records without importing the target.

```sh
uv run --locked --offline --no-sync --no-python-downloads python -B - example-dist example_pkg <<'PY'
import sys
from importlib import metadata

distribution, import_name = sys.argv[1:]
try:
    installed = metadata.distribution(distribution)
except metadata.PackageNotFoundError:
    print(f"{distribution}: no distribution metadata in this interpreter")
else:
    print(installed.name, installed.version)
    print("advertised extras:", installed.metadata.get_all("Provides-Extra", []))
    for entry in sorted(installed.entry_points, key=lambda entry: (entry.group, entry.name)):
        print("entry point:", entry.group, entry.name, entry.value)
providers = metadata.packages_distributions().get(import_name)
print(f"{import_name}: candidate distributions", providers or "unknown")
PY
```

[uv tree](https://docs.astral.sh/uv/reference/cli/#uv-tree) ·
[Python distribution metadata](https://docs.python.org/3.14/library/importlib.metadata.html) ·
[Python extras metadata](https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use)

### Inspect written Python imports

Use the repository's Python interpreter to parse explicitly selected files when a text search
cannot distinguish written imports from strings and comments. The command reports one source
statement per match, including nested and conditional imports. It preserves multiline text and
separates skipped inputs on stderr. Exit status 1 indicates incomplete coverage.

```sh
uv run --locked --offline --no-sync --no-python-downloads python -B - path/to/selected.py <<'PY'
import ast
import sys
import tokenize

incomplete = False
for path in sys.argv[1:]:
    try:
        with tokenize.open(path) as stream:
            source = stream.read()
        tree = ast.parse(source, filename=path)
    except (OSError, SyntaxError, UnicodeError) as error:
        print(f"{path}: skipped ({error})", file=sys.stderr)
        incomplete = True
        continue
    imports = (node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    for node in sorted(imports, key=lambda node: (node.lineno, node.col_offset)):
        print(f"{path}:{node.lineno}: {ast.get_source_segment(source, node)}")
sys.exit(int(incomplete))
PY
```

For a one-off structural query, use the installed ast-grep CLI on selected paths. This example
finds `from` statements, including multiline imports. Record the command, scope and tool version
when matches inform a claim. Read candidates in context.

```sh
ast-grep run --lang python --kind import_from_statement --json=stream path/to/selected.py
```

[Python AST](https://docs.python.org/3.14/library/ast.html) ·
[ast-grep run](https://ast-grep.github.io/reference/cli/run.html)

### When a richer tool would help

Use richer analysis when a consequential attribution question warrants it. LibCST scope and
qualified-name metadata can expose possible bindings for aliased or shadowed names; preserve
ambiguity and check the selected release against repository syntax. Tree-sitter can support
error recovery and incremental grammar queries; recovered syntax remains partial evidence.
ast-grep-py can reuse a parsed root for several structural queries. These are optional research
routes, not required dependencies or preparation steps.

## Write the briefings

Maintain `docs/library_leverage/libraries/<family>/briefing.md` using the existing family account
when there is one. Add a route from the [briefing index](../libraries/README.md#library-led-briefings)
when creating a discovery account. The entry point may contain the complete discovery or summarize
and link to focused briefings under `briefings/`. Choose the organization, document boundaries and
level of detail that sufficiently explain the opportunities, without a fixed segmentation scheme
or document count. When using multiple briefings, the summary connects findings, explains research
priorities across topics and identifies useful compositions. Focused briefings carry supporting
analysis and enough context for selective reading. Across the discovery account, include:

1. **Scope and evidence.** Objective, inspected baseline and selection, evidence used, and limits.
2. **Capabilities and current use.** A map of relevant capabilities and representative uses,
   with links to original docs, local call sites, configuration or existing evidence. Include
   useful territory outside the current integration.
3. **Research priorities.** For each direction, name the mechanism, potential value, conditions
   that could defeat it, and a question whose answer would change the next step. Describe any
   reason to retain the current approach.
4. **Handoff.** Link existing types, opportunities or assessments when they exist. A useful lead
   can remain a proposed question until a concrete responsibility warrants further work.

Refresh the summary and affected focused briefings together. Link shared baseline and coverage
context where appropriate; make differing dates or source conditions explicit and retain inherited
evidence dates.

For example, a synthetic family might advertise a batching plugin while an inspected test imports
an alias from a namespace with multiple possible providers. Record the advertised plugin, the
test-only import and the unresolved provider separately. If production configuration was outside
scope, leave production use unknown. A next question could ask whether the plugin preserves the
per-item error reporting a caller relies on.
