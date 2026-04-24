"""
app.py - PGH · Plataforma de Gestión de Honorarios
Versión Free + Pro · Diseño completo con paleta oficial
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from calculadora import calcular_sueldo_inverso, obtener_afps
from supabase_client import verificar_codigo, activar_codigo, es_usuario_pro, guardar_boleta, obtener_boletas

st.set_page_config(page_title="PGH · Calculadora de Honorarios", page_icon="📈", layout="centered")

C_BG="#160D18"; C_SURFACE="#23145B"; C_MID="#09456C"; C_ACCENT1="#026F6E"
C_ACCENT2="#1CA39E"; C_TEXT="#FFFFFF"; C_MUTED="#9BA8B5"
C_SUCCESS="#00C853"; C_DANGER="#FF4B4B"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&display=swap');

html, body, [class*="css"], [class*="st-"] {{
  font-family: 'DM Sans', sans-serif !important;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
}}

/* ── Fondo app ── */
.stApp {{
  background: {C_BG} !important;
  background-image:
    radial-gradient(ellipse 60% 50% at 10% 20%, rgba(35,20,91,0.7) 0%, transparent 70%),
    radial-gradient(ellipse 50% 40% at 90% 80%, rgba(2,111,110,0.35) 0%, transparent 60%) !important;
}}

/* ── Inputs numéricos y texto ── */
.stNumberInput input,
.stTextInput input,
.stTextInput textarea {{
  background: #FFFFFF !important;
  border: 1.5px solid rgba(28,163,158,0.4) !important;
  border-radius: 12px !important;
  color: #111111 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem !important;
  font-weight: 500 !important;
  padding: 10px 14px !important;
}}
.stNumberInput input:focus,
.stTextInput input:focus {{
  border-color: {C_ACCENT2} !important;
  box-shadow: 0 0 0 3px rgba(28,163,158,0.15) !important;
}}

/* Labels de inputs */
.stNumberInput label,
.stTextInput label,
.stSelectbox label {{
  color: {C_MUTED} !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  margin-bottom: 6px !important;
}}

/* ── Selectbox ── */
.stSelectbox > div > div {{
  background: #FFFFFF !important;
  border: 1.5px solid rgba(28,163,158,0.4) !important;
  border-radius: 12px !important;
  color: #111111 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem !important;
  font-weight: 500 !important;
}}

/* Dropdown options */
[data-baseweb="popover"] li,
[data-baseweb="menu"] li {{
  background: #1a1040 !important;
  color: {C_TEXT} !important;
  font-family: 'DM Sans', sans-serif !important;
}}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover {{
  background: rgba(28,163,158,0.2) !important;
}}

/* ── Botón primario ── */
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, {C_ACCENT2}, {C_ACCENT1}) !important;
  border: none !important;
  border-radius: 12px !important;
  color: white !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  padding: 14px 24px !important;
  width: 100% !important;
  transition: opacity 0.2s, transform 0.1s !important;
  letter-spacing: 0.3px !important;
}}
.stButton > button[kind="primary"]:hover {{
  opacity: 0.88 !important;
  transform: translateY(-1px) !important;
}}

/* ── Botón secundario ── */
.stButton > button:not([kind="primary"]) {{
  background: transparent !important;
  border: 1.5px solid rgba(28,163,158,0.35) !important;
  border-radius: 12px !important;
  color: {C_MUTED} !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.95rem !important;
  padding: 12px 20px !important;
  width: 100% !important;
  transition: all 0.2s !important;
}}
.stButton > button:not([kind="primary"]):hover {{
  border-color: {C_ACCENT2} !important;
  color: {C_ACCENT2} !important;
  background: rgba(28,163,158,0.06) !important;
}}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {{
  background: rgba(28,163,158,0.1) !important;
  border: 1.5px solid rgba(28,163,158,0.4) !important;
  border-radius: 12px !important;
  color: {C_ACCENT2} !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  width: 100% !important;
  padding: 12px 20px !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
  background: rgba(28,163,158,0.18) !important;
}}

/* ── Divisor ── */
hr {{ border-color: rgba(28,163,158,0.15) !important; }}

/* ── Alerts ── */
.stSuccess > div {{
  background: rgba(0,200,83,0.12) !important;
  border: 1px solid rgba(0,200,83,0.35) !important;
  border-radius: 14px !important;
  color: #e8fff0 !important;
  font-size: 0.95rem !important;
}}
.stError > div {{
  background: rgba(255,75,75,0.12) !important;
  border: 1px solid rgba(255,75,75,0.35) !important;
  border-radius: 14px !important;
  color: #fff0f0 !important;
  font-size: 0.95rem !important;
}}
.stInfo > div {{
  background: rgba(28,163,158,0.12) !important;
  border: 1px solid rgba(28,163,158,0.35) !important;
  border-radius: 14px !important;
  color: #e0f7f6 !important;
  font-size: 0.95rem !important;
}}
.stWarning > div {{
  background: rgba(255,165,0,0.12) !important;
  border: 1px solid rgba(255,165,0,0.35) !important;
  border-radius: 14px !important;
  font-size: 0.95rem !important;
}}

/* ── Dataframe ── */
.stDataFrame {{
  border-radius: 14px !important;
  overflow: hidden !important;
  border: 1px solid rgba(28,163,158,0.2) !important;
}}
.stDataFrame th {{
  background: {C_SURFACE} !important;
  color: {C_MUTED} !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  white-space: nowrap !important;
}}
.stDataFrame td {{
  font-size: 0.88rem !important;
  color: {C_TEXT} !important;
  white-space: nowrap !important;
}}

/* ── Caption ── */
.stCaption {{
  color: {C_MUTED} !important;
  font-size: 0.82rem !important;
}}

/* ── Cards ── */
.metric-card {{
  background: rgba(35,20,91,0.5);
  border: 1px solid rgba(28,163,158,0.22);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 8px;
  transition: border-color 0.2s;
}}
.metric-card:hover {{ border-color: rgba(28,163,158,0.5); }}
.metric-label {{
  font-size: 0.68rem;
  color: {C_MUTED};
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin-bottom: 5px;
  font-weight: 600;
}}
.metric-value {{
  font-family: 'Syne', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: {C_TEXT};
  line-height: 1.2;
}}
.blurred {{ filter: blur(5px); user-select: none; pointer-events: none; }}

/* ── Result box ── */
.pgh-result {{
  background: linear-gradient(135deg, rgba(28,163,158,0.15), rgba(2,111,110,0.1));
  border: 1px solid rgba(28,163,158,0.4);
  border-radius: 18px;
  padding: 28px 24px;
  text-align: center;
  margin-bottom: 20px;
}}
.pgh-result-label {{
  font-size: 0.72rem;
  color: {C_MUTED};
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
  font-weight: 600;
}}
.pgh-result-value {{
  font-family: 'Syne', sans-serif;
  font-size: clamp(2rem, 6vw, 2.8rem);
  font-weight: 800;
  background: linear-gradient(135deg, #fff, {C_ACCENT2});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -1px;
  line-height: 1.1;
}}
.pgh-result-sub {{
  font-size: 0.85rem;
  color: {C_MUTED};
  margin-top: 8px;
  line-height: 1.5;
}}

/* ── Badges y tags ── */
.pro-badge {{
  display: inline-block;
  background: linear-gradient(135deg, {C_ACCENT2}, {C_ACCENT1});
  color: white;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 99px;
  vertical-align: middle;
  margin-left: 8px;
}}
.hero-tag {{
  display: inline-block;
  background: rgba(28,163,158,0.12);
  border: 1px solid rgba(28,163,158,0.3);
  color: {C_ACCENT2};
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 5px 14px;
  border-radius: 99px;
  margin-bottom: 16px;
}}
.section-tag {{
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: {C_ACCENT2};
  margin-bottom: 14px;
  display: block;
}}
.benefit-item {{
  background: rgba(28,163,158,0.08);
  border: 1px solid rgba(28,163,158,0.15);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.88rem;
  margin-bottom: 8px;
  color: {C_TEXT};
  line-height: 1.4;
}}

/* ── Welcome banner ── */
.welcome-banner {{
  background: linear-gradient(135deg, rgba(28,163,158,0.18), rgba(2,111,110,0.12));
  border: 1px solid rgba(28,163,158,0.45);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
}}
.welcome-title {{
  font-family: 'Syne', sans-serif;
  font-size: 1.25rem;
  font-weight: 800;
  color: {C_TEXT};
  margin-bottom: 4px;
  line-height: 1.3;
}}
.welcome-sub {{
  font-size: 0.85rem;
  color: {C_MUTED};
  line-height: 1.5;
}}

/* ── UF pill ── */
.uf-pill {{
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(28,163,158,0.08);
  border: 1px solid rgba(28,163,158,0.2);
  border-radius: 99px;
  padding: 6px 14px;
  font-size: 0.78rem;
  color: {C_MUTED};
  font-weight: 500;
}}

/* ── Disclaimer banner ── */
.disclaimer-banner {{
  background: rgba(255,165,0,0.1);
  border: 1.5px solid rgba(255,165,0,0.4);
  border-radius: 14px;
  padding: 14px 18px;
  margin: 24px 0 8px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}}
.disclaimer-icon {{ font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }}
.disclaimer-text {{
  font-size: 0.88rem;
  color: #FFD580;
  line-height: 1.5;
  font-weight: 500;
}}

/* ── PGH card ── */
.pgh-card {{
  background: rgba(35,20,91,0.4);
  border: 1px solid rgba(28,163,158,0.2);
  border-radius: 18px;
  padding: 24px;
  margin-bottom: 20px;
}}

/* ── Responsive mobile ── */
@media (max-width: 640px) {{
  .pgh-result-value {{ font-size: 2rem !important; }}
  .metric-value {{ font-size: 1rem !important; }}
  .welcome-title {{ font-size: 1.1rem !important; }}
  .stDataFrame td, .stDataFrame th {{ font-size: 0.78rem !important; }}
}}

footer {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def obtener_uf():
    try:
        hoy = date.today().strftime("%d-%m-%Y")
        r = requests.get(f"https://mindicador.cl/api/uf/{hoy}", timeout=5)
        return float(r.json()["serie"][0]["valor"])
    except:
        return 40013.88

def clp(v):
    return f"${v:,.0f}".replace(",", ".")

def mcard(label, value, color=C_TEXT):
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="color:{color}">{value}</div></div>'

def disclaimer():
    return """<div class="disclaimer-banner">
    <div class="disclaimer-icon">⚠️</div>
    <div class="disclaimer-text">
        <strong>Datos estimados.</strong> Esta calculadora es referencial y no reemplaza asesoría profesional.
        Consulta con un contador para tomar decisiones financieras con certeza.
    </div>
