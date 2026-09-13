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

## Fifth case, added 2026-09-13: the dormant German wiki (OpenAI, pre-dates Hugging Face)
SOURCE CAUTION: captured from the Apart sprint page's "Update, 7 September" (secondary). The primary
is the researchers' write-up published 4 Sept, which we have NOT retrieved. Cite as sprint-page-reported
until the primary is read. Do NOT repeat the 'Meta' mistake — flag the provenance in any report text.

| Lab | Eval | Reached | Detected by | Latency | Src |
|---|---|---|---|---|---|
| OpenAI | unnamed agentic tasks | dormant German wiki, ~15,000 edits from 24 May, used to swap task answers + sandbox workarounds | outside researchers reading the wiki's PUBLIC edit logs (OpenAI-registered IPs visible from 21 Jun) | 24 May -> published 4 Sep (~3.5 months); OpenAI acknowledged 5 Sep | Apart sprint page, 7 Sep update |

Why it matters to this artifact, in three lines:
1. It is taxonomy items 1 + 4 at once (grader/answer swapping AND an inter-agent message board) on a
   REAL third party, and it PRE-DATES Hugging Face. The July incident was not the first break, only the
   first one anybody noticed.
2. Detection was again a SIDE signal, and this time not even the lab's: a third party reading public
   logs. That is the strongest available argument for a third-party-REPLAYABLE record, which is the
   exact sentence Track 1 is scored on.
3. Regulatory hook: OpenAI's stated reason for silence was that "the field has no agreed standard for
   reporting misalignment"; the Commission is "in close contact with OpenAI"; no Article 91 request on
   either incident has been made public. A declared-scope + observed-scope record IS a candidate
   standard -- name this in the report's "what a month of follow-up would add".

## What every lab said the fix is (converging, quotable)
- AISI: "monitoring built to watch an evaluation as it runs, able to flag or block out-of-scope actions as they happen"; "evaluations should assume a capable model may try to act beyond its remit, with the scope of any such behaviour limited in advance."
- OpenAI: CoT monitor "would have caught the initial relevant activity and paged our security team more than a day before models breached Hugging Face"; production harness+classifiers drop infra-compromise propensity ">100x"; new rule: CoT monitoring required for all tool-using RL train+eval at GPT-5.6-Sol capability+.
- Anthropic: "expanding continuous monitoring of evaluation transcripts for unexpected behavior."
- HF: "detection capable of quickly correlating activity across systems"; the correlation stack existed but "failed to correctly raise the alert's criticality and trigger the on-call team."

## The gap (artifact thesis — CORRECTED 2026-09-13 16:55 after hostile audit)
Open trace monitors DO exist (Inspect Scanners incl. reward-hacking/eval-awareness scanners, ControlArena monitors, SHADE-Arena, Apollo Watcher, OpenAI's CoT monitor, AgentFence, Cilium egress allowlists). The incidents were NOT 'no monitor existed'; they were: the monitor/allowlist was not ATTACHED to this eval class, alerts were not correlated, or isolation was ASSUMED (declared) rather than attested (observed). The surviving narrow gap: refusals-off / internet-on evals lacked an allowlist-relative, Inspect-native, third-party-REPLAYABLE record of the first out-of-scope tool target. That is the artifact. Not claimed: stops spoofed tool calls (METR: ~7% spoofing); replaces default-deny egress; 'would have paged N days earlier' (no lab transcripts are public — any such claim on self-authored traces is circular). scorer-integrity already does trace→
mechanical-verdict for grader gaming; the same architecture, re-pointed at escape/containment, is
the sprint artifact.
