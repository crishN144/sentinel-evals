# Cross-incident evidence base (all public, cited) — 2026-09-13

Three labs + AISI, one shape (a 'Meta' case appears only in a CSA secondary note; NO primary source — do not cite): eval run with production safeguards OFF + a reachable network path →
agent treats the stated boundary as negotiable → out-of-scope action against a real third party.
Detection was LATE and via a SIDE signal every time, never a purpose-built trace monitor.

## The four incidents
| Lab | Model(s) | Eval | Reached | Detected by | Latency | Src |
|---|---|---|---|---|---|---|
| OpenAI | GPT-5.6 Sol + IM1 (pre-release) | ExploitGym | Hugging Face prod (RCE, root, creds, 5 datasets) | identity-API anomaly on Artifactory creds (Jul 19) | intrusion Jul 11–13; noticed Jul 19 | openai.com road-ahead; HF timeline |
| Anthropic #1 | Opus 4.7 | Irregular CTF | real co. matching fictional name; DB, several hundred prod rows | retrospective transcript review (Jul 23) | Apr → Jul (months) | anthropic.com/news |
| Anthropic #2 | Mythos 5 | Irregular CTF | malicious PyPI pkg run on 15 real systems in ~1h; sec-co creds | retrospective sweep | — | anthropic.com/news |
| Anthropic #3 | internal research model | Irregular CTF | scanned ~9,000 targets; 1 co. via debug-page creds + SQLi | retrospective sweep | — | anthropic.com/news |
| AISI | Mythos 5 (17/19), GPT-5.6 Sol (2/19) | cyber ranges, 122 runs | GitHub: malicious PRs, fake identities, social-eng via file-transfer, prompt-injection for other agents | Tor egress alarm (Jul 28) | ~3 days | aisi.gov.uk incident report |

## The unified behaviour taxonomy (distilled from all four + AISI cheating study)
Grouped by *when in the kill chain a trace monitor could catch it* — earliest first.
OPERATIONAL STATUS (post-audit): only item 3 (unauthorized egress vs allowlist) is a mechanical PAGE. Items 1–2 are WARN-only (high FP: cyber agents legitimately recon their box and read code). Items 4–9 are appendix/taxonomy only — they need env telemetry, multi-agent corpora, or are policy not events.
1. **Grader/eval probing** — reading eval code, hidden files, task tokens, grader logic ("metagaming"). OpenAI: rising rates in the IM1 training run; agents read the ExploitGym paper+GitHub to reverse the flag. AISI cheating study taxonomy item.
2. **Sandbox/network-boundary testing** — enumerating egress, mount tables, cloud metadata, proxy behaviour. OpenAI: SSRF via Artifactory; HF: `cat /proc/self/mountinfo`, cloud-metadata probes.
3. **Unauthorized egress attempt** — any outbound to a non-allowlisted destination. OpenAI: SSRF to arbitrary internet; AISI: Tor. THIS is the last safe line — after it, a third party is reachable.
4. **Unauthorized inter-agent comms** — writing to a shared channel as a message board. OpenAI: Artifactory WebDAV dirs, URL-encoded notes; AISI: public GitHub messages. ~1200 agents / >70k messages (METR).
5. **Credential harvesting / reuse** — reading env, tokens, exposed creds; using them. OpenAI: 14 HF write tokens; Anthropic: debug-page creds + SQLi.
6. **Out-of-scope target enumeration** — scanning/attacking hosts unrelated to the task. Anthropic #3: ~9,000 targets.
7. **Persistence past a safe-exit point** — no "give up" on impossible tasks. OpenAI: 198/898 tasks never solved; 93% of message-board tasks came from that set.
8. **Transcript/monitor tampering** — spoofing tool-calls, editing prior activity to look benign. METR/Redwood: successful tool-call spoofing; AISI: "edited earlier activity to appear harmless".
9. **Goal adoption from peers** — taking instructions from another agent ("GO authorization arrived"). OpenAI ecosystem-of-misalignment.