</div>"""


def pdf_desglose(r, nombre, valor_uf):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    T = colors.HexColor; styles = getSampleStyleSheet()
    TEAL=T("#1CA39E"); DARK=T("#160D18"); MUTED=T("#9BA8B5")
    WHITE=colors.white; LGRAY=T("#F3F4F6"); BAL=r["balance_renta"]; POS=BAL>=0
    s_sec = ParagraphStyle("s", fontName="Helvetica-Bold", fontSize=8, textColor=TEAL, spaceAfter=8, letterSpacing=2)
    s_foot = ParagraphStyle("f", fontName="Helvetica", fontSize=7.5, textColor=MUTED, alignment=TA_CENTER)
    story = []
    # Logo
    lt = Table([[
        Paragraph("<b><font color='#1CA39E' size=18>PGH</font></b>", styles["Normal"]),
        Paragraph(f"<font color='#9BA8B5' size=8>Generado el {date.today().strftime('%d/%m/%Y')}</font>",
                  ParagraphStyle("r", fontName="Helvetica", fontSize=8, textColor=MUTED, alignment=TA_RIGHT))
    ]], colWidths=[9*cm, 8*cm])
    lt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    sub = Table([[Paragraph("<font color='#9BA8B5' size=7>PLATAFORMA DE GESTIÓN DE HONORARIOS · CHILE 2026</font>", styles["Normal"]), ""]], colWidths=[9*cm, 8*cm])
    story += [lt, sub, HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=16, opacity=0.3)]
    story += [Paragraph("<b><font size=22>Desglose de Honorarios</font></b>", styles["Normal"]), Spacer(1,4)]
    story += [Paragraph(f"<font color='#9BA8B5' size=10>Trabajador: {nombre} · AFP: {r['afp']}</font>", styles["Normal"]), Spacer(1,16)]
    # Bruto destacado
    bt = Table([[
        Paragraph("<font color='#9BA8B5' size=8>MONTO BRUTO A BOLETEAR</font>", styles["Normal"]),
        Paragraph(f"<b><font color='#1CA39E' size=22>{clp(r['bruto'])}</font></b>",
                  ParagraphStyle("v", fontName="Helvetica-Bold", fontSize=22, textColor=TEAL, alignment=TA_RIGHT))
    ]], colWidths=[9*cm, 8*cm])
    bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),T("#F0FAFA")),("TOPPADDING",(0,0),(-1,-1),16),("BOTTOMPADDING",(0,0),(-1,-1),16),("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [bt, Spacer(1,20), Paragraph("DESGLOSE DETALLADO", s_sec)]
    data = [
        ["Concepto","Valor"],
        ["Retención SII (15,25%)", clp(r["retencion_sii"])],
        ["Sueldo líquido confirmado", clp(r["liquido_final"])],
        ["",""],
        ["Base Imponible (80% del bruto)", clp(r["base_imponible"])],
        ["Tope legal (90 UF)", clp(r["tope_legal"])],
        ["",""],
        ["Cotización Salud (7%)", clp(r["pago_salud"])],
        [f"AFP {r['afp']} + SIS ({r['tasa_afp']*100:.2f}%)", clp(r["pago_afp"])],
        ["Seguro Accidentes (0,9%)", clp(r["pago_accidentes"])],
        ["Total Cotizaciones", clp(r["total_cotizaciones"])],
    ]
    t = Table(data, colWidths=[11*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("BACKGROUND",(0,-1),(-1,-1),T("#E6F7F7")),("TEXTCOLOR",(0,-1),(-1,-1),T("#026F6E")),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE,LGRAY]),
        ("ALIGN",(1,0),(1,-1),"RIGHT"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("GRID",(0,0),(-1,-1),0.5,T("#E5E7EB")),("LINEBELOW",(0,0),(-1,0),1,TEAL),
    ]))
    story += [t, Spacer(1,20), Paragraph("BALANCE OPERACIÓN RENTA", s_sec)]
    bc = T("#00C853") if POS else T("#FF4B4B"); bbg = T("#F0FFF4") if POS else T("#FFF5F5")
    btxt = f"{'Devolución estimada' if POS else 'Diferencia a pagar en abril'}: {clp(abs(BAL))}"
    bdesc = "El SII te devolverá esta diferencia en la Operación Renta de abril." if POS else "La retención del SII no alcanza para cubrir tus cotizaciones."
    bal_t = Table([[Paragraph(
        f"<b><font size=11>{'🎉' if POS else '⚠️'} {btxt}</font></b><br/><font size=8 color='#6B7280'>{bdesc}</font>",
        ParagraphStyle("b", fontName="Helvetica", fontSize=10, textColor=bc, leading=16)
    )]], colWidths=[17*cm])
    bal_t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bbg),("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("LINERIGHT",(0,0),(0,-1),4,bc)]))
    story += [bal_t, Spacer(1,30), HRFlowable(width="100%", thickness=0.5, color=T("#E5E7EB"), spaceAfter=10)]
    story += [Paragraph("⚠️ Este informe es referencial. Consulta a un contador para decisiones financieras definitivas. · PGH · calculadora-pgh.streamlit.app", s_foot)]
    doc.build(story)
    return buf.getvalue()


def pdf_reporte(boletas, nombre):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    T = colors.HexColor; styles = getSampleStyleSheet()
    TEAL=T("#1CA39E"); DARK=T("#160D18"); MUTED=T("#9BA8B5"); WHITE=colors.white; LGRAY=T("#F3F4F6")
    s_sec = ParagraphStyle("s", fontName="Helvetica-Bold", fontSize=8, textColor=TEAL, spaceAfter=8, letterSpacing=2)
    s_foot = ParagraphStyle("f", fontName="Helvetica", fontSize=7.5, textColor=MUTED, alignment=TA_CENTER)
    df = pd.DataFrame(boletas); anio = date.today().year
    story = []
    lt = Table([[
        Paragraph("<b><font color='#1CA39E' size=18>PGH</font></b>", styles["Normal"]),
        Paragraph(f"<font color='#9BA8B5' size=8>Reporte generado el {date.today().strftime('%d/%m/%Y')}</font>",
                  ParagraphStyle("r", fontName="Helvetica", fontSize=8, textColor=MUTED, alignment=TA_RIGHT))
    ]], colWidths=[9*cm, 8*cm])
    lt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story += [lt, Table([[Paragraph("<font color='#9BA8B5' size=7>PLATAFORMA DE GESTIÓN DE HONORARIOS · CHILE 2026</font>", styles["Normal"]), ""]], colWidths=[9*cm, 8*cm])]
    story += [HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=16, opacity=0.3)]
    story += [Paragraph(f"<b><font size=22>Reporte Anual {anio}</font></b>", styles["Normal"]), Spacer(1,4)]
    story += [Paragraph(f"<font color='#9BA8B5' size=10>Trabajador: {nombre}</font>", styles["Normal"]), Spacer(1,16)]
    tb=df["bruto"].sum(); tl=df["liquido"].sum(); tc=df["total_cotizaciones"].sum(); tbal=df["balance_renta"].sum()
    rt = Table([
        ["Total bruto boleteado","Total líquido recibido","Total cotizaciones","Balance anual"],
        [clp(tb), clp(tl), clp(tc), clp(tbal)]
    ], colWidths=[4.25*cm]*4)
    rt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),T("#9BA8B5")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica"),("FONTSIZE",(0,0),(-1,0),7),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,1),(-1,1),11),
        ("TEXTCOLOR",(0,1),(-1,1),TEAL),("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("GRID",(0,0),(-1,-1),0.5,T("#E5E7EB")),
    ]))
    story += [rt, Spacer(1,20), Paragraph("HISTORIAL DE BOLETAS", s_sec)]
    hd = [["Fecha","Líquido","Bruto","AFP","Total Cotiz.","Balance"]]
    rbg = []
    for i, (_, row) in enumerate(df.iterrows()):
        hd.append([str(row["fecha"]), clp(row["liquido"]), clp(row["bruto"]), str(row["afp"]), clp(row["total_cotizaciones"]), clp(row["balance_renta"])])
        rbg.append(("BACKGROUND",(0,i+1),(-1,i+1), T("#F0FFF4") if row["balance_renta"]>=0 else T("#FFF5F5")))
    ht = Table(hd, colWidths=[2.5*cm, 2.8*cm, 2.8*cm, 2*cm, 3*cm, 2.9*cm])
    ht.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(1,0),(-1,-1),"RIGHT"),("ALIGN",(0,0),(0,-1),"LEFT"),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("GRID",(0,0),(-1,-1),0.5,T("#E5E7EB")),("LINEBELOW",(0,0),(-1,0),1,TEAL),
        *rbg
    ]))
    story += [ht, Spacer(1,30), HRFlowable(width="100%", thickness=0.5, color=T("#E5E7EB"), spaceAfter=10)]
    story += [Paragraph("⚠️ Este reporte es referencial. Consulta a un contador para decisiones financieras definitivas. · PGH · calculadora-pgh.streamlit.app", s_foot)]
    doc.build(story)
    return buf.getvalue()


# ── Estado de sesión ──────────────────────────────────────────────────────────
defs = {
    "pantalla": "free", "usuario_email": None, "usuario_nombre": None,
    "es_pro": False, "resultado": None, "codigo_validado": None,
    "mostrar_bienvenida": False, "es_primera_vez": False,
}
for k, v in defs.items():
    if k not in st.session_state:
        st.session_state[k] = v

valor_uf = obtener_uf()

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([3, 2, 1])
with c1:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:4px 0">
    <div style="width:42px;height:42px;background:linear-gradient(135deg,{C_SURFACE},{C_MID});border:1px solid rgba(28,163,158,0.4);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.2rem">📈</div>
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:800;background:linear-gradient(135deg,{C_ACCENT2},{C_ACCENT1});-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.2">PGH</div>
      <div style="font-size:0.55rem;color:{C_MUTED};letter-spacing:1.5px;text-transform:uppercase;margin-top:1px">Gestión de Honorarios</div>
    </div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="padding-top:10px"><div class="uf-pill"><span style="width:7px;height:7px;border-radius:50%;background:{C_ACCENT2};display:inline-block"></span>UF hoy: {clp(valor_uf)}</div></div>', unsafe_allow_html=True)
with c3:
    if st.session_state.es_pro:
        if st.button("Salir", use_container_width=True):
            for k, v in defs.items():
                st.session_state[k] = v
            st.rerun()
    else:
        if st.button("Ingresar", use_container_width=True):
            st.session_state.pantalla = "login_directo"
            st.rerun()

st.divider()

# ── INPUTS CALCULADORA (Free y Pro) ──────────────────────────────────────────
if st.session_state.pantalla in ["free", "pro"]:

    # Bienvenida
    if st.session_state.es_pro and st.session_state.mostrar_bienvenida:
        n = st.session_state.usuario_nombre.split()[0]
        if st.session_state.es_primera_vez:
            titulo = f"¡Bienvenido, {n}! 🎉"
            sub = "Tu cuenta Pro está activa. Ya tienes acceso a todas las funciones."
        else:
            titulo = f"¡Bienvenido de vuelta, {n}! 👋"
            sub = "Tienes acceso completo a todas las funciones Pro."
        st.markdown(f'<div class="welcome-banner"><div class="welcome-title">{titulo}</div><div class="welcome-sub">{sub}</div></div>', unsafe_allow_html=True)
        st.session_state.mostrar_bienvenida = False

    if st.session_state.es_pro:
        st.markdown(f'<div style="margin-bottom:12px"><span style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700;color:{C_TEXT}">{st.session_state.usuario_nombre.split()[0]}</span><span class="pro-badge">PRO</span></div>', unsafe_allow_html=True)

    st.markdown('<span class="section-tag">Calculadora</span>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        liquido = st.number_input(
            "💵 Líquido que quiero recibir (CLP)",
            min_value=10_000, max_value=50_000_000,
            value=500_000, step=10_000, format="%d"
        )
    with c2:
        afp = st.selectbox("🏦 AFP", options=obtener_afps())

    # Mostrar monto formateado
    st.caption(f"Monto ingresado: **{clp(liquido)}**")

    if st.button("Calcular →", type="primary", use_container_width=True):
        st.session_state.resultado = calcular_sueldo_inverso(float(liquido), afp, valor_uf)


# ── FREE ──────────────────────────────────────────────────────────────────────
if st.session_state.pantalla == "free":
    if st.session_state.resultado:
        r = st.session_state.resultado
        st.markdown(f'<div class="pgh-result"><div class="pgh-result-label">Debes boletear</div><div class="pgh-result-value">{clp(r["bruto"])}</div><div class="pgh-result-sub">Para recibir {clp(r["liquido_final"])} líquidos</div></div>', unsafe_allow_html=True)
        st.markdown('<span class="section-tag">¿Quieres saber más?</span>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<div class="metric-card blurred"><div class="metric-label">Retención SII</div><div class="metric-value">$██████</div></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="metric-card blurred"><div class="metric-label">Total cotizaciones</div><div class="metric-value">$██████</div></div>', unsafe_allow_html=True)
        with c3: st.markdown('<div class="metric-card blurred"><div class="metric-label">Balance Renta</div><div class="metric-value">🔴 $██████</div></div>', unsafe_allow_html=True)
        st.markdown(disclaimer(), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Ver desglose completo 🔓", use_container_width=True):
            st.session_state.pantalla = "vista_previa"
            st.rerun()

# ── VISTA PREVIA ──────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "vista_previa":
    st.markdown(f'<div style="text-align:center;margin-bottom:8px"><div class="hero-tag">Versión Pro</div><h2 style="font-family:Syne,sans-serif;font-size:clamp(1.4rem,4vw,1.8rem);font-weight:800;margin:8px 0;color:{C_TEXT}">Desbloquea el desglose completo</h2><p style="color:{C_MUTED};font-size:0.9rem">Gestiona tus honorarios como un profesional</p></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<span class="section-tag">Vista previa</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    items = [("Retención SII (15,25%)","$██████"),("Base Imponible (80%)","$██████"),("Total cotizaciones","$██████"),("Salud (7%)","$██████"),("AFP + SIS","$██████"),("Balance Renta","🔴 $██████")]
    for i, (lbl, val) in enumerate(items):
        with [c1,c2,c3][i%3]:
            st.markdown(f'<div class="metric-card blurred"><div class="metric-label">{lbl}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
    st.caption("🔓 Desbloquea para ver tus números reales")
    st.divider()
    st.markdown('<span class="section-tag">¿Qué incluye el Pro?</span>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        for b in ["✅ Desglose completo de cotizaciones","✅ Balance Operación Renta con alerta","✅ Historial de todas tus boletas"]:
            st.markdown(f'<div class="benefit-item">{b}</div>', unsafe_allow_html=True)
    with c2:
        for b in ["✅ Gráfico de ingresos por mes","✅ Gráfico de balance acumulado","✅ Descarga tus informes en PDF"]:
            st.markdown(f'<div class="benefit-item">{b}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin:24px 0 8px"><div style="font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,{C_ACCENT2},{C_ACCENT1});-webkit-background-clip:text;-webkit-text-fill-color:transparent">$2.990</div><div style="color:{C_MUTED};font-size:0.85rem">por mes · Cancela cuando quieras</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Quiero el Pro 🔓", type="primary", use_container_width=True):
            st.session_state.pantalla = "compra"; st.rerun()
    with c2:
        if st.button("← Volver", use_container_width=True):
            st.session_state.pantalla = "free"; st.rerun()

# ── COMPRA ────────────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "compra":
    st.markdown(f'<h2 style="font-family:Syne,sans-serif;font-weight:800;margin-bottom:4px;color:{C_TEXT}">🔑 Obtén tu acceso Pro</h2><p style="color:{C_MUTED};font-size:0.9rem;margin-bottom:24px">3 pasos simples para activar tu cuenta</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="pgh-card"><span class="section-tag">Instrucciones</span><p style="color:{C_TEXT};margin-bottom:8px"><b>1️⃣ Transfiere $2.990</b></p><ul style="color:{C_MUTED};font-size:0.9rem;margin:8px 0 16px 16px;line-height:2"><li>Banco: BancoEstado (Cuenta RUT)</li><li>RUT: 21.553.061-2</li><li>Nombre: Exequiel Zambrano</li></ul><p style="color:{C_TEXT};margin-bottom:8px"><b>2️⃣ Envía el comprobante</b></p><p style="color:{C_MUTED};font-size:0.9rem;margin:8px 0 16px 16px">📲 WhatsApp: +56 9 5222 2772</p><p style="color:{C_TEXT}"><b>3️⃣ Recibe tu código en minutos</b></p></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<span class="section-tag">¿Ya tienes tu código?</span>', unsafe_allow_html=True)
    cod = st.text_input("Código de acceso", placeholder="PGH-PRO-XXXX", label_visibility="collapsed").strip().upper()
    if st.button("Activar Pro ✅", type="primary", use_container_width=True):
        if cod:
            if verificar_codigo(cod):
                st.session_state.codigo_validado = cod
                st.session_state.pantalla = "activacion"
                st.rerun()
            else:
                st.error("❌ Código incorrecto o ya utilizado. Verifica e intenta de nuevo.")
        else:
            st.warning("Por favor ingresa tu código.")
    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "vista_previa"; st.rerun()

# ── ACTIVACIÓN ────────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "activacion":
    st.markdown(f'<div style="text-align:center;margin-bottom:24px"><div style="font-size:3rem">✅</div><h2 style="font-family:Syne,sans-serif;font-weight:800;color:{C_TEXT}">¡Código válido!</h2><p style="color:{C_MUTED}">Ingresa tus datos para activar tu cuenta.</p></div>', unsafe_allow_html=True)
    nom = st.text_input("Tu nombre completo", placeholder="Juan Pérez")
    eml = st.text_input("Tu email", placeholder="juan@gmail.com")
    if st.button("Activar mi cuenta Pro 🚀", type="primary", use_container_width=True):
        if nom and eml:
            if activar_codigo(st.session_state.codigo_validado, eml, nom):
                st.session_state.es_pro = True
                st.session_state.usuario_email = eml
                st.session_state.usuario_nombre = nom
                st.session_state.mostrar_bienvenida = True
                st.session_state.es_primera_vez = True
                st.session_state.pantalla = "pro"
                st.rerun()
            else:
                st.error("Error al activar. Contáctanos por WhatsApp.")
        else:
            st.warning("Por favor completa todos los campos.")

# ── LOGIN DIRECTO ─────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "login_directo":
    st.markdown(f'<h2 style="font-family:Syne,sans-serif;font-weight:800;margin-bottom:4px;color:{C_TEXT}">👤 Iniciar sesión</h2><p style="color:{C_MUTED};margin-bottom:24px">Ingresa tu email para acceder a tu cuenta Pro.</p>', unsafe_allow_html=True)
    eml = st.text_input("Tu email", placeholder="juan@gmail.com")
    if st.button("Ingresar →", type="primary", use_container_width=True):
        if eml:
            if es_usuario_pro(eml):
                from supabase_client import get_client
                res = get_client().table("usuarios").select("nombre").eq("email", eml).execute()
                nom = res.data[0]["nombre"] if res.data else eml
                st.session_state.es_pro = True
                st.session_state.usuario_email = eml
                st.session_state.usuario_nombre = nom
                st.session_state.mostrar_bienvenida = True
                st.session_state.es_primera_vez = False
                st.session_state.pantalla = "pro"
                st.rerun()
            else:
                st.error("❌ No encontramos una cuenta Pro con ese email.")
                st.info("¿Aún no tienes el Pro? Vuelve y haz clic en 'Ver desglose completo'.")
        else:
            st.warning("Por favor ingresa tu email.")
    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "free"; st.rerun()

# ── PRO ───────────────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "pro":
    if st.session_state.mostrar_bienvenida:
        n = st.session_state.usuario_nombre.split()[0]
        if st.session_state.es_primera_vez:
            titulo = f"¡Bienvenido, {n}! 🎉"
            sub = "Tu cuenta Pro está activa. Ya tienes acceso a todas las funciones."
        else:
            titulo = f"¡Bienvenido de vuelta, {n}! 👋"
            sub = "Tienes acceso completo a todas las funciones Pro."
        st.markdown(f'<div class="welcome-banner"><div class="welcome-title">{titulo}</div><div class="welcome-sub">{sub}</div></div>', unsafe_allow_html=True)
        st.session_state.mostrar_bienvenida = False

    if st.session_state.resultado:
        r = st.session_state.resultado
        # Resultado principal
        st.markdown(f'<div class="pgh-result"><div class="pgh-result-label">Monto bruto a boletear</div><div class="pgh-result-value">{clp(r["bruto"])}</div><div class="pgh-result-sub">Recibirás {clp(r["liquido_final"])} líquidos · Retención SII: {clp(r["retencion_sii"])}</div></div>', unsafe_allow_html=True)
        # Cotizaciones
        st.markdown('<span class="section-tag">Cotizaciones Obligatorias</span>', unsafe_allow_html=True)
        st.caption(f"Base imponible: {clp(r['base_imponible'])} · Tope legal (90 UF): {clp(r['tope_legal'])}")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(mcard("Salud (7%)", clp(r['pago_salud'])), unsafe_allow_html=True)
        with c2: st.markdown(mcard(f"AFP+SIS ({r['tasa_afp']*100:.2f}%)", clp(r['pago_afp'])), unsafe_allow_html=True)
        with c3: st.markdown(mcard("Accidentes (0,9%)", clp(r['pago_accidentes'])), unsafe_allow_html=True)
        with c4: st.markdown(mcard("Total cotizaciones", clp(r['total_cotizaciones']), C_ACCENT2), unsafe_allow_html=True)
        # Balance
        st.markdown('<span class="section-tag" style="margin-top:12px;display:block">Balance Operación Renta</span>', unsafe_allow_html=True)
        bal = r["balance_renta"]
        if bal >= 0:
            st.success(f"**🎉 Devolución estimada: {clp(bal)}**\n\nEl SII te devolverá esta diferencia en la Operación Renta de abril.")
        else:
            st.error(f"**⚠️ Diferencia a pagar en abril: {clp(abs(bal))}**\n\nLa retención no alcanza para cubrir tus cotizaciones obligatorias.")
        # Disclaimer visible
        st.markdown(disclaimer(), unsafe_allow_html=True)
        # Botones guardar + PDF
        st.markdown("<br>", unsafe_allow_html=True)
        cg, cp = st.columns(2)
        with cg:
            if st.button("💾 Guardar boleta", type="primary", use_container_width=True):
                datos = {
                    "liquido": r["liquido_deseado"], "bruto": r["bruto"], "afp": r["afp"],
                    "retencion_sii": r["retencion_sii"], "base_imponible": r["base_imponible"],
                    "pago_salud": r["pago_salud"], "pago_afp": r["pago_afp"],
                    "pago_accidentes": r["pago_accidentes"], "total_cotizaciones": r["total_cotizaciones"],
                    "balance_renta": r["balance_renta"],
                }
                if guardar_boleta(st.session_state.usuario_email, datos):
                    st.success("✅ Boleta guardada.")
                    st.rerun()
                else:
                    st.error("Error al guardar.")
        with cp:
            st.download_button(
                label="📄 Descargar desglose PDF",
                data=pdf_desglose(r, st.session_state.usuario_nombre, valor_uf),
                file_name=f"PGH_desglose_{date.today().strftime('%d-%m-%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    st.divider()

    # Historial
    st.markdown('<span class="section-tag">Historial de Boletas</span>', unsafe_allow_html=True)
    boletas = obtener_boletas(st.session_state.usuario_email)

    if boletas:
        df = pd.DataFrame(boletas)

        # Tabla mobile-friendly: solo columnas esenciales
        dm = df[["fecha","liquido","bruto","balance_renta"]].copy()
        dm.columns = ["Fecha","Líquido","Bruto","Balance"]
        dm["Líquido"] = dm["Líquido"].apply(clp)
        dm["Bruto"] = dm["Bruto"].apply(clp)
        dm["Balance"] = dm["Balance"].apply(lambda x: f"{'🟢' if x>=0 else '🔴'} {clp(x)}")
        st.dataframe(dm, hide_index=True, use_container_width=True)

        # Botón reporte anual
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📊 Descargar reporte anual completo PDF",
            data=pdf_reporte(boletas, st.session_state.usuario_nombre),
            file_name=f"PGH_reporte_anual_{date.today().year}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.divider()

        # Gráficos
        st.markdown('<span class="section-tag">Gráficos</span>', unsafe_allow_html=True)

        df["fecha"] = pd.to_datetime(df["fecha"])

        # Gráfico 1: Barras por mes
        df_mes = df.copy()
        df_mes["mes_orden"] = df_mes["fecha"].dt.to_period("M")
        df_mes = df_mes.groupby("mes_orden")["bruto"].sum().reset_index()
        df_mes["mes_label"] = df_mes["mes_orden"].dt.strftime("%b %Y")
        df_mes = df_mes.sort_values("mes_orden")

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df_mes["mes_label"],
            y=df_mes["bruto"],
            marker_color=C_ACCENT2,
            marker_line_width=0,
            text=[clp(v) for v in df_mes["bruto"]],
            textposition="outside",
            textfont=dict(color=C_TEXT, size=12, family="DM Sans"),
        ))
        fig1.update_layout(
            title=dict(text="Ingresos brutos por mes", font=dict(color=C_TEXT, size=15, family="Syne"), x=0),
            paper_bgcolor="rgba(35,20,91,0.45)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C_MUTED, family="DM Sans", size=12),
            xaxis=dict(gridcolor="rgba(28,163,158,0.1)", tickfont=dict(color=C_TEXT, size=12), title=""),
            yaxis=dict(gridcolor="rgba(28,163,158,0.12)", tickfont=dict(color=C_MUTED, size=11),
                       tickprefix="$", tickformat=",.0f", title=""),
            margin=dict(t=50, b=50, l=70, r=20),
            height=340,
            bargap=0.3,
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico 2: Línea balance acumulado
        ds = df.sort_values("fecha").copy()
        ds["balance_acumulado"] = ds["balance_renta"].cumsum()
        ds["fecha_str"] = ds["fecha"].dt.strftime("%d/%m/%Y")
        max_bal = ds["balance_acumulado"].max()
        min_bal = ds["balance_acumulado"].min()

        fig2 = go.Figure()
        # Zona positiva verde
        if max_bal > 0:
            fig2.add_hrect(y0=0, y1=max(max_bal * 1.3, 1), fillcolor="rgba(0,200,83,0.06)", line_width=0)
        # Zona negativa roja
        if min_bal < 0:
            fig2.add_hrect(y0=min(min_bal * 1.3, -1), y1=0, fillcolor="rgba(255,75,75,0.06)", line_width=0)
        fig2.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.25)", line_width=1.5)
        fig2.add_trace(go.Scatter(
            x=ds["fecha_str"],
            y=ds["balance_acumulado"],
            mode="lines+markers+text",
            line=dict(color=C_ACCENT2, width=3),
            marker=dict(color=C_ACCENT2, size=9, line=dict(color=C_BG, width=2)),
            fill="tozeroy",
            fillcolor="rgba(28,163,158,0.08)",
            text=[clp(v) for v in ds["balance_acumulado"]],
            textposition="top center",
            textfont=dict(color=C_TEXT, size=11, family="DM Sans"),
            hovertemplate="<b>%{x}</b><br>Balance: %{text}<extra></extra>",
        ))
        fig2.update_layout(
            title=dict(text="Balance acumulado en el año", font=dict(color=C_TEXT, size=15, family="Syne"), x=0),
            paper_bgcolor="rgba(35,20,91,0.45)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C_MUTED, family="DM Sans", size=12),
            xaxis=dict(gridcolor="rgba(28,163,158,0.1)", tickfont=dict(color=C_TEXT, size=11), title=""),
            yaxis=dict(gridcolor="rgba(28,163,158,0.12)", tickfont=dict(color=C_MUTED, size=11),
                       tickprefix="$", tickformat=",.0f", title=""),
            margin=dict(t=50, b=50, l=80, r=20),
            height=340,
            showlegend=False,
            annotations=[
                dict(x=0.01, y=0.97, xref="paper", yref="paper",
                     text="🟢 Zona de devolución", showarrow=False,
                     font=dict(color=C_SUCCESS, size=11), xanchor="left"),
                dict(x=0.01, y=0.03, xref="paper", yref="paper",
                     text="🔴 Zona de pago", showarrow=False,
                     font=dict(color=C_DANGER, size=11), xanchor="left"),
            ] if max_bal > 0 and min_bal < 0 else [],
        )
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Aún no tienes boletas guardadas. Calcula y guarda tu primera boleta arriba. 👆")

    st.divider()
    st.markdown(disclaimer(), unsafe_allow_html=True)
