"""The live-answer proxy (`live-proxy/`), run by its own `node --test` suite.

The suite stands up a fake OpenAI on localhost: no network, no key, no spend.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

PROXY = Path(__file__).resolve().parents[2] / "live-proxy"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node to run the proxy")
def test_the_live_proxy_suite_passes():
    # Its requests go to localhost; an ambient proxy setting must not catch them.
    env = {k: v for k, v in os.environ.items() if k.lower() not in {"https_proxy", "http_proxy", "node_use_env_proxy"}}
    result = subprocess.run(["node", "--test"], cwd=PROXY, env=env, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]


def test_the_proxy_holds_no_key():
    for path in PROXY.rglob("*"):
        if path.is_file():
            assert "sk-proj-" not in path.read_text(encoding="utf-8", errors="ignore"), path.name
    assert not (PROXY / ".env").exists()
