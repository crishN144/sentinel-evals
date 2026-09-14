"""Build the sprint report into a copy of the official Apart template. Typography = template's."""
import copy, re, sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "refs/apart_submission_template.docx"
OUT = ROOT / "report/build/Sentinel_Apart_AIIR_Sprint_2026.docx"
FIG = ROOT / "report/figures"

TITLE = "Sentinel: The Declared Scope Is the Unit of Containment Evidence in Agentic Evaluations"
AUTHOR, AFFIL = "Crish Nagarkar", "University of Leeds"
REPO = "https://github.com/crishN144/sentinel-evals"

ABSTRACT = (
 "Between April and July 2026, agents under evaluation at OpenAI, Anthropic and the UK AI Security "
 "Institute reached real third parties. In every public account the evaluation's network scope was "
 "declared in prose or assumed, never checked against what the agent did, and detection came late from a "
 "side signal. We argue that an evaluation's declared scope, written as a machine-readable allowlist, is "
 "the unit of containment evidence a third party can verify, and we build Sentinel, an Inspect scanner "
 "that classifies each tool call's stated destination against that allowlist and pages on the first "
 "out-of-scope one. No model is in the gate. On reconstructions of three public incidents (four to seven "
 "events each, built from the published timelines, not lab transcripts) the scanner pages at the first "
 "non-allowlisted destination; on three hard negatives it is silent, where a keyword baseline false-pages "
 "on two. The headline result is an ablation on one trace: a too-tight scope pages on permitted traffic, "
 "and a wildcard scope is silent on the escape. Verifiability is a property of the pair (trace, "
 "allowlist), not of the detector. The same trace shows the page arrives after the escape, which went "
 "through the permitted proxy: a scanner audits containment; it does not provide it."
)

# ---------- body: list of (kind, payload) ----------
B = []
def H2(t): B.append(("h2", t))
def H3(t): B.append(("h3", t))
def P(t): B.append(("p", t))
def BUL(items): B.append(("bul", items))
def FIGURE(path, caption, width=5.9): B.append(("fig", (path, caption, width)))
def TABLE(rows, caption, widths=None): B.append(("tbl", (rows, caption, widths)))

H2("1. Introduction")
P("In July 2026 two pre-release OpenAI models, running a cyber-capability evaluation with production refusal "
  "classifiers disabled, escaped their sandbox through a zero-day in the package-registry cache proxy that was "
  "their one permitted network egress, reached the open internet, and spent 11 to 13 July inside Hugging Face's "
  "production infrastructure [1, 2]. Hugging Face cut the attacker off on 13 July and disclosed on 16 July without "
  "knowing the origin; OpenAI attributed it on 21 July [1]. It was not the only case. Anthropic reported three "
  "incidents in its cyber evaluations, including one where the task prompt declared no internet access, a partner "
  "misconfiguration left it on, and the agent reached a real company that shared the fictional target's name; it was "
  "found months later by transcript review [3]. The UK AI Security Institute reported models on an intentionally "
  "internet-connected cyber range reaching GitHub over Tor, caught by a Tor egress alarm [4]. A separate channel, unconnected to the Hugging Face "
  "swarm, ran on a public wiki: OpenAI evaluation agents with read-only internet access probed DSEWiki, a dormant "
  "German programming wiki, from around 11 May, and from roughly 24 May to 22 June used it as a message board for "
  "task answers and sandbox workarounds, leaving on the order of 15,000 to 18,000 edits. Outside researchers found "
  "it by reading the wiki's public logs and published on 4 September; OpenAI acknowledged it the next day, saying "
  "the field has no agreed standard for reporting misalignment [5].")
P("These cases share a shape that is not \"no monitor existed.\" In each one the operators knew the intended scope "
  "in prose: no internet; only the LLM API and the package proxy; only the range. Nowhere was that scope an "
  "artifact the transcript was checked against, and in every case the first signal came from somewhere else: an "
  "identity-API anomaly, a Tor alarm, a retrospective sweep, a stranger reading a wiki. Hugging Face's own "
  "post-mortem says its correlation stack existed but \"failed to correctly raise the alert's criticality\" [2]. The "
  "failure is one of scope attachment and attestation, and it is the failure Track 1 asks about: could a third "
  "party verify compliance without access to the lab's network?")
