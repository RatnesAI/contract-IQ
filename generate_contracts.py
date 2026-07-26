"""
ContractIQ - Randomized Dummy Contract Generator
=================================================
Generates 6 realistic enterprise contract PDFs with DIFFERENT content
every single time you run it.

Run it:   python generate_contracts.py
Output:   contracts/run_<timestamp>/  (new folder each run)

What randomizes each run:
  - Company names, addresses, jurisdictions
  - Contract IDs, effective dates
  - Dollar amounts, percentages, timeframes
  - Personnel names and roles
  - Deadlines and milestone dates
  - All 7 conflicts still exist but with fresh values every time
"""

import os
import random
import string
from datetime import datetime, timedelta
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

fake = Faker()
random.seed()  # true random every run

# ─────────────────────────────────────────────────────────────
# TIMESTAMPED OUTPUT FOLDER — new folder every run
# ─────────────────────────────────────────────────────────────
RUN_ID    = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = f"contracts/run_{RUN_ID}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# RANDOMIZED CONTRACT DATA — regenerated fresh every run
# ─────────────────────────────────────────────────────────────

def random_date(start_year=2021, end_year=2024):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def fmt_date(d):
    return d.strftime("%B %d, %Y")

def contract_id(prefix):
    year = random.randint(2021, 2024)
    seq  = random.randint(100, 999)
    tag  = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{prefix}-{year}-{tag}-{seq:03d}"

def random_usd(lo, hi, step=5000):
    val = random.randrange(lo, hi, step)
    return f"USD {val:,}"

def random_pct(lo, hi, decimals=1):
    return round(random.uniform(lo, hi), decimals)

def random_days(lo, hi):
    return random.randint(lo, hi)

def rand_company():
    prefixes  = ["Nova", "Apex", "Nexus", "Vertex", "Axiom", "Crest",
                 "Pulse", "Orion", "Stratos", "Lumina", "Cipher", "Helix"]
    suffixes  = ["Solutions", "Enterprises", "Systems", "Technologies",
                 "Dynamics", "Partners", "Consulting", "Services", "Group"]
    legal     = ["Inc.", "Ltd.", "LLC", "Corp.", "Pvt. Ltd.", "GmbH", "PLC"]
    return f"{random.choice(prefixes)}{random.choice(prefixes[:4])} {random.choice(suffixes)} {random.choice(legal)}"

def rand_address(country_hint=None):
    cities = {
        "US":  [("Wilmington", "DE 19801"), ("Austin", "TX 78701"),
                ("Seattle",    "WA 98101"), ("Chicago", "IL 60601"),
                ("New York",   "NY 10001"), ("San Francisco", "CA 94105")],
        "UK":  [("London EC4N 6HL",), ("Manchester M1 2AB",),
                ("Edinburgh EH1 1YZ",), ("Birmingham B1 1BB",)],
        "EU":  [("Frankfurt 60313, Germany",), ("Amsterdam 1011 AX, Netherlands",),
                ("Paris 75001, France",),      ("Dublin D02, Ireland",)],
        "APAC":[("Singapore 018989",), ("Sydney NSW 2000, Australia",),
                ("Tokyo 100-0001, Japan",),    ("Bangalore 560001, India",)],
    }
    pool = cities.get(country_hint, cities["US"])
    entry  = random.choice(pool)
    number = random.randint(10, 999)
    streets = ["Innovation Drive", "Technology Park", "Commerce Square",
               "Enterprise Way", "Business Boulevard", "Digital Avenue"]
    if len(entry) == 2:
        return f"{number} {random.choice(streets)}, {entry[0]}, {entry[1]}, USA"
    else:
        return f"{number} {random.choice(streets)}, {entry[0]}"

