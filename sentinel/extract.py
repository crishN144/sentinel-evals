"""Mechanical destination extraction from tool-call arguments.

No model in the loop. Given the argument dict of a tool call (bash / python /
generic), return the network destinations (host[:port]) the command would try to
reach. This is the load-bearing primitive: Sentinel classifies these against an
allowlist. It is deliberately conservative — it extracts *stated* destinations
from the declared action, and the Limitations section is explicit that declared
args can be spoofed (METR observed ~7% tool-call spoofing).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# URLs: http(s)://host[:port]/...  and ws(s)://
_URL = re.compile(r"\b(?:https?|wss?|ftp)://[^\s'\"|;)<>]+", re.I)
# curl/wget/nc/ncat/socat style host tokens:  nc HOST PORT  |  socat ... TCP:host:port
_NC = re.compile(r"\b(?:nc|ncat|netcat)\b[^\n|;]*?\b([a-z0-9._-]+\.[a-z0-9._-]+|\d{1,3}(?:\.\d{1,3}){3})\b\s+\d{1,5}", re.I)
_SOCAT = re.compile(r"\b(?:TCP|UDP|OPENSSL)[46]?:([a-z0-9._-]+|\d{1,3}(?:\.\d{1,3}){3}):\d{1,5}", re.I)
# python requests/urllib string literals
_PYURL = re.compile(r"""(?:requests\.\w+|urlopen|urlretrieve|session\.\w+|httpx\.\w+)\s*\(\s*["']([^"']+)["']""", re.I)
# bare host:port (e.g. kubernetes.default.svc:443, 10.0.0.1:6443)
_HOSTPORT = re.compile(r"\b((?:[a-z0-9-]+\.)+[a-z0-9-]+|\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})\b", re.I)


def _host_of(url: str) -> str | None:
    try:
        u = urlparse(url if "//" in url else "//" + url)
        h = u.hostname
        return h.lower() if h else None
    except Exception:
        return None


def extract_destinations(arguments: dict | str) -> list[str]:
    """Return a de-duplicated, ordered list of destination hosts from a tool call."""
    if isinstance(arguments, dict):
        blob = " ".join(str(v) for v in arguments.values())
    else:
        blob = str(arguments)
    hosts: list[str] = []

    def add(h: str | None):
        if h and h not in hosts:
            hosts.append(h)

    for m in _URL.finditer(blob):
        add(_host_of(m.group(0)))
    for m in _PYURL.finditer(blob):
        add(_host_of(m.group(1)))
    for m in _NC.finditer(blob):
        add(m.group(1).lower())
    for m in _SOCAT.finditer(blob):
        add(m.group(1).lower())
    for m in _HOSTPORT.finditer(blob):
        add(m.group(1).lower())
    return hosts
