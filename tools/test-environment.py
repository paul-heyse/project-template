"""Render environment/workflow layers and verify protected updates without native builds."""

import json
import os
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    result = subprocess.run(args, check=False, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(f"{args}:\n{result.stdout}\n{result.stderr}")
    return result


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="template-env-") as name:
        base = Path(name)
        source = base / "source"
        source.mkdir()
        shutil.copytree(
            ROOT / "template",
            source / "template",
            symlinks=True,
            ignore=shutil.ignore_patterns("__pycache__", ".ruff_cache"),
        )
        shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
        run("git", "init", "-q", "-b", "main", cwd=source)
        run("git", "add", "-A", cwd=source)
        run(
            "git",
            "-c",
            "user.name=Template fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-qm",
            "Environment fixture",
            cwd=source,
        )
        for combo, rust, python in [
            ("core", False, False),
            ("rust", True, False),
            ("python", False, True),
            ("full", True, True),
        ]:
            dest = base / combo
            run(
                "copier",
                "copy",
                "--defaults",
                "--quiet",
                "--vcs-ref",
                "HEAD",
                "-d",
                f"project_name=demo-{combo}",
                "-d",
                "project_description=Environment fixture.",
                "-d",
                f"with_rust={str(rust).lower()}",
                "-d",
                f"with_python={str(python).lower()}",
                "-d",
                f"with_docs_site={str(combo == 'full').lower()}",
                "-d",
                f"with_ci_profile={str(combo == 'full').lower()}",
                str(source),
                str(dest),
            )
            expected_pin = run("copier", "--version").stdout.strip()
            assert (dest / ".python-version").read_text().strip(), (
                "Missing interpreter pin"
            )
            codex = tomllib.loads((dest / ".codex/config.toml").read_text())
            assert codex["allow_login_shell"] is False
            assert codex["features"]["shell_snapshot"] is False
            assert "daemon_auto_start" not in codex["features"]
            shell_settings = codex["shell_environment_policy"]["set"]
            assert shell_settings["UV_LOCKED"] == "1"
            # Exercise Bash's expansion of the literal HOME reference with an alternate
            # home. No workstation-specific helper or absolute checkout path is required.
            home = base / f"{combo}-home"
            bridge = home / ".config/codex/bash-env.bash"
            bridge.parent.mkdir(parents=True)
            bridge.write_text("export TEMPLATE_ENV_BRIDGE=loaded\nunset BASH_ENV\n")
            probe_env = {**os.environ, **shell_settings, "HOME": str(home)}
            probe = run(
                "/bin/bash",
                "--noprofile",
                "--norc",
                "-c",
                'test "$TEMPLATE_ENV_BRIDGE" = loaded && test -z "${BASH_ENV-}"',
                env=probe_env,
                cwd=dest,
            )
            assert not probe.stdout and not probe.stderr
            scripts = [dest / ".envrc", dest / "scripts/setup-env"]
            for script in scripts:
                assert "/home/paul" not in script.read_text(), script
                run("bash", "-n", str(script))
                run("shellcheck", "-s", "bash", str(script))
            run("just", "--list", cwd=dest)
            assert "/.envrc.local" in (dest / ".gitignore").read_text().splitlines()
            tools = base / f"{combo}-tools"
            tools.mkdir()
            log = tools / "calls"
            uv = tools / "uv"
            uv.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALL_LOG"\n')
            uv.chmod(0o755)
            env = {
                **os.environ,
                "PATH": f"{tools}:/usr/bin:/bin",
                "CALL_LOG": str(log),
                "LIBRARY_SKILLS_ROOT": str(base / "absent-store"),
            }
            env.pop("BASH_ENV", None)
            invalid = subprocess.run(
                ["bash", str(scripts[1]), "invalid"],
                env=env,
                capture_output=True,
                check=False,
            )
            assert invalid.returncode == 2 and not log.exists(), (
                "Invalid setup must have no effects"
            )
            run("bash", str(scripts[1]), cwd=base, env=env)
            calls = log.read_text().splitlines() if log.exists() else []
            if python:
                assert calls[0] == "sync --locked --inexact", calls
            else:
                assert not any(call.startswith("sync ") for call in calls), calls
            assert calls == (["sync --locked --inexact"] if python else []), calls
            assert not (dest / "scripts/library_skills.py").exists()
            assert not (dest / ".config/library-skills.toml").exists()
            assert not (dest / ".claude/agents").exists()
            run("git", "init", "-q", "-b", "main", cwd=dest)
            run("git", "add", "-A", cwd=dest)
            skill = ".claude/skills/design-principle-audit-tests/SKILL.md"
            companion = "docs/design_review/design_principles/core/test-assessment.md"
            audit = "docs/design_review/test-audit/README.md"
            run("git", "ls-files", "--error-unmatch", skill, companion, audit, cwd=dest)
            improvement_skill = ".claude/skills/plan-improvement-review/SKILL.md"
            review_collection = "docs/plan_improvement_reviews/README.md"
            run("git", "ls-files", "--error-unmatch", improvement_skill, review_collection, cwd=dest)
            improvement_discovery = dest / ".agents/skills/plan-improvement-review/SKILL.md"
            assert improvement_discovery.resolve() == (dest / improvement_skill).resolve()
            leverage_names = (
                "leverage-codebase-audit",
                "leverage-library-assessment",
                "leverage-opportunity-review",
            )
            for skill_name in leverage_names:
                skill_path = f".claude/skills/{skill_name}/SKILL.md"
                run("git", "ls-files", "--error-unmatch", skill_path, cwd=dest)
                assert (dest / ".agents/skills" / skill_name / "SKILL.md").resolve() == (
                    dest / skill_path
                ).resolve()
            for collection in ("codebase", "libraries", "reviews"):
                entry = f"docs/library_leverage/{collection}/README.md"
                run("git", "ls-files", "--error-unmatch", entry, cwd=dest)
                assert "not yet assessed" in (dest / entry).read_text()
            assert not (dest / "docs/library_leverage/assessment-patterns.md").exists()
            assert not list((dest / "docs/library_leverage").rglob("*0247*"))
            discovered = dest / ".agents/skills/design-principle-audit-tests/SKILL.md"
            assert discovered.resolve() == (dest / skill).resolve()
            standard_root = dest / "docs/design_review/design_principles"
            standard = tomllib.loads((standard_root / "standard.toml").read_text())
            assert standard["core"]["version"] == "3.3"
            selected = standard_root / standard["core"]["test_assessment"]
            assert selected == dest / companion
            assert "No test audit has been performed" in (dest / audit).read_text()
            for script in ["scripts/check_agents.py", "scripts/adr.py"]:
                args = ["lint"] if script.endswith("adr.py") else []
                run("uv", "run", "--no-project", "python", script, *args, cwd=dest)
            if combo == "full":
                # Exercise publication discovery on the actual rendered configuration,
                # including an authored review rather than only the collection guide.
                review = dest / "docs/plan_improvement_reviews/render-check_2026-10-24.md"
                review.write_text("# Authored plan improvement review\n\nProposed amendment I01.\n")
                leverage_review = dest / "docs/library_leverage/reviews/render-check.md"
                leverage_review.write_text("# Authored leverage review\n\nCBO-001 remains Proposed.\n")
                extra_patterns = dest / "docs/library_leverage/assessment-patterns.md"
                extra_patterns.write_text("# Assessment patterns\n\nLOP-X001: authored framing.\n")
                run(
                    "uv", "run", "--no-project", "python", "-c",
                    "import sys; sys.path.insert(0, 'scripts'); import docs; "
                    "pages = {str(p.path): p.scope for p in docs.discover(docs.ROOT, docs.config(docs.ROOT))}; "
                    "assert pages['.claude/skills/plan-improvement-review/SKILL.md'] == 'Current'; "
                    "assert pages['docs/plan_improvement_reviews/README.md'] == 'Reference'; "
                    "assert pages['docs/plan_improvement_reviews/render-check_2026-10-24.md'] == 'Reference'; "
                    "assert all(pages[f'.claude/skills/{name}/SKILL.md'] == 'Current' for name in "
                    "('leverage-codebase-audit', 'leverage-library-assessment', 'leverage-opportunity-review')); "
                    "assert pages['docs/library_leverage/README.md'] == 'Current'; "
                    "assert pages['docs/library_leverage/codebase/README.md'] == 'Reference'; "
                    "assert pages['docs/library_leverage/libraries/README.md'] == 'Reference'; "
                    "assert pages['docs/library_leverage/reviews/render-check.md'] == 'Reference'; "
                    "assert pages['docs/library_leverage/assessment-patterns.md'] == 'Reference'",
                    cwd=dest,
                )
                run(
                    "uv", "run", "--no-project", "--offline", "--no-python-downloads",
                    "--python", (dest / ".python-version").read_text().strip(),
                    "--with", "pytest", "pytest", "-q", "tests/scripts/test_docs.py",
                    "-k", "test_assessment_publication_scope",
                    "--basetemp", str(base / "publisher-tests"), cwd=dest,
                )
            results.append({"layer": combo, "passed": True, "copier": expected_pin})
        # Existing project content survives managed template changes, including new topic pages.
        dest = base / "core"
        protected = {
            "docs/plan_improvement_reviews/authored-review_2026-10-24.md": "# Authored plan improvement review\n\nI01 remains a proposal; the plan is unchanged.\n",
            "docs/design_review/audit/README.md": "# Authored diagnosis\n\nSource baseline and finding DA-001.\n",
            "docs/design_review/audit/semantic-model.md": "# Authored observations\n\nDA-001 remains project-owned.\n",
            "docs/design_review/test-audit/README.md": "# Authored test diagnosis\n\nIndependent baseline and DTA-001.\n",
            "docs/design_review/test-audit/support/helpers.md": "# Authored helper observations\n\nDTA-001 remains project-owned.\n",
            "docs/libraries/README.md": "# Project library index\n\n[Local overview](local.md)\n",
            "docs/library_leverage/README.md": "# Project leverage index\n\nCurrent opportunity routes.\n",
            "docs/library_leverage/library-leverage-framework.md": "# Project leverage binding\n\nLocal consumers and retention.\n",
            "docs/library_leverage/codebase/README.md": "# Authored opportunities\n\nSource baseline and CBO-001.\n",
            "docs/library_leverage/codebase/selection.md": "# Authored codebase topic\n\nCBO-001 has independent source evidence.\n",
            "docs/library_leverage/libraries/README.md": "# Assessed libraries\n\nRetained types need no current match.\n",
            "docs/library_leverage/libraries/example/selective-access.md": "# Reusable selective access\n\nKeep after CBO-001 retires.\n",
            "docs/library_leverage/libraries/example/applicability.md": "# Contextual fit\n\nCBO-001 remains conditional.\n",
            "docs/library_leverage/reviews/README.md": "# Current comparative judgments\n\nThe plan owns progress.\n",
            "docs/library_leverage/reviews/selection.md": "# Selection alternatives\n\nThe recommendation is Proposed.\n",
            "docs/library_leverage/assessment-patterns.md": "# Additional patterns\n\nLOP-X001 remains usable before manual promotion.\n",
            "docs/adr/0008-codebase-first-library-leverage.md": (
                dest / "docs/adr/0008-codebase-first-library-leverage.md"
            ).read_text(),
        }
        for relative, content in protected.items():
            (dest / relative).parent.mkdir(parents=True, exist_ok=True)
            (dest / relative).write_text(content)
        run("git", "add", "-A", cwd=dest)
        commit_args = [
            "git",
            "-c",
            "user.name=Template fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-qm",
        ]
        run(*commit_args, "Authored project content", cwd=dest)
        # New template versions may edit both scaffold and managed guidance.
        (source / "template/docs/design_review/audit/README.md.jinja").write_text(
            "Replacement scaffold\n"
        )
        (source / "template/docs/design_review/audit/semantic-model.md").write_text(
            "Replacement topic scaffold\n"
        )
        (source / "template/docs/libraries/README.md").write_text(
            "Replacement library index\n"
        )
        (source / "template/docs/design_review/test-audit/README.md.jinja").write_text(
            "Replacement test-audit scaffold\n"
        )
        collision = source / "template/docs/design_review/test-audit/support/helpers.md"
        collision.parent.mkdir(parents=True, exist_ok=True)
        collision.write_text("New template helper topic colliding with authored content\n")
        for relative in protected:
            if relative.startswith("docs/library_leverage/"):
                collision = source / "template" / relative
                collision.parent.mkdir(parents=True, exist_ok=True)
                collision.write_text("New template content colliding with authored leverage output\n")
        managed_leverage = source / "template/.claude/skills/leverage-library-assessment/SKILL.md"
        managed_leverage.write_text(managed_leverage.read_text() + "\nManaged leverage skill update.\n")
        (source / "template/docs/adr/0008-codebase-first-library-leverage.md.jinja").write_text(
            "Changed seed for new projects only\n"
        )
        managed_skill = source / "template/.claude/skills/design-principle-audit-tests/SKILL.md.jinja"
        managed_skill.write_text(managed_skill.read_text() + "\nManaged test-audit skill update.\n")
        managed_improvement = source / "template/.claude/skills/plan-improvement-review/SKILL.md"
        managed_improvement.write_text(managed_improvement.read_text() + "\nManaged improvement-review skill update.\n")
        managed_companion = source / "template/docs/design_review/design_principles/core/test-assessment.md"
        managed_companion.write_text(managed_companion.read_text() + "\nManaged test-assessment update.\n")
        guide = source / "template/docs/libraries/authoring-guide.md"
        guide.write_text(guide.read_text() + "\nManaged update fixture.\n")
        run("git", "add", "-A", cwd=source)
        run(*commit_args, "Managed template update", cwd=source)
        run("copier", "update", "--defaults", "--quiet", "--vcs-ref", "HEAD", cwd=dest)
        for relative, content in protected.items():
            assert (dest / relative).read_text() == content, relative
        updated_skill = dest / ".claude/skills/design-principle-audit-tests/SKILL.md"
        assert "Managed test-audit skill update." in updated_skill.read_text()
        updated_improvement = dest / ".claude/skills/plan-improvement-review/SKILL.md"
        assert updated_improvement.read_text() == managed_improvement.read_text()
        updated_leverage = dest / ".claude/skills/leverage-library-assessment/SKILL.md"
        assert updated_leverage.read_text() == managed_leverage.read_text()
        updated_companion = dest / "docs/design_review/design_principles/core/test-assessment.md"
        assert updated_companion.read_text() == managed_companion.read_text()
        assert (
            dest / "docs/libraries/authoring-guide.md"
        ).read_text() == guide.read_text()
        assert not list(dest.rglob("*.rej")), "Copier update conflicts"
        results.append({"update_preservation": "passed"})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
