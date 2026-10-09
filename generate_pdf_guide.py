import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "FinGuard: Zero to Hero Architecture & Reproduction Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_text)
        self.drawString(54, 32, "Confidential & Engineering Overview • arXiv:2605.29427")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 44, letter[0] - 54, 44)
        
        self.restoreState()

def build_pdf(filename="FinGuard_Zero_To_Hero_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary = colors.HexColor("#1A365D")    # Deep Navy
    secondary = colors.HexColor("#2B6CB0")  # Slate Blue
    dark_text = colors.HexColor("#2D3748")  # Charcoal
    accent = colors.HexColor("#C53030")     # Danger / Red
    bg_light = colors.HexColor("#F7FAFC")
    border_color = colors.HexColor("#E2E8F0")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=secondary,
        spaceAfter=14
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        spaceAfter=6
    )
    
    body_bold = ParagraphStyle(
        'CustomBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )
    
    code_box_style = ParagraphStyle(
        'CodeBox',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=dark_text
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#FFFFFF")
    )
    
    story = []
    
    # Title & Metadata Banner
    story.append(Paragraph("FinGuard: Zero to Hero Guide", title_style))
    story.append(Paragraph("Detecting Financial Regulatory Non-Compliance in LLMs • Paper Reproduction & System Architecture", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=12))
    
    # Section 1: The Core Problem
    story.append(Paragraph("1. The Core Problem: The 'Wall Street AI' Trap", h1_style))
    story.append(Paragraph(
        "Standard commercial LLMs (GPT-4, Claude, Gemini, Llama) are trained with generic safety guardrails targeting hate speech, weapons, malware, and self-harm. "
        "However, they possess <b>zero native comprehension of technical financial regulations</b>, making them dangerously susceptible to regulatory evasion, fraud, and illegal market actions.",
        body_style
    ))
    
    # Examples of LLM Non-Compliance
    story.append(Paragraph("<b>Real-World Catastrophic Failure Modes:</b>", body_style))
    story.append(Paragraph("• <b>Anti-Money Laundering (BSA / 31 CFR § 1020):</b> User asks how to break up $50,000 across accounts to avoid CTR filings. Standard LLM provides structuring schedules (felony offence under federal law).", bullet_style))
    story.append(Paragraph("• <b>Securities Fraud (SEC Rule 10b-5):</b> User seeks guidance on trading prior to undisclosed earnings calls. Standard LLM offers derivative masking strategies rather than refusing.", bullet_style))
    story.append(Paragraph("• <b>Consumer Debt Collection (CFPB Reg E / FDCPA):</b> Model drafts threatening letters alleging false arrest warrants, violating debt harassment statues.", bullet_style))
    story.append(Paragraph("• <b>Corporate Accounting (SOX Section 802):</b> Model suggests methods to alter or purge ledger archives prior to a PCAOB audit.", bullet_style))
    
    story.append(Spacer(1, 10))
    
    # Section 2: Architecture
    story.append(Paragraph("2. System Architecture: The Two-Checkpoint Guardrail", h1_style))
    story.append(Paragraph(
        "FinGuard introduces a dual-checkpoint architecture that scrutinizes interactions both at the input query stage and the generated response stage.",
        body_style
    ))
    
    arch_diagram_text = (
        "                    [ User Financial Query ]<br/>"
        "                               │<br/>"
        "             ▼─────────────────┴─────────────────▼<br/>"
        "     [CHECKPOINT 1: Query Compliance Guard]<br/>"
        "           │                               │<br/>"
        "      [RISKY]                         [SAFE]<br/>"
        "           ▼                               ▼<br/>"
        "  [Safe Policy Layer]           [Statutory Retriever (FAISS/TF-IDF)]<br/>"
        "  - Immediate Refusal           - Fetches SEC, BSA, CFPB, SOX texts<br/>"
        "  - Exact Statutory Citation              │<br/>"
        "                                           ▼<br/>"
        "                                [Response Synthesizer / LLM]<br/>"
        "                                           │<br/>"
        "             ▼─────────────────────────────┴─────────────────────▼<br/>"
        "     [CHECKPOINT 2: Response Compliance Guard]<br/>"
        "           │                               │<br/>"
        "      [RISKY]                         [SAFE]<br/>"
        "           ▼                               ▼<br/>"
        "  [Intercept & Neutralize]      [Deliver Verified Compliant Output]<br/>"
        "  - Replace with legal notice"
    )
    
    diagram_table = Table([[Paragraph(arch_diagram_text, code_box_style)]], colWidths=[504])
    diagram_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(diagram_table)
    
    story.append(Spacer(1, 12))
    
    # Section 3: The 4 Core Engineering Pillars
    story.append(Paragraph("3. The 4 Engineering Pillars of this Codebase", h1_style))
    
    story.append(Paragraph("Pillar I: Financial Risk Taxonomy (11 Categories, 35 Subcategories)", h2_style))
    story.append(Paragraph(
        "Defined in <code>src/taxonomy.py</code>. Covers the full spectrum of financial crimes: "
        "Market Manipulation, Insider Trading, AML/CFT, Credit Violations, Consumer Harassment (FDCPA), "
        "GLBA Data Leakage, SOX Record Manipulation, FCPA Bribery, and Fiduciary Breaches.",
        body_style
    ))
    
    story.append(Paragraph("Pillar II: Statutory Ingestion & Compliance Points", h2_style))
    story.append(Paragraph(
        "Implemented in <code>src/ingestion/download_regulations.py</code> and <code>extract_compliance_points.py</code>. "
        "Parses statutory legal frameworks (SEC, FINRA, CFPB, DOJ, FTC) and extracts atomic affirmative duties, prohibited behaviors, and penalty clauses into <code>compliance_points.json</code>.",
        body_style
    ))
    
    story.append(Paragraph("Pillar III: Multi-Agent Judge & Adversarial Self-Play", h2_style))
    story.append(Paragraph(
        "Implemented in <code>src/judge.py</code> and <code>src/self_play_reward.py</code>. "
        "Replicates paper Equations (2) & (3). An Attacker LLM generates adversarial circumventions (hypotheticals, roleplays, academic cloaking), "
        "while Defender agents are rewarded for detecting non-compliance without yielding false alarms.",
        body_style
    ))
    
    story.append(Paragraph("Pillar IV: Grounded FinGuard-Bench Evaluation", h2_style))
    story.append(Paragraph(
        "Synthesizes paired real-world splits (<code>train.jsonl</code>, <code>val.jsonl</code>, <code>test.jsonl</code>) and executes micro/macro F1, recall, precision, and false positive evaluations (<code>src/evaluator.py</code>).",
        body_style
    ))
    
    story.append(Spacer(1, 12))
    
    # Section 4: What We Completed in Stage 1 Improvements
    story.append(Paragraph("4. Summary of Recent Improvements (Branch: stage1-improvements)", h1_style))
    
    summary_data = [
        [Paragraph("Component", table_cell_bold), Paragraph("File Path", table_cell_bold), Paragraph("Accomplishment & Impact", table_cell_bold)],
        [
            Paragraph("Paper Modules", table_cell),
            Paragraph("<code>src/*.py</code>", table_cell),
            Paragraph("Implemented pure paper taxonomy (11 cat/35 subcat), multi-agent judge parser, self-play reward engine, and evaluation suite.", table_cell)
        ],
        [
            Paragraph("Statutory Corpus", table_cell),
            Paragraph("<code>src/ingestion/</code>", table_cell),
            Paragraph("Ingested 8 federal regulatory bodies (BSA, Reg B, Reg E, FCPA, FINRA, GLBA, SEC, SOX) and extracted structured compliance rules.", table_cell)
        ],
        [
            Paragraph("Benchmark Gen", table_cell),
            Paragraph("<code>src/evaluation/</code>", table_cell),
            Paragraph("Synthesized grounded benchmark datasets (<code>train</code>, <code>val</code>, <code>test</code>) anchored directly in statutory law.", table_cell)
        ],
        [
            Paragraph("Verification Suite", table_cell),
            Paragraph("<code>src/verify.py</code>", table_cell),
            Paragraph("Created and validated end-to-end unit test suite. Verified output parsing, reward calculation, and mock evaluation passing 100%.", table_cell)
        ],
    ]
    
    summary_table = Table(summary_data, colWidths=[90, 114, 300])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    
    story.append(Spacer(1, 14))
    
    # Section 5: Decision Matrix & Next Steps
    story.append(Paragraph("5. Next Steps Decision Matrix", h1_style))
    
    decision_data = [
        [Paragraph("Option", table_cell_bold), Paragraph("Goal", table_cell_bold), Paragraph("Description & Next Command", table_cell_bold)],
        [
            Paragraph("<b>A. Real Benchmark Evaluation</b>", table_cell),
            Paragraph("Evaluate Performance", table_cell),
            Paragraph("Benchmark the new <code>finguard_bench_real</code> dataset against retrieval algorithms to evaluate precision, recall, and Macro-F1.", table_cell)
        ],
        [
            Paragraph("<b>B. Interactive Web App</b>", table_cell),
            Paragraph("Visual Demonstration", table_cell),
            Paragraph("Launch Streamlit app (<code>streamlit run app/streamlit_app.py</code>) to test live compliance queries and inspection in browser.", table_cell)
        ],
        [
            Paragraph("<b>C. Self-Play Synthesis</b>", table_cell),
            Paragraph("Adversarial Generation", table_cell),
            Paragraph("Execute <code>synthesis_pipeline.py</code> to generate automated adversarial test cases using extracted compliance points.", table_cell)
        ],
        [
            Paragraph("<b>D. Git Merge & Review</b>", table_cell),
            Paragraph("Production Release", table_cell),
            Paragraph("Review diff, run tests, and merge <code>stage1-improvements</code> into <code>main</code> branch.", table_cell)
        ]
    ]
    
    decision_table = Table(decision_data, colWidths=[120, 110, 274])
    decision_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(decision_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {os.path.abspath(filename)}")

if __name__ == "__main__":
    build_pdf()
