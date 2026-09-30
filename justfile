# Template self-test. `just test` renders every layer combination from the working tree into
# build/render/<combo>/ and runs each generated project's own checks there.

set shell := ["bash", "-euo", "pipefail", "-c"]

# List recipes
default:
    @just --list

# Render all combinations and run their checks
test: (combo "core" "-d with_rust=false -d with_python=false -d with_ast_grep=false") (combo "rust" "-d with_rust=true -d with_python=false -d with_ast_grep=false") (combo "python" "-d with_rust=false -d with_python=true -d with_ast_grep=true") (combo "full" "-d with_docs_site=true -d with_ci_profile=true")
    @echo "template test: passed (core, rust, python, full)"

# Render one combination from the working tree (HEAD plus uncommitted changes) and check it
combo name data:
    #!/usr/bin/env bash
    set -euo pipefail
    unset VIRTUAL_ENV
    dest="$PWD/build/render/{{name}}"
    rm -rf "$dest"
    copier copy --defaults --quiet --vcs-ref HEAD \
      -d project_name="demo-{{name}}" \
      -d project_description="Rendered by the template self-test ({{name}})." \
      {{data}} "$PWD" "$dest" 2> >(grep -v -e DirtyLocalWarning -e '^  warn(' >&2)
    cd "$dest"
    git init -q -b main
    # Lockfiles belong to the scaffold commit, as in tools/new-project
    if [ -f Cargo.toml ]; then cargo generate-lockfile --quiet; fi
    if [ -f pyproject.toml ]; then uv sync --quiet; fi
    git add -A
    git -c commit.gpgsign=false -c user.name=template-test -c user.email=test@example.invalid commit -qm "render {{name}}"
    echo "== {{name}}: just check"
    just check
    docs_tools=true
    command -v mdbook >/dev/null && command -v pagefind >/dev/null && command -v lychee >/dev/null || docs_tools=false
    for check in $(just --dump --dump-format json | python3 -c 'import json, sys; print(*[d["recipe"] for d in json.load(sys.stdin)["recipes"]["hygiene"]["dependencies"]])'); do
      if [ "$check" = docs-check ] && ! $docs_tools; then
        echo "== {{name}}: docs-check not_run (mdbook, pagefind or lychee missing; run just bootstrap-docs in a render)"
        continue
      fi
      echo "== {{name}}: just $check"
      just "$check"
    done
    if [ -f docs/site.toml ] && $docs_tools; then echo "== {{name}}: just docs-test"; just docs-test; fi
    echo "== {{name}}: end-of-turn smoke (fixer off)"
    echo '{}' | AFTER_TURN_FIXER=off uv run --no-project --python 3.14 python scripts/after_turn.py stop --harness claude
    uv run --no-project --python 3.14 python scripts/after_turn.py prompt --harness claude </dev/null >/dev/null
    python3 - "$(git rev-parse --absolute-git-dir)/after-turn/report.json" "$docs_tools" <<'EOF'
    import json, sys
    report = json.load(open(sys.argv[1]))
    failed = sorted(k for k, v in report["checks"].items() if v["status"] != "passed")
    allowed = [] if sys.argv[2] == "true" else ["docs-check"]
    assert report["complete"], "end-of-turn report incomplete"
    assert set(failed) <= set(allowed), f"end-of-turn checks failed: {failed}"
    print(f"end-of-turn report: {len(report['checks'])} steps, failed {failed or 'none'}")
    EOF
    test -z "$(git status --porcelain)" || { echo "{{name}}: checks left the tree dirty"; git status --short; exit 1; }
    echo "== {{name}}: passed"
