"""Pytest defaults that keep the suite hermetic.

Production workflows may set SPORTS_ENABLE_LIVE_FEED=1 at the job level so the
publish steps can use live data. Tests must not inherit that ambient setting:
unit tests should be deterministic and must never depend on third-party API
availability or free-tier rate limits.
"""

from __future__ import annotations

import os


def pytest_configure() -> None:
    """Disable network-backed feeds for the whole test process by default."""
    os.environ.setdefault("SPORTS_DISABLE_NETWORK", "1")
