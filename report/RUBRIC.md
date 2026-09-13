# AI Incident Response Sprint — Evaluator Rubric (grounded)

Compiled 2026-09-13. Evaluator-side only: what the judges reward, from the sprint's own
verbatim criteria, the judge roster, Apart's standard sprint format, and the primary incident
record. Tagged to source. "→" = implication, not a quote.

## Sources
- S1 sprint page (Overview/Tracks/Deliverable/Who-should-join/After) — apartresearch.com/sprints/ai-incident-response-sprint-2026-09-11-to-2026-09-13
- S2 judge roster (25 judges + 10 speakers), from the sprint page
- S3 Apart sprint format (from PAST Apart sprint pages, S-search): report on a template that is "provided at the start of the Sprint / linked on the submission page" (per-sprint Google Doc, on the Guidelines tab / Discord — NOT a stable public file); teams 1-5; peer review + open-licence publication. The official template for THIS sprint has NOT yet been retrieved (JS-gated Guidelines tab) — get it from the live page before writing the PDF.
- S4 primary incident record — EVIDENCE.md (OpenAI road-ahead, HF timeline, Anthropic 141k review, AISI incident + cheating study, METR/Redwood, CSA note)

Authority order: S1 > S2 > S3 > S4 (S4 is the substance a submission is judged against, not a rule).

---

## 0. The deliverable (S1, hard requirements)
- **Research report, PDF, on the official template** (Guidelines-tab template; abstract ≤150 words per checklist; template recommends ~4pp: Intro/Related ~1p, Methods+Results ~2.5p, Discussion ~0.5p; Limitations & Dual-Use appendix required; resubmit with SAME title to replace). Max 8 pages excluding refs/appendices; "most strong reports are 4 to 8."
- **Required structure (S1 verbatim):** "what you built, how you tested it, the headline finding, its limits, and what you would do next."
- **A `Limitations and Dual-Use Considerations` appendix is REQUIRED.** Not optional. Its absence is a gap a judge will note.
- **The artifact goes in a linked repo or an appendix** — "a benchmark, a harness, a filled-in regulatory instrument, a control matrix, a detector, a dataset, a protocol, a kit."
- Optional: public repo, 3–5 min video.
- Team 1–5; no prior participation required; AI tooling permitted (research sprint, not a no-LLM exam — cf. LASR/ERA).

→ Checklist: template used · ≤8pp body · all five structural elements present · Dual-Use appendix present · artifact linked and runnable/inspectable.

---

## 1. The scoring axes — THE REAL RUBRIC (apartresearch.notion.site/sprint-evaluation-rubric)
Three INDEPENDENT 1–5 dimensions. Calibration: 3 = solid weekend work; 5 ≈ top 5–10% on that dimension. Quality over quantity; verbosity hiding substance → minus Presentation; scattered experiments → minus Execution. Off-topic flag excludes from prizes.

| Dim | 3 | 4 | 5 |
|---|---|---|---|
| Impact & Innovation | clear problem, reasonable approach, some novelty beyond routine tool use | important problem + original approach OR neglected area; others can build on it | critical problem + genuinely novel approach + CLEAR THEORY OF CHANGE |
| Execution Quality | technically solid for the duration; interpretable; limitations acknowledged | thorough method, CONVINCING VALIDATION, results support conclusions, immediately useful | ambitious AND rigorous; surprising or unusually robust validation |
| Presentation & Clarity | problem/method/findings/limits present without undue effort | target audience gets it quickly | model for presenting this kind of work |

Reviewer instruction on 4–5 Impact: *is this actually new to the field, or replicating recent work?* → UNDISCLOSED prior work can disqualify; cite Inspect Scanners / ControlArena / SHADE / Watcher / Cilium by name.

(Below: my earlier synthesis, kept only as a lens.)
**Caveat:** Apart has not published a per-criterion scorecard for this sprint. The table below is MY synthesis, abstracted from the per-track "Judged on" lines (S1, verbatim) — treat the S1 lines in §2 as authoritative and this as a lens. The recurring emphasis it captures ("use", grounding, adoption, honest limits) IS directly quoted from S1.

| Axis | What it means here | Where S1 says it |
|---|---|---|
| **Usefulness / impact** | An artifact somebody OUTSIDE the sprint can pick up and use | "turn ... into an artifact somebody outside this sprint can use"; every track's "Judged on" leads with a usable output |
| **Rigor / grounding** | Claims tied to the public record — dates, quotes, named channels, per-phase counts | Track 2: "resolvable questions, checks somebody could run tomorrow"; Track 4: "grounding in the record (dates, quotes, named channels)" |
| **Adoption realism** | Would the intended recipient actually use it | Track 1: "would a lab actually adopt it"; Track 3: "could a regulator or legislator use it with light edits" |
| **Honesty about limits** | A stated bound on what the work establishes + a credible next step | Track 5: "a stated limit on what it establishes, and what a month of follow-up would add"; required Dual-Use appendix |

→ The single most repeated word across the track criteria is **"use"/"usable."** A judge's first question is "who picks this up, and does it work?" A polished analysis with no usable artifact scores below a rough artifact somebody could run.

---

## 2. Per-track criteria (S1 verbatim + what it operationalises)

