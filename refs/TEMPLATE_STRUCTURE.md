# Apart submission template — extracted structure (source: refs/apart_submission_template.docx)

Original file: `~/Downloads/Copy of Apart Research hackathon submission template.docx`
Links embedded in the template:
- sprint page: https://apartresearch.com/sprints/ai-incident-response-sprint-2026-09-11-to-2026-09-13
- **Evaluation Rubric: https://apartresearch.notion.site/sprint-evaluation-rubric**

## Front matter
- `PROJECT TITLE` (Title style)
- Author name 1..6 + Affiliation (one line each)
- "With **Apart Research**"
- **Abstract** — 150–250 words. "A strong abstract lets a reviewer understand what you did
  and why it matters without reading anything else." Must cover: **the problem, your
  approach, key results, the main takeaway.** Polish it last; it should reflect final
  results, not the initial plan.

## Info box (DELETE before submitting)
- "Replace the italicized guidance text under each section with your content. The section
  structure is **strong guidance but not rigid**. If your project requires a different
  organization, feel free to adapt. **Delete all guidance text including this info box
  before submitting.** Make sure the project title and author information above are up to
  date."
- "Your project will be judged on **the quality of this written report**."
- **"Recommended length: 4 pages excluding references and appendix. Rough guide: Intro &
  Related Work 1p, Methods and Results: 2.5p, Discussion 0.5p."**

## Sections
1. **Introduction** — what problem, why it matters; why the work is *practically* valuable;
   enough background; briefly describe the **threat model or failure mode**, with prior work
   motivating it. Ends with an explicit bulleted list: *"Our main contributions are:"*
   (first / second / third contribution).
2. **Related Work** — most similar prior work and how yours differs; cite the most relevant
   papers, tools, projects; **explain what gap your work addresses.** Prompts to answer:
   *when and why would someone use your method over the existing state of the art?* and
   *what information/insight does your method provide which we did not have before?*
3. **Methods** — replicable description; key design choices justified ("the more you can back
   up your design choices by referencing prior work, the better"); models/datasets/tools and
   why; key parameters; **what you tried that didn't work**; reproducibility.
4. **Results** — main findings with evidence; **at least one figure strongly encouraged**;
   distinguish observations from interpretations; argue robustness (enough data? significant?
   robust to small setup changes?). Number all figures/tables, captions standalone, place near
   first reference, legible text.
5. **Discussion and Limitations** — broader implications for AI safety; what the results mean;
   trends and what they indicate.
   - **Limitations** (H3) — honest constraints: methodological, scope, hackathon-timeframe;
     **explicitly note assumptions and how interpretation changes if an assumption fails.**
   - **Future Work** (H3) — natural next steps.
6. **Conclusion** — 1–2 paragraphs.
- **Code and Data** — Code repository / Data / Other artifacts (demo, video, HF Space). Note
  info-hazard considerations here if any.
- **Author Contributions** (optional)
- **References** — consistent format: Author(s), Year, Title, Venue/Publisher, URL or DOI.
- **Appendix** (optional in the template) — additional figures, detailed methodology, prompts,
  extended results.

## Two conflicts with the sprint page — resolve in our favour
1. **Length.** Template says "recommended 4 pages excluding references and appendix" with a
   1p / 2.5p / 0.5p split. Sprint page says "maximum 8 pages ... most strong reports are 4 to
   8." → Treat **4 pages as the target for the main body** and let references + the required
   appendix carry the overflow. Do not pad to 8.
2. **Dual-use appendix.** The template has Limitations inside section 5 but **no Dual-Use
   section**. The sprint page states: *"A Limitations and Dual-Use Considerations appendix is
   required."* → We add it as a named appendix, `Appendix A: Limitations and Dual-Use
   Considerations`, regardless of the template's silence. The template explicitly permits
   adapting the structure.

## Still to fetch
- The **Evaluation Rubric** at apartresearch.notion.site/sprint-evaluation-rubric — already
  reflected in `report/RUBRIC.md` (three 1–5 dimensions: Impact & Innovation, Execution
  Quality, Presentation & Clarity). Re-check against the live page if time allows.
