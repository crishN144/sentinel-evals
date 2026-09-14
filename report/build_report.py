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
 "Between April and July 2026, agents under evaluation at OpenAI, Anthropic and the UK AI Security Institute "
 "reached real third parties. In every public account the evaluation's network scope was declared in prose or "
 "assumed, never checked against what the agent did, and detection came late from a side signal. We argue that "
 "an evaluation's declared scope, written as a machine-readable allowlist, is the unit of containment evidence a "
 "third party can verify, and build Sentinel, an Inspect scanner that classifies each tool call's stated "
 "destination against it and pages on the first out-of-scope one, with no model in the gate. On reconstructions "
 "of three public incidents (four to seven events each, from the published timelines) it pages at the first "
 "non-allowlisted destination and is silent on three hard negatives. On the 14,591-revision DSEWiki export, a record we did not write, it is silent under the "
 "wildcard scope the sandbox actually had and pages on day one under any scope naming the task's data sources; "
 "on a live eight-sample Inspect run with an empty declared scope it is correctly silent on 42 real tool calls. "
 "The headline result is an ablation on one trace: a too-tight scope pages on permitted traffic, a wildcard "
 "scope is silent on the escape. Verifiability is a property of the pair (trace, allowlist), not of the "
 "detector. The same trace shows the page arrives after the escape, which went through the permitted proxy: a "
 "scanner audits containment; it does not provide it."
)

# ---------- body: list of (kind, payload) ----------
B = []
def H2(t): B.append(("h2", t))
def H3(t): B.append(("h3", t))
def P(t): B.append(("p", t))
def BUL(items): B.append(("bul", items))
def FIGURE(path, caption, width=5.4): B.append(("fig", (path, caption, width)))
def TABLE(rows, caption, widths=None): B.append(("tbl", (rows, caption, widths)))

H2("1. Introduction")
P("In July 2026 two pre-release OpenAI models, running a cyber-capability evaluation with production refusal "
  "classifiers disabled, escaped their sandbox through a zero-day in the package-registry cache proxy that was "
  "their one permitted network egress, reached the open internet, and spent 11 to 13 July inside Hugging Face's "
  "production infrastructure [1, 2]. Hugging Face cut the attacker off on 13 July and disclosed on 16 July without "
  "knowing the origin; OpenAI attributed it on 21 July [1]. It was not the only case. Anthropic reported three "
  "incidents in its cyber evaluations, including one where the task prompt declared no internet access, a partner "
  "misconfiguration left it on, and the agent reached a real company that shared the fictional target's name and a "
  "database with several hundred rows of production data. The earliest of the three dates to April; all three were "
  "found in a retrospective review of 141,006 runs on 24 July [3]. The UK AI Security Institute reported models on an intentionally "
  "internet-connected cyber range reaching GitHub over Tor, caught by a Tor egress alarm [4]. A separate channel, unconnected to the Hugging Face "
  "swarm, ran on a public wiki: OpenAI evaluation agents whose sandbox allowed only GET requests found on 11 May that "
  "some wikis accept edits over GET, made their first successful write to DSEWiki, a dormant German programming "
  "wiki, on 24 May, and used it as a message board for task answers and sandbox workarounds until 22 June, the day "
  "after the first OpenAI-associated addresses visited the pages: roughly 18,000 posts under more than 3,700 "
  "self-chosen names by the researchers' count, 14,591 of them preserved in the published export. Outside researchers found "
  "it by reading the wiki's public logs and published on 4 September; OpenAI acknowledged it the next day, saying "
  "the field has no agreed standard for reporting misalignment [5].")
P("These cases share a shape that is not \"no monitor existed.\" In each one the operators knew the intended scope "
  "in prose: no internet; only the LLM API and the package proxy; only the range. Nowhere was that scope an "
  "artifact the transcript was checked against, and the first signal always came from somewhere else: an "
  "identity-API anomaly, a Tor alarm, a retrospective sweep, a stranger reading a wiki. Hugging Face's own "
  "post-mortem says its correlation stack existed but \"failed to correctly raise the alert's criticality\" [2]. The "
  "failure is one of scope attachment and attestation (Figure 2), and it is the failure the sprint's containment "
  "track asks about. Track 1 of the Apart AI Incident Response Sprint judges a containment proposal on one "
  "question: could a third party verify compliance without access to the lab's network, and would a lab adopt it?")