### Track 1 — Containment: "what standard would have stopped this?"
Judged on (verbatim): "could a third party verify compliance without access to the lab's network, and would a lab actually adopt it."
→ Two hard tests: (a) **third-party-verifiable** — the standard/detector must work from evidence a lab would share (transcripts, configs, logs), NOT require access to the lab's internal network; (b) **adoptable** — cheap enough, and framed against what labs already said they'd build (AISI's real-time monitor, OpenAI's CoT-monitor requirement). A control matrix, an escape-detection harness, or a compliance-checkable containment spec all fit.

### Track 2 — What happened, and what breaks next
Judged on: "resolvable questions, checks somebody could run tomorrow, and causal explanations that predict something."
→ Not a retelling. Every claim must be (a) resolvable (someone could settle it), (b) actionable tomorrow, (c) predictive. A forecasting question set with resolution criteria, or a detection-rule set with a "run this on your own eval logs" checklist, fits.

### Track 3 — Regulatory Response
Judged on: "legal accuracy and specificity — could a regulator or a legislator use it with light edits?" CeSIA transmits passing outputs to its contacts with team credit.
→ A drafting exercise: a filled-in Article 91/serious-incident-report instrument, or a comparative reporting-duty analysis across EU AI Act / CA / NY. Requires legal precision; a real recipient exists.

### Track 4 — Communication: making the warning shot count
Judged on: "grounding in the record (dates, quotes, named channels) and evidence of reach — a playtest, a journalist's read, a creator's reply." "Producing communication counts as much as analysing it."
→ Must ship a communication artifact AND show it reached someone (a playtest, a reader reply).

### Track 5 — Open
Judged on: "an artifact somebody can use, a stated limit on what it establishes, and what a month of follow-up would add."

---

## 3. Who is judging → what actually gets weight (S2)
The roster is dominated by **detection/security engineers and eval-science people**, not policy generalists.

- **Detection & cloud-security engineers (largest bloc):** Ved K (Databricks, Kubernetes detection), Gaurav Thakur (Zscaler, agent red-teaming), Hariharan Subramanian & Nikhil Pallepati (Microsoft, AKS/Envoy — *the exact proxy layer the OpenAI egress abused*), Shashank Shelat (Earnest, DFIR/SOAR), Amey Kulkarni (Walmart, AI-agent governance/provenance). → A **Track 1/2 detection or containment artifact is read by people who build this for a living.** It must be technically real: correlate-not-page failure modes, short-lived-credential logic, egress boundaries. Hand-wave and they'll see it.
- **Eval-science / governance:** Kevin Wei (GovAI, *science of evaluations*, ex-AISI), Francesca Gomez (Arcadia, incident-escalation thresholds paper), Twm Stone (MATS security stream), Richard Willats (Mercor red-teaming). → reward correct framing of the eval-harness failure and measurement.
- **EU-AI-Act law:** Hannes Bastians (co-authored the Article 55 serious-incident-reporting commentary). → Track 3 legal accuracy is checked by someone who wrote the commentary.
- **Policy/forecasting:** Peter Wildeford, Heather Frase, David Manheim. → Track 2/3 base-rates and T&E realism.

→ For Crish specifically: the roster is **built for the Sentinel artifact.** A trace-level containment detector, framed in detection-engineering language, is the highest-fit thing on this board.

---

## 4. What a strong submission does (synthesised)
- **Leads with the artifact, not the narrative.** The incident is context; the deliverable is the point.
- **Grounds every number in the record.** 17,600 actions; 198/898 unsolved tasks → 93% of message-board tasks; 141,006 runs → 3 incidents; 7.8–14.1% cheating; detection latencies (days–months). Cite them.
- **States the counterfactual precisely.** "At trace event X, this monitor pages; the lab actually noticed at Y." That single sentence is the headline.
- **Names its own weak link + dual-use.** A detector is also an evasion map → mitigate by staying behavioural, not signature. Required appendix; do it well and it reads as maturity.
- **Third-party-verifiable and adoptable.** Works from shareable evidence; framed against what labs already committed to build.
- **Ships runnable.** Repo, Apache-2.0 (matches ExploitGym), tests, synthetic traces clearly labelled as reconstructed-from-public-record.

## 5. What sinks a submission
- No usable artifact (analysis only) — the criteria lead with "use" every time.
- Ungrounded claims / retelling without resolvable checks (Track 2's explicit failure).
- A detector/standard that needs the lab's internal network to verify (fails Track 1's first test).
- Missing Dual-Use appendix (required).
- Over-length or off-template.
- Treating it as red-teaming or "AI for SecOps" — S1 explicitly says it is neither.

## 6. Self-check (apply before submit)
- [ ] Official template, ≤8pp body, all five structural elements.
- [ ] Dual-Use + Limitations appendix present and real.
- [ ] Artifact linked, runnable/inspectable, open-licensed.
- [ ] Every quantitative claim cites a primary source.
- [ ] The counterfactual sentence (monitor-pages-at-X vs lab-noticed-at-Y) is explicit.
- [ ] Third-party-verifiable without lab-internal access.
- [ ] A named weak link + a "what a month adds" next step.
- [ ] Submitted early — Apart judges on a rolling/published-criteria basis; deadline Sep 13 AoE = ~1pm UK Mon.