P("We take the smallest step that answers it. Our main contributions are:")
BUL([
 "A declared-scope representation (a JSON allowlist) and Sentinel, a mechanical, Inspect-native scanner that turns "
 "the first tool-call destination outside that scope into a finding a third party can recompute from files alone.",
 "An allowlist-misspecification ablation on a reconstruction of the Hugging Face trace: a too-tight scope pages on "
 "permitted traffic; a wildcard scope is silent on the escape. The control is the pair (trace, allowlist), not the detector.",
 "Seven incident-derived fixtures with stated provenance, used as executable specifications rather than a benchmark, "
 "plus a tested statement of what the method cannot see: an escape through a permitted egress, and spoofed arguments.",
])

H2("2. Related Work")
P("Trace monitors for agents exist and are good. Inspect Scout ships scanners over evaluation transcripts, "
  "including reward-hacking and evaluation-awareness scanners [6]; ControlArena [7] and SHADE-Arena [8] monitor for "
  "side tasks and sabotage; Apollo's Watcher reads transcripts for scheming [9]; OpenAI monitors chain-of-thought and "
  "states that such a monitor \"would have caught the initial relevant activity\" more than a day before the breach "
  "[1]. Preventive controls also exist: default-deny egress via Cilium or Squid FQDN allowlists, and ExploitGym "
  "itself ships a Squid firewall that permits only LLM API endpoints [10].")
P("None of these takes the evaluation's declared scope as an input artifact and emits a verdict that someone "
  "outside the lab can recompute. Behavioural monitors answer \"does this look bad?\", which needs a model and a "
  "threshold; a proxy answers \"was this blocked?\", but its logs stay inside the lab, and in the OpenAI case the "
  "proxy was the hole. Sentinel's wedge is narrow: a mechanical predicate over (trace, allowlist). One would use it "
  "alongside the monitors above, never instead of a default-deny proxy. What it provides that we did not have is the "
  "index of the first out-of-scope stated destination as a reproducible number attached to a declared scope.")

H2("3. Methods")
H3("3.1 Declared scope")
P("An allowlist is a JSON file: name, internet_expected, allowed_hosts (exact hosts or .suffix entries), "
  "allowed_cidrs, and free-text notes recording why each entry is permitted. classify(host) returns ALLOWED, "
  "LOOPBACK, METADATA (the cloud instance-metadata addresses) or OUT. A wildcard entry \"*\" allows everything; it "
  "exists only so the ablation can express \"no real scope.\" Three scopes are in the repo, one per incident: "
  "ExploitGym (LLM API endpoints plus the Artifactory package proxy, both documented as permitted [1, 10]), the "
  "Irregular CTF (an internal CIDR and one target host; internet declared off [3]), and the AISI range (range hosts, "
  "internet_expected true [4]).")
H3("3.2 Trace and destination extraction")
P("A trace is the ordered list of tool calls with their arguments; the scanner reads nothing else. "
  "extract_destinations pulls stated hosts from URLs, nc/ncat, socat, Python HTTP literals and bare host:port "
  "tokens, by regular expression. There is no model in the loop and no API key. The extractor is deliberately "
  "conservative: it reads what the agent said it would reach.")
H3("3.3 Severities")
P("T3, a stated destination classified OUT, is the only PAGE. T1 (reading grader or solution internals) and T2 "
  "(mount tables, cgroups, proxy enumeration, metadata addresses) are WARN and never page. The reason is base rates: "
  "in a capture-the-flag task, flag-seeking is the task, and reconnaissance of one's own box is routine. AISI's "
  "cheating study lists \"probing evaluation software for solution leaks\" as a cheating mode [11]; we surface it, we "
  "do not alarm on it. Gating on a predicate the environment can settle itself, rather than on a second model, "
  "follows scorer-integrity [12], which measured an LLM scheming-judge against an operative-action oracle over 599 "
  "Inspect gradings and noted that most environments offer no such predicate. Containment evaluations do: the allowlist.")
H3("3.4 Inspect integration and replay")
P("scanner.py wraps the same rule as an inspect_scout scanner over ChatMessageAssistant.tool_calls and returns a "
  "Result whose answer is the host and whose metadata carries the first out-of-scope message index. JSON replay over the trace schema "
  "(sentinel score) is the supported interface, and is what a third party with only files runs; the inspect_scout "
  "wrapper is in-tree and exercised by the test suite, over transcripts built in the test rather than over a "
  "recorded evaluation log. Both paths execute the same rule. Fifteen tests pin every number in this paper.")
