"""Exercise the guide's runnable examples on local fixtures, without product builds."""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, check=False, **kwargs)
    if result.returncode:
        raise RuntimeError(f"{args}:\n{result.stdout}\n{result.stderr}")
    return result


def main():
    guide = (
        ROOT / "template/docs/library_leverage/references/discovery-and-evidence.md"
    ).read_text()
    examples = re.findall(r"```sh\n(.*?)\n```", guide, re.DOTALL)
    cargo, tree, metadata, imports, _ast_grep = examples
    with tempfile.TemporaryDirectory(prefix="library-discovery-") as name:
        base = Path(name)
        rust = base / "rust"
        (rust / "src").mkdir(parents=True)
        (rust / "src/lib.rs").write_text("")
        (rust / "Cargo.toml").write_text(
            '[package]\nname = "consumer"\nversion = "1.0.0"\nedition = "2021"\n'
            '[workspace]\nmembers = ["example"]\nresolver = "2"\n'
            '[dependencies]\nrenamed = { package = "example-crate", version = "=1.0.0", '
            'path = "example", optional = true, features = ["extra"] }\n'
            '[features]\ndefault = ["dep:renamed"]\n'
        )
        (rust / "example/src").mkdir(parents=True)
        (rust / "example/src/lib.rs").write_text("")
        (rust / "example/Cargo.toml").write_text(
            '[package]\nname = "example-crate"\nversion = "1.0.0"\nedition = "2021"\n'
            "[features]\nextra = []\n"
        )
        run("cargo", "generate-lockfile", "--offline", cwd=rust)
        lock = (rust / "Cargo.lock").read_bytes()
        commands = cargo.splitlines()
        graph = json.loads(run("bash", "-euc", commands[0], cwd=rust).stdout)
        consumer = next(p for p in graph["packages"] if p["name"] == "consumer")
        assert consumer["dependencies"][0]["rename"] == "renamed"
        example = next(p for p in graph["packages"] if p["name"] == "example-crate")
        node = next(n for n in graph["resolve"]["nodes"] if n["id"] == example["id"])
        assert "extra" in node["features"]
        features = run("bash", "-euc", commands[1], cwd=rust).stdout
        assert 'example-crate feature "extra"' in features
        assert (rust / "Cargo.lock").read_bytes() == lock
        assert not (rust / "target").exists(), "Inspection unexpectedly built a target"
        print(run("rustc", "--version", cwd=rust).stdout.strip())

        python = base / "python"
        python.mkdir()
        (python / "pyproject.toml").write_text(
            '[project]\nname = "example-dist"\nversion = "1.0.0"\nrequires-python = ">=3.11"\n'
        )
        run(
            "uv",
            "lock",
            "--offline",
            "--no-python-downloads",
            "--python",
            sys.executable,
            cwd=python,
            env={**os.environ, "UV_LOCKED": "0"},
        )
        run(
            "uv",
            "venv",
            "--offline",
            "--no-python-downloads",
            "--python",
            sys.executable,
            ".venv",
            cwd=python,
        )
        interpreter = python / ".venv/bin/python"
        site = Path(
            run(
                str(interpreter),
                "-c",
                "import sysconfig; print(sysconfig.get_path('purelib'))",
            ).stdout.strip()
        )
        distribution = site / "example_dist-1.0.0.dist-info"
        distribution.mkdir()
        (distribution / "METADATA").write_text(
            "Metadata-Version: 2.3\nName: example-dist\nVersion: 1.0.0\nProvides-Extra: batch\n"
        )
        (distribution / "top_level.txt").write_text("example_pkg\n")
        (distribution / "entry_points.txt").write_text(
            "[example.plugins]\nbatch = example_pkg:plugin\n"
        )
        (site / "example_pkg.py").write_text(
            "raise RuntimeError('Target library was imported')\n"
        )
        # Do not inherit the caller's project/interpreter selection into this independent fixture.
        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in (
                "VIRTUAL_ENV",
                "UV_PROJECT_ENVIRONMENT",
                "UV_PROJECT",
                "PYTHONPATH",
                "PYTHONHOME",
            )
        }
        lock = (python / "uv.lock").read_bytes()
        assert "example-dist" in run("bash", "-euc", tree, cwd=python, env=env).stdout
        installed = run("bash", "-euc", metadata, cwd=python, env=env).stdout
        assert "example-dist 1.0.0" in installed
        assert "advertised extras: ['batch']" in installed
        assert "entry point: example.plugins batch example_pkg:plugin" in installed
        assert "candidate distributions ['example-dist']" in installed
        missing = metadata.replace(
            "example-dist example_pkg", "missing-dist missing_pkg", 1
        )
        absent = run("bash", "-euc", missing, cwd=python, env=env).stdout
        assert "no distribution metadata" in absent
        assert "missing_pkg: candidate distributions unknown" in absent
        (python / "selected.py").write_text(
            "import example_pkg as alias\nif False:\n    from example_pkg import (\n"
            "        first,\n        second,\n    )\ndef nested():\n    import os\n"
            'text = "import misleading"\n# import comment_only\n'
        )
        selected = imports.replace("path/to/selected.py", "selected.py")
        parsed = run("bash", "-euc", selected, cwd=python, env=env).stdout
        assert "selected.py:1: import example_pkg as alias" in parsed
        assert (
            "selected.py:3: from example_pkg import (\n        first,\n        second,"
            in parsed
        )
        assert "selected.py:8: import os" in parsed
        assert "misleading" not in parsed and "comment_only" not in parsed
        (python / "broken.py").write_text("from (\n")
        incomplete = selected.replace(
            "selected.py <<", "selected.py broken.py missing.py <<", 1
        )
        partial = subprocess.run(
            ["bash", "-euc", incomplete],
            cwd=python,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert partial.returncode == 1
        assert partial.stdout == parsed
        assert (
            "broken.py: skipped" in partial.stderr
            and "missing.py: skipped" in partial.stderr
        )
        assert (python / "uv.lock").read_bytes() == lock
    print(
        "Library discovery examples: passed (Rust graph/features; Python tree/metadata/imports/gaps)"
    )


if __name__ == "__main__":
    main()
