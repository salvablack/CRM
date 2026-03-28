"""
LeadPro CRM — Streamlit
Captación y Seguimiento de Leads con PDF Reporting
Diseño: dark blue (#0f172a) con cyan/verde (#00d4ff / #00ffaa)
"""

import streamlit as st
import sqlite3
import os
import io
import csv
from datetime import datetime, timedelta

# ── PDF ──────────────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
    _PDF_OK = True
except ImportError:
    _PDF_OK = False

# ── PÁGINA CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LeadPro CRM",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ESTILOS GLOBALES ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Reset global ── */
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif !important; }

/* ── Fondo principal ── */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e2937 100%) !important;
    color: #e2e8f0 !important;
}

/* ── Ocultar elementos de Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }

/* ── Header personalizado ── */
.lp-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1rem 0;
    border-bottom: 1px solid #334155;
    margin-bottom: 1.5rem;
}
.lp-logo {
    font-size: 26px;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #00ffaa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.lp-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #64748b;
}
.lp-dot {
    width: 8px; height: 8px;
    background: #00ffaa;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.lp-user {
    background: #1e2937;
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 13px;
    color: #e2e8f0;
}

/* ── Tabs de navegación ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1e2937 !important;
    border-radius: 9999px !important;
    padding: 6px !important;
    gap: 4px !important;
    border: none !important;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,.3) !important;
    width: fit-content !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 9999px !important;
    padding: 10px 24px !important;
    font-weight: 500 !important;
    border: none !important;
    font-size: 14px !important;
}
.stTabs [aria-selected="true"] {
    background: #00d4ff !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 6px -1px rgba(0,212,255,.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Cards ── */
.lp-card {
    background: #1e2937;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,.3);
    margin-bottom: 1.5rem;
}
.lp-metric {
    background: #1e2937;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid #334155;
}
.lp-metric-val {
    font-size: 30px;
    font-weight: 700;
    line-height: 1;
}
.lp-metric-lbl {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .05em;
    margin-top: 4px;
}

/* ── Inputs ── */
.stTextInput input, .stSelectbox select, .stTextArea textarea,
.stNumberInput input {
    background: #0f172a !important;
    border: 2px solid #334155 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus, .stSelectbox select:focus {
    border-color: #00d4ff !important;
}

