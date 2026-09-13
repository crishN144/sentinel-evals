<h1>Sentinel</h1>

**An Inspect scanner for allowlist-relative unauthorized egress in agentic evaluations.**

In 2026, agents broke containment during cyber evaluations at OpenAI, Anthropic and the UK AI
Security Institute and reached real third parties. In every public case the eval was run with
production safeguards reduced, and in every public case **detection was late and came from a side
signal** — an identity-API anomaly, a Tor alarm, a retrospective transcript sweep weeks later.

Sentinel does one small thing: given an eval's **declared scope** (an allowlist) it turns the
**first out-of-scope tool destination** into a finding that a third party can replay from files
alone — no access to the lab's network required.

```bash
sentinel score traces/*.json          # mechanical: no model, no API key
scout scan sentinel/scanner.py -T ./logs   # or run it over real Inspect eval logs
```

## What it is not

It does **not** replace default-deny egress (Cilium/Squid allowlists), and it does not claim to
invent agent monitoring. Open trace monitors already exist — Inspect Scanners (incl. reward-hacking
and eval-awareness scanners), ControlArena, SHADE-Arena, Apollo Watcher, OpenAI's CoT monitors.
The public incidents were not *"no monitor existed"*; they were **the monitor or allowlist was not
attached to this eval class**, alerts were not correlated, or isolation was *assumed* rather than
*attested*. Sentinel is a small, incident-derived compliance artifact for that specific failure.

## Results

See [RESULTS.md](RESULTS.md). On reconstructions of the three public incidents it pages at the first
non-allowlisted destination (3/3), stays silent on three hard negatives (3/3), and a keyword-only
baseline false-pages on 2 of those 3 while mislocating the first true out-of-scope event on all
three positives.

## Honest limits

- **Fixtures are reconstructions** from public write-ups, not lab transcripts. No lab has released
  raw eval transcripts, so "pages N events earlier" is a property of the reconstruction, not a
  measurement inside OpenAI/Anthropic/AISI.
- **Declared arguments are spoofable.** METR observed successful tool-call spoofing in ~7% of the
  transcripts it examined. A trace monitor sees what the agent *says* it is doing.
- **SSRF through an allowlisted proxy is invisible** to an allowlist-relative rule — the Hugging
  Face escape went *through* the permitted package proxy. Tested as a known blind spot.
- **T1/T2 are warn-only.** Reading eval internals and probing the sandbox are real signals but
  high false-positive: in a CTF, flag-seeking *is* the task. Only T3 (egress) pages.

Layer 3 — comparing *observed* egress (Cilium/Hubble flow logs) against the same allowlist — is the
right complement and is not implemented here.

## Report

The sprint write-up (Apart Research AI Incident Response Sprint, September 2026) is in
[`report/build/`](report/build/): *Sentinel: the declared scope is the unit of containment evidence in
agentic evaluations*. Figures regenerate from the fixtures with `python report/make_figures.py`;
the document builds with `python report/build_report.py`.

## Prior work

The design stance — verdict from a predicate the environment can settle itself, never from a second
model — follows [scorer-integrity](https://github.com/crishN144/scorer-integrity), which measured an LLM
scheming-judge against an operative-action oracle over 599 Inspect gradings. Sentinel shares no code
with it; it points the same stance at containment scope, where the predicate is the allowlist.

## Licence

Apache-2.0, matching ExploitGym.