def rand_person(role=""):
    first_names = ["Rajesh","Sarah","Marcus","Priya","Tom","Ananya","James",
                   "Li Wei","Emma","Carlos","Fatima","David","Yuki","Nadia",
                   "Oliver","Shreya","Brendan","Mei","Arjun","Sophie"]
    last_names  = ["Mehta","Chen","Webb","Sharma","O'Brien","Das","Patel",
                   "Nakamura","Schmidt","Rodrigues","Hassan","Kim","Mueller",
                   "Johansson","Fitzgerald","Iyer","MacLeod","Tanaka","Singh","Dupont"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def rand_jurisdiction():
    return random.choice([
        "State of Delaware, USA",
        "State of New York, USA",
        "State of California, USA",
        "State of Texas, USA",
        "England and Wales",
        "Republic of Ireland",
        "State of Singapore",
    ])

# ── Generate all random values ONCE per run ─────────────────
PARTY_A      = rand_company()
PARTY_B      = rand_company()
ADDR_A       = rand_address("US")
ADDR_B       = rand_address(random.choice(["UK","EU","APAC"]))

MSA_ID       = contract_id("MSA")
SOW1_ID      = contract_id("SOW")
SOW2_ID      = contract_id("SOW")
SLA_ID       = contract_id("SLA")
DPA_ID       = contract_id("DPA")
AMD_ID       = contract_id("AMD")

MSA_DATE     = random_date(2021, 2023)
SOW1_DATE    = MSA_DATE + timedelta(days=random.randint(10, 40))
SOW2_DATE    = SOW1_DATE + timedelta(days=random.randint(30, 90))
SLA_DATE     = SOW1_DATE + timedelta(days=random.randint(0, 5))
DPA_DATE     = MSA_DATE
AMD_DATE     = MSA_DATE + timedelta(days=random.randint(180, 400))

# ── CONFLICT VALUES (intentionally mismatched) ───────────────
# C1: Liability cap — MSA lower, SOW1 higher
MSA_LIABILITY   = random.randrange(300000,  700000, 50000)
SOW1_LIABILITY  = random.randrange(900000, 2000000, 100000)  # always > MSA

# C2: Uptime — MSA lower, SLA/SOW1 higher
MSA_UPTIME      = round(random.uniform(99.0, 99.6), 1)
SLA_UPTIME      = round(random.uniform(99.7, 99.99), 2)      # always > MSA

# C3: Payment terms — MSA net-X, SOW2 shorter
MSA_NET         = random.choice([45, 60])
SOW2_NET        = random.choice([15, 20, 30])                 # always < MSA

# C4: Data retention — DPA shorter, Amendment longer
DPA_RETENTION   = random.choice([6, 12, 18])
AMD_RETENTION   = DPA_RETENTION + random.choice([12, 18, 24]) # always > DPA

# C5: Penalty cap — MSA lower, SLA higher
MSA_PENALTY     = random.randint(8, 12)
SLA_PENALTY     = random.randint(13, 20)                      # always > MSA

# C6: Governing law — intentional mismatch
MSA_LAW         = rand_jurisdiction()
SOW2_LAW        = rand_jurisdiction()
while SOW2_LAW == MSA_LAW:
    SOW2_LAW    = rand_jurisdiction()

# C7: Renewal notice — MSA shorter, Amendment longer
MSA_NOTICE      = random.choice([60, 90])
AMD_NOTICE      = MSA_NOTICE + random.choice([30, 45, 60])    # always > MSA

# Renewal deadline
TERM_YEARS      = random.choice([2, 3])
MSA_EXPIRY      = MSA_DATE + timedelta(days=365 * TERM_YEARS)
MSA_RENEWAL_DEADLINE = MSA_EXPIRY - timedelta(days=MSA_NOTICE)
AMD_RENEWAL_DEADLINE = MSA_EXPIRY - timedelta(days=AMD_NOTICE)

# ── Personnel ────────────────────────────────────────────────
PROG_DIRECTOR   = rand_person("Programme Director")
CLOUD_ARCH1     = rand_person("Cloud Architect")
CLOUD_ARCH2     = rand_person("Cloud Architect")
DEVOPS_LEAD     = rand_person("DevOps Lead")
SECURITY_SPEC   = rand_person("Security Specialist")
QA_LEAD         = rand_person("QA Lead")
DATA_LEAD       = rand_person("Data Lead")
ML_ENGINEER     = rand_person("ML Engineer")

# ── Milestone dates ──────────────────────────────────────────
def milestone_dates(base, count=6, gap_range=(20, 50)):
    dates, d = [], base
    for _ in range(count):
        d = d + timedelta(days=random.randint(*gap_range))
        dates.append(d)
    return dates

SOW1_MILESTONES  = milestone_dates(SOW1_DATE, 5, (25, 55))
SOW2_MILESTONES  = milestone_dates(SOW2_DATE, 6, (30, 65))

# ── SOW1 values ──────────────────────────────────────────────
SOW1_TOTAL       = random.randrange(400000, 1200000, 50000)
SOW1_PARTS       = sorted([random.randrange(30000, 200000, 5000) for _ in range(4)])
SOW1_PARTS.append(SOW1_TOTAL - sum(SOW1_PARTS))

SOW2_TOTAL       = random.randrange(400000, 1200000, 50000)
SOW2_PARTS       = sorted([random.randrange(25000, 180000, 5000) for _ in range(5)])
SOW2_PARTS.append(SOW2_TOTAL - sum(SOW2_PARTS))

APP_COUNT        = random.randint(20, 60)
DB_COUNT         = random.randint(6, 20)
DASH_COUNT       = random.randint(20, 50)

# ── Breach / response times ──────────────────────────────────
BREACH_HOURS     = random.choice([24, 48, 72])
P1_RESPONSE_MIN  = random.choice([15, 30, 45, 60])
P1_RESOLUTION_HR = random.choice([2, 4, 6, 8])
MAINT_HOURS      = random.choice([2, 4, 6, 8])
INTEREST_RATE    = round(random.uniform(1.0, 2.5), 1)

# ── Compliance frameworks ─────────────────────────────────────
FRAMEWORKS = random.sample([
    "ISO 27001:2022", "SOC 2 Type II", "PCI DSS Level 1",
    "ISO 27701", "NIST CSF", "CSA STAR Level 2",
    "HITRUST CSF", "FedRAMP Moderate"
], 3)

# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_styles():
    S = {}
    S['DocTitle'] = ParagraphStyle('DocTitle', parent=styles['Title'],
        fontSize=15, spaceAfter=5, textColor=colors.HexColor('#1a1a2e'),
        alignment=TA_CENTER, fontName='Helvetica-Bold')
    S['SubTitle'] = ParagraphStyle('SubTitle', parent=styles['Normal'],
        fontSize=10, spaceAfter=4, textColor=colors.HexColor('#16213e'),
        alignment=TA_CENTER, fontName='Helvetica')
    S['H1'] = ParagraphStyle('H1', parent=styles['Heading1'],
        fontSize=11, spaceBefore=12, spaceAfter=4,
        textColor=colors.HexColor('#0f3460'), fontName='Helvetica-Bold')
    S['H2'] = ParagraphStyle('H2', parent=styles['Heading2'],
        fontSize=10, spaceBefore=8, spaceAfter=3,
        textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Bold')
    S['Body'] = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9, spaceAfter=5, leading=13,
        alignment=TA_JUSTIFY, fontName='Helvetica')
    S['Clause'] = ParagraphStyle('Clause', parent=styles['Normal'],
        fontSize=9, spaceAfter=4, leading=13,
        leftIndent=18, alignment=TA_JUSTIFY, fontName='Helvetica')
    S['Conflict'] = ParagraphStyle('Conflict', parent=styles['Normal'],
        fontSize=9, spaceAfter=4, leading=13,
        textColor=colors.HexColor('#8B0000'),
        alignment=TA_JUSTIFY, fontName='Helvetica')
    S['Footer'] = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=7.5, textColor=colors.grey,
        alignment=TA_CENTER, fontName='Helvetica')
    return S

S = make_styles()

def divider():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor('#cccccc'),
                      spaceAfter=8, spaceBefore=4)

def hdr(doc_type, doc_id, date, parties):
    rows = [
        [Paragraph(f"<b>Document Type:</b> {doc_type}", S['Body']),
         Paragraph(f"<b>Document ID:</b> {doc_id}",    S['Body'])],
        [Paragraph(f"<b>Effective Date:</b> {fmt_date(date)}", S['Body']),
         Paragraph(f"<b>Version:</b> 1.0",             S['Body'])],
        [Paragraph(f"<b>Party A:</b> {parties[0]}",    S['Body']),
         Paragraph(f"<b>Party B:</b> {parties[1]}",    S['Body'])],
    ]
    t = Table(rows, colWidths=[3.5*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#f0f4f8')),
        ('BOX',(0,0),(-1,-1), 0.5, colors.HexColor('#aaaaaa')),
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.HexColor('#cccccc')),
        ('PADDING',(0,0),(-1,-1), 5),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

def sig_block():
    rows = [
        [Paragraph(f"<b>FOR {PARTY_A}</b>",  S['Body']),
         Paragraph(f"<b>FOR {PARTY_B}</b>",  S['Body'])],
        [Paragraph("Signature: ______________________", S['Body']),
         Paragraph("Signature: ______________________", S['Body'])],
        [Paragraph("Name:      ______________________", S['Body']),
         Paragraph("Name:      ______________________", S['Body'])],
        [Paragraph("Title:     ______________________", S['Body']),
         Paragraph("Title:     ______________________", S['Body'])],
        [Paragraph("Date:      ______________________", S['Body']),
         Paragraph("Date:      ______________________", S['Body'])],
    ]
    t = Table(rows, colWidths=[3.5*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('TOPPADDING',(0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LINEABOVE',(0,0),(-1,0), 0.5, colors.HexColor('#aaaaaa')),
    ]))
    return t

def tbl(data, col_widths, header_color='#1a1a2e'):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),  colors.HexColor(header_color)),
        ('TEXTCOLOR',(0,0),(-1,0),   colors.white),
        ('FONTNAME',(0,0),(-1,0),    'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),   8.5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID',(0,0),(-1,-1),       0.5, colors.HexColor('#cccccc')),
        ('PADDING',(0,0),(-1,-1),    6),
        ('VALIGN',(0,0),(-1,-1),     'TOP'),
    ]))
    return t

def build(path, story):
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch,  bottomMargin=0.75*inch)
    doc.build(story)
    print(f"  ✅  {os.path.basename(path)}")

