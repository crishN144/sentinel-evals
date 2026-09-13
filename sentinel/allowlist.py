"""Allowlist model + host classification. Allowlist-relative is the whole point:
a destination is out-of-scope iff it is not explicitly allowed and not local."""
from __future__ import annotations

import ipaddress
import json
from dataclasses import dataclass, field
from pathlib import Path

METADATA_IPS = {"169.254.169.254", "fd00:ec2::254"}  # cloud metadata (boundary probe)


@dataclass
class Allowlist:
    name: str
    internet_expected: bool = False
    allowed_hosts: set[str] = field(default_factory=set)      # exact host or ".suffix.com"
    allowed_cidrs: list[str] = field(default_factory=list)    # e.g. "10.0.0.0/8" for an internal range eval
    notes: str = ""

    def classify(self, host: str) -> str:
        """ALLOWED | LOOPBACK | METADATA | OUT."""
        h = host.lower().strip()
        if h in ("localhost",) or h.endswith(".localhost"):
            return "LOOPBACK"
        ip = None
        try:
            ip = ipaddress.ip_address(h)
        except ValueError:
            pass
        if ip is not None and (ip.is_loopback):
            return "LOOPBACK"
        if h in METADATA_IPS:
            return "METADATA"
        # wildcard: a scope that allows everything is not a scope (see ablation)
        if "*" in self.allowed_hosts:
            return "ALLOWED"
        # explicit allow (exact or domain-suffix)
        if h in self.allowed_hosts:
            return "ALLOWED"
        for a in self.allowed_hosts:
            if a.startswith(".") and (h == a[1:] or h.endswith(a)):
                return "ALLOWED"
        if ip is not None:
            for c in self.allowed_cidrs:
                try:
                    if ip in ipaddress.ip_network(c, strict=False):
                        return "ALLOWED"
                except ValueError:
                    continue
        return "OUT"


def load_allowlist(path: str | Path) -> Allowlist:
    p = Path(path)
    raw = p.read_text()
    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml  # optional
            data = yaml.safe_load(raw)
        except ModuleNotFoundError as e:  # pragma: no cover
            raise RuntimeError("PyYAML not installed; use a .json allowlist or `pip install pyyaml`") from e
    else:
        data = json.loads(raw)
    return Allowlist(
        name=data.get("name", p.stem),
        internet_expected=bool(data.get("internet_expected", False)),
        allowed_hosts={h.lower() for h in data.get("allowed_hosts", [])},
        allowed_cidrs=list(data.get("allowed_cidrs", [])),
        notes=data.get("notes", ""),
    )
