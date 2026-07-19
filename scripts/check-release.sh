#!/usr/bin/env bash
# Local release-readiness check. Run from project root. Mirrors CI.
set -euo pipefail

PY="${PYTHON:-python3}"
ROOT=$(pwd)

rm -rf dist build venv-check src/typing_refined/_version.py

"$PY" -m build
"$PY" -m ruff check src tests
"$PY" -m mypy src
"$PY" -m twine check dist/*

WHL=$(ls dist/*.whl)
SDIST=$(ls dist/*.tar.gz)

for label_artifact in "wheel:$WHL" "sdist:$SDIST"; do
    label=${label_artifact%%:*}
    artifact=${label_artifact#*:}
    venv="venv-check/$label"

    "$PY" -m venv "$venv"
    "$venv/bin/pip" install --quiet --upgrade pip
    "$venv/bin/pip" install --quiet --no-deps "$artifact"
    "$venv/bin/pip" install --quiet pytest

    tmp=$(mktemp -d)
    ln -s "$ROOT/tests" "$tmp/tests"
    (
        cd "$tmp"
        PYTHONPATH="" "$ROOT/$venv/bin/python" -m pytest tests/ -v
    )
    rm -rf "$tmp"
done

rm -rf venv-check
echo "==> SUCCESS"
ls -la dist/