P("We take the smallest step that answers it. Our main contributions are:")
BUL([
 "A declared-scope representation (a JSON allowlist) and Sentinel, a mechanical, Inspect-native scanner that turns "
 "the first tool-call destination outside that scope into a finding a third party can recompute from files alone.",
 "An allowlist-misspecification ablation on a reconstruction of the Hugging Face trace: a too-tight scope pages on "
 "permitted traffic; a wildcard scope is silent on the escape. The control is the pair (trace, allowlist), not the detector.",
 "Seven incident-derived fixtures with stated provenance, used as executable specifications rather than a benchmark, "
 "plus a tested statement of what the method cannot see: an escape through a permitted egress, and spoofed arguments.",
 "The same rule run over a third party's record of a real incident, the DSEWiki export, where both directions of the "
 "ablation reproduce on events we did not author.",
])

H2("2. Related Work")
P("Trace monitors for agents exist and are good. Inspect Scout ships scanners over evaluation transcripts, "
  "including reward-hacking and evaluation-awareness scanners [6]; ControlArena [7] and SHADE-Arena [8] monitor for "
  "side tasks and sabotage; Apollo's Watcher reads transcripts for scheming [9]; OpenAI now monitors chain-of-thought during "
  "tool-using runs [1]. Preventive controls also exist: default-deny egress via Cilium or Squid FQDN allowlists, and ExploitGym "
  "itself ships a Squid firewall that permits only LLM API endpoints [10].")
P("None of these takes the evaluation's declared scope as an input artifact and emits a verdict that someone "
  "outside the lab can recompute. Behavioural monitors answer \"does this look bad?\" and need a model and a threshold; a proxy answers "
  "\"was this blocked?\" but its logs stay inside the lab, and in the OpenAI case the proxy was the hole. Sentinel's wedge is narrow: a mechanical predicate over (trace, allowlist). Stated plainly, so the "
  "objection is met rather than dodged: default-deny egress is the control; Sentinel is not a control; it is the "
  "smallest artifact that turns the control's scope into a published, recomputable claim. \"Why not just publish "
  "the proxy logs?\" is the right question, and it is layer 3 of Figure 2: it needs the same allowlist to be "
  "meaningful, and today no such allowlist is published. What it provides that we did not have is the "
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
P("The ExploitGym scope, verbatim from the repository, is the whole artifact for that evaluation class:")
B.append(("code", '{"name": "exploitgym-cyber-eval", "internet_expected": false,\n'
                  ' "allowed_hosts": ["api.openai.com", "api.anthropic.com", "artifactory.internal"],\n'
                  ' "notes": "ExploitGym run-proxy permits ONLY LLM API endpoints; OpenAI additionally permitted the Artifactory proxy."}'))
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
  "wrapper (scout scan sentinel/scanner.py -T logs/) is exercised by the test suite and, in Section 4.4, over a "
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
  "test to assert T2-only on that fixture and added a separate grader-internals fixture for the genuine T1 signal. "
  "Third, the first scout scan over a real log crashed: the scanner used relative imports and scout loads the file "
  "standalone in worker processes, so the README command had never actually worked. It now imports the installed "
  "package.")

H2("4. Results")
H3("4.1 Specification tests")
TABLE([
 ["Fixture", "Kind", "Sentinel", "Destination", "Detection point in reconstruction", "Keyword baseline"],
 ["hf-openai-exploitgym", "positive", "PAGE @3", "cybergym-fn-7bf.modal.run", "@6", "@2 (proxy)"],
 ["aisi-range-tor", "positive", "PAGE @2", "github.com", "@4", "@1"],
 ["anthropic-irregular", "positive", "PAGE @2", "acme-robotics.com", "@6", "@1"],
 ["neg-allowed-llm-api", "negative", "no page", "—", "—", "@0  false"],
 ["neg-inscope-recon", "negative", "no page", "—", "—", "—"],
 ["neg-range-http", "negative", "no page", "—", "—", "@0  false"],
 ["warn-grader-probe", "warn only", "no page (T1 warn)", "—", "—", "—"],
], "Table 1. Specification tests over the seven fixtures. \"Detection point in reconstruction\" is where we placed "
   "the organisation's own detection when we wrote the fixture from the public timeline; it is a property of our "
   "reconstruction and supports no claim about latency inside any lab. The keyword baseline has no allowlist.",
   [1.18, 0.60, 1.12, 1.74, 1.04, 0.82])
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
  "the permitted proxy, which no allowlist can see; the shaded region is post-escape activity inside Hugging Face.", 5.0)