/* ── Botones ── */
.stButton > button {
    background: linear-gradient(90deg, #00d4ff, #00ffaa) !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 10px 28px !important;
    font-size: 14px !important;
    transition: transform .2s !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; }

/* Botón secundario */
.btn-secondary > button {
    background: #1e2937 !important;
    color: #00d4ff !important;
    border: 1px solid #334155 !important;
}

/* ── Tabla ── */
.lp-table-wrap { border-radius: 12px; overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th { background: #0f172a !important; color: #94a3b8 !important;
     font-size: 12px !important; text-transform: uppercase; letter-spacing:.05em;
     padding: 12px 14px !important; text-align: left; }
td { padding: 12px 14px !important; border-bottom: 1px solid #1e2937;
     background: #0f172a; color: #e2e8f0; font-size: 14px; }
tr:hover td { background: #1a2540 !important; }

/* ── Badge de estado ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
}

/* ── Kanban ── */
.kanban-col {
    background: #1e2937;
    border-radius: 16px;
    padding: 14px;
    min-height: 200px;
}
.kanban-hdr {
    font-weight: 600;
    font-size: 14px;
    padding-bottom: 10px;
    border-bottom: 3px solid;
    margin-bottom: 12px;
}
.kanban-card {
    background: #0f172a;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all .25s;
}
.kanban-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,212,255,.15);
}

/* ── Historial ── */
.hist-item {
    background: #0f172a;
    border-left: 3px solid #00d4ff;
    padding: 10px 14px;
    border-radius: 0 10px 10px 0;
    margin-bottom: 8px;
    font-size: 13px;
}

/* ── Título de sección ── */
.sec-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 4px;
}
.sec-sub {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 1.5rem;
}

/* Divider */
.lp-divider { border-top: 1px solid #334155; margin: 1rem 0; }

/* Sidebar oculto */
[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── BASE DE DATOS ─────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leadpro.db")

def _db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def _init_db():
    conn = _db(); c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS crm_leads (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT NOT NULL,
        empresa     TEXT DEFAULT '',
        email       TEXT DEFAULT '',
        telefono    TEXT DEFAULT '',
        origen      TEXT DEFAULT 'Manual',
        estado      TEXT DEFAULT 'Nuevo',
        prioridad   TEXT DEFAULT 'Media',
        valor       REAL DEFAULT 0,
        etiquetas   TEXT DEFAULT '',
        notas       TEXT DEFAULT '',
        asignado_a  TEXT DEFAULT '',
        fecha_crea  TEXT,
        fecha_mod   TEXT
    );
    CREATE TABLE IF NOT EXISTS crm_actividades (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id     INTEGER,
        tipo        TEXT,
        descripcion TEXT,
        fecha       TEXT,
        FOREIGN KEY (lead_id) REFERENCES crm_leads(id)
    );
    CREATE TABLE IF NOT EXISTS crm_tareas (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id     INTEGER,
        titulo      TEXT,
        descripcion TEXT DEFAULT '',
        vencimiento TEXT,
        completada  INTEGER DEFAULT 0,
        prioridad   TEXT DEFAULT 'Media',
        fecha_crea  TEXT,
        FOREIGN KEY (lead_id) REFERENCES crm_leads(id)
    );
    """)
    conn.commit(); conn.close()

_init_db()

# ── CONSTANTES ────────────────────────────────────────────────────────────────
ESTADOS    = ["Nuevo","Contactado","Calificado","Propuesta","Negociación","Ganado","Perdido","En espera"]
PRIORIDADES= ["Alta","Media","Baja"]
ORIGENES   = ["Manual","Web","Referido","Redes Sociales","Email","Llamada","Evento","Otro"]
TIPOS_ACT  = ["Llamada","Email","Reunión","Demo","Propuesta","Seguimiento","Nota","Otro"]

ESTADO_COLOR = {
    "Nuevo":"#0ea5e9","Contactado":"#06b6d4","Calificado":"#f59e0b",
    "Propuesta":"#8b5cf6","Negociación":"#ec4899","Ganado":"#00ffaa",
    "Perdido":"#ef4444","En espera":"#64748b",
}
PRIORIDAD_COLOR = {"Alta":"#ef4444","Media":"#f59e0b","Baja":"#00ffaa"}

def _now():  return datetime.now().strftime("%Y-%m-%d %H:%M")
def _today(): return datetime.now().strftime("%Y-%m-%d")
def _fmt_valor(v):
    try:    return f"${float(v or 0):,.2f}"
    except: return "$0.00"

# ── QUERIES ───────────────────────────────────────────────────────────────────
def fetch_leads(search="", estado_f="Todos", prior_f="Todos"):
    conn = _db(); c = conn.cursor()
    q = "SELECT id,nombre,empresa,email,telefono,estado,prioridad,valor,etiquetas,fecha_crea,fecha_mod,asignado_a,origen,notas FROM crm_leads WHERE 1=1"
    p = []
    if search:
        q += " AND (nombre LIKE ? OR empresa LIKE ? OR email LIKE ? OR telefono LIKE ? OR etiquetas LIKE ?)"
        s = f"%{search}%"
        p += [s,s,s,s,s]
    if estado_f != "Todos":
        q += " AND estado=?"; p.append(estado_f)
    if prior_f != "Todos":
        q += " AND prioridad=?"; p.append(prior_f)
    q += " ORDER BY fecha_mod DESC"
    c.execute(q, p)
    rows = c.fetchall(); conn.close()
    return rows

def fetch_lead(lid):
    conn = _db(); c = conn.cursor()
    c.execute("SELECT * FROM crm_leads WHERE id=?", (lid,))
    r = c.fetchone(); conn.close(); return r

def fetch_actividades(lid):
    conn = _db(); c = conn.cursor()
    c.execute("SELECT id,tipo,descripcion,fecha FROM crm_actividades WHERE lead_id=? ORDER BY fecha DESC", (lid,))
    r = c.fetchall(); conn.close(); return r

def fetch_tareas(lid=None, solo_pend=False):
    conn = _db(); c = conn.cursor()
    if lid:
        q = "SELECT t.id,t.titulo,t.descripcion,t.vencimiento,t.completada,t.prioridad,l.nombre FROM crm_tareas t LEFT JOIN crm_leads l ON t.lead_id=l.id WHERE t.lead_id=?"
        p = [lid]
    else:
        q = "SELECT t.id,t.titulo,t.descripcion,t.vencimiento,t.completada,t.prioridad,l.nombre FROM crm_tareas t LEFT JOIN crm_leads l ON t.lead_id=l.id WHERE 1=1"
        p = []
    if solo_pend: q += " AND t.completada=0"
    q += " ORDER BY t.vencimiento ASC NULLS LAST"
    c.execute(q, p); r = c.fetchall(); conn.close(); return r

def stats():
    conn = _db(); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM crm_leads"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM crm_leads WHERE estado='Ganado'"); ganados = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM crm_leads WHERE estado='Perdido'"); perdidos = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(valor),0) FROM crm_leads WHERE estado='Ganado'"); revenue = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(valor),0) FROM crm_leads WHERE estado NOT IN ('Ganado','Perdido')"); pipeline = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM crm_tareas WHERE completada=0"); tareas_p = c.fetchone()[0]
    conn.close()
    tasa = round((ganados / (ganados + perdidos) * 100) if (ganados + perdidos) > 0 else 0, 1)
    return total, ganados, perdidos, revenue, pipeline, tareas_p, tasa

def save_lead(data, lid=None):
    conn = _db(); c = conn.cursor(); now = _now()
    if lid:
        c.execute("""UPDATE crm_leads SET nombre=?,empresa=?,email=?,telefono=?,
                     origen=?,estado=?,prioridad=?,valor=?,etiquetas=?,notas=?,
                     asignado_a=?,fecha_mod=? WHERE id=?""",
                  (*data, now, lid))
        c.execute("INSERT INTO crm_actividades (lead_id,tipo,descripcion,fecha) VALUES (?,?,?,?)",
                  (lid, "Nota", "Registro actualizado", now))
    else:
        c.execute("""INSERT INTO crm_leads (nombre,empresa,email,telefono,origen,estado,
                     prioridad,valor,etiquetas,notas,asignado_a,fecha_crea,fecha_mod)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (*data, now, now))
        lid2 = c.lastrowid
        c.execute("INSERT INTO crm_actividades (lead_id,tipo,descripcion,fecha) VALUES (?,?,?,?)",
                  (lid2, "Nota", "Lead creado", now))
    conn.commit(); conn.close()

def delete_lead(lid):
    conn = _db(); c = conn.cursor()
    c.execute("DELETE FROM crm_actividades WHERE lead_id=?", (lid,))
    c.execute("DELETE FROM crm_tareas WHERE lead_id=?", (lid,))
    c.execute("DELETE FROM crm_leads WHERE id=?", (lid,))
    conn.commit(); conn.close()

def add_actividad(lid, tipo, desc):
    conn = _db(); c = conn.cursor()
    c.execute("INSERT INTO crm_actividades (lead_id,tipo,descripcion,fecha) VALUES (?,?,?,?)",
              (lid, tipo, desc, _now()))
    conn.commit(); conn.close()

def save_tarea(lid, titulo, desc, venc, prio):
    conn = _db(); c = conn.cursor()
    c.execute("INSERT INTO crm_tareas (lead_id,titulo,descripcion,vencimiento,prioridad,fecha_crea) VALUES (?,?,?,?,?,?)",
              (lid, titulo, desc, venc, prio, _now()))
    conn.commit(); conn.close()

def toggle_tarea(tid, val):
    conn = _db(); c = conn.cursor()
    c.execute("UPDATE crm_tareas SET completada=? WHERE id=?", (val, tid))
    conn.commit(); conn.close()

def delete_tarea(tid):
    conn = _db(); c = conn.cursor()
    c.execute("DELETE FROM crm_tareas WHERE id=?", (tid,))
    conn.commit(); conn.close()

# ── PDF BUILDERS ──────────────────────────────────────────────────────────────
def _color(hex_str):
    return colors.HexColor(hex_str)

def build_lead_pdf(lid):
    lead = fetch_lead(lid)
    if not lead: return None
    acts  = fetch_actividades(lid)
    tareas = fetch_tareas(lid)

    buf = io.BytesIO()
    GR10=_color("#1a1a1a"); GR20=_color("#333333"); GR40=_color("#666666")
    GR60=_color("#999999"); GR85=_color("#d9d9d9"); GR95=_color("#f2f2f2")
    WHITE=colors.white; ACC=_color("#444444")

    PW, PH = letter; M = 0.65*inch; W = PW - 2*M

    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=M, rightMargin=M,
                            topMargin=0.5*inch, bottomMargin=0.6*inch,
                            title=f"Ficha Lead — {lead[1]}")
    base = getSampleStyleSheet()
    _nc = [0]
    def _sty(**kw):
        _nc[0] += 1
        return ParagraphStyle(f"s{_nc[0]}", parent=base["Normal"], **kw)

    story = []

    hdr = Table([[
        Paragraph(f"<b>{lead[1].upper()}</b>",
                  _sty(fontName="Helvetica-Bold", fontSize=20, textColor=WHITE, leading=24)),
        Paragraph(f"<b>FICHA DE SEGUIMIENTO</b><br/><font size='9'>{lead[6] or '—'}  ·  {lead[7] or '—'}</font>",
                  _sty(fontName="Helvetica", fontSize=9, textColor=GR85, leading=13, alignment=TA_RIGHT)),
    ]], colWidths=[W*0.65, W*0.35])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),GR10),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LINEBELOW",(0,0),(-1,-1),2,ACC),
    ]))
    story += [hdr, Spacer(1,8)]

    def _info_grid(pairs):
        col_w = W/2
        for i in range(0, len(pairs), 2):
            chunk = pairs[i:i+2]
            while len(chunk) < 2: chunk.append(("",""))
            cells = []
            for lbl, val in chunk:
                cell = Table([
                    [Paragraph(lbl, _sty(fontName="Helvetica-Bold", fontSize=7, textColor=GR60))],
                    [Paragraph(str(val) if val else "—", _sty(fontName="Helvetica", fontSize=8.5, textColor=GR20))],
                ], colWidths=[col_w-12])
                cell.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                                          ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
                cells.append(cell)
            row_t = Table([cells], colWidths=[col_w, col_w])
            row_t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),GR95),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LINEBELOW",(0,0),(-1,-1),0.3,GR85),
                ("BOX",(0,0),(-1,-1),0.5,ACC),
            ]))
            story.append(row_t)
            story.append(Spacer(1,2))

    s_h1 = _sty(fontName="Helvetica-Bold", fontSize=10, textColor=GR10, leading=14, spaceBefore=8, spaceAfter=3)

    story.append(Paragraph("INFORMACIÓN DEL LEAD", s_h1))
    story.append(HRFlowable(width=W, thickness=0.5, color=ACC, spaceAfter=4))
    _info_grid([
        ("NOMBRE", lead[1]),("EMPRESA", lead[2]),
        ("EMAIL", lead[3]),("TELÉFONO", lead[4]),
        ("ESTADO", lead[6]),("PRIORIDAD", lead[7]),
        ("ORIGEN", lead[12] if len(lead)>12 else "—"),("VALOR", _fmt_valor(lead[8])),
        ("ASIGNADO A", lead[11]),("ETIQUETAS", lead[9]),
        ("CREADO", str(lead[13])[:10] if len(lead)>13 and lead[13] else "—"),
        ("MODIFICADO", str(lead[14])[:10] if len(lead)>14 and lead[14] else "—"),
    ])

    if lead[10]:
        story += [Spacer(1,8), Paragraph("NOTAS", s_h1),
                  HRFlowable(width=W, thickness=0.5, color=ACC, spaceAfter=4)]
        nt = Table([[Paragraph(lead[10], _sty(fontName="Helvetica", fontSize=8.5, textColor=GR20, leading=13, alignment=TA_JUSTIFY))]], colWidths=[W])
        nt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),GR95),("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),10),
            ("RIGHTPADDING",(0,0),(-1,-1),10),("BOX",(0,0),(-1,-1),0.5,ACC),
        ]))
        story.append(nt)

    story += [Spacer(1,10), Paragraph("HISTORIAL DE ACTIVIDADES", s_h1),
              HRFlowable(width=W, thickness=0.5, color=ACC, spaceAfter=6)]
    if acts:
        a_rows = [[Paragraph(f"<b>{x}</b>", _sty(fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)) for x in ["TIPO","DESCRIPCIÓN","FECHA"]]]
        for a in acts:
            a_rows.append([
                Paragraph(str(a[1]), _sty(fontName="Helvetica-Bold", fontSize=8, textColor=GR10)),
                Paragraph(str(a[2]), _sty(fontName="Helvetica", fontSize=8, textColor=GR20)),
                Paragraph(str(a[3])[:10] if a[3] else "—", _sty(fontName="Helvetica", fontSize=7.5, textColor=GR40, alignment=TA_RIGHT)),
            ])
        at = Table(a_rows, colWidths=[W*0.16, W*0.60, W*0.24], repeatRows=1)
        at.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),GR10),("ROWBACKGROUNDS",(0,1),(-1,-1),[GR95,WHITE]),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("BOX",(0,0),(-1,-1),0.5,ACC),
            ("LINEBELOW",(0,0),(-1,-1),0.25,GR85),("LINEBELOW",(0,0),(-1,0),1,ACC),
        ]))
        story.append(at)
        story.append(Paragraph(f"Total: {len(acts)} actividad(es)", _sty(fontName="Helvetica", fontSize=7.5, textColor=GR60)))
    else:
        story.append(Paragraph("Sin actividades registradas.", _sty(fontName="Helvetica", fontSize=8.5, textColor=GR60)))

    story += [Spacer(1,10), Paragraph("TAREAS", s_h1),
              HRFlowable(width=W, thickness=0.5, color=ACC, spaceAfter=6)]
    if tareas:
        t_rows = [[Paragraph(f"<b>{x}</b>", _sty(fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)) for x in ["ESTADO","TÍTULO","PRIORIDAD","VENCIMIENTO"]]]
        pendientes = 0
        for t in tareas:
            comp = bool(t[4]); estado_t = "✔ COMPLETADA" if comp else "⏳ PENDIENTE"
            if not comp: pendientes += 1
            t_rows.append([
                Paragraph(estado_t, _sty(fontName="Helvetica-Bold", fontSize=8, textColor=GR40 if comp else GR10)),
                Paragraph(str(t[1]), _sty(fontName="Helvetica", fontSize=8, textColor=GR40 if comp else GR20)),
                Paragraph(str(t[5]), _sty(fontName="Helvetica-Bold", fontSize=8, textColor=GR20, alignment=TA_CENTER)),
                Paragraph(str(t[3])[:10] if t[3] else "—", _sty(fontName="Helvetica", fontSize=7.5, textColor=GR40, alignment=TA_RIGHT)),
            ])
        tt = Table(t_rows, colWidths=[W*0.16, W*0.47, W*0.17, W*0.20], repeatRows=1)
        tt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),GR10),("ROWBACKGROUNDS",(0,1),(-1,-1),[GR95,WHITE]),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOX",(0,0),(-1,-1),0.5,ACC),
            ("LINEBELOW",(0,0),(-1,-1),0.25,GR85),("LINEBELOW",(0,0),(-1,0),1,ACC),
        ]))
        story.append(tt)
        story.append(Paragraph(f"Total: {len(tareas)}  ·  Pendientes: {pendientes}  ·  Completadas: {len(tareas)-pendientes}",
                               _sty(fontName="Helvetica", fontSize=7.5, textColor=GR60)))
    else:
        story.append(Paragraph("Sin tareas registradas.", _sty(fontName="Helvetica", fontSize=8.5, textColor=GR60)))

    def _footer(canv, doc_obj):
        canv.saveState()
        canv.setFillColor(GR10); canv.rect(0, 0, PW, 0.44*inch, fill=1, stroke=0)
        canv.setFillColor(WHITE); canv.setFont("Helvetica-Bold", 7)
        canv.drawString(M, 0.17*inch, f"LeadPro CRM  —  FICHA DE SEGUIMIENTO  |  {lead[1].upper()}")
        canv.setFillColor(GR60); canv.setFont("Helvetica", 7)
        canv.drawString(M, 0.06*inch, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Confidencial")
        canv.setFillColor(WHITE); canv.setFont("Helvetica-Bold", 8)
        canv.drawRightString(PW-M, 0.14*inch, f"Pág. {doc_obj.page}")
        canv.setStrokeColor(ACC); canv.setLineWidth(1)
        canv.line(M, 0.45*inch, PW-M, 0.45*inch)
        canv.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buf.seek(0); return buf

def build_listado_pdf(leads):
    buf = io.BytesIO()
    GR10=_color("#1a1a1a"); GR20=_color("#333333"); GR40=_color("#666666")
    GR60=_color("#999999"); GR85=_color("#d9d9d9"); GR95=_color("#f2f2f2")
    WHITE=colors.white; ACC=_color("#444444"); CYAN=_color("#0369a1")

    PW, PH = letter; M = 0.60*inch; W = PW - 2*M

    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=M, rightMargin=M,
                            topMargin=0.5*inch, bottomMargin=0.65*inch,
                            title="Listado de Leads — LeadPro CRM")
    base = getSampleStyleSheet()
    _nc = [0]
    def _sty(**kw):
        _nc[0] += 1
        return ParagraphStyle(f"s{_nc[0]}", parent=base["Normal"], **kw)

    story = []
    total_leads = len(leads)
    ganados = sum(1 for l in leads if l[5]=="Ganado")
    pipeline_val = sum(float(l[7] or 0) for l in leads if l[5] not in ("Ganado","Perdido"))
    revenue_val  = sum(float(l[7] or 0) for l in leads if l[5]=="Ganado")

    hdr = Table([[
        Paragraph("<b>LISTADO DE LEADS</b><br/><font size='9'>LeadPro CRM — Reporte General</font>",
                  _sty(fontName="Helvetica-Bold", fontSize=18, textColor=WHITE, leading=26)),
        Paragraph(f"<b>{total_leads}</b> leads<br/><font size='8'>{_today()}</font>",
                  _sty(fontName="Helvetica", fontSize=10, textColor=GR85, leading=14, alignment=TA_RIGHT)),
    ]], colWidths=[W*0.65, W*0.35])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),GR10),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LINEBELOW",(0,0),(-1,-1),2,ACC),
    ]))
    story += [hdr, Spacer(1,10)]

    # Stats bar
    s_sc = _sty(fontName="Helvetica-Bold", fontSize=7, textColor=GR60)
    s_sv = _sty(fontName="Helvetica-Bold", fontSize=13, textColor=GR10)
    stats_cells = [
        [Paragraph("TOTAL LEADS", s_sc), Paragraph(f"{total_leads}", s_sv)],
        [Paragraph("GANADOS", s_sc), Paragraph(f"{ganados}", _sty(fontName="Helvetica-Bold", fontSize=13, textColor=_color("#0a9060")))],
        [Paragraph("PIPELINE", s_sc), Paragraph(f"${pipeline_val:,.0f}", _sty(fontName="Helvetica-Bold", fontSize=13, textColor=_color("#c08010")))],
        [Paragraph("INGRESOS", s_sc), Paragraph(f"${revenue_val:,.0f}", _sty(fontName="Helvetica-Bold", fontSize=13, textColor=CYAN))],
    ]
    st_tbl = Table([[Table([r], colWidths=[(W/4)-10]) for r in stats_cells]], colWidths=[W/4]*4)
    st_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),GR95),
        ("BOX",(0,0),(-1,-1),0.5,ACC),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
    ]))
    story += [st_tbl, Spacer(1,12)]

    # Tabla principal
    # Índices de fetch_leads: 0=id,1=nombre,2=empresa,3=email,4=telefono,
    #                         5=estado,6=prioridad,7=valor,8=etiquetas,
    #                         9=fecha_crea,10=fecha_mod,11=asignado_a,12=origen,13=notas
    # Columnas y anchos fijos que suman exactamente W
    COL_W = [
        W * 0.04,   # #
        W * 0.21,   # NOMBRE
        W * 0.18,   # EMPRESA
        W * 0.12,   # ESTADO
        W * 0.10,   # PRIORIDAD
        W * 0.11,   # VALOR
        W * 0.12,   # ORIGEN
        W * 0.12,   # CREADO
    ]
    # Verificar que suman W (tolerancia float)
    # sum(COL_W) == W * 1.00

    def _th(txt, align=TA_LEFT):
        return Paragraph(f"<b>{txt}</b>",
                         _sty(fontName="Helvetica-Bold", fontSize=7.5,
                              textColor=WHITE, alignment=align))

    def _td(txt, bold=False, align=TA_LEFT, color=None):
        fn = "Helvetica-Bold" if bold else "Helvetica"
        tc = color if color else GR20
        return Paragraph(str(txt) if txt else "—",
                         _sty(fontName=fn, fontSize=8, textColor=tc,
                              leading=10, alignment=align))

    rows = [[
        _th("#",        TA_CENTER),
        _th("NOMBRE"),
        _th("EMPRESA"),
        _th("ESTADO",   TA_CENTER),
        _th("PRIORIDAD",TA_CENTER),
        _th("VALOR",    TA_RIGHT),
        _th("ORIGEN",   TA_CENTER),
        _th("CREADO",   TA_CENTER),
    ]]

    for i, l in enumerate(leads, 1):
        rows.append([
            _td(i,               align=TA_CENTER, color=GR60),
            _td(l[1],            bold=True, color=GR10),
            _td(l[2] or "—",     color=GR20),
            _td(l[5] or "—",     bold=True, align=TA_CENTER, color=GR10),
            _td(l[6] or "—",     align=TA_CENTER, color=GR40),
            _td(_fmt_valor(l[7]),align=TA_RIGHT,  color=GR10),
            _td(l[12] or "—",    align=TA_CENTER, color=GR40),
            _td(str(l[9])[:10] if l[9] else "—", align=TA_CENTER, color=GR60),
        ])

    tbl = Table(rows, colWidths=COL_W, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), GR10),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [GR95, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOX",           (0, 0), (-1, -1), 0.5, ACC),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.25, GR85),
        ("LINEBELOW",     (0, 0), (-1,  0), 1,    ACC),
        ("LINEBEFORE",    (1, 0), (-1, -1), 0.25, GR85),
    ]))
    story.append(tbl)
    story.append(Paragraph(f"Total registros: {total_leads}  |  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                           _sty(fontName="Helvetica", fontSize=7.5, textColor=GR60)))

    def _footer(canv, doc_obj):
        canv.saveState()
        canv.setFillColor(GR10); canv.rect(0, 0, PW, 0.44*inch, fill=1, stroke=0)
        canv.setFillColor(WHITE); canv.setFont("Helvetica-Bold", 7)
        canv.drawString(M, 0.17*inch, "LeadPro CRM  —  LISTADO GENERAL DE LEADS")
        canv.setFillColor(GR60); canv.setFont("Helvetica", 7)
        canv.drawString(M, 0.06*inch, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Confidencial")
        canv.setFillColor(WHITE); canv.setFont("Helvetica-Bold", 8)
        canv.drawRightString(PW-M, 0.14*inch, f"Pág. {doc_obj.page}")
        canv.setStrokeColor(ACC); canv.setLineWidth(1)
        canv.line(M, 0.45*inch, PW-M, 0.45*inch)
        canv.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buf.seek(0); return buf

# ── HELPERS UI ────────────────────────────────────────────────────────────────
def badge(text, color):
    return f'<span class="badge" style="background:{color}20; color:{color}; border:1px solid {color}60;">{text}</span>'

def metric_card(label, value, color="#00d4ff"):
    return f"""<div class="lp-metric">
        <div class="lp-metric-val" style="color:{color};">{value}</div>
        <div class="lp-metric-lbl">{label}</div>
    </div>"""

def export_csv(leads):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID","Nombre","Empresa","Email","Teléfono","Estado","Prioridad","Valor","Etiquetas","Fecha Creación","Fecha Mod","Asignado A","Origen","Notas"])
    for l in leads:
        writer.writerow(l)
    return buf.getvalue().encode("utf-8")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "edit_id" not in st.session_state:     st.session_state.edit_id = None
if "view_lead" not in st.session_state:   st.session_state.view_lead = None
if "confirm_del" not in st.session_state: st.session_state.confirm_del = None
if "tab_idx" not in st.session_state:     st.session_state.tab_idx = 0

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lp-header">
  <div class="lp-logo">🚀 RedRock</div>
  <div class="lp-status">
    <span class="lp-dot"></span>
    RedRock
  </div>
  <div class="lp-user">👤 RedRock</div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_dash, tab_nuevo, tab_leads, tab_kanban, tab_seguimiento, tab_reportes = st.tabs([
    "🏠 Dashboard", "📝 Capturar Lead", "📋 Mis Leads",
    "📊 Pipeline", "📞 Seguimiento", "📈 Reportes"
])

# ═══════════════════════════════════════════════════════
#  TAB 0 — DASHBOARD
# ═══════════════════════════════════════════════════════
with tab_dash:
    st.markdown('<div class="sec-title">Bienvenido a LeadPro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Tu sistema profesional de captación y seguimiento de leads • 100% Python + Streamlit</div>', unsafe_allow_html=True)

    total, ganados, perdidos, revenue, pipeline, tareas_p, tasa = stats()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(metric_card("TOTAL LEADS", total, "#00d4ff"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("GANADOS", ganados, "#00ffaa"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("PERDIDOS", perdidos, "#ef4444"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("TASA CIERRE", f"{tasa}%", "#00d4ff"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card("PIPELINE", f"${pipeline:,.0f}", "#f59e0b"), unsafe_allow_html=True)
    with c6: st.markdown(metric_card("TAREAS PEND.", tareas_p, "#ef4444"), unsafe_allow_html=True)

    st.markdown("<div class='lp-divider'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([3,2])
    with col_a:
        st.markdown("#### 📋 Leads Recientes")
        leads_recientes = fetch_leads()[:6]
        if leads_recientes:
            for l in leads_recientes:
                col1, col2, col3 = st.columns([3,2,1])
                with col1:
                    st.markdown(f"**{l[1]}** — *{l[2] or '—'}*")
                with col2:
                    ec = ESTADO_COLOR.get(l[5], "#64748b")
                    st.markdown(badge(l[5], ec), unsafe_allow_html=True)
                with col3:
                    st.markdown(f"**{_fmt_valor(l[7])}**")
                st.markdown("<div class='lp-divider'></div>", unsafe_allow_html=True)
        else:
            st.info("Sin leads todavía. ¡Captura el primero en la pestaña **Capturar Lead**!")

    with col_b:
        st.markdown("#### 📊 Distribución por Estado")
        all_leads = fetch_leads()
        if all_leads:
            from collections import Counter
            dist = Counter(l[5] for l in all_leads)
            for estado, count in dist.most_common():
                ec = ESTADO_COLOR.get(estado, "#64748b")
                pct = int(count / len(all_leads) * 100)
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;">
                    <span style="color:{ec};">{estado}</span>
                    <span style="color:#64748b;">{count} ({pct}%)</span>
                  </div>
                  <div style="background:#1e2937;border-radius:9999px;height:6px;">
                    <div style="width:{pct}%;background:{ec};height:6px;border-radius:9999px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Sin datos aún.")

    st.markdown("<div class='lp-divider'></div>", unsafe_allow_html=True)
    st.markdown("#### ✅ Tareas Próximas")
    tareas = fetch_tareas(solo_pend=True)
    if tareas:
        for t in tareas[:5]:
            pc = PRIORIDAD_COLOR.get(t[5], "#64748b")
            st.markdown(f"""
            <div class="hist-item" style="border-left-color:{pc};">
              <div style="display:flex;justify-content:space-between;">
                <span><b>{t[1]}</b> — {t[6] or '—'}</span>
                <span style="color:{pc};font-size:12px;">{t[5]} · {t[3] or 'Sin fecha'}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 Sin tareas pendientes")

# ═══════════════════════════════════════════════════════
#  TAB 1 — CAPTURAR LEAD
# ═══════════════════════════════════════════════════════
with tab_nuevo:
    edit_id = st.session_state.edit_id
    lead_edit = fetch_lead(edit_id) if edit_id else None

    if edit_id:
        st.markdown(f'<div class="sec-title">✏️ Editar Lead — {lead_edit[1] if lead_edit else ""}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Modifica los datos del lead y guarda los cambios.</div>', unsafe_allow_html=True)
        if st.button("← Cancelar edición", key="cancel_edit"):
            st.session_state.edit_id = None
            st.rerun()
    else:
        st.markdown('<div class="sec-title">📝 Capturar Nuevo Lead</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Completa los datos del prospecto para añadirlo al CRM.</div>', unsafe_allow_html=True)

    def _v(idx, default=""):
        if lead_edit and len(lead_edit) > idx and lead_edit[idx] is not None:
            return lead_edit[idx]
        return default

    with st.form("form_lead", clear_on_submit=not bool(edit_id)):
        c1, c2 = st.columns(2)
        with c1:
            nombre     = st.text_input("👤 Nombre completo *", value=str(_v(1)), placeholder="Ej: Carlos Ramírez")
            email      = st.text_input("📧 Email", value=str(_v(3)), placeholder="correo@empresa.com")
            origen     = st.selectbox("📌 Origen", ORIGENES, index=ORIGENES.index(str(_v(5,"Manual"))) if str(_v(5,"Manual")) in ORIGENES else 0)
            valor      = st.number_input("💰 Valor estimado ($)", value=float(_v(8,0)), min_value=0.0, step=100.0)
        with c2:
            empresa    = st.text_input("🏢 Empresa", value=str(_v(2,"")), placeholder="Nombre de la empresa")
            telefono   = st.text_input("📞 Teléfono", value=str(_v(4,"")), placeholder="+503 0000-0000")
            estado     = st.selectbox("🎯 Estado", ESTADOS, index=ESTADOS.index(str(_v(6,"Nuevo"))) if str(_v(6,"Nuevo")) in ESTADOS else 0)
            prioridad  = st.selectbox("⚡ Prioridad", PRIORIDADES, index=PRIORIDADES.index(str(_v(7,"Media"))) if str(_v(7,"Media")) in PRIORIDADES else 1)

        c3, c4 = st.columns(2)
        with c3:
            etiquetas  = st.text_input("🏷️ Etiquetas", value=str(_v(9,"")), placeholder="vip, urgente, referido")
        with c4:
            asignado_a = st.text_input("👤 Asignado a", value=str(_v(11,"")), placeholder="Usuario responsable")

        notas = st.text_area("📝 Notas", value=str(_v(10,"")), height=100, placeholder="Información adicional del lead...")

        submitted = st.form_submit_button("💾 Guardar Lead" if not edit_id else "💾 Actualizar Lead",
                                          use_container_width=True)
        if submitted:
            if not nombre.strip():
                st.error("❌ El nombre es obligatorio.")
            else:
                data = (nombre.strip(), empresa.strip(), email.strip(), telefono.strip(),
                        origen, estado, prioridad, valor, etiquetas.strip(), notas.strip(), asignado_a.strip())
                save_lead(data, edit_id)
                st.success(f"✅ Lead **{nombre}** {'actualizado' if edit_id else 'guardado'} correctamente.")
                st.session_state.edit_id = None
                st.balloons()

# ═══════════════════════════════════════════════════════
#  TAB 2 — MIS LEADS
# ═══════════════════════════════════════════════════════
with tab_leads:
    st.markdown('<div class="sec-title">📋 Mis Leads</div>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([3,2,2,1])
    with fc1: search = st.text_input("🔍 Buscar", placeholder="Nombre, empresa, email...", label_visibility="collapsed")
    with fc2: estado_f = st.selectbox("Estado", ["Todos"] + ESTADOS, label_visibility="collapsed")
    with fc3: prior_f  = st.selectbox("Prioridad", ["Todos"] + PRIORIDADES, label_visibility="collapsed")
    with fc4:
        all_leads_dl = fetch_leads(search, estado_f, prior_f)
        st.download_button("📤 CSV", export_csv(all_leads_dl), f"leads_{_today()}.csv", "text/csv", use_container_width=True)

    leads_list = fetch_leads(search, estado_f, prior_f)
    st.markdown(f"<div style='font-size:13px;color:#64748b;margin-bottom:1rem;'>{len(leads_list)} lead(s) encontrado(s)</div>", unsafe_allow_html=True)

    if not leads_list:
        st.info("No hay leads. ¡Captura el primero!")
    else:
        # Encabezado tabla
        h = st.columns([3,2,2,2,2,1,1,1])
        for col, txt in zip(h, ["NOMBRE","EMPRESA","TELÉFONO","ESTADO","VALOR","","",""]):
            col.markdown(f"<div style='font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.05em;padding:8px 0;border-bottom:1px solid #334155;'>{txt}</div>", unsafe_allow_html=True)

        for l in leads_list:
            ec = ESTADO_COLOR.get(l[5], "#64748b")
            row = st.columns([3,2,2,2,2,1,1,1])
            with row[0]: st.markdown(f"**{l[1]}**")
            with row[1]: st.markdown(l[2] or "—")
            with row[2]: st.markdown(l[4] or "—")
            with row[3]: st.markdown(badge(l[5], ec), unsafe_allow_html=True)
            with row[4]: st.markdown(f"**{_fmt_valor(l[7])}**")
            with row[5]:
                if st.button("✏️", key=f"edit_{l[0]}", help="Editar"):
                    st.session_state.edit_id = l[0]
                    st.rerun()
            with row[6]:
                if _PDF_OK:
                    pdf_buf = build_lead_pdf(l[0])
                    if pdf_buf:
                        st.download_button("📄", pdf_buf, f"Lead_{l[1].replace(' ','_')}.pdf",
                                           "application/pdf", key=f"pdf_{l[0]}", help="Descargar PDF")
            with row[7]:
                if st.button("🗑️", key=f"del_{l[0]}", help="Eliminar"):
                    st.session_state.confirm_del = l[0]
            st.markdown("<div class='lp-divider'></div>", unsafe_allow_html=True)

    if st.session_state.confirm_del:
        lid_del = st.session_state.confirm_del
        ld = fetch_lead(lid_del)
        if ld:
            st.warning(f"⚠️ ¿Eliminar el lead **{ld[1]}**? Esta acción no se puede deshacer.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Sí, eliminar", key="confirm_yes"):
                    delete_lead(lid_del)
                    st.session_state.confirm_del = None
                    st.success("Lead eliminado.")
                    st.rerun()
            with c2:
                if st.button("❌ Cancelar", key="confirm_no"):
                    st.session_state.confirm_del = None
                    st.rerun()

# ═══════════════════════════════════════════════════════
#  TAB 3 — KANBAN PIPELINE
# ═══════════════════════════════════════════════════════
with tab_kanban:
    st.markdown('<div class="sec-title">📊 Pipeline Kanban</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Visualiza el estado de tu pipeline de ventas.</div>', unsafe_allow_html=True)

    all_leads_k = fetch_leads()
    estados_k = ["Nuevo","Contactado","Calificado","Propuesta","Negociación","Ganado","Perdido"]
    cols_k = st.columns(len(estados_k))

    for col, estado in zip(cols_k, estados_k):
        ec = ESTADO_COLOR.get(estado, "#64748b")
        leads_est = [l for l in all_leads_k if l[5] == estado]
        total_val = sum(float(l[7] or 0) for l in leads_est)

        with col:
            st.markdown(f"""
            <div class="kanban-col">
              <div class="kanban-hdr" style="color:{ec}; border-bottom-color:{ec};">
                {estado}
                <span style="float:right; background:#0f172a; color:#64748b;
                             font-size:11px; padding:2px 8px; border-radius:9999px;">
                  {len(leads_est)}
                </span>
              </div>
              <div style="font-size:11px; color:#64748b; margin-bottom:10px;">{_fmt_valor(total_val)}</div>
            """, unsafe_allow_html=True)

            if leads_est:
                for l in leads_est:
                    pc = PRIORIDAD_COLOR.get(l[6], "#64748b")
                    st.markdown(f"""
                    <div class="kanban-card">
                      <div style="font-weight:600; font-size:13px;">{l[1]}</div>
                      <div style="font-size:12px; color:#64748b;">{l[2] or '—'}</div>
                      <div style="margin-top:8px; display:flex; justify-content:space-between; font-size:12px;">
                        <span style="color:#00d4ff;">{_fmt_valor(l[7])}</span>
                        <span style="color:{pc};">{l[6]}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#334155; text-align:center; padding:20px 0; font-style:italic; font-size:12px;">Vacío</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  TAB 4 — SEGUIMIENTO
# ═══════════════════════════════════════════════════════
with tab_seguimiento:
    st.markdown('<div class="sec-title">📞 Seguimiento de Leads</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Registra actividades, tareas y notas para cada lead.</div>', unsafe_allow_html=True)

    all_leads_s = fetch_leads()
    if not all_leads_s:
        st.info("No hay leads. ¡Captura el primero!")
    else:
        opciones = {l[0]: f"{l[1]} — {l[2] or '—'} ({l[5]})" for l in all_leads_s}
        sel_id = st.selectbox("Selecciona un lead", options=list(opciones.keys()),
                              format_func=lambda x: opciones[x], label_visibility="visible")

        if sel_id:
            lead_s = fetch_lead(sel_id)
            if lead_s:
                ec = ESTADO_COLOR.get(lead_s[6], "#64748b")
                pc = PRIORIDAD_COLOR.get(lead_s[7], "#64748b")

                # Info card
                st.markdown(f"""
                <div class="lp-card">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                      <div style="font-size:22px; font-weight:700;">{lead_s[1]}</div>
                      <div style="color:#64748b; margin-top:2px;">{lead_s[2] or '—'} · {lead_s[4] or '—'} · {lead_s[3] or '—'}</div>
                    </div>
                    <div style="text-align:right;">
                      {badge(lead_s[6], ec)}
                      &nbsp;{badge(lead_s[7], pc)}
                      <div style="margin-top:8px; color:#00d4ff; font-size:18px; font-weight:700;">{_fmt_valor(lead_s[8])}</div>
                    </div>
                  </div>
                  {f'<div style="margin-top:12px; padding-top:12px; border-top:1px solid #334155; color:#94a3b8; font-size:13px;">📝 {lead_s[10]}</div>' if lead_s[10] else ''}
                </div>
                """, unsafe_allow_html=True)

                col_act, col_tar = st.columns(2)

                # ── Actividades ──
                with col_act:
                    st.markdown("##### ➕ Nueva Actividad")
                    with st.form(f"form_act_{sel_id}"):
                        tipo_a = st.selectbox("Tipo", TIPOS_ACT)
                        desc_a = st.text_area("Descripción", height=80, placeholder="Detalle de la actividad...")
                        estado_nuevo = st.selectbox("Actualizar estado", ["Sin cambio"] + ESTADOS)
                        if st.form_submit_button("📝 Registrar Actividad", use_container_width=True):
                            if desc_a.strip():
                                add_actividad(sel_id, tipo_a, desc_a.strip())
                                if estado_nuevo != "Sin cambio":
                                    conn = _db(); c2 = conn.cursor()
                                    c2.execute("UPDATE crm_leads SET estado=?, fecha_mod=? WHERE id=?",
                                               (estado_nuevo, _now(), sel_id))
                                    conn.commit(); conn.close()
                                st.success("✅ Actividad registrada.")
                                st.rerun()
                            else:
                                st.error("Escribe una descripción.")

                    st.markdown("##### 📜 Historial")
                    acts_s = fetch_actividades(sel_id)
                    if acts_s:
                        for a in acts_s:
                            st.markdown(f"""
                            <div class="hist-item">
                              <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                                <span style="color:#00d4ff;font-size:12px;font-weight:600;">{a[1]}</span>
                                <span style="color:#64748b;font-size:11px;">{str(a[3])[:16]}</span>
                              </div>
                              <div style="font-size:13px;">{a[2]}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#64748b;font-size:13px;">Sin actividades registradas.</div>', unsafe_allow_html=True)

                # ── Tareas ──
                with col_tar:
                    st.markdown("##### ✅ Nueva Tarea")
                    with st.form(f"form_tarea_{sel_id}"):
                        tit_t = st.text_input("Título", placeholder="Ej: Llamar para seguimiento")
                        desc_t = st.text_input("Descripción", placeholder="Detalle opcional")
                        c_t1, c_t2 = st.columns(2)
                        with c_t1:
                            venc_t = st.date_input("Vencimiento", value=datetime.now()+timedelta(days=7))
                        with c_t2:
                            prio_t = st.selectbox("Prioridad", PRIORIDADES)
                        if st.form_submit_button("➕ Crear Tarea", use_container_width=True):
                            if tit_t.strip():
                                save_tarea(sel_id, tit_t.strip(), desc_t.strip(), str(venc_t), prio_t)
                                st.success("✅ Tarea creada.")
                                st.rerun()
                            else:
                                st.error("El título es obligatorio.")

                    st.markdown("##### 📋 Tareas")
                    tareas_s = fetch_tareas(sel_id)
                    if tareas_s:
                        for t in tareas_s:
                            pc2 = PRIORIDAD_COLOR.get(t[5], "#64748b")
                            comp = bool(t[4])
                            c_ta1, c_ta2, c_ta3 = st.columns([1,4,1])
                            with c_ta1:
                                nuevo_val = st.checkbox("", value=comp, key=f"chk_{t[0]}")
                                if nuevo_val != comp:
                                    toggle_tarea(t[0], 1 if nuevo_val else 0)
                                    st.rerun()
                            with c_ta2:
                                estilo = "text-decoration:line-through; color:#64748b;" if comp else ""
                                st.markdown(f"""
                                <div style="{estilo}">
                                  <div style="font-size:13px; font-weight:600;">{t[1]}</div>
                                  <div style="font-size:11px; color:{pc2};">{t[5]} · {t[3] or 'Sin fecha'}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            with c_ta3:
                                if st.button("🗑️", key=f"del_t_{t[0]}"):
                                    delete_tarea(t[0]); st.rerun()
                    else:
                        st.markdown('<div style="color:#64748b;font-size:13px;">Sin tareas.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  TAB 5 — REPORTES
# ═══════════════════════════════════════════════════════
with tab_reportes:
    st.markdown('<div class="sec-title">📈 Reportes y Exportaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Genera reportes PDF y exporta datos del CRM.</div>', unsafe_allow_html=True)

    total, ganados, perdidos, revenue, pipeline, tareas_p, tasa = stats()
    all_leads_r = fetch_leads()

    # Stats resumidas
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_card("TOTAL LEADS",  total,   "#00d4ff"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("INGRESOS",     f"${revenue:,.0f}", "#00ffaa"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("PIPELINE",     f"${pipeline:,.0f}", "#f59e0b"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("TASA CIERRE",  f"{tasa}%", "#00d4ff"), unsafe_allow_html=True)

    st.markdown("<div class='lp-divider'></div>", unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        st.markdown("""
        <div class="lp-card">
          <div style="font-size:18px; font-weight:700; margin-bottom:6px;">📄 Listado General PDF</div>
          <div style="color:#64748b; font-size:13px; margin-bottom:16px;">
            Exporta todos los leads en un PDF profesional con estadísticas.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if _PDF_OK and all_leads_r:
            pdf_list = build_listado_pdf(all_leads_r)
            st.download_button("📥 Descargar Listado PDF", pdf_list,
                               f"leads_listado_{_today()}.pdf", "application/pdf",
                               use_container_width=True)
        elif not _PDF_OK:
            st.error("reportlab no instalado. `pip install reportlab`")
        else:
            st.info("Sin leads para exportar.")

    with col_r2:
        st.markdown("""
        <div class="lp-card">
          <div style="font-size:18px; font-weight:700; margin-bottom:6px;">📊 Exportar CSV</div>
          <div style="color:#64748b; font-size:13px; margin-bottom:16px;">
            Descarga todos los leads en formato CSV para Excel u otras herramientas.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if all_leads_r:
            st.download_button("📥 Descargar CSV", export_csv(all_leads_r),
                               f"leads_{_today()}.csv", "text/csv",
                               use_container_width=True)
        else:
            st.info("Sin leads para exportar.")

    with col_r3:
        st.markdown("""
        <div class="lp-card">
          <div style="font-size:18px; font-weight:700; margin-bottom:6px;">📋 Ficha Individual PDF</div>
          <div style="color:#64748b; font-size:13px; margin-bottom:16px;">
            Genera la ficha completa de seguimiento de un lead específico.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if _PDF_OK and all_leads_r:
            opts_r = {l[0]: f"{l[1]} — {l[2] or '—'}" for l in all_leads_r}
            sel_r = st.selectbox("Selecciona lead", list(opts_r.keys()), format_func=lambda x: opts_r[x], label_visibility="collapsed")
            pdf_ind = build_lead_pdf(sel_r)
            if pdf_ind:
                lead_sel = fetch_lead(sel_r)
                st.download_button("📥 Descargar Ficha PDF", pdf_ind,
                                   f"Lead_{lead_sel[1].replace(' ','_')}.pdf",
                                   "application/pdf", use_container_width=True)
        elif not _PDF_OK:
            st.error("reportlab no instalado.")
        else:
            st.info("Sin leads para exportar.")

    st.markdown("<div class='lp-divider'></div>", unsafe_allow_html=True)

    # Distribución por origen
    if all_leads_r:
        st.markdown("#### 📊 Análisis por Origen")
        from collections import Counter
        orig_dist = Counter(l[12] or "Manual" for l in all_leads_r)
        c_o1, c_o2 = st.columns(2)
        with c_o1:
            for orig, cnt in orig_dist.most_common():
                pct = int(cnt / len(all_leads_r) * 100)
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;">
                    <span style="color:#e2e8f0;">{orig}</span>
                    <span style="color:#64748b;">{cnt} ({pct}%)</span>
                  </div>
                  <div style="background:#1e2937;border-radius:9999px;height:6px;">
                    <div style="width:{pct}%;background:linear-gradient(90deg,#00d4ff,#00ffaa);height:6px;border-radius:9999px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        with c_o2:
            st.markdown("#### 📊 Análisis por Prioridad")
            pri_dist = Counter(l[6] or "Media" for l in all_leads_r)
            for pri, cnt in pri_dist.most_common():
                pct = int(cnt / len(all_leads_r) * 100)
                pc3 = PRIORIDAD_COLOR.get(pri, "#64748b")
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;">
                    <span style="color:{pc3};">{pri}</span>
                    <span style="color:#64748b;">{cnt} ({pct}%)</span>
                  </div>
                  <div style="background:#1e2937;border-radius:9999px;height:6px;">
                    <div style="width:{pct}%;background:{pc3};height:6px;border-radius:9999px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
