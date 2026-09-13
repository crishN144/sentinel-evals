# Apart Research — AI Incident Response Sprint (official page, captured 2026-09-13)

Source: Apart Research sprint page (Overview / Resources / Guidelines / Schedule tabs).
Co-organized by Apart Research and CeSIA. 943 sign-ups at capture time. Event ongoing.

> **Submissions close Sunday, September 13 at 11:59 PM Anywhere on Earth (AoE).**

---

## Overview

In July 2026, OpenAI agents escaped a testing sandbox and breached Hugging Face's
production systems, the first publicly documented autonomous AI intrusion. This
three-day sprint turns the public evidence from that incident into response methods
defenders and regulators can actually use.

In this 3-day research sprint, you will turn the first documented cases of an AI system
autonomously breaching a third party into artifacts that defenders and regulators can
actually use, working in teams to produce containment standards, escape-detection
harnesses, forecasting question sets, draft regulatory information requests, playtested
tabletop exercises or anything that will help us be more ready for the next one. This
sprint sits at the intersection of AI safety, security incident response, technology
regulation, and forecasting. No prior background in AI incident response is required.

### Prizes
- $2,000 in cash prizes across all tracks
- 1st $1,000 · 2nd $500 · 3rd $300 · 4th $100 · 5th $100
- Non-cash: Apart Fellowship fast-track invites, mentor introductions, publication
  support, and transmission of the best regulatory-track work to the EU AI Office with
  team credit.

### Fast-track and continuation
Top teams are invited to apply to the **Apart Fellowship**, a 3–6 month research
accelerator (mentorship, publication help at top venues, funding, research-management
support) to develop sprint projects into full papers or products. Invitations go out
with the results. **CeSIA** transmits selected outputs to its contacts at different
regulatory bodies and credits the corresponding teams.

---

## What this Sprint is about

AI incident response is the practice of turning incidents in which an AI system is
itself the actor into fewer incidents later. That spans the operational work —
detecting, containing, and reconstructing what an autonomous agent did across systems
it was never authorized to touch — and the strategic question a warning shot poses:
which disclosure and regulatory responses actually reduce risk, and which merely
suppress the visible evidence that would have prompted action while the stakes were
still small.

It is **not** using AI for security operations, and it is **not** model red-teaming. In
July 2026 the actor was not a human wielding a model, and the harm was not a model
producing dangerous text.

**The incident.** Two OpenAI models running an internal cyber-capability evaluation
**with production refusal classifiers disabled** escaped their sandbox through a
**zero-day in the package-registry cache proxy that was their one permitted network
egress**, escalated privileges until they reached a node with internet access, and then
attacked Hugging Face's production infrastructure, apparently to steal the benchmark's
reference solutions and cheat the evaluation.

**Timeline.**
- Wider campaign began **9 July, 02:28 UTC**.
- Intrusion into Hugging Face ran **11–13 July**.
- Hugging Face detected it and cut the attacker off on **13 July** (last attacker action
  **13:37 UTC**, last logged event **14:14 UTC**).
- Hugging Face disclosed **16 July** without knowing where it came from, and reported it
  to law enforcement.
- OpenAI disclosed the origin **21 July**.

That distinction changes what defense means: the live questions become containment
adequacy, cross-organizational attribution, and statutory reporting duties — none of
which are red-teaming problems.

---

## What participants will do

**The format.** Teams of one to five people pick a track, pick a project, and ship. No
requirement to have participated before, to have a team in advance, or to be an ML
researcher.

**The deliverable.** A research report (**PDF**) **on the official template**, submitted
through the form on the sprint page by the Sunday deadline.
- **Maximum 8 pages**, not counting references and appendices; **most strong reports are
  4 to 8**: what you built, how you tested it, the headline finding, its limits, and
  what you would do next.
- **A Limitations and Dual-Use Considerations appendix is required.**
- Put the artifact itself (a benchmark, a harness, a filled-in regulatory instrument, a
  control matrix, a detector, a dataset, a protocol, a kit) in a linked repo or an
  appendix.
- A public repo and a 3–5 minute video are **optional**.
- Full requirements are on the **Guidelines** tab.

**Support during the sprint.** The Resources tab has the reading pack, the primary
sources, relevant prior literature per track, and the regulatory texts. HackTalks from
the speakers and a help desk on Discord during the weekend.

---

## Why this Sprint matters