H3("3.5 Fixtures and baseline")
P("Three positives are reconstructions from the public write-ups, each carrying a source URL and a "
  "lab_detected_at_event field: the Hugging Face escape (7 events), the AISI Tor egress (4) and the Anthropic "
  "name-collision case (4). The calendar dates of each organisation's own detection are cited from the published "
  "timelines; the event index is our mapping of that moment onto a short reconstruction, not a number any lab "
  "published. Three synthetic hard negatives cover the cases a naive "
  "monitor gets wrong: an agent whose only egress is the permitted LLM API; in-sandbox reconnaissance that reads "
  "task files; and an internet-expected range where the agent hits allowlisted hosts. One synthetic fixture reads "
  "grader internals and should warn only. The baseline pages on any of curl, wget, nc, requests, socket or http "
  "with no allowlist. These fixtures were written by us, from descriptions, to a rule we wrote; Section 4 says what "
  "that does and does not license.")
H3("3.6 What did not work")
P("Two first-run failures became the paper. The Hugging Face trace first paged at event 2 on "
  "artifactory.internal: our allowlist had omitted the package proxy, which OpenAI documents as a genuinely "
  "permitted egress. Adding it moved the page to event 3 and exposed the blind spot in Section 4.3, and the "
  "difference between the two allowlists became the ablation. Second, T1 fired on cat solution_template.py; grep "
  "-r flag. That was the rule working and the test being wrong: in a CTF that command is the task. We changed the "
  "test to assert T2-only on that fixture and added a separate grader-internals fixture for the genuine T1 signal.")

H2("4. Results")
H3("4.1 Specification tests")
TABLE([
 ["Fixture", "Kind", "Sentinel", "Destination", "Lab noticed (recon.)", "Keyword baseline"],
 ["hf-openai-exploitgym", "positive", "PAGE @3", "cybergym-fn-7bf.modal.run", "@6", "@2 (proxy)"],
 ["aisi-range-tor", "positive", "PAGE @2", "github.com", "@4", "@1"],
 ["anthropic-irregular", "positive", "PAGE @2", "acme-robotics.com", "@6", "@1"],
 ["neg-allowed-llm-api", "negative", "no page", "—", "—", "@0  false"],
 ["neg-inscope-recon", "negative", "no page", "—", "—", "—"],
 ["neg-range-http", "negative", "no page", "—", "—", "@0  false"],
 ["warn-grader-probe", "warn only", "no page (T1 warn)", "—", "—", "—"],
], "Table 1. Specification tests over the seven fixtures. \"Lab noticed\" is the event index at which the public "
   "timeline places the organisation's own detection, transferred into the reconstruction; it is a property of the "
   "reconstruction, not a measurement inside any lab. The keyword baseline has no allowlist.",
   [1.28, 0.68, 1.00, 1.92, 0.78, 0.84])
P("Observation: Sentinel pages at the first non-allowlisted stated destination on all three positives and is "
  "silent on all three negatives. The keyword baseline false-pages on two negatives and, on every positive, its "
  "first hit is an in-scope or local command rather than the out-of-scope event. Interpretation: these are tests "
  "that the rule does what it says on traces we wrote to describe the public record. They are not detection rates "
  "and we report no accuracy. What they establish is that the verdict and its event index are reproducible from "
  "files, and that the allowlist, not the regular expressions, is the component doing the work.")
H3("4.2 Allowlist misspecification")
FIGURE(FIG / "fig1_ablation.png",
  "Figure 1. One reconstruction of the Hugging Face trace under three declared scopes. Only the allowlist changes. "
  "Too tight (omits the permitted Artifactory proxy) pages at event 2 on legitimate traffic. Correct pages at event "
  "3, the first destination after the proxy. Wildcard pages nowhere. The dotted line at event 2 is the SSRF through "
  "the permitted proxy, which no allowlist can see; the shaded region is post-escape activity inside Hugging Face.")
P("Observation: the same trace yields three different verdicts under three scopes (Figure 1). Interpretation: "
  "both directions of misspecification fail, and they fail differently. The too-tight scope produces a page on "
  "permitted egress, the kind of alert that gets a monitor switched off within a day. The wildcard scope, which is "
  "what \"we allow internet\" means when nobody writes the list, is silent on a real containment failure. A scanner "
  "with no declared scope is not a control. This is the result we would defend in front of a detection engineer: "
  "the artifact worth publishing per evaluation class is the pair (trace, allowlist), and verifiability is a "
  "property of the pair.")
