"""Render and check environment setup for each layer without installs or native builds."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs)


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
            env = {**os.environ, "PATH": f"{tools}:/usr/bin:/bin", "CALL_LOG": str(log)}
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
            calls = log.read_text().splitlines()
            if python:
                assert calls[0] == "sync --locked --inexact", calls
            else:
                assert not any(call.startswith("sync ") for call in calls), calls
            results.append({"layer": combo, "passed": True, "copier": expected_pin})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