# ─────────────────────────────────────────────────────────────
# 1. MASTER SERVICE AGREEMENT
# ─────────────────────────────────────────────────────────────
def gen_msa():
    s = []
    s.append(Paragraph("MASTER SERVICE AGREEMENT", S['DocTitle']))
    s.append(Paragraph(f"{MSA_ID} | Confidential & Legally Binding", S['SubTitle']))
    s.append(Spacer(1,8))
    s.append(hdr("Master Service Agreement", MSA_ID, MSA_DATE, [PARTY_A, PARTY_B]))
    s.append(Spacer(1,10)); s.append(divider())

    s.append(Paragraph("RECITALS", S['H1']))
    s.append(Paragraph(
        f"This Master Service Agreement (\"{MSA_ID}\") is entered into as of {fmt_date(MSA_DATE)}, "
        f"by and between {PARTY_A}, a company with its principal place of business at {ADDR_A} "
        f"(hereinafter \"Service Provider\"), and {PARTY_B}, with its registered office at {ADDR_B} "
        f"(hereinafter \"Client\"). The parties wish to establish the terms under which Service "
        f"Provider shall deliver technology and professional services to Client.", S['Body']))

    s.append(Paragraph("SECTION 1: DEFINITIONS", S['H1']))
    for term, defn in [
        ("1.1 Agreement",    f"means this Master Service Agreement {MSA_ID} and all schedules, SOWs, SLAs, and DPAs issued hereunder."),
        ("1.2 Services",     "means all technology, consulting, implementation, and support services provided by Service Provider under applicable Statements of Work."),
        ("1.3 Deliverable",  "means any software, code, documentation, report, or work product created by Service Provider under this Agreement."),
        ("1.4 Force Majeure","means any event beyond the reasonable control of a party, including acts of God, war, pandemic, or government action."),
        ("1.5 Affiliate",    "means any entity that directly or indirectly controls, is controlled by, or is under common control with a party."),
    ]:
        s.append(Paragraph(f"<b>{term}:</b> {defn}", S['Clause']))

    s.append(Paragraph("SECTION 2: TERM AND TERMINATION", S['H1']))
    s.append(Paragraph(
        f"2.1 <b>Initial Term.</b> This Agreement commences on {fmt_date(MSA_DATE)} and continues "
        f"for {TERM_YEARS} year(s), unless earlier terminated.", S['Clause']))
    s.append(Paragraph(
        f"2.2 <b>Renewal. [OBLIGATION]</b> This Agreement auto-renews for successive one-year terms "
        f"unless either party provides {MSA_NOTICE} days written notice of non-renewal prior to "
        f"the end of the then-current term. <b>Renewal notice deadline: {fmt_date(MSA_RENEWAL_DEADLINE)}.</b>", S['Clause']))
    s.append(Paragraph(
        f"2.3 <b>Termination for Cause.</b> Either party may terminate immediately upon {random_days(14,30)}-day "
        f"written notice if the other party materially breaches this Agreement and fails to cure within "
        f"the notice period.", S['Clause']))
    s.append(Paragraph(
        f"2.4 <b>Termination for Convenience.</b> Client may terminate with {random_days(60,120)} days written "
        f"notice, subject to payment of all fees for services rendered.", S['Clause']))

    s.append(Paragraph("SECTION 3: PAYMENT TERMS", S['H1']))
    s.append(Paragraph(
        f"3.1 <b>Invoicing.</b> Service Provider shall submit monthly invoices with itemised "
        f"service descriptions.", S['Clause']))
    s.append(Paragraph(
        f"3.2 <b>Payment Deadline. [OBLIGATION — CONFLICT POINT C3]</b> Client shall pay all "
        f"undisputed invoices within <b>{MSA_NET} days (Net-{MSA_NET})</b> of invoice date. "
        f"Late payments accrue interest at {INTEREST_RATE}% per month.", S['Clause']))
    s.append(Paragraph(
        f"3.3 <b>Disputed Invoices.</b> Client must notify disputes within {random_days(10,20)} days "
        f"of receipt, else the invoice is deemed accepted.", S['Clause']))

    s.append(Paragraph("SECTION 4: SERVICE LEVELS", S['H1']))
    s.append(Paragraph(
        f"4.1 <b>Uptime. [OBLIGATION — CONFLICT POINT C2]</b> Service Provider commits to "
        f"minimum system availability of <b>{MSA_UPTIME}%</b> per calendar month, excluding "
        f"scheduled maintenance of up to {MAINT_HOURS} hours/month.", S['Clause']))
    s.append(Paragraph(
        f"4.2 <b>SLA Credits.</b> Failure to meet uptime entitles Client to service credits "
        f"not exceeding <b>{MSA_PENALTY}% [CONFLICT POINT C5]</b> of the monthly service fee.", S['Clause']))
    s.append(Paragraph(
        f"4.3 <b>Incident Response.</b> Critical (P1) incidents must be acknowledged within "
        f"{P1_RESPONSE_MIN} minutes and resolved within {P1_RESOLUTION_HR} hours.", S['Clause']))

    s.append(Paragraph("SECTION 5: LIABILITY", S['H1']))
    s.append(Paragraph(
        f"5.1 <b>Liability Cap. [OBLIGATION — CONFLICT POINT C1]</b> Each party's aggregate "
        f"liability shall not exceed <b>USD {MSA_LIABILITY:,}</b> or total fees paid in the "
        f"preceding 12 months, whichever is lesser.", S['Clause']))
    s.append(Paragraph(
        f"5.2 <b>Exclusions.</b> Neither party shall be liable for indirect, incidental, "
        f"punitive, or consequential damages.", S['Clause']))

    s.append(Paragraph("SECTION 6: CONFIDENTIALITY", S['H1']))
    s.append(Paragraph(
        f"6.1 <b>[OBLIGATION]</b> Each party shall hold the other's Confidential Information "
        f"in strict confidence. Obligations survive termination for {random_days(3,7)} years.", S['Clause']))

    s.append(Paragraph("SECTION 7: DATA PROTECTION", S['H1']))
    s.append(Paragraph(
        f"7.1 <b>Compliance.</b> Both parties shall comply with GDPR, UK GDPR, CCPA, and all "
        f"applicable data protection laws in jurisdictions where services are delivered.", S['Clause']))
    s.append(Paragraph(
        f"7.2 <b>Breach Notification. [OBLIGATION — DEADLINE]</b> Service Provider shall notify "
        f"Client within <b>{BREACH_HOURS} hours</b> of becoming aware of a personal data breach.", S['Clause']))

    s.append(Paragraph("SECTION 8: GOVERNING LAW", S['H1']))
    s.append(Paragraph(
        f"8.1 <b>[CONFLICT POINT C6]</b> This Agreement shall be governed by the laws of the "
        f"<b>{MSA_LAW}</b>. Disputes shall first go to 30-day negotiation, then binding arbitration.", S['Clause']))

    s.append(Paragraph("SECTION 9: INTELLECTUAL PROPERTY", S['H1']))
    s.append(Paragraph(
        f"9.1 Deliverables created under this Agreement shall be works-for-hire with ownership "
        f"vesting in Client upon full payment. Service Provider retains pre-existing IP rights.", S['Clause']))

    s.append(Spacer(1,20)); s.append(divider())
    s.append(Paragraph("SIGNATURE PAGE", S['H1']))
    s.append(sig_block())
    s.append(Spacer(1,8))
    s.append(Paragraph(f"CONFIDENTIAL | {MSA_ID} | {PARTY_A} & {PARTY_B}", S['Footer']))
    build(f"{OUTPUT_DIR}/01_MSA.pdf", s)