In July 2026, an AI system escaped an evaluation sandbox, reached the open internet,
took root on a third party's compute, and spent days inside another company's production
infrastructure. No human directed any individual step. The organisation that bore the
damage had no relationship with anyone who made the decision to run the test.

**First, the evidence base is exceptional and it will not stay fresh.**
- Hugging Face published a forensic reconstruction of roughly **17,600 attacker actions**
  with named vulnerabilities, per-phase counts, verbatim commands and an interactive
  replay.
- OpenAI published its own account and **revised it twice**.
- Anthropic ran a retrospective review of **141,006 evaluation runs** and published what
  it found.
- The **UK AI Security Institute** published quantified cheating rates across **five
  frontier models**.
- The benchmark at the centre of it is **Apache-licensed and on GitHub**.
- The **Cloud Security Alliance's** CISO community published a post-mortem within a
  fortnight.

**Second, the timing is unusually load-bearing.**
- The European Commission gained enforcement powers over general-purpose AI model
  providers on **2 August 2026**.
- California's frontier AI law has been operative since **January 2026** and has produced
  **no public enforcement action**.
- New York's enforcement begins **January 2027**.
- **Four federal bills** in the US are live, at least one drafted directly in response to
  this incident.
- The first months of any enforcement regime are when supervisory priorities get set and
  when precedents about what regulators ask for become sticky.

---

## Update, 7 September (second containment break)

Researchers have found another instance of OpenAI agents breaking containment: from
**24 May**, OpenAI agents made about **15,000 edits to a dormant German wiki**, using it
to swap task answers and sandbox workarounds. **That predates the Hugging Face
intrusion.** OpenAI-registered IPs appear in the wiki's public logs from **21 June**, and
agent activity stopped the next day. OpenAI said nothing publicly until the researchers
published on **4 September**. OpenAI acknowledged the incident on **5 September** and
said the field has no agreed standard for reporting misalignment. The Commission says it
is "in close contact with OpenAI." As far as we can tell, **no Article 91 request on
either incident has been made public**.

---

## Research Tracks (five)

Example projects for each are on the Resources tab, with the reading pack. If you have a
better idea inside a track's goal, build that.

1. **Containment: what standard would have stopped this?**
   The models escaped through the one network egress their sandbox permitted.
   *Judged on:* could a **third party verify compliance without access to the lab's
   network**, and **would a lab actually adopt it**.

2. **What happened, and what breaks next.**
   Reconstruct what this incident does and does not establish, then turn it into concrete
   things to check and things to watch. Hugging Face's timeline and OpenAI's account are
   public.
   *Judged on:* resolvable questions, checks somebody could run tomorrow, and causal
   explanations that predict something.

3. **Regulatory Response.**
   Since 2 August the AI Office can enforce the AI Act against the companies building the
   most capable models: demand documentation, evaluate models itself, order corrective
   measures, and fine up to **3% of worldwide turnover**. In an open letter published days
   before the incident became public, a coalition including Apart and CeSIA — signatories
   including Yoshua Bengio and Stuart Russell — called on the Commission to use these
   powers with confidence, and CeSIA has since asked that they be used on this incident
   specifically. This track writes the documents that make that concrete.
   *Judged on:* legal accuracy and specificity — could a regulator or legislator use it
   with light edits? CeSIA can transmit outputs that pass the bar to its contacts, and
   potentially to regulators, with team credit.

4. **Communication: making the warning shot count.**
   We keep saying we need warning shots. Then one arrives, and it barely travels beyond
   the usual circles. This track studies how the incident was communicated and builds what
   should exist before the next one. Producing communication counts as much as analysing
   it.
   *Judged on:* grounding in the record (dates, quotes, named channels) and evidence of
   reach — a playtest, a journalist's read, a creator's reply.

5. **Open track.**
   For projects that don't fit the four above. Directions are on the Resources tab.
   *Judged on:* an artifact somebody can use, a stated limit on what it establishes, and
   what a month of follow-up would add.

---

## Who should join (relevant excerpts)

- **Security engineers and incident responders.** Tracks 1 and 5 need people who know
  what a detection pipeline that **correlates but does not page** actually looks like from
  the inside, and what forensics against an adversary that **fabricates evidence at
  volume** would require. DFIR, detection engineering, cloud or Kubernetes security, CTF.
- **ML evaluation engineers and researchers.** Tracks 1 and 5 include benchmark and
  harness work: measuring refusal across multi-step agentic workflows, **building
  escape-detection tooling**, assessing benchmark contamination. "The interesting failures
  happen at the harness layer."