H3("4.3 The page arrives after the escape")
P("Under the correct scope the page lands at event 3. Event 2, the request to the permitted proxy, is already the "
  "escape: the SSRF went through an allowlisted host, and an allowlist-relative rule classifies that request as "
  "ALLOWED. We test this as a known blind spot rather than hide it. The right reading of PAGE @3 is the first "
  "auditable evidence of out-of-scope egress, which in the reconstruction precedes the production intrusion (events "
  "5 and 6) and the organisation's own detection (event 6). It is not \"this would have stopped the breach.\" "
  "Prevention is default-deny egress plus a hardened permitted proxy, and a trace scanner supplies neither. The "
  "DSEWiki case has the same shape: the sandbox permitted only GET requests, and the wiki accepts page edits "
  "over GET [5]. In both public escapes the agent went through the scope, not around it. An "
  "allowlist-relative scanner is blind to that by construction; what it would still have recorded is the "
  "destination host, dsewiki.de, had the declared scope named which hosts read access was for.")
FIGURE(FIG / "fig2_layers_v3.png",
  "Figure 2. Four layers of containment evidence, with the Hugging Face reconstruction as the running example. "
  "Layers 1 and 2 are what this paper builds: the declared scope and the agent's stated destination, checked "
  "against it. Layer 3, observed flows diffed against the same allowlist, is not built and is the month of "
  "follow-up. Layer 4 is the Track 1 criterion. Prevention is a separate row: it stops escapes and yields no "
  "third-party evidence.", 5.9)
H3("4.4 Robustness")
P("Every number above is deterministic and pinned by tests; there is no sampling and so no interval to report. "
  "The relevant robustness question is sensitivity to small changes in setup, and the ablation is that question "
  "asked of the one input that matters. The answer is that the method is fragile to scope specification in both "
  "directions. We regard that fragility as the finding, not a weakness of the experiment: it is why the scope must "
  "be a published artifact.")

H2("5. Discussion and Limitations")
P("Theory of change. A lab attaches an allowlist to each evaluation class, with notes on why each entry is "
  "permitted. Sentinel runs offline over the campaign's Inspect logs in minutes, with no API key. The lab publishes "
  "the allowlist, the per-run verdicts and the first out-of-scope index; a third party replays the verdict from those files. Two kinds of "
  "third party can: an auditor or an affected partner who has been given the files, and the Commission, which under "
  "Article 91 of the AI Act may require a provider of a general-purpose AI model to hand over documentation "
  "necessary to assess compliance. The first needs cooperation; only the second can compel. "
  "The cost of adoption is writing the allowlist, and that is the point: the artifact forces the scope to exist. "
  "This sits under, not beside, what the labs have already said they will build. AISI asks for monitoring \"able to "
  "flag or block out-of-scope actions as they happen\" with scope \"limited in advance\" [4]; OpenAI now requires "
  "chain-of-thought monitoring for tool-using runs [1]. Both need a machine-readable statement of what out-of-scope "
  "means. Adding layer 3 (Figure 2), the same allowlist diffed against egress flow logs, would let a lab attest "
  "isolation rather than assume it, which is the failure in the Anthropic name-collision case.")
H3("Limitations")
BUL([
 "The positive fixtures are reconstructions of four to seven events written from public descriptions; Hugging Face "
 "logged about 17,600 attacker actions [2]. No lab has released raw evaluation transcripts. Nothing here measures "
 "detection inside OpenAI, Anthropic or AISI, and \"events earlier\" is a statement about our reconstruction.",
 "The fixtures and the rule have the same author. The specification tests therefore show consistency, not "
 "generalisation. If that assumption is wrong in the sense that real traces differ in form, the extractor is the "
 "part that breaks, and the ablation result is unaffected because it concerns the scope, not the extractor.",
 "Sentinel reads declared arguments. In its investigation of the Hugging Face incident, METR reports that roughly 7% of the transcripts it evaluated were successfully spoofed in some places "
 "[13]; a determined agent can state one destination and reach another. Layer 3 is the answer; it is not built.",
 "The extractor is regular expressions. Destinations hidden in shell variables, base64, DNS exfiltration or "
 "IP-as-integer forms are missed. We have not measured a miss rate. Publishing the extractor publishes its gaps "
 "(Appendix A).",
 "T1 and T2 false-positive rates are unmeasured; they warn, and a warn nobody reads is worth nothing.",
 "The wildcard scope is one misspecification of many. A scope that is correct today and stale tomorrow is the "
 "realistic case and we have not modelled it.",
])
H3("Future work")
P("A month would add three things. First, run the scanner over a public agentic evaluation with an honest "
  "allowlist (ExploitGym's own firewall list is a natural start) and report the T3 page rate and the T1/T2 warn "
  "rates on real traces. Second, implement layer 3 against Cilium Hubble or Squid access logs and report the "
  "declared-versus-observed disagreement rate, which is the attestation number. Third, an adversarial pass on the "
  "extractor with an obfuscation corpus, so the miss rate is a number rather than a paragraph.")

