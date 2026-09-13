"""Sentinel: allowlist-relative unauthorized-egress detection for agentic evals."""
__version__ = "0.1.0"
from .core import scan_trace, Finding, Severity  # noqa: F401
from .allowlist import Allowlist, load_allowlist  # noqa: F401