P("Observation: the same trace yields three different verdicts under three scopes (Figure 1). Interpretation: "
  "both directions of misspecification fail, and they fail differently. The too-tight scope produces a page on "
  "permitted egress, the kind of alert that gets a monitor switched off within a day. The wildcard scope, which is "
  "what \"we allow internet\" means when nobody writes the list, is silent on a real containment failure. A scanner "
  "with no declared scope is not a control. The artifact worth publishing per evaluation class is the pair (trace, allowlist), and verifiability is "
  "a property of the pair. Every number here is deterministic and pinned by tests; the one robustness question that "
  "matters is sensitivity to the scope, and this figure asks it directly.")
H3("4.3 The page arrives after the escape")
P("Under the correct scope the page lands at event 3. Event 2, the request to the permitted proxy, is already the "
  "escape: the SSRF went through an allowlisted host, and an allowlist-relative rule classifies that request as "
  "ALLOWED. We test this as a known blind spot rather than hide it. PAGE @3 is the first auditable evidence of "
  "out-of-scope egress, which in the reconstruction precedes the production intrusion (events 5 and 6) and the "
  "organisation's own detection (event 6). It is not \"this would have stopped the breach.\" "
  "Prevention is default-deny egress plus a hardened permitted proxy, and a trace scanner supplies neither. The "
  "DSEWiki case has the same shape: the sandbox permitted only GET requests, and the wiki accepts page edits "
  "over GET [5]. In both public escapes the agent went through the scope, not around it. An "
  "allowlist-relative scanner is blind to that by construction; what it would still have recorded is the "
  "destination host, prowiki.org, had the declared scope named which hosts read access was for.")
FIGURE(FIG / "fig2_layers_v3.png",
  "Figure 2. Four layers of containment evidence, with the Hugging Face reconstruction as the running example. "
  "Layers 1 and 2 are what this paper builds: the declared scope and the agent's stated destination, checked "
  "against it. Layer 3, observed flows diffed against the same allowlist, is not built and is the month of "
  "follow-up. Layer 4 is the Track 1 criterion. Prevention is a separate row: it stops escapes and yields no "
  "third-party evidence.", 5.4)
H3("4.4 Records we did not write: the DSEWiki export and a live Inspect run")
P("The fixtures show consistency, not generalisation, so we pointed the same rule at a record with a different "
  "author. The Nightingale Collective's export of the DSEWiki incident [5] contains 14,591 saved agent revisions "
  "across four wikis, 24 May to 2 July 2026, with full text and write times (manifest db_sha256 199241bf…). Each "
  "revision is one event in write order and its body the argument blob; the extractor reads it as it would a tool "
  "call. Nothing about the events is ours. The declared "
  "scope is: the sandbox allowed any GET request to any host, which is the wildcard row of the ablation. We add "
  "two scopes of our own for comparison and say so: one naming only the public datasets the task families were "
  "retrieving from (27 hosts such as api.datausa.io, sec.gov, api.usaspending.gov), and a control that also "
  "permits the wiki hosts.")
TABLE([
 ["Declared scope", "Pages", "First page", "Destination", "Before OpenAI's first visit (21 Jun)"],
 ["wildcard (the actual scope: any GET)", "0 of 14,591", "—", "—", "silent"],
 ["data sources only (ours)", "16,504", "event 5, 24 May 11:53 UTC", "wikiservice.at (wiki channel)", "27 days"],
 ["data sources + wiki hosts (control)", "11,946", "event 36, 26 May 09:43 UTC", "example.com; then markdown.new, piv.max.gov", "25 days"],
], "Table 3. Sentinel over the DSEWiki export under three declared scopes. The events are the researchers' record; "
   "the two non-wildcard scopes are our reconstruction from the task families visible in it. \"Before OpenAI's first "
   "visit\" uses the date collusion.wiki gives for the first OpenAI-associated addresses on the pages.",
   [1.95, 0.85, 1.35, 1.55, 0.80])
