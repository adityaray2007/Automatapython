"""Shared Word-document styling (same look as the Milestone-2 report). Used by the M1 generator."""
import re
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

NAVY, BLUE, GREY = RGBColor(0x0F, 0x17, 0x2A), RGBColor(0x1D, 0x4E, 0xD8), RGBColor(0x47, 0x55, 0x69)
HEADFILL, ALTFILL = "E8EEF9", "F8FAFC"


class Doc:
    def __init__(self, header_text, footer_text):
        self.doc = d = docx.Document()
        self.fig_n = self.tab_n = 0
        for s in d.sections:
            s.page_width, s.page_height = Inches(8.27), Inches(11.69)
            s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)
        st = d.styles["Normal"]
        st.font.name, st.font.size = "Calibri", Pt(11)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        st.paragraph_format.line_spacing = 1.15
        st.paragraph_format.space_after = Pt(6)
        for name, size, before in (("Heading 1", 16, 18), ("Heading 2", 13, 12), ("Heading 3", 11.5, 8)):
            h = d.styles[name]
            h.font.name, h.font.size, h.font.bold = "Calibri", Pt(size), True
            h.font.color.rgb = BLUE if name == "Heading 1" else NAVY
            for k in ("w:eastAsia", "w:ascii", "w:hAnsi"):
                h.element.rPr.rFonts.set(qn(k), "Calibri")
            h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(before), Pt(4)
            h.paragraph_format.keep_with_next = True
        sec = d.sections[0]
        sec.different_first_page_header_footer = True
        r = sec.header.paragraphs[0].add_run(header_text); r.font.size = Pt(8.5); r.font.color.rgb = GREY
        fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run(footer_text + "   |   Page "); r.font.size = Pt(8.5); r.font.color.rgb = GREY
        self._field(fp, "PAGE")

    # -- low level
    @staticmethod
    def _field(p, instr):
        for kind, txt in (("begin", None), (None, instr), ("end", None)):
            r = p.add_run()
            if kind:
                fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind); r._r.append(fc)
            else:
                it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)

    @staticmethod
    def shade(cell, fill):
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:fill="{fill}"/>'))

    @staticmethod
    def margins(cell, t=50, b=50, l=90, r=90):
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:bottom w:w="{b}" w:type="dxa"/>'
            f'<w:left w:w="{l}" w:type="dxa"/><w:right w:w="{r}" w:type="dxa"/></w:tcMar>'))

    @staticmethod
    def borders(table, color="BFC8D6"):
        table._tbl.tblPr.append(parse_xml(
            f'<w:tblBorders {nsdecls("w")}>' + "".join(
                f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
                for e in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"))

    @staticmethod
    def runs(p, text, bold=False, italic=False, size=None):
        for part in re.split(r"(\*\*.+?\*\*|`.+?`|\[\[.+?\]\])", text):
            if not part: continue
            if part.startswith("**"):
                r = p.add_run(part[2:-2]); r.bold = True
            elif part.startswith("`"):
                r = p.add_run(part[1:-1]); r.font.name = "Consolas"; r.font.size = Pt((size or 11) - 1)
                r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas"); continue
            elif part.startswith("[["):
                r = p.add_run("[" + part[2:-2] + "]"); r.font.highlight_color = 7
            else:
                r = p.add_run(part); r.bold = bold
            r.italic = italic
            if size: r.font.size = Pt(size)

    # -- content
    def h(self, text, level=1):
        return self.doc.add_heading(text, level)

    def p(self, text="", bold=False, italic=False, size=None, align=None, after=None, keep=False, indent=None):
        p = self.doc.add_paragraph()
        self.runs(p, text, bold, italic, size)
        if align is not None: p.alignment = align
        if after is not None: p.paragraph_format.space_after = Pt(after)
        if keep: p.paragraph_format.keep_with_next = True
        if indent: p.paragraph_format.left_indent = Inches(indent)
        return p

    def bullet(self, text, level=0, size=None):
        p = self.doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.space_after = Pt(2)
        self.runs(p, text, size=size)
        return p

    def numbered_item(self, num, text, indent=0.0):
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3 + indent)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(0.3 + indent))
        p.add_run(f"{num}\t")
        self.runs(p, text)
        return p

    def caption(self, kind, text):
        if kind == "Figure": self.fig_n += 1; n = self.fig_n
        else: self.tab_n += 1; n = self.tab_n
        p = self.doc.add_paragraph()
        r = p.add_run(f"{kind} {n}: "); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = GREY
        r = p.add_run(text); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = GREY
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if kind == "Figure" else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(8 if kind == "Figure" else 3)
        if kind == "Table": p.paragraph_format.keep_with_next = True
        return n

    def figure(self, path, text, width=6.0):
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(str(path), width=Inches(width))
        return self.caption("Figure", text)

    def table(self, headers, rows, widths=None, size=9, caption=None, bold_first_col=False):
        if caption: self.caption("Table", caption)
        t = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        self.borders(t)
        for j, hd in enumerate(headers):
            c = t.rows[0].cells[j]; self.shade(c, HEADFILL); self.margins(c)
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(hd); r.bold = True; r.font.size = Pt(size)
        for i, row in enumerate(rows, start=1):
            for j, val in enumerate(row):
                c = t.rows[i].cells[j]; self.margins(c)
                if i % 2 == 0: self.shade(c, ALTFILL)
                p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
                self.runs(p, str(val), bold=(bold_first_col and j == 0), size=size)
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        for row in t.rows: row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        if widths:
            for row in t.rows:
                for j, w in enumerate(widths): row.cells[j].width = Inches(w)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def code(self, text, size=8.5):
        t = self.doc.add_table(rows=1, cols=1); self.borders(t, "CBD5E1")
        c = t.rows[0].cells[0]; self.shade(c, "F1F5F9"); self.margins(c, 80, 80, 120, 120)
        lines = text.strip("\n").split("\n")
        p = c.paragraphs[0]
        for i, line in enumerate(lines):
            r = p.add_run(line); r.font.name = "Consolas"; r.font.size = Pt(size)
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            if i < len(lines) - 1: r.add_break()
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def save(self, path):
        self.doc.save(path)