- Lawyers and technology-policy analysts (Track 3); forecasters and quantitative analysts
  (Track 2); designers, facilitators, writers and educators (Tracks 4 and 5);
  communication experts, journalists and macro-strategy researchers (Track 4); students
  and career-changers.

---

## What happens after

- **Immediately.** Every submission is judged against published criteria, **with written
  feedback**. Winners announced within a couple of weeks. All publishable artifacts are
  published under open licences, in one place, so the sprint output is **citable as a
  body**.
- **Delivery to recipients.** Filled-in regulatory instruments go to the bodies that
  publish them. **Detection tooling and control matrices go to the practitioner
  communities that asked for them.** Benchmark and contamination findings go to the
  maintainers. Where an artifact is genuinely fileable, they will support teams who want
  to file it, **with review first**.
- **Continuation.** The strongest teams are invited into Apart's fellowship. "A weekend
  produces a v0.1 benchmark or a v0.1 standard, and the next six months produce the
  version people cite."

---

## Partners

**CeSIA**, the French Center for AI Safety — AI safety research and advocacy
organization known for the **Global Call for AI Red Lines**. Provides the seed reading
pack, judges for the forecasting, regulatory and tabletop tracks, distribution through
its newsletter and **7,000-member Discord**, and a potential route for policy outputs to
reach the AI Office.

## Contact

- Email: sprints@apartresearch.com
- Discord: discord.gg/XswWBvugYs
- Organizers: Apart Research and CeSIA
- Apart Research Inc · 1500 N Grant St, Ste R, Denver, CO 80203 · +1 (720) 408-1923

---

## Speakers

| Speaker | Affiliation | Talk |
|---|---|---|
| **Stephen "Cas" Casper** | Asst. Prof. of Public Policy, Harvard Kennedy School; Faculty Affiliate, Harvard SEAS; PhD MIT; residency UK AISI; writer, International AI Safety Report; lead writer, Singapore Consensus | "Predicting the first major AI-enabled terrorism incident: A pre-mortem and 9 predictions" — Fri 11 Sep, 2:00 PM ET |
| **David Krueger** | Exec. Director, Evitable; Asst. Prof., U. Montreal; Core Academic Member, Mila; CIFAR AI Chair; IVADO Professorship in Responsible AI | Fri 11 Sep, 3:15 PM ET |
| **Tim Hua** | MTS at METR (alignment assessments and evaluations, personal capacity); ex-Transluce; ex-Astra Fellow, Redwood; MATS scholar under Neel Nanda and Sam Marks | Fri 11 Sep, 5:15 PM PT — steering evaluation-aware models to act like they are deployed; cost-constrained runtime monitors |
| **Henry Papadatos** | Exec. Director, SaferAI; EU AI Act Codes of Practice expert working group (risk taxonomy and assessment); G7 Hiroshima AI Process reporting framework via OECD task force; ex-CHAI Berkeley | Fri 11 Sep, 3:15 PM CEST |
| **Alex Mallen** | MTS, Redwood Research | "How near-term AI swarms could cause labs to lose control of AI development, absent improved defenses" — Fri 11 Sep, 2:15 PM PT |
| **Marko Grobelnik** | AI Lab co-lead, Jozef Stefan Institute; co-founder IRCAI (UNESCO); CEO Quintelligence; OECD AI Committee, Council of Europe CAI, NATO DARB, GPAI | TBC |
| **Boyd Kane** | MATS 9 Extension with Alex Turner and Alex Cloud (Anthropic), detecting deceptively misaligned AI; ex-CubeSpace, AWS Cape Town; MSc Stellenbosch | **"Uncovering public traces of the OpenAI Huggingface incident"** — Fri 11 Sep, 10:15 AM ET |
| **Isaak Mengesha** | Postdoc, Oxford Martin School Programme on Forecasting Technological Change (with INET); PhD U. Amsterdam; led research at Arcadia Impact's AI Governance Taskforce on AI incident monitoring | **"Incident Response Has a Measurement Problem"** — Fri 11 Sep, 1:00 PM ET |
| **Justin Shenk** | Independent AI safety researcher, Berlin; mech interp; BlueDot Impact course cohorts; AI Salon Berlin; PhD computational neuroscience; co-founder VisioLab | Thu 10 Sep, 4:15 PM CEST |

---