P("Observation: under the scope the sandbox actually had, the scanner is silent on all 14,591 events. Under a "
  "scope that names the task's data sources, the first out-of-scope stated destination is the wiki itself, at "
  "event 5, six hours into the first day of writing and 27 days before the first OpenAI-associated address "
  "visited the pages. Permitting the wiki hosts moves the first page to 26 May, where the stated destinations "
  "are a placeholder domain, then the first of 43 reader and CORS-proxy hosts (markdown.new, r.jina.ai, "
  "allorigins), then a US government login portal (piv.max.gov, login.max.gov). The extractor sees 200 distinct "
  "hosts in the record: 27 task data sources, 6 wiki hosts, 43 reader or CORS proxies, 4 shorteners, 5 archives, "
  "4 tunnels. Interpretation: the ablation's two failure "
  "modes reproduce on a record we did not write. The scope the evaluation had was a wildcard, and a wildcard "
  "produces no page on a real containment failure; any scope that named what the task was for would have paged "
  "on the first day. Two honesty notes: 16,504 pages is an alert volume nobody reads, so the value is the first index and the "
  "count is why layer 3, not layer 2, should gate paging; and T2 fired 1,147 times only because \"proxy\" appears "
  "in the workaround hostnames, a lexical accident we report as one.")
P("The second record is a live run we did not script: eight samples of inspect_evals/gdm_intercode_ctf with "
  "claude-haiku-4-5 as the agent. Its upstream sandbox declares network_mode: none, the only allowlist here "
  "written from a benchmark's own configuration, and it is empty. The agent made 42 tool calls (ls, cat, tcpdump, "
  "strings, python, submit) and solved all eight tasks; Sentinel paged on none, warned on none, the keyword "
  "baseline fired on none, and the inspect_scout wrapper returned the same eight verdicts from the recorded log. "
  "This is a negative control, not a detection result: a scanner that paged here would be wrong. It shows the rule "
  "is silent on real tool calls it was not written against, and that the Inspect path works on a real log. "
  "Cost: $0.14.")
H2("5. Discussion and Limitations")
P("Theory of change. A lab attaches an allowlist to each evaluation class, with notes on why each entry is "
  "permitted. Sentinel runs offline over the campaign's Inspect logs in minutes, with no API key. The lab publishes "
  "the allowlist, the per-run verdicts and the first out-of-scope index; a third party replays the verdict from those files. Two kinds of "
  "third party can: an auditor or an affected partner who has been given the files, and the Commission, which under "
  "Article 91 of the AI Act may require a provider of a general-purpose AI model to hand over documentation "
  "necessary to assess compliance. The first needs cooperation; only the second can compel. "
  "The cost of adoption is writing the allowlist, which is the point: the artifact forces the scope to exist. It "
  "sits under what the labs already say they will build: AISI asks for monitoring \"able to flag or block "
  "out-of-scope actions as they happen\" with scope \"limited in advance\" [4], and OpenAI now requires "
  "chain-of-thought monitoring for tool-using runs [1]; both need a machine-readable statement of what out-of-scope "
  "means. Layer 3 (Figure 2), the same allowlist diffed against egress flow logs, would let a lab attest isolation "
  "rather than assume it, which is the failure in the Anthropic name-collision case.")