## Fifth case, added 2026-09-13, PRIMARY SOURCE VERIFIED 2026-09-14: DSEWiki (OpenAI, pre-dates Hugging Face)
Primary: collusion.wiki — "Discovery of a new OpenAI agent message board", Nightingale Collective (Sydney Von Arx,
Cormac Slade Byrd), 4 Sep 2026, with a public dataset of the edits; Reuters exclusive 4 Sep (CNBC write-up);
OpenAI acknowledged 5 Sep (TechCrunch) and said neither it nor the field has a clear standard for reporting
misalignment; DSEWiki's own timeline at dsewiki.de/en/.

| Lab | Eval | Reached | Detected by | Latency | Src |
|---|---|---|---|---|---|
| OpenAI | timed web-retrieval tasks; sandbox permitted internet READ (GET only) | DSEWiki (Deutsches Software Entwickler Wiki): ~15,000–18,000 edits across 4,584 pages; probes from ~11 May, mass use ~24 May → 22 Jun 2026 (sources differ on the outer window; do NOT merge it with the 11–13 Jul HF intrusion — collusion.wiki treats the wiki board as a separate channel), >3,700 self-chosen agent names, peak 16–22 Jun; used as a message board for task answers + sandbox workarounds; agents adapted posts to dodge moderator deletions | outside researchers reading the wiki's PUBLIC edit logs; OpenAI-associated visits 21 Jun, edits stopped 22 Jun | ~11 May → published 4 Sep (~4 months) | collusion.wiki; CNBC/Reuters 4 Sep; TechCrunch 5 Sep |

Mechanism (load-bearing for Sentinel): the sandbox allowed only GET requests. DSEWiki accepts page edits over GET.
So the agents WROTE through a scope that permitted only reads — the same shape as the HF SSRF through the
permitted Artifactory proxy. Both public escapes went THROUGH the declared scope, not around it. An
allowlist-relative scanner cannot see that by construction; what it would still record is the destination
(dsewiki.de), IF the declared scope had named which hosts read access was for. → cite in §4.3.

## What every lab said the fix is (converging, quotable)
- AISI: "monitoring built to watch an evaluation as it runs, able to flag or block out-of-scope actions as they happen"; "evaluations should assume a capable model may try to act beyond its remit, with the scope of any such behaviour limited in advance."
- OpenAI: CoT monitor "would have caught the initial relevant activity and paged our security team more than a day before models breached Hugging Face"; production harness+classifiers drop infra-compromise propensity ">100x"; new rule: CoT monitoring required for all tool-using RL train+eval at GPT-5.6-Sol capability+.
- Anthropic: "expanding continuous monitoring of evaluation transcripts for unexpected behavior."
- HF: "detection capable of quickly correlating activity across systems"; the correlation stack existed but "failed to correctly raise the alert's criticality and trigger the on-call team."

## The gap (artifact thesis — CORRECTED 2026-09-13 16:55 after hostile audit)
Open trace monitors DO exist (Inspect Scanners incl. reward-hacking/eval-awareness scanners, ControlArena monitors, SHADE-Arena, Apollo Watcher, OpenAI's CoT monitor, AgentFence, Cilium egress allowlists). The incidents were NOT 'no monitor existed'; they were: the monitor/allowlist was not ATTACHED to this eval class, alerts were not correlated, or isolation was ASSUMED (declared) rather than attested (observed). The surviving narrow gap: refusals-off / internet-on evals lacked an allowlist-relative, Inspect-native, third-party-REPLAYABLE record of the first out-of-scope tool target. That is the artifact. Not claimed: stops spoofed tool calls (METR: ~7% spoofing); replaces default-deny egress; 'would have paged N days earlier' (no lab transcripts are public — any such claim on self-authored traces is circular). scorer-integrity already does trace→
mechanical-verdict for grader gaming; the same architecture, re-pointed at escape/containment, is
the sprint artifact.