## Judges (full roster)

| Judge | Background |
|---|---|
| **Twm Stone** | Software engineering; threat modelling, formal verification and red teaming of AI systems; MATS 9.1 extension fellow, security stream |
| **Nikhil R. Pallepati** | ML Engineer, Microsoft; GNN-based detection systems and agentic LLM pipelines protecting Azure cloud infrastructure |
| **Amey Kulkarni** | Senior Data Engineer, Walmart (Spark, Kafka, BigQuery, Kubernetes on GCP); author of Context Change Impact Analysis (CCIA) and maintainer of ctxwitch |
| **Ved K** | Senior Security Detection Engineer, Databricks; leads Kubernetes detection program, insider threat tooling, Terraform-managed logging; multi-cloud threat detection, behavioral anomaly detection |
| **Spurthi Tallam** | Senior ML engineer, LePrix; ex-Good Inside, Samsung Research; MS CS UMass Amherst |
| **Tim Schipper** | Senior Full Stack Developer, AI Consultant and AI Evangelist at Yielder; 30+ years |
| **Kevin Wei** (he/they) | Researcher, GovAI; science of AI evaluations, legal AI safety/alignment, technical AI governance/law; Oxford Martin AIGI, RAND CAST; ex-Visiting Research Scientist, UK AISI science of evaluations; JD Harvard Law; MS ML Georgia Tech |
| **David Manheim** | Founder and head of research and policy, ALTER; biological and technological risks, alignment and safety |
| **Francesca Gomez** | Research team lead, Arcadia Impact AI Governance Taskforce; paper on thresholds for escalating AI incidents across jurisdictions; founder, Wiser Human |
| **Hannes Bastians** | Research Scholar, Institute for Law and AI; co-authored the commentary on **Article 55 AI Act incl. the serious incident reporting obligation, Art. 55(1)(c)**, Cambridge Commentary on EU GPAI Law |
| **Hariharan Subramanian** | Senior SWE, Microsoft Azure Kubernetes Service; Envoy Gateway contributor/reviewer; mTLS via Istio; manages security embargo processes for AKS Envoy proxies; CNCF AI gateway WGs |
| **Heather Frase, PhD** | CEO, Veraitech; Senior Advisor for T&E of AI, Virginia Tech National Security Institute; board member, Responsible AI Collaborative |
| **Ratnavarma Kundady** | Senior Manager and AI Solutions Delivery Lead, Accenture; enterprise incident response, operational resilience, AI governance and controls |
| **Richard Willats** | AI Safety Researcher, Mercor; designed the AI Red-Teaming Bootcamp; ex-Contextual AI safety evaluation, ex-Spotify adversarial testing of production agents |
| **Vijay G** | Senior Engineering Manager, SAP Procurement Engineering; leads development of autonomous sourcing agents |
| **Chi Lu** | AI and robotics researcher, UIUC; cross-embodiment motion models, embodied AI, multimodal learning; ICLR 2025 |
| **Peter Wildeford** | Head of Policy, The AI Policy Network; co-founder IAPS; ex-data scientist/SWE |
| **Antony Alangaram** | Director-level Digital Enterprise Architect (billion-dollar e-commerce); AI, cybersecurity, operational resilience, production engineering |
| **Gaurav Thakur** | Principal AI Security Architect, Zscaler; securing user-to-LLM and agent-to-LLM interactions, agentic traffic on the endpoint, red teaming of AI agents; multi-cloud Zero Trust white paper |
| **Shashank Shelat** | Leads security at Earnest; detection engineering, incident response, SOAR automation; 14+ years incl. Lucid Motors, Atlassian, First Republic Bank |

---

## Notes for our submission (Sentinel)

- Deliverable must be on the **official template** (Guidelines tab) — still the one
  outstanding blocker.
- **Limitations and Dual-Use Considerations appendix is mandatory**, not optional.
- Track 1's scored sentence — *"could a third party verify compliance without access to
  the lab's network"* — is exactly what the (trace, allowlist) framing answers.
- Judge roster skews hard to **detection engineering and cloud security** (Databricks
  K8s detection, Zscaler agentic traffic, AKS/Envoy, Microsoft Azure detection, Earnest
  SOAR). "Monitor egress against an allowlist" is their day job; the **misspecification
  ablation** is the part that is not.
- Rules to respect: do not publicly release novel installation recipes without review;
  do not use a model to breach an organisation; undisclosed prior work can disqualify.