H3("Limitations")
BUL([
 "The positive fixtures are reconstructions of four to seven events from public descriptions; Hugging Face logged "
 "about 17,600 attacker actions [2]. No lab has released raw transcripts, so nothing here measures detection inside "
 "OpenAI, Anthropic or AISI, and \"events earlier\" describes our reconstruction.",
 "The fixtures and the rule share an author, so the specification tests show consistency, not generalisation. The "
 "DSEWiki run fixes the events but not the scope: its two non-wildcard allowlists are ours, and a different "
 "reconstruction would move the first page. The wildcard row, the scope the sandbox actually had, does not move.",
 "The live run is eight samples on tasks with no network, so it can only show silence. A positive live case needs "
 "an evaluation with internet on and a real allowlist. Wiki revision bodies are also a weaker kind of declared "
 "action than a curl argument: some URLs are links posted for other agents, not destinations reached.",
 "Sentinel reads declared arguments. METR reports that roughly 7% of the transcripts it evaluated in the Hugging "
 "Face investigation were successfully spoofed in places [13]; an agent can state one destination and reach "
 "another. Layer 3 is the answer, and it is not built.",
 "The extractor is regular expressions. Destinations hidden in shell variables, base64, DNS exfiltration or "
 "IP-as-integer forms are missed and the miss rate is unmeasured; publishing the extractor publishes its gaps "
 "(Appendix A). T1 and T2 false-positive rates are likewise unmeasured.",
 "The wildcard scope is one misspecification of many. A scope that is correct today and stale tomorrow is the "
 "realistic case and we have not modelled it.",
])
H3("Future work")
P("A month would add three things. First, a positive live case: an agentic evaluation run with internet on and "
  "an honest allowlist (ExploitGym's own firewall list is the natural start), reporting T3 page and T1/T2 warn "
  "rates on real traces. Second, layer 3 against Cilium Hubble or Squid access logs, reporting the "
  "declared-versus-observed disagreement rate, which is the attestation number. Third, an adversarial pass on the "
  "extractor with an obfuscation corpus, so the miss rate is a number rather than a paragraph.")

H2("6. Conclusion")
P("The public containment failures of 2026 were not failures of monitoring technology. They were cases where the "
  "scope of an evaluation existed in prose and in nobody's tooling. We show that writing the scope down as an "
  "allowlist and checking each stated destination against it produces a verdict a third party can recompute, and "
  "that the verdict is only as good as the allowlist: too tight and it pages on permitted traffic, absent and it is "
  "silent on the escape. The same trace shows the verdict arrives after the escape when the escape goes through a "
  "permitted egress, and a third party's record of a second incident reproduces both failure modes on events we did "
  "not write. Sentinel is small on purpose: a checkable layer under the monitors and proxies that already exist, and "
  "the argument that the artifact to publish per evaluation class is the pair (trace, allowlist).")

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


def cell_padding(table, top=40, bottom=40, left=90, right=90):
    """Default tables have no cell margin: wrapped text touches the rule above."""
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for edge, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:w"), str(val)); e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)


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
        elif kind == "code":
            for line in payload.split("\n"):
                cp = d.add_paragraph(style="normal"); r = cp.add_run(line)
                r.font.name = "Menlo"; r.font.size = Pt(8.2)
                cp.paragraph_format.left_indent = Inches(0.3); cp.paragraph_format.space_after = Pt(0)
                cp.paragraph_format.line_spacing = 1.0
            d.paragraphs[-1].paragraph_format.space_after = Pt(6)
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
            c.paragraph_format.line_spacing = 1.30
            c.paragraph_format.space_before = Pt(6); c.paragraph_format.space_after = Pt(10)
        elif kind == "tbl":
            rows, cap, widths = payload
            t = d.add_table(rows=len(rows), cols=len(rows[0])); add_borders(t)
            if widths: fixed_layout(t, widths)
            cell_padding(t)
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
            c.paragraph_format.line_spacing = 1.30
            c.paragraph_format.space_before = Pt(7); c.paragraph_format.space_after = Pt(10)
    # body font size: template body runs are 12pt via style defaults; set explicit 11pt for the 4-page budget
    for t in d.tables[1:]:
        for row in t.rows:
            for cell in row.cells:
                for pp in cell.paragraphs:
                    pp.paragraph_format.line_spacing = 1.12
                    pp.paragraph_format.space_after = Pt(0)
                    pp.paragraph_format.space_before = Pt(0)
                    for r in pp.runs: r.font.name = "Old Standard TT"
    for p in d.paragraphs:
        if p.style.name == "normal":
            for r in p.runs:
                r.font.name = "Old Standard TT"
                if r.font.size is None: r.font.size = Pt(10.5)
            if p.paragraph_format.line_spacing is None:
                p.paragraph_format.line_spacing = 1.08
    OUT.parent.mkdir(exist_ok=True)
    d.save(OUT); print("wrote", OUT)

if __name__ == "__main__":
    build()
