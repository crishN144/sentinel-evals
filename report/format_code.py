"""Formatting-only pass over a finished .docx: monospace identifiers, grey-field commands, shaded code blocks,
noProof on all of them. Touches no text. Usage: python report/format_code.py IN.docx OUT.docx"""
import copy, re, sys
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

MONO = "Courier New"
CMDS = ["scout scan sentinel/scanner.py -T logs/", "sentinel score traces/hf_openai.json", "sentinel score"]
IDENTS = ["ChatMessageAssistant.tool_calls", "lab_detected_at_event", "extract_destinations", "network_mode: none",
          "internet_expected", "allowed_hosts", "allowed_cidrs", "classify(host)", "python -m pytest",
          "scanner.py", "extract.py", "core.py", "nc/ncat", "socat", "ALLOWED", "LOOPBACK", "METADATA", "Result"]
# lookarounds, not \b: identifiers like classify(host) end in a non-word character
CODE_RE = re.compile("|".join([re.escape(c) for c in CMDS] + [r"(?<!\w)" + re.escape(i) + r"(?!\w)" for i in IDENTS]
                              + [r"(?<!\w)OUT(?!\w)", r"(?<!\w)T[123](?!\w)"]))

def set_mono(run, size=Pt(9.5)):
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None: rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs"): rf.set(qn(a), MONO)
    if size: run.font.size = size
    if rpr.find(qn("w:noProof")) is None:
        e = OxmlElement("w:noProof"); e.set(qn("w:val"), "1"); rpr.append(e)

def shade(el_pr, fill="EDEDED"):
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    el_pr.append(shd)

def merge_runs(par):
    """Word resaves split runs at proofing boundaries; rejoin neighbours with identical rPr."""
    runs = list(par.runs); i = 1; merged = 0
    while i < len(runs):
        a, b = runs[i - 1], runs[i]
        same = (a._r.getnext() is b._r) and (a._r.rPr is None and b._r.rPr is None or
                (a._r.rPr is not None and b._r.rPr is not None and a._r.rPr.xml == b._r.rPr.xml))
        if same and b._r.find(qn("w:br")) is None and b._r.find(qn("w:drawing")) is None:
            a.text = a.text + b.text; b._r.getparent().remove(b._r); runs.pop(i); merged += 1
        else:
            i += 1
    return merged


JSON_PREFIXES = ('{"name": "exploitgym-cyber-eval"', ' "allowed_hosts": [', ' "notes": "ExploitGym run-proxy')

def split_runs(par):
    changed = 0
    merge_runs(par)
    for run in list(par.runs):
        text = run.text
        if not text or not CODE_RE.search(text): continue
        pieces = []; pos = 0
        for m in CODE_RE.finditer(text):
            if m.start() > pos: pieces.append((text[pos:m.start()], False))
            pieces.append((m.group(0), True)); pos = m.end()
        if pos < len(text): pieces.append((text[pos:], False))
        run.text = pieces[0][0]; last = run._r
        if pieces[0][1]: set_mono(run); shade(run._r.get_or_add_rPr()) if pieces[0][0] in CMDS else None
        for txt, is_code in pieces[1:]:
            new = copy.deepcopy(run._r)
            for t in new.findall(qn("w:t")): new.remove(t)
            for e in new.findall(qn("w:rFonts")): new.remove(e)
            last.addnext(new); last = new
            r = type(run)(new, par); r.text = txt
            if is_code:
                set_mono(r)
                if txt in CMDS: shade(r._r.get_or_add_rPr())
            else:
                # restore the paragraph's body face on non-code fragments cloned from a code run
                rpr = r._r.get_or_add_rPr()
                for e in list(rpr):
                    if e.tag in (qn("w:noProof"), qn("w:shd")): rpr.remove(e)
                rf = rpr.find(qn("w:rFonts"))
                if rf is not None: rpr.remove(rf)
                r.font.name = "Old Standard TT"
            changed += 1
    return changed

def main(src, dst):
    d = Document(src); n_ident = 0; n_block = 0
    # Word's resave litters <w:proofErr> markers between runs; they are spell-check state, not content
    for el in list(d.element.body.iter(qn("w:proofErr"))): el.getparent().remove(el)
    paras = list(d.paragraphs) + [p for t in d.tables for row in t.rows for c in row.cells for p in c.paragraphs]
    for p in paras:
        # code blocks: the JSON lines were emitted in Menlo; restyle the whole paragraph
        if p.text.startswith(JSON_PREFIXES) or (p.runs and all((r.font.name == "Menlo") for r in p.runs)):
            for r in p.runs: set_mono(r)
            shade(p._p.get_or_add_pPr())
            p.paragraph_format.left_indent = Inches(0.3); p.paragraph_format.right_indent = Inches(0.3)
            n_block += 1; continue
        n_ident += split_runs(p)
    d.save(dst); print(f"code-block lines restyled: {n_block}; identifier/command runs set: {n_ident}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