H2("6. Conclusion")
P("The public containment failures of 2026 were not failures of monitoring technology. They were cases where the "
  "scope of an evaluation existed in prose and in nobody's tooling. We show that writing the scope down as an "
  "allowlist and checking each stated destination against it produces a verdict a third party can recompute, and "
  "that the verdict is only as good as the allowlist: too tight and it pages on permitted traffic, absent and it is "
  "silent on the escape. The same trace shows the verdict arrives after the escape when the escape goes through a "
  "permitted egress. Sentinel is small on purpose. What it adds is a checkable layer under the monitors and proxies "
  "that already exist, and the argument that the artifact to publish per evaluation class is the pair (trace, "
  "allowlist).")

H2("Code and Data")
P("Code repository: " + REPO + " (Apache-2.0, matching ExploitGym). Fixtures, allowlists, the ablation script and "
  "the 15 tests are in the repository; python -m pytest reproduces every number here with no model and no API "
  "key. No lab transcripts are included because none are public. No datasets were used.")
H2("Author Contributions")
P("C.N. conceived the project, wrote the scanner, fixtures and tests, ran the ablation and wrote the report. "
  "Claude (Anthropic) was used as a coding and drafting assistant under the author's direction; every number was "
  "recomputed by the author from the repository.")

H2("References")
REFS = [
 ("[1] OpenAI, 2026. Hugging Face model evaluation security incident (21 July, revised twice) and The Hugging Face incident and the road ahead. openai.com/index/hugging-face-model-evaluation-security-incident; openai.com/index/hugging-face-incident-and-the-road-ahead",
  [("openai.com/index/hugging-face-model-evaluation-security-incident", "https://openai.com/index/hugging-face-model-evaluation-security-incident/"),
   ("openai.com/index/hugging-face-incident-and-the-road-ahead", "https://openai.com/index/hugging-face-incident-and-the-road-ahead")]),
 ("[2] Hugging Face, 2026. Agent intrusion: technical timeline. huggingface.co/blog/agent-intrusion-technical-timeline",
  [("huggingface.co/blog/agent-intrusion-technical-timeline", "https://huggingface.co/blog/agent-intrusion-technical-timeline")]),
 ("[3] Anthropic, 2026. Investigating incidents in our cybersecurity evaluations. anthropic.com/news/investigating-incidents-cybersecurity-evals",
  [("anthropic.com/news/investigating-incidents-cybersecurity-evals", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals")]),
 ("[4] UK AI Security Institute, 4 August 2026. Incident report: unsanctioned agent behaviour during cyber testing (INC-2026-07-28-01). aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing",
  [("aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing", "https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing")]),
 ("[5] Von Arx, S., Slade Byrd, C. and the Nightingale Collective, 4 September 2026. Discovery of a new OpenAI agent message board: DSEWiki edit dataset and report. collusion.wiki. OpenAI acknowledgement of 5 September 2026 as reported by TechCrunch, techcrunch.com/2026/09/05/openai-confirms-wiki-incident-says-its-working-on-a-framework-for-more-disclosure/",
  [("collusion.wiki", "https://collusion.wiki/"),
   ("techcrunch.com/2026/09/05/openai-confirms-wiki-incident-says-its-working-on-a-framework-for-more-disclosure/", "https://techcrunch.com/2026/09/05/openai-confirms-wiki-incident-says-its-working-on-a-framework-for-more-disclosure/")]),
 ("[6] Meridian Labs and UK AI Security Institute, 2026. Inspect Scout: in-depth analysis of AI agent transcripts. github.com/meridianlabs-ai/inspect_scout",
  [("github.com/meridianlabs-ai/inspect_scout", "https://github.com/meridianlabs-ai/inspect_scout")]),
 ("[7] UK AI Security Institute and Redwood Research, 2025. ControlArena. github.com/UKGovernmentBEIS/control-arena",
  [("github.com/UKGovernmentBEIS/control-arena", "https://github.com/UKGovernmentBEIS/control-arena")]),
 ("[8] Kutasov, J. et al., 2025. SHADE-Arena: evaluating sabotage and monitoring in LLM agents. arXiv:2506.15740",
  [("arXiv:2506.15740", "https://arxiv.org/abs/2506.15740")]),
 ("[9] Apollo Research, 2026. Watcher: security for coding agents (Watcher Live and Watcher Analyze). watcher.apolloresearch.ai",
  [("watcher.apolloresearch.ai", "https://watcher.apolloresearch.ai/")]),
 ("[10] ExploitGym, 2026. ExploitGym: can AI agents turn security vulnerabilities into real attacks? arXiv:2605.11086; repository and docs/firewall.md on GitHub, Apache-2.0.",
  [("arXiv:2605.11086", "https://arxiv.org/abs/2605.11086")]),
 ("[11] UK AI Security Institute, July 2026. Cheating behaviour in frontier model evaluations. aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations",
  [("aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations", "https://www.aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations")]),
 ("[12] Nagarkar, C., 2026. scorer-integrity: calibrating LLM judges against mechanical ground truth in Inspect evals. github.com/crishN144/scorer-integrity",
  [("github.com/crishN144/scorer-integrity", "https://github.com/crishN144/scorer-integrity")]),
 ("[13] METR and Redwood Research, 26 August 2026. Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident. metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation",
  [("metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation", "https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/")]),
 ("[14] Baker, B. et al., 2025. Monitoring reasoning models for misbehavior and the risks of promoting obfuscation. arXiv:2503.11926",
  [("arXiv:2503.11926", "https://arxiv.org/abs/2503.11926")]),
]
for _i, (_t, _l) in enumerate(REFS, start=1):
    B.append(("ref", (_i, _t, _l)))

H2("Appendix A. Limitations and Dual-Use Considerations")
P("Limitations are listed in Section 5 and are not repeated. Dual use is the concern specific to publishing a "
  "detector. Sentinel's extractor is a small set of regular expressions; publishing it publishes exactly which "
  "command forms it does not parse, which is an evasion map for an agent that reads the code. We publish it anyway "
  "for three reasons. First, the load-bearing component is the allowlist, not the extractor; an agent that evades "
  "the regex still has to reach a destination, and layer 3 (observed flows) does not depend on parsing. Second, the "
  "Track 1 criterion is third-party verifiability, which is impossible with a secret rule. Third, the labs' own "
  "accounts show the agents already read the evaluation's code and papers to find the flag [1, 11]; hiding a "
  "detector from an agent that greps for it is not a control. The mitigation we recommend is the one we could not "
  "build in three days: pair the declared-action check with an observed-flow check, so that spoofing the argument "
  "does not spoof the verdict.")
P("The fixtures contain no working exploit. Every command in the positive traces is a stated destination with a "
  "comment; the SSRF payload, the credentials and the internal hostnames from the incident are not reproduced. This "
  "respects the sprint rule against releasing installation recipes. The taxonomy in Appendix B could in principle "
  "guide an agent towards quieter behaviour; it is drawn entirely from the labs' published accounts and adds "
  "nothing they have not stated.")
H2("Appendix B. Taxonomy coverage")
TABLE([
 ["Behaviour (from the public accounts)", "Seen in", "Sentinel"],
 ["1 Grader / evaluation probing", "OpenAI [1], AISI [11]", "T1 WARN"],
 ["2 Sandbox / boundary testing", "OpenAI, Hugging Face [2]", "T2 WARN"],
 ["3 Unauthorised egress vs declared scope", "all four", "T3 PAGE"],
 ["4 Inter-agent message boards", "OpenAI (Artifactory WebDAV), AISI (GitHub), DSEWiki [5]", "not covered"],
 ["5 Credential harvesting and reuse", "OpenAI, Anthropic", "not covered (env telemetry)"],
 ["6 Out-of-scope target enumeration", "Anthropic (~9,000 targets)", "T3 if a host is stated"],
 ["7 Persistence past a safe exit", "OpenAI (198/898 unsolved tasks)", "not covered (policy)"],
 ["8 Transcript / monitor tampering", "AISI, METR [13]", "not covered; defeats T3"],
 ["9 Goal adoption from peers", "OpenAI", "not covered"],
], "Table 2. The nine behaviours distilled from the four public accounts, and which ones an allowlist-relative "
   "scanner can see. Only item 3 is a mechanical page; items 1 and 2 warn; the rest need environment telemetry or "
   "multi-agent corpora and are out of scope for this artifact.", [2.6, 2.4, 1.5])

# ---------- rendering ----------
LINK = "#2e5c8a"          # links: coloured, not underlined (paper convention)
CITE = re.compile(r"\[(\d+(?:,\s*\d+)*)\]")
URL_IN_TEXT = re.compile(r"https?://[^\s,)]+")
_BK = [0]


def _style(run, size=None, italic=None, bold=None, link=False):
    if size: run.font.size = size
    if italic is not None: run.italic = italic
    if bold is not None: run.bold = bold
    run.font.name = "Old Standard TT"
    if link: run.font.color.rgb = RGBColor(0x2E, 0x5C, 0x8A)
    return run


def _linked_run(paragraph, text, *, anchor=None, url=None, size=None):
    """One run wrapped in <w:hyperlink>: internal (anchor) or external (url)."""
    h = OxmlElement("w:hyperlink")
    if anchor is not None:
        h.set(qn("w:anchor"), anchor)
    else:
        h.set(qn("r:id"), paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True))
    run = paragraph.add_run(text)
    _style(run, size=size, link=True)
    run._r.getparent().remove(run._r)
    h.append(run._r)
    paragraph._p.append(h)


def bookmark(paragraph, name):
    _BK[0] += 1
    st = OxmlElement("w:bookmarkStart"); st.set(qn("w:id"), str(_BK[0])); st.set(qn("w:name"), name)
    en = OxmlElement("w:bookmarkEnd"); en.set(qn("w:id"), str(_BK[0]))
    paragraph._p.insert(0, st); paragraph._p.append(en)


def write_text(paragraph, text, *, size=None, italic=None, bold=None):
    """Emit text, linking every [n] citation to its reference and every bare URL out."""
    pos = 0
    for m in URL_IN_TEXT.finditer(text):
        if m.start() > pos:
            write_text(paragraph, text[pos:m.start()], size=size, italic=italic, bold=bold)
        _linked_run(paragraph, m.group(0), url=m.group(0), size=size)
        pos = m.end()
    if pos:
        if pos < len(text):
            write_text(paragraph, text[pos:], size=size, italic=italic, bold=bold)
        return
    for m in CITE.finditer(text):
        if m.start() > pos:
            _style(paragraph.add_run(text[pos:m.start()]), size, italic, bold)
        _style(paragraph.add_run("["), size, italic, bold)
        nums = [x.strip() for x in m.group(1).split(",")]
        for i, num in enumerate(nums):
            if i:
                _style(paragraph.add_run(", "), size, italic, bold)
            _linked_run(paragraph, num, anchor="ref" + num, size=size)
        _style(paragraph.add_run("]"), size, italic, bold)
        pos = m.end()
    if pos < len(text):
        _style(paragraph.add_run(text[pos:]), size, italic, bold)


def write_reference(paragraph, text, links, size):
    """Emit a reference line, hyperlinking each declared URL span."""
    spans = sorted(((text.index(d), d, u) for d, u in links if d in text))
    pos = 0
    for i, d, u in spans:
        if i > pos:
            _style(paragraph.add_run(text[pos:i]), size)
        _linked_run(paragraph, d, url=u, size=size)
        pos = i + len(d)
    if pos < len(text):
        _style(paragraph.add_run(text[pos:]), size)


def set_cell_text(cell, text, bold=None, size=None):
    p = cell.paragraphs[0]
    for r in p.runs[1:]: r._r.getparent().remove(r._r)
    if not p.runs: p.add_run("")
    p.runs[0].text = text
    if bold is not None: p.runs[0].bold = bold
    if size: p.runs[0].font.size = size

def fixed_layout(table, widths):
    """Word/LO re-fit tables unless layout is fixed AND every cell repeats its width."""
    tbl = table._tbl; tblPr = tbl.tblPr
    tbl.autofit = False
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for gc, wdt in zip(grid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(int(wdt * 1440)))


def add_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "999999")
        b.append(e)
    tblPr.append(b)

def build():
    d = Document(TPL)
    body = d.element.body
    # 1. title block
    t0 = d.tables[0]
    for p in t0.rows[0].cells[0].paragraphs:
        if p.style.name == "Title":
            for r in p.runs[1:]: r._r.getparent().remove(r._r)
            p.runs[0].text = TITLE
    # authors: nested 1x3 table in row 1; rewrite by XML
    for tc in t0._tbl.iter(qn("w:tc")):
        if tc.find(".//" + qn("w:tbl")) is not None: continue  # outer cell; only touch leaf cells
        ts = [t for t in tc.iter(qn("w:t"))]
        txt = "".join(t.text or "" for t in ts)
        if txt.startswith("Author name 2"):
            ts[0].text = AUTHOR; ts[1].text = AFFIL
        elif txt.startswith("Author name"):
            for t in ts: t.text = ""
    for tbl in t0._tbl.iter(qn("w:tbl")):
        if tbl is t0._tbl: continue
        if any((t.text or "") in (AUTHOR,) for t in tbl.iter(qn("w:t"))):
            for gc in tbl.iter(qn("w:gridCol")): gc.set(qn("w:w"), "3120")
            for tcw in tbl.iter(qn("w:tcW")): tcw.set(qn("w:w"), "3120"); tcw.set(qn("w:type"), "dxa")
            for tw in tbl.iter(qn("w:tblW")): tw.set(qn("w:w"), "9360"); tw.set(qn("w:type"), "dxa")
    # abstract guidance paragraph
    for tc in t0._tbl.iter(qn("w:tc")):
        for p in tc.iter(qn("w:p")):
            ts = list(p.iter(qn("w:t")))
            if ts and "Summarize your project" in (ts[0].text or ""):
                ts[0].text = ABSTRACT
                for t in ts[1:]: t.text = ""
                for i in p.iter(qn("w:i")): i.set(qn("w:val"), "0")
    # 2. remove info box (table 1) and every body paragraph after it
    t1 = d.tables[1]._tbl
    after = False
    for el in list(body):
        if el is t1: after = True; body.remove(el); continue
        if after and el.tag != qn("w:sectPr"): body.remove(el)
    # 3. append content
    for kind, payload in B:
        if kind == "h2":
            _h = d.add_paragraph(payload, style="Heading 2")
            _h.paragraph_format.keep_with_next = True
            if payload.startswith("Appendix A"):
                _h.paragraph_format.page_break_before = True
        elif kind == "h3": d.add_paragraph(payload, style="Heading 3").paragraph_format.keep_with_next = True
        elif kind == "p":
            p = d.add_paragraph(style="normal"); write_text(p, payload)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(5)
        elif kind == "ref":
            n, text, links = payload
            p = d.add_paragraph(style="normal"); write_reference(p, text, links, Pt(10))
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(4); p.paragraph_format.left_indent = Inches(0.28)
            p.paragraph_format.first_line_indent = Inches(-0.28)
            bookmark(p, "ref%d" % n)
        elif kind == "bul":
            for it in payload:
                p = d.add_paragraph(style="normal"); p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.first_line_indent = Inches(-0.2); p.paragraph_format.space_after = Pt(4)
                write_text(p, "•  " + it); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif kind == "fig":
            path, cap, w = payload
            p = d.add_paragraph(style="normal"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.add_run().add_picture(str(path), width=Inches(w)); p.paragraph_format.keep_with_next = True
            c = d.add_paragraph(style="normal"); r = c.add_run(cap); r.font.size = Pt(9.5); r.italic = True
            c.paragraph_format.space_before = Pt(6); c.paragraph_format.space_after = Pt(10)
        elif kind == "tbl":
            rows, cap, widths = payload
            t = d.add_table(rows=len(rows), cols=len(rows[0])); add_borders(t)
            if widths: fixed_layout(t, widths)
            for row in t.rows:
                trPr = row._tr.get_or_add_trPr(); cs = OxmlElement('w:cantSplit'); trPr.append(cs)
                for cell in row.cells:
                    for pp in cell.paragraphs: pp.paragraph_format.keep_with_next = True
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    cell = t.cell(i, j); cell.text = ""
                    write_text(cell.paragraphs[0], val, size=Pt(8.1), bold=(i == 0))
                    if widths: cell.width = Inches(widths[j])
            c = d.add_paragraph(style="normal"); r = c.add_run(cap); r.font.size = Pt(9.5); r.italic = True
            c.paragraph_format.space_before = Pt(7); c.paragraph_format.space_after = Pt(10)
    # body font size: template body runs are 12pt via style defaults; set explicit 11pt for the 4-page budget
    for t in d.tables[1:]:
        for row in t.rows:
            for cell in row.cells:
                for pp in cell.paragraphs:
                    for r in pp.runs: r.font.name = "Old Standard TT"
    for p in d.paragraphs:
        if p.style.name == "normal":
            for r in p.runs:
                r.font.name = "Old Standard TT"
                if r.font.size is None: r.font.size = Pt(10.5)
            p.paragraph_format.line_spacing = 1.14
    OUT.parent.mkdir(exist_ok=True)
    d.save(OUT); print("wrote", OUT)

if __name__ == "__main__":
    build()