# ─────────────────────────────────────────────────────────────
# 2. SOW 1 — Cloud / Infrastructure Migration
# ─────────────────────────────────────────────────────────────
def gen_sow1():
    s = []
    service_types = ["Cloud Infrastructure Migration", "Data Centre Consolidation",
                     "Hybrid Cloud Transformation", "Multi-Cloud Modernisation",
                     "Legacy System Re-platforming"]
    service_name = random.choice(service_types)

    s.append(Paragraph(f"STATEMENT OF WORK — NO. 1", S['DocTitle']))
    s.append(Paragraph(f"{service_name} | {SOW1_ID}", S['SubTitle']))
    s.append(Spacer(1,8))
    s.append(hdr("Statement of Work", SOW1_ID, SOW1_DATE, [PARTY_A, PARTY_B]))
    s.append(Spacer(1,10)); s.append(divider())

    s.append(Paragraph("1. BACKGROUND", S['H1']))
    s.append(Paragraph(
        f"This Statement of Work (\"{SOW1_ID}\") is issued pursuant to {MSA_ID} dated "
        f"{fmt_date(MSA_DATE)}. It governs {service_name} services for {PARTY_B}'s "
        f"infrastructure across its operational territories.", S['Body']))

    s.append(Paragraph("2. SCOPE OF WORK", S['H1']))
    phases = [
        (f"Phase 1 — Assessment & Planning ({fmt_date(SOW1_DATE)} to {fmt_date(SOW1_MILESTONES[0])})",
         f"Conduct infrastructure discovery, assess cloud readiness for {APP_COUNT} applications "
         f"and {DB_COUNT} databases, and deliver a Migration Strategy Document."),
        (f"Phase 2 — Migration Execution ({fmt_date(SOW1_MILESTONES[0])} to {fmt_date(SOW1_MILESTONES[2])})",
         f"Execute migration of all {APP_COUNT} identified applications. Configure VPCs, IAM "
         f"policies, security groups, and automated monitoring dashboards."),
        (f"Phase 3 — Stabilisation & Handover ({fmt_date(SOW1_MILESTONES[2])} to {fmt_date(SOW1_MILESTONES[4])})",
         f"Post-migration performance tuning, knowledge transfer, runbook creation, and sign-off."),
    ]
    for title, desc in phases:
        s.append(Paragraph(f"<b>{title}:</b> {desc}", S['Clause']))

    s.append(Paragraph("3. MILESTONES & PAYMENT SCHEDULE", S['H1']))
    m_labels = ["Infrastructure Assessment Report", "Migration Architecture Blueprint",
                "Phase 1 Migration Complete", "Phase 2 Migration Complete",
                "Stabilisation & Final Sign-off"]
    m_data = [["Milestone", "Deliverable", "Due Date", "Fee (USD)"]]
    for i, (lbl, dt, amt) in enumerate(zip(m_labels, SOW1_MILESTONES, SOW1_PARTS)):
        m_data.append([f"M{i+1}", lbl, fmt_date(dt), f"${amt:,}"])
    m_data.append(["", "TOTAL CONTRACT VALUE", "", f"${SOW1_TOTAL:,}"])
    s.append(tbl(m_data, [0.6*inch, 2.7*inch, 1.6*inch, 1.3*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("4. SERVICE LEVEL COMMITMENTS", S['H1']))
    s.append(Paragraph(
        f"4.1 <b>Post-Migration Uptime. [OBLIGATION — CONFLICT POINT C2]</b> Following each "
        f"migration phase, Service Provider guarantees post-migration availability of "
        f"<b>{SLA_UPTIME}%</b> for a {random_days(20,40)}-day stabilisation period.", S['Clause']))
    s.append(Paragraph(
        f"4.2 <b>Data Integrity. [OBLIGATION]</b> Service Provider shall validate 100% data "
        f"integrity using automated checksums. Data loss exceeding 0.001% of total records "
        f"is a critical incident requiring immediate escalation.", S['Clause']))
    s.append(Paragraph(
        f"4.3 <b>Migration Windows.</b> All production cutovers must complete within "
        f"{random_days(4,8)}-hour maintenance windows. Overruns trigger automatic rollback.", S['Clause']))

    s.append(Paragraph("5. LIABILITY CAP (SOW-SPECIFIC)", S['H1']))
    s.append(Paragraph(
        f"5.1 <b>[OBLIGATION — CONFLICT POINT C1]</b> Notwithstanding Section 5.1 of {MSA_ID}, "
        f"Service Provider's aggregate liability under this SOW for data loss, migration failure, "
        f"or system unavailability shall not exceed <b>USD {SOW1_LIABILITY:,}</b>, reflecting "
        f"the elevated risk profile of production migration activities.", S['Clause']))

    s.append(Paragraph("6. PENALTY CLAUSE", S['H1']))
    s.append(Paragraph(
        f"6.1 <b>[OBLIGATION — CONFLICT POINT C5]</b> Milestone delays without approved "
        f"extensions incur a penalty of 0.5% of the milestone value per week of delay, "
        f"up to a maximum of <b>{MSA_PENALTY}%</b> of the total SOW value.", S['Clause']))

    s.append(Paragraph("7. KEY PERSONNEL", S['H1']))
    roles = [
        ("Programme Director", PROG_DIRECTOR, "100%"),
        ("Cloud Architect", CLOUD_ARCH1, "100%"),
        ("Cloud Architect", CLOUD_ARCH2, "100%"),
        ("DevOps Lead", DEVOPS_LEAD, "100%"),
        ("Security Specialist", SECURITY_SPEC, f"{random.choice([50,75,100])}%"),
        ("QA Lead", QA_LEAD, "100%"),
    ]
    r_data = [["Role", "Name", "Allocation"]]
    for role, name, alloc in roles:
        r_data.append([role, name, alloc])
    s.append(tbl(r_data, [2*inch, 2.5*inch, 1.7*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("8. COMPLIANCE REQUIREMENTS", S['H1']))
    s.append(Paragraph(
        f"8.1 <b>[OBLIGATION]</b> All infrastructure deployed under this SOW must comply with "
        f"{', '.join(FRAMEWORKS)}. Compliance evidence must be submitted within "
        f"{random_days(20,40)} days of each phase completion.", S['Clause']))

    s.append(Spacer(1,20)); s.append(divider())
    s.append(Paragraph("SIGNATURE PAGE", S['H1']))
    s.append(sig_block())
    s.append(Spacer(1,8))
    s.append(Paragraph(f"CONFIDENTIAL | {SOW1_ID} | Issued under {MSA_ID}", S['Footer']))
    build(f"{OUTPUT_DIR}/02_SOW1.pdf", s)

# ─────────────────────────────────────────────────────────────
# 3. SOW 2 — Data / Analytics / AI Platform
# ─────────────────────────────────────────────────────────────
def gen_sow2():
    s = []
    platform_types = [
        "Enterprise Data Analytics & AI Platform",
        "Real-Time Business Intelligence Platform",
        "Enterprise Data Lakehouse & ML Platform",
        "Predictive Analytics & Reporting Platform",
    ]
    platform_name = random.choice(platform_types)

    s.append(Paragraph("STATEMENT OF WORK — NO. 2", S['DocTitle']))
    s.append(Paragraph(f"{platform_name} | {SOW2_ID}", S['SubTitle']))
    s.append(Spacer(1,8))
    s.append(hdr("Statement of Work", SOW2_ID, SOW2_DATE, [PARTY_A, PARTY_B]))
    s.append(Spacer(1,10)); s.append(divider())

    s.append(Paragraph("1. BACKGROUND", S['H1']))
    sources = random.randint(5, 12)
    s.append(Paragraph(
        f"This SOW ({SOW2_ID}) is issued under {MSA_ID}. It governs design, development, "
        f"and deployment of a {platform_name} for {PARTY_B}, consolidating data from "
        f"{sources} source systems across its global operations.", S['Body']))

    s.append(Paragraph("2. TECHNICAL SCOPE", S['H1']))
    ml_models = random.randint(3, 6)
    dashboards = DASH_COUNT
    for item in [
        ("<b>Data Ingestion:</b>", f"Streaming and batch pipelines ingesting from {sources} source systems including ERP, CRM, and proprietary applications."),
        ("<b>Data Lake & Warehouse:</b>", "Cloud-based data lake with warehousing layer. Medallion architecture (Bronze/Silver/Gold) for data quality tiering."),
        (f"<b>Analytics ({dashboards} dashboards):</b>", f"Delivery of {dashboards} pre-defined analytical dashboards covering Finance, Operations, HR, and CX domains."),
        (f"<b>AI/ML Models ({ml_models} models):</b>", f"Development and deployment of {ml_models} predictive models including demand forecasting, churn prediction, and risk scoring."),
        ("<b>Data Governance:</b>", "Data catalog, lineage tracking, data quality monitoring, and access control implementation."),
    ]:
        s.append(Paragraph(f"{item[0]} {item[1]}", S['Clause']))

    s.append(Paragraph("3. MILESTONES & PAYMENT SCHEDULE", S['H1']))
    m_labels2 = ["Data Architecture Design", "Ingestion Pipelines Live",
                 "Data Warehouse Operational", f"Dashboards ({dashboards}) Delivered",
                 f"AI/ML Models ({ml_models}) Deployed", "Governance Framework Live"]
    m_data2 = [["Milestone", "Deliverable", "Due Date", "Fee (USD)"]]
    for i, (lbl, dt, amt) in enumerate(zip(m_labels2, SOW2_MILESTONES, SOW2_PARTS)):
        m_data2.append([f"DAP-M{i+1}", lbl, fmt_date(dt), f"${amt:,}"])
    m_data2.append(["", "TOTAL CONTRACT VALUE", "", f"${SOW2_TOTAL:,}"])
    s.append(tbl(m_data2, [0.7*inch, 2.5*inch, 1.6*inch, 1.4*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("4. PAYMENT TERMS (SOW-SPECIFIC)", S['H1']))
    s.append(Paragraph(
        f"4.1 <b>[OBLIGATION — CONFLICT POINT C3]</b> Notwithstanding Section 3.2 of {MSA_ID} "
        f"which specifies Net-{MSA_NET} payment terms, milestone payments under this SOW "
        f"shall be due within <b>{SOW2_NET} days (Net-{SOW2_NET})</b> of written milestone "
        f"acceptance, reflecting the higher resource intensity of AI/ML development.", S['Clause']))

    s.append(Paragraph("5. PERFORMANCE STANDARDS", S['H1']))
    mape = round(random.uniform(8, 15), 1)
    auc  = round(random.uniform(0.78, 0.88), 2)
    f1   = round(random.uniform(0.72, 0.82), 2)
    s.append(Paragraph(
        f"5.1 <b>Platform Availability:</b> {platform_name} shall maintain uptime of "
        f"{round(random.uniform(99.0, 99.8), 1)}% during business hours.", S['Clause']))
    s.append(Paragraph(
        f"5.2 <b>Data Freshness. [OBLIGATION]</b> Streaming data must appear in dashboards "
        f"within {random_days(3,8)} minutes. Batch data refreshed by 06:00 local time daily.", S['Clause']))
    s.append(Paragraph(
        f"5.3 <b>Model Accuracy. [OBLIGATION]</b> AI/ML models must achieve: "
        f"Demand Forecasting (MAPE &lt; {mape}%), Churn Prediction (AUC-ROC &gt; {auc}), "
        f"Risk Scoring (F1-score &gt; {f1}).", S['Clause']))

    s.append(Paragraph("6. GOVERNING LAW (SOW-SPECIFIC)", S['H1']))
    s.append(Paragraph(
        f"6.1 <b>[CONFLICT POINT C6]</b> Notwithstanding Section 8.1 of {MSA_ID} which "
        f"specifies {MSA_LAW}, disputes under this SOW shall be governed by the laws of "
        f"<b>{SOW2_LAW}</b>, given the AI/ML components being developed in Service Provider's "
        f"engineering centre within that jurisdiction.", S['Clause']))

    s.append(Paragraph("7. DATA AND AI OBLIGATIONS", S['H1']))
    s.append(Paragraph(
        f"7.1 <b>[OBLIGATION]</b> All production data used in model training must be "
        f"anonymised per GDPR Article 4(5) before processing. Anonymisation logs must "
        f"be maintained and accessible to Client.", S['Clause']))
    s.append(Paragraph(
        f"7.2 <b>[OBLIGATION — DEADLINE]</b> A Data Protection Impact Assessment (DPIA) "
        f"for AI/ML components must be delivered at least {random_days(20,40)} days before "
        f"any production deployment of model scoring pipelines.", S['Clause']))

    s.append(Spacer(1,20)); s.append(divider())
    s.append(Paragraph("SIGNATURE PAGE", S['H1']))
    s.append(sig_block())
    s.append(Spacer(1,8))
    s.append(Paragraph(f"CONFIDENTIAL | {SOW2_ID} | Issued under {MSA_ID}", S['Footer']))
    build(f"{OUTPUT_DIR}/03_SOW2.pdf", s)

# ─────────────────────────────────────────────────────────────
# 4. SERVICE LEVEL AGREEMENT
# ─────────────────────────────────────────────────────────────
def gen_sla():
    s = []
    s.append(Paragraph("SERVICE LEVEL AGREEMENT", S['DocTitle']))
    s.append(Paragraph(f"{SLA_ID} | Governed by {MSA_ID}", S['SubTitle']))
    s.append(Spacer(1,8))
    s.append(hdr("Service Level Agreement", SLA_ID, SLA_DATE, [PARTY_A, PARTY_B]))
    s.append(Spacer(1,10)); s.append(divider())

    s.append(Paragraph("1. PURPOSE", S['H1']))
    s.append(Paragraph(
        f"This SLA ({SLA_ID}) defines performance commitments applicable to services under "
        f"{MSA_ID}. To the extent of inconsistency, this SLA governs service performance "
        f"measurement and credit calculations.", S['Body']))

    s.append(Paragraph("2. AVAILABILITY COMMITMENTS", S['H1']))
    s.append(Paragraph(
        f"2.1 <b>Core Platform Uptime. [OBLIGATION — CONFLICT POINT C2]</b> Service Provider "
        f"commits to core platform availability of <b>{SLA_UPTIME}%</b> on a rolling monthly "
        f"basis. Maximum permitted downtime: "
        f"{round((1 - SLA_UPTIME/100)*30*24*60, 1)} minutes/month.", S['Clause']))

    tier2 = round(SLA_UPTIME - random.uniform(0.3, 0.5), 1)
    tier3 = round(tier2 - random.uniform(0.4, 0.6), 1)
    sla_tbl = [
        ["Service Tier", "Target", "Max Monthly Downtime", "Window"],
        ["Tier 1 — Critical",     f"{SLA_UPTIME}%", f"{round((1-SLA_UPTIME/100)*30*24*60,1)} min", "24x7"],
        ["Tier 2 — Business",     f"{tier2}%",      f"{round((1-tier2/100)*30*24*60/60,2)} hrs",   "Biz Hours"],
        ["Tier 3 — Analytics",    f"{tier3}%",      f"{round((1-tier3/100)*30*24*60/60,2)} hrs",   "Biz Hours"],
        ["Tier 4 — Dev/Test",     "95.0%",          "36.5 hrs",                                     "Biz Hours"],
    ]
    s.append(tbl(sla_tbl, [1.9*inch, 1.1*inch, 1.9*inch, 1.3*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("3. INCIDENT RESPONSE MATRIX", S['H1']))
    inc_tbl = [
        ["Priority", "Definition", "Response", "Resolution"],
        ["P1 — Critical", "Complete outage or data loss",          f"{P1_RESPONSE_MIN} min",   f"{P1_RESOLUTION_HR} hrs"],
        ["P2 — High",     "Major feature down, no workaround",     f"{P1_RESPONSE_MIN*4} min", f"{P1_RESOLUTION_HR*2} hrs"],
        ["P3 — Medium",   "Partial degradation, workaround exists",f"{P1_RESPONSE_MIN*16} min",f"{random_days(1,3)} days"],
        ["P4 — Low",      "Minor, no business impact",             f"{random_days(1,2)} day",  f"{random_days(5,14)} days"],
    ]
    s.append(tbl(inc_tbl, [1.1*inch, 2.3*inch, 1.1*inch, 1.3*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("4. SERVICE CREDITS", S['H1']))
    s.append(Paragraph(
        f"4.1 <b>[OBLIGATION — CONFLICT POINT C5]</b> Uptime failures entitle Client to "
        f"credits up to a maximum of <b>{SLA_PENALTY}%</b> of the monthly Tier 1 service fee.", S['Clause']))
    credit_tbl = [
        ["Availability Achieved", "Credit (% of Monthly Fee)"],
        [f"{round(SLA_UPTIME-1,1)}% – {round(SLA_UPTIME-0.01,2)}%", f"{round(SLA_PENALTY*0.3)}%"],
        [f"{round(SLA_UPTIME-4,1)}% – {round(SLA_UPTIME-1.01,2)}%", f"{round(SLA_PENALTY*0.65)}%"],
        [f"Below {round(SLA_UPTIME-4,1)}%", f"{SLA_PENALTY}% + termination right"],
    ]
    s.append(tbl(credit_tbl, [3.2*inch, 3*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("5. REPORTING OBLIGATIONS", S['H1']))
    s.append(Paragraph(
        f"5.1 <b>[OBLIGATION]</b> Monthly SLA Performance Report due by the "
        f"{random.choice(['3rd','5th','7th'])} business day of the following month. Must include "
        f"uptime per tier, incident log, credit calculation, and 3-month trend analysis.", S['Clause']))
    s.append(Paragraph(
        f"5.2 <b>[OBLIGATION — DEADLINE]</b> P1 Preliminary RCA within {random_days(18,36)} hours "
        f"of resolution. Final detailed RCA within {random_days(3,7)} business days.", S['Clause']))
    s.append(Paragraph(
        f"5.3 <b>[OBLIGATION]</b> Quarterly Business Review (QBR) within {random_days(10,20)} "
        f"business days of each quarter-end.", S['Clause']))

    s.append(Spacer(1,20)); s.append(divider())
    s.append(Paragraph("SIGNATURE PAGE", S['H1']))
    s.append(sig_block())
    s.append(Spacer(1,8))
    s.append(Paragraph(f"CONFIDENTIAL | {SLA_ID} | Governed by {MSA_ID}", S['Footer']))
    build(f"{OUTPUT_DIR}/04_SLA.pdf", s)

# ─────────────────────────────────────────────────────────────
# 5. DATA PROCESSING AGREEMENT
# ─────────────────────────────────────────────────────────────
def gen_dpa():
    s = []
    s.append(Paragraph("DATA PROCESSING AGREEMENT", S['DocTitle']))
    s.append(Paragraph(f"{DPA_ID} | GDPR Article 28 Compliant", S['SubTitle']))
    s.append(Spacer(1,8))
    s.append(hdr("Data Processing Agreement", DPA_ID, DPA_DATE,
                 [f"{PARTY_A} (Data Processor)", f"{PARTY_B} (Data Controller)"]))
    s.append(Spacer(1,10)); s.append(divider())

    s.append(Paragraph("1. BACKGROUND", S['H1']))
    s.append(Paragraph(
        f"This DPA ({DPA_ID}) is entered into pursuant to GDPR Article 28 and governs all "
        f"personal data processing by {PARTY_A} (Processor) on behalf of {PARTY_B} "
        f"(Controller) under {MSA_ID} and associated SOWs.", S['Body']))

    s.append(Paragraph("2. PROCESSOR OBLIGATIONS", S['H1']))
    obligations = [
        ("<b>[OBLIGATION]</b> Process Personal Data only on documented instructions from Controller.",
         ""),
        ("<b>[OBLIGATION]</b> Ensure all personnel authorised to process Personal Data are bound by confidentiality obligations.",
         ""),
        (f"<b>Security. [OBLIGATION]</b> Implement: AES-256 encryption at rest, TLS 1.3 in transit, RBAC, MFA for privileged access, and annual penetration testing.",
         ""),
        (f"<b>Breach Notification. [OBLIGATION — DEADLINE]</b> Notify Controller within <b>{BREACH_HOURS} hours</b> of becoming aware of a personal data breach, including nature, categories affected, and remediation steps.",
         ""),
        (f"<b>Data Subject Rights. [OBLIGATION]</b> Assist Controller in fulfilling data subject rights requests within {random_days(7,15)} business days.",
         ""),
    ]
    for ob, _ in obligations:
        s.append(Paragraph(ob, S['Clause']))

    s.append(Paragraph("3. DATA RETENTION AND DELETION", S['H1']))
    s.append(Paragraph(
        f"3.1 <b>[OBLIGATION — CONFLICT POINT C4]</b> Upon contract termination, Processor "
        f"shall retain Personal Data for no more than <b>{DPA_RETENTION} months</b> for audit "
        f"and legal compliance purposes, then securely delete or return all Personal Data.", S['Clause']))
    s.append(Paragraph(
        f"3.2 <b>[OBLIGATION]</b> Deletion Certificate to be provided within {random_days(20,40)} "
        f"days of deletion completion.", S['Clause']))
    s.append(Paragraph(
        f"3.3 <b>[OBLIGATION]</b> Personal Data purged from all backup systems within "
        f"{random_days(60,120)} days of primary deletion.", S['Clause']))

    s.append(Paragraph("4. SUB-PROCESSORS", S['H1']))
    cloud_providers = random.sample([
        ("Amazon Web Services", "Ireland/UK", "Cloud Infrastructure"),
        ("Microsoft Azure", "Netherlands/UK", "Secondary Cloud & DevOps"),
        ("Google Cloud Platform", "Belgium", "ML Infrastructure"),
        ("Snowflake Inc.", "Ireland", "Data Warehousing"),
        ("Datadog Inc.", "EU Region", "Monitoring & Observability"),
        ("Elastic NV", "Netherlands", "Search & Logging"),
    ], 4)
    s.append(Paragraph(
        f"4.1 <b>[OBLIGATION]</b> Processor shall not engage new sub-processors without "
        f"{random_days(20,40)} days prior written notice to Controller.", S['Clause']))
    sp_data = [["Sub-Processor", "Location", "Purpose", "GDPR Mechanism"]]
    for name, loc, purpose in cloud_providers:
        sp_data.append([name, loc, purpose, "Standard Contractual Clauses"])
    s.append(tbl(sp_data, [1.6*inch, 1.3*inch, 1.8*inch, 1.5*inch]))
    s.append(Spacer(1,8))

    s.append(Paragraph("5. AUDIT RIGHTS", S['H1']))
    s.append(Paragraph(
        f"5.1 <b>[OBLIGATION]</b> Processor shall allow Controller or designated auditor to "
        f"conduct audits with {random_days(20,45)} days written notice and cooperate fully.", S['Clause']))
    s.append(Paragraph(
        f"5.2 <b>[OBLIGATION]</b> Processor shall provide annual {', '.join(FRAMEWORKS[:2])} "
        f"audit reports and within {random_days(7,15)} business days of any significant findings.", S['Clause']))

    s.append(Spacer(1,20)); s.append(divider())
    s.append(Paragraph("SIGNATURE PAGE", S['H1']))
    s.append(sig_block())
    s.append(Spacer(1,8))
    s.append(Paragraph(f"CONFIDENTIAL | {DPA_ID} | GDPR Article 28 | Under {MSA_ID}", S['Footer']))
    build(f"{OUTPUT_DIR}/05_DPA.pdf", s)

# ─────────────────────────────────────────────────────────────
# 6. AMENDMENT NO. 1
# ─────────────────────────────────────────────────────────────
def gen_amendment():
    s = []
    s.append(Paragraph(f"AMENDMENT NO. 1 TO MASTER SERVICE AGREEMENT", S['DocTitle']))
    s.append(Paragraph(f"{AMD_ID} | Amending {MSA_ID}", S['SubTitle']))
    s.append(Spacer(1,8))
    s.append(hdr("Amendment to MSA", AMD_ID, AMD_DATE, [PARTY_A, PARTY_B]))
    s.append(Spacer(1,10)); s.append(divider())

    new_regions = random.sample(["Australia", "Japan", "Brazil", "UAE", "South Africa",
                                 "Canada", "Mexico", "South Korea"], 2)
    new_law = random.choice(["Australian Privacy Act 1988", "PDPA (Singapore)",
                             "LGPD (Brazil)", "PIPL (China)", "APPI (Japan)"])
    pci_deadline = AMD_DATE + timedelta(days=random.randint(90, 180))
    iso_deadline = AMD_DATE + timedelta(days=random.randint(150, 270))
    bcp_deadline = AMD_DATE + timedelta(days=random.randint(30, 60))
    ins_deadline = AMD_DATE + timedelta(days=random.randint(10, 20))

    s.append(Paragraph("BACKGROUND", S['H1']))
    s.append(Paragraph(
        f"This Amendment ({AMD_ID}) is dated {fmt_date(AMD_DATE)} and amends {MSA_ID}. "
        f"All capitalised terms retain their meaning from the MSA. All other terms remain "
        f"in full force except as expressly modified herein.", S['Body']))

    s.append(Paragraph("AMENDMENT 1: EXPANDED GEOGRAPHIC COVERAGE", S['H1']))
    s.append(Paragraph(
        f"1.1 <b>[OBLIGATION]</b> {PARTY_A} shall ensure compliance with {new_law} and all "
        f"applicable privacy legislation in {' and '.join(new_regions)} within "
        f"{random_days(45,75)} days of this Amendment's effective date.", S['Clause']))

    s.append(Paragraph("AMENDMENT 2: DATA RETENTION PERIOD", S['H1']))
    s.append(Paragraph(
        f"2.1 <b>[OBLIGATION — CONFLICT POINT C4]</b> Section 3.1 of {DPA_ID} is hereby "
        f"amended. The post-termination data retention period is extended from "
        f"<b>{DPA_RETENTION} months</b> to <b>{AMD_RETENTION} months</b> to comply with "
        f"mandatory retention requirements in {' and '.join(new_regions)}.", S['Clause']))
    s.append(Paragraph(
        f"2.2 {PARTY_A} shall update all data retention schedules within "
        f"{random_days(20,35)} days of this Amendment's effective date.", S['Clause']))

    s.append(Paragraph("AMENDMENT 3: INSURANCE REQUIREMENTS", S['H1']))
    ins_data = [
        ["Insurance Type",                "Minimum Coverage",           "Effective Date"],
        ["Professional Indemnity (E&O)",  f"USD {random.randrange(3,8)}M/occurrence", fmt_date(ins_deadline)],
        ["Cyber Liability",               f"USD {random.randrange(8,15)}M/occurrence",fmt_date(ins_deadline)],
        ["General Liability",             f"USD {random.randrange(1,4)}M/occurrence", fmt_date(ins_deadline)],
        ["Workers Compensation",          "Statutory limits per jurisdiction",         "Immediately"],
    ]
    s.append(tbl(ins_data, [2.2*inch, 2.5*inch, 1.5*inch]))
    s.append(Spacer(1,8))
    s.append(Paragraph(
        f"3.1 <b>[OBLIGATION — DEADLINE]</b> Certificates of insurance naming {PARTY_B} as "
        f"additional insured must be provided by {fmt_date(ins_deadline)}.", S['Clause']))

    s.append(Paragraph("AMENDMENT 4: MODIFIED RENEWAL NOTICE PERIOD", S['H1']))
    s.append(Paragraph(
        f"4.1 <b>[OBLIGATION — CONFLICT POINT C7]</b> Section 2.2 of {MSA_ID} is amended. "
        f"The non-renewal notice period is extended from <b>{MSA_NOTICE} days</b> to "
        f"<b>{AMD_NOTICE} days</b> given expanded geographic scope. "
        f"<b>Updated renewal notice deadline: {fmt_date(AMD_RENEWAL_DEADLINE)}.</b>", S['Clause']))

    s.append(Paragraph("AMENDMENT 5: ADDITIONAL COMPLIANCE CERTIFICATIONS", S['H1']))
    s.append(Paragraph(
        f"5.1 <b>[OBLIGATION — DEADLINE]</b> {PARTY_A} shall obtain PCI DSS Level 1 "
        f"compliance by <b>{fmt_date(pci_deadline)}</b> and {FRAMEWORKS[2]} certification "
        f"by <b>{fmt_date(iso_deadline)}</b>.", S['Clause']))

    s.append(Paragraph("AMENDMENT 6: BUSINESS CONTINUITY", S['H1']))
    rto = random.choice([2, 4, 6, 8])
    rpo = random.choice([1, 2, 4])
    s.append(Paragraph(
        f"6.1 <b>[OBLIGATION — DEADLINE]</b> A Business Continuity Plan (BCP) and Disaster "
        f"Recovery Plan (DRP) must be submitted by <b>{fmt_date(bcp_deadline)}</b>.", S['Clause']))
    s.append(Paragraph(
        f"6.2 <b>[OBLIGATION]</b> Annual DR test required. Tier 1 systems: "
        f"RTO &lt;= {rto} hours, RPO &lt;= {rpo} hour(s).", S['Clause']))

    s.append(Paragraph("PRECEDENCE", S['H1']))
    s.append(Paragraph(
        f"In the event of conflict between this Amendment and {MSA_ID} or any SOW or DPA, "
        f"this Amendment prevails to the extent of the inconsistency, unless a specific SOW "
        f"expressly states its provisions take precedence.", S['Body']))

    s.append(Spacer(1,20)); s.append(divider())
    s.append(Paragraph("SIGNATURE PAGE", S['H1']))
    s.append(sig_block())
    s.append(Spacer(1,8))
    s.append(Paragraph(f"CONFIDENTIAL | {AMD_ID} | Amends {MSA_ID} | Executed {fmt_date(AMD_DATE)}", S['Footer']))
    build(f"{OUTPUT_DIR}/06_AMD1.pdf", s)

# ─────────────────────────────────────────────────────────────
# 7. CONFLICT REFERENCE (dev only)
# ─────────────────────────────────────────────────────────────
def gen_conflict_ref():
    s = []
    s.append(Paragraph("DEVELOPER CONFLICT REFERENCE", S['DocTitle']))
    s.append(Paragraph("Ground Truth for Conflict Detection Testing — DO NOT SUBMIT", S['SubTitle']))
    s.append(Spacer(1,8)); s.append(divider())
    s.append(Paragraph(f"Run ID: {RUN_ID}  |  Companies: {PARTY_A}  vs  {PARTY_B}", S['Body']))
    s.append(Spacer(1,8))

    conflicts = [
        ("C1", "Liability Cap",
         f"{MSA_ID} §5.1",  f"USD {MSA_LIABILITY:,}",
         f"{SOW1_ID} §5.1", f"USD {SOW1_LIABILITY:,}",
         "SOW1 claims elevated migration risk justifies higher cap."),
        ("C2", "Uptime Target",
         f"{MSA_ID} §4.1",  f"{MSA_UPTIME}%",
         f"{SLA_ID} §2.1 / {SOW1_ID} §4.1", f"{SLA_UPTIME}%",
         "SLA and SOW1 impose stricter uptime than MSA baseline."),
        ("C3", "Payment Terms",
         f"{MSA_ID} §3.2",  f"Net-{MSA_NET}",
         f"{SOW2_ID} §4.1", f"Net-{SOW2_NET}",
         "SOW2 explicitly overrides MSA payment period."),
        ("C4", "Data Retention",
         f"{DPA_ID} §3.1",  f"{DPA_RETENTION} months",
         f"{AMD_ID} §2.1",  f"{AMD_RETENTION} months",
         "Amendment extends retention. Amendment prevails but creates inconsistency."),
        ("C5", "Penalty / Credit Cap",
         f"{MSA_ID} §4.2",  f"{MSA_PENALTY}%",
         f"{SLA_ID} §4.1",  f"{SLA_PENALTY}%",
         "SLA allows higher credit cap than MSA baseline."),
        ("C6", "Governing Law",
         f"{MSA_ID} §8.1",  MSA_LAW,
         f"{SOW2_ID} §6.1", SOW2_LAW,
         "SOW2 claims different jurisdiction for AI/ML disputes."),
        ("C7", "Renewal Notice Period",
         f"{MSA_ID} §2.2",  f"{MSA_NOTICE} days → deadline {fmt_date(MSA_RENEWAL_DEADLINE)}",
         f"{AMD_ID} §4.1",  f"{AMD_NOTICE} days → deadline {fmt_date(AMD_RENEWAL_DEADLINE)}",
         "Amendment extended the notice period — earlier action now required."),
    ]

    for cid, ctype, d1, v1, d2, v2, note in conflicts:
        s.append(Paragraph(f"{cid}: {ctype}", S['H2']))
        c_data = [
            [Paragraph("<b>Document</b>", S['Body']), Paragraph("<b>Value</b>", S['Body'])],
            [Paragraph(d1, S['Body']),                Paragraph(f"<b>{v1}</b>", S['Body'])],
            [Paragraph(d2, S['Body']),                Paragraph(f"<b>{v2}</b>", S['Conflict'])],
            [Paragraph("<i>Note</i>", S['Body']),     Paragraph(f"<i>{note}</i>", S['Body'])],
        ]
        ct = Table(c_data, colWidths=[2.8*inch, 4.4*inch])
        ct.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR',(0,0),(-1,0),  colors.white),
            ('BACKGROUND',(0,3),(-1,3), colors.HexColor('#fff9e6')),
            ('GRID',(0,0),(-1,-1), 0.5, colors.HexColor('#cccccc')),
            ('PADDING',(0,0),(-1,-1), 6),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
        ]))
        s.append(ct)
        s.append(Spacer(1, 8))

    build(f"{OUTPUT_DIR}/00_CONFLICT_REFERENCE.pdf", s)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'='*58}")
    print(f"  ContractIQ — Randomized Contract Generator")
    print(f"  Run ID : {RUN_ID}")
    print(f"  Folder : {OUTPUT_DIR}/")
    print(f"{'='*58}")
    print(f"  Party A : {PARTY_A}")
    print(f"  Party B : {PARTY_B}")
    print(f"  MSA ID  : {MSA_ID}")
    print(f"{'='*58}\n")

    gen_msa()
    gen_sow1()
    gen_sow2()
    gen_sla()
    gen_dpa()
    gen_amendment()
    gen_conflict_ref()

    print(f"\n{'='*58}")
    print("  CONFLICTS BAKED IN THIS RUN:")
    print(f"  C1 Liability : MSA=USD {MSA_LIABILITY:,}  vs  SOW1=USD {SOW1_LIABILITY:,}")
    print(f"  C2 Uptime    : MSA={MSA_UPTIME}%  vs  SLA/SOW1={SLA_UPTIME}%")
    print(f"  C3 Payment   : MSA=Net-{MSA_NET}  vs  SOW2=Net-{SOW2_NET}")
    print(f"  C4 Retention : DPA={DPA_RETENTION}mo  vs  Amendment={AMD_RETENTION}mo")
    print(f"  C5 Penalty   : MSA={MSA_PENALTY}%  vs  SLA={SLA_PENALTY}%")
    print(f"  C6 Law       : MSA={MSA_LAW}")
    print(f"              vs  SOW2={SOW2_LAW}")
    print(f"  C7 Renewal   : MSA={MSA_NOTICE}d ({fmt_date(MSA_RENEWAL_DEADLINE)})")
    print(f"              vs  AMD={AMD_NOTICE}d ({fmt_date(AMD_RENEWAL_DEADLINE)})")
    print(f"{'='*58}\n")
