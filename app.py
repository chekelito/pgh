"""
app.py - PGH · Plataforma de Gestión de Honorarios
Versión Free + Pro · Diseño completo con paleta oficial
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import io
from datetime import date, datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from calculadora import calcular_sueldo_inverso, obtener_afps
from supabase_client import verificar_codigo, activar_codigo, validar_login, guardar_boleta, obtener_boletas, eliminar_boleta, obtener_todos_usuarios, renovar_suscripcion_usuario
# --- CONFIGURACIÓN DE PESTAÑA (LOGO COMPLETO PGH) ---
favicon_svg = """
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 110 150'>
    <defs>
        <linearGradient id='dg' x1='0%' y1='0%' x2='100%' y2='100%'>
            <stop offset='0%' style='stop-color:%2309456C'/>
            <stop offset='100%' style='stop-color:%2323145B'/>
        </linearGradient>
    </defs>
    <rect x='4' y='4' width='102' height='132' rx='12' fill='url(%23dg)' stroke='%231CA39E' stroke-width='10'/>
    <text x='29' y='75' font-family='sans-serif' font-size='22' font-weight='900' fill='%231CA39E' opacity='0.7' text-anchor='middle'>P</text>
    <text x='55' y='57' font-family='sans-serif' font-size='22' font-weight='900' fill='%231CA39E' opacity='0.85' text-anchor='middle'>G</text>
    <text x='81' y='39' font-family='sans-serif' font-size='22' font-weight='900' fill='%231CA39E' text-anchor='middle'>H</text>
    <rect x='20' y='85' width='18' height='32' rx='3' fill='%231CA39E' opacity='0.4'/>
    <rect x='45' y='70' width='18' height='47' rx='3' fill='%231CA39E' opacity='0.7'/>
    <rect x='70' y='55' width='18' height='62' rx='3' fill='%231CA39E' opacity='1'/>
</svg>
"""

# Codificación compatible
favicon_data = f"data:image/svg+xml,{favicon_svg.replace(' ', '%20').replace('#', '%23')}"

st.set_page_config(
    page_title="PGH · Plataforma de Gestión de Honorarios",
    page_icon=favicon_data,
    layout="centered"
)

# --- OCULTAR TEXTO "PRESS ENTER TO APPLY" ---
st.markdown("""
    <style>
        [data-testid="InputInstructions"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------

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

/* ── Selectbox (Estilo Botón Final) ── */
.stSelectbox > div > div {{
  background: linear-gradient(180deg, #FFFFFF 0%, #F8F9FA 100%) !important;
  border: 1.5px solid rgba(28,163,158,0.5) !important;
  border-radius: 16px !important;
  color: #1a1040 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important; /* <--- Fuerza la manito en la caja */
}}

/* Efecto al pasar el mouse por encima (Hover) */
.stSelectbox > div > div:hover {{
  border-color: #1ca39e !important;
  box-shadow: 0 4px 8px rgba(28,163,158,0.15) !important;
  transform: translateY(-1px);
}}

/* Ocultar la rayita de escritura y forzar la manito sobre el texto */
.stSelectbox input {{
  caret-color: transparent !important;
  cursor: pointer !important; /* <--- Fuerza la manito sobre las letras */
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
  font-family: 'DM Sans', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: {C_TEXT};
  line-height: 1.3;
  letter-spacing: 0px;
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
  font-family: 'DM Sans', sans-serif;
  font-size: clamp(2rem, 6vw, 2.6rem);
  font-weight: 700;
  color: {C_ACCENT2};
  letter-spacing: 0px;
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

/* --- ARREGLO PARA MODO CLARO (FORZAR VISIBILIDAD) --- */
.stCaption, .stMarkdown em, .stMarkdown p {{
    color: #9BA8B5 !important;
}}

.stNumberInput label, .stTextInput label, .stSelectbox label {{
    color: #9BA8B5 !important;
}}

.pgh-result-sub {{
    color: #9BA8B5 !important;
}}

footer {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN PWA (IDENTIDAD INVISIBLE) ---
st.markdown(f"""
    <link rel="manifest" href="https://raw.githubusercontent.com/chekelito/pgh/main/manifest.json">
    <meta name="theme-color" content="#1CA39E">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/chekelito/pgh/main/logo_pgh.jpg">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="PGH">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
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

def calcular_dias_restantes(email):
    """Calcula cuántos días le quedan al usuario Pro."""
    try:
        from supabase_client import get_client
        supabase = get_client()
        
        # 1. Buscamos en Supabase cuándo se registró este usuario
        res = supabase.table("usuarios").select("fecha_registro").eq("email", email).execute()
        
        if res.data:
            # 2. Si lo encontramos, extraemos esa fecha
            fecha_str = res.data[0]["fecha_registro"]
            fecha_registro = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            
            # 3. Le sumamos 30 días de suscripción
            fecha_expiracion = fecha_registro + timedelta(days=30)
            
            # 4. Vemos la diferencia entre la fecha de expiración y el día de hoy
            dias_restantes = (fecha_expiracion - date.today()).days
            
            # 5. Entregamos el resultado (usamos max para que nunca dé números negativos)
            return max(0, dias_restantes) 
    except Exception as e:
        print(f"Error al calcular días: {e}")
        
    # Si algo falla, por defecto decimos 30
    return 30

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
    story += [lt, sub, HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=16)]
    story += [Spacer(1,16)]
    story += [Paragraph("<b><font size=22>Desglose de Honorarios</font></b>", styles["Normal"]), Spacer(1,20)]
    story += [Paragraph(f"<font color='#9BA8B5' size=10>Trabajador: {nombre} · AFP: {r['afp']}</font>", styles["Normal"]), Spacer(1,28)]
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
    story += [HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=16)]
    story += [Spacer(1,16)]
    story += [Paragraph(f"<b><font size=22>Reporte Anual {anio}</font></b>", styles["Normal"]), Spacer(1,20)]
    story += [Paragraph(f"<font color='#9BA8B5' size=10>Trabajador: {nombre}</font>", styles["Normal"]), Spacer(1,28)]
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
        # Limpiamos la fecha para que solo muestre Día/Mes/Año
        fecha_limpia = pd.to_datetime(row["fecha"]).strftime("%d/%m/%Y")
        
        hd.append([fecha_limpia, clp(row["liquido"]), clp(row["bruto"]), str(row["afp"]), clp(row["total_cotizaciones"]), clp(row["balance_renta"])])
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

def conversion_excel(df_input):
    """Convierte un DataFrame a Excel quitando las horas de las fechas."""
    # Hacemos una copia para no alterar los datos originales de la app
    df_temp = df_input.copy()
    
    # Si existe la columna 'fecha', la transformamos a solo texto (DD-MM-YYYY)
    if 'fecha' in df_temp.columns:
        # Convertimos a datetime por si acaso y luego a formato limpio
        df_temp['fecha'] = pd.to_datetime(df_temp['fecha']).dt.strftime('%d-%m-%Y')
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_temp.to_excel(writer, index=False, sheet_name='Datos_PGH')
    return output.getvalue()

# ── Estado de sesión ──────────────────────────────────────────────────────────
defs = {
    "pantalla": "free", "usuario_email": None, "usuario_nombre": None,
    "es_pro": False, "resultado": None, "codigo_validado": None,
    "mostrar_bienvenida": False, "es_primera_vez": False,
    "calculos_free": 0,
}
for k, v in defs.items():
    if k not in st.session_state:
        st.session_state[k] = v

valor_uf = obtener_uf()

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c3 = st.columns([4, 1])
# --- SUBIR CABECERA Y ELIMINAR ESPACIO SUPERIOR ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)

with c1:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:16px;padding:4px 0">
    <svg width="48" height="56" viewBox="0 -5 110 160" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0; margin-top:-3px"><defs><linearGradient id="dg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{{C_ACCENT2}}"/><stop offset="100%" stop-color="{{C_ACCENT1}}"/></linearGradient></defs><rect width="100" height="150" rx="15" fill="none" stroke="url(#dg)" stroke-width="6"/><rect x="25" y="80" width="12" height="40" rx="4" fill="url(#dg)"/><rect x="45" y="60" width="12" height="60" rx="4" fill="url(#dg)"/><rect x="65" y="30" width="12" height="90" rx="4" fill="url(#dg)"/><circle cx="31" cy="70" r="3" fill="url(#dg)"/><circle cx="51" cy="50" r="3" fill="url(#dg)"/><circle cx="71" cy="20" r="3" fill="url(#dg)"/></svg>
    <div>
    <div style="font-family:'Syne',sans-serif;font-size:1.75rem;font-weight:800;background:linear-gradient(135deg,{{C_ACCENT2}},{{C_ACCENT1}});-webkit-background-clip:text;-webkit-text-fill-color:transparent">PGH</div>
    <div style="font-size:0.7rem;color:{{C_MUTED}};letter-spacing:1.5px;text-transform:uppercase;margin-top:2px">Plataforma de Gestión de Honorarios</div>
    </div></div>""", unsafe_allow_html=True)
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

# --- 1. FUNCIÓN DE LA VENTANA ---
@st.dialog("📲 Instalar PGH App")
def modal_instalacion():
    st.markdown(f"""
    <div style="font-size: 0.95rem; color: {C_TEXT}; line-height: 1.6;">
        <p>Para llevar <b>PGH</b> en tu celular como una App real:</p>
        <hr style="border-color: rgba(28,163,158,0.2)">
        <p><b>iPhone (Safari) 🍎:</b><br>
        1. Toca <b>Compartir</b> (el cuadrado con la flecha ↑ abajo).<br>
        2. Elige <b>'Agregar a la pantalla de inicio'</b>.</p>
        <p><b>Android (Chrome) 🤖:</b><br>
        1. Toca los tres puntos (⋮) arriba.<br>
        2. Elige <b>'Instalar aplicación'</b>.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. FILA DE INFORMACIÓN (Ajustada para Celular) ---
c_izq, c_der = st.columns([3, 1]) 

with c_izq:
    # Le quitamos el margin-top negativo para que no choque en el celular
    st.markdown(f'<div class="uf-pill"><span class="uf-dot"></span>UF hoy: ${valor_uf:,.0f}</div>', unsafe_allow_html=True)

with c_der:
    st.markdown(f"""
        <style>
        div[data-testid="stColumn"]:nth-of-type(2) button {{
            background-color: transparent !important;
            border: 1px solid rgba(28, 163, 158, 0.4) !important;
            border-radius: 20px !important;
            color: #1CA39E !important;
            transition: all 0.3s ease !important;
        }}
        div[data-testid="stColumn"]:nth-of-type(2) button:hover {{
            border-color: #1CA39E !important;
            background-color: rgba(28, 163, 158, 0.1) !important;
        }}
        /* Esto ayuda a que en el celular haya un espacio sutil entre ambos */
        @media (max-width: 600px) {{
            div[data-testid="stColumn"]:nth-of-type(2) {{
                margin-top: 10px; 
            }}
        }}
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("📲 Instalar App", use_container_width=True):
        modal_instalacion()

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
        # Llamamos a la función que acabas de crear
        dias_restantes = calcular_dias_restantes(st.session_state.usuario_email)
        
        # Colores por defecto (Turquesa/Gris)
        color_pildora = C_MUTED
        borde_pildora = "rgba(28,163,158,0.2)"
        fondo_pildora = "rgba(28,163,158,0.1)"
        icono = "⏳"
        
        # Lógica de urgencia
        if dias_restantes <= 3:
            color_pildora = C_DANGER # Rojo
            borde_pildora = "rgba(255,75,75,0.4)"
            fondo_pildora = "rgba(255,75,75,0.15)"
            icono = "⚠️"
        elif dias_restantes <= 7:
            color_pildora = "#FFD580" # Naranja
            borde_pildora = "rgba(255,165,0,0.4)"
            fondo_pildora = "rgba(255,165,0,0.1)"

        nombre = st.session_state.usuario_nombre.split()[0]
        
        # Imprimimos en pantalla
        st.markdown(f'''
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 16px;">
                <span style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700;color:{C_TEXT}">{nombre}</span>
                <span class="pro-badge">PRO</span>
                <span style="color: {color_pildora}; font-size: 0.75rem; background: {fondo_pildora}; padding: 3px 10px; border-radius: 99px; border: 1px solid {borde_pildora}; font-weight: 500;">
                    {icono} {dias_restantes} días restantes
                </span>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('<span class="section-tag">Calculadora</span>', unsafe_allow_html=True)

    # El Guardia de Seguridad (Muro de pago)
    if not st.session_state.es_pro and st.session_state.calculos_free >= 3:
        st.warning("🚨 **¡Límite de prueba alcanzado!** Has usado tus 3 cálculos gratuitos.")
        st.info("Para seguir calculando sin límites, guardar tu historial y descargar reportes automáticos, actualízate a **PGH Pro**.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("👑 Desbloquear acceso sin límites", type="primary", use_container_width=True):
            st.session_state.pantalla = "compra"
            st.rerun()
            
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    else:
        # Si es Pro, o si es Free pero lleva menos de 3, muestra la calculadora
        if not st.session_state.es_pro:
            restantes = 3 - st.session_state.calculos_free
            st.markdown(f"<p style='color:#9BA8B5; font-size:0.85rem; margin-bottom: 15px;'>🎁 <i>Te quedan {restantes} cálculos de prueba gratis</i></p>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            liquido = st.number_input(
                "💵 Líquido que quiero recibir (CLP)",
                min_value=10_000, max_value=50_000_000,
                value=500_000, step=10_000, format="%d"
            )
        with c2:
            afp = st.selectbox("🏦 AFP", options=obtener_afps())

        st.markdown(f"<p style='color:#9BA8B5; font-size:0.82rem;'>Monto ingresado: <b>{clp(liquido)}</b></p>", unsafe_allow_html=True)

        if st.button("Calcular →", type="primary", use_container_width=True):
            # Sumamos 1 al contador si el usuario NO es pro
            if not st.session_state.es_pro:
                st.session_state.calculos_free += 1
            
            # Hacemos el cálculo
            st.session_state.resultado = calcular_sueldo_inverso(float(liquido), afp, valor_uf)
            st.rerun() # Recarga la pantalla para actualizar el contador visual


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
    st.markdown("<p style='color:#9BA8B5; font-size:0.82rem; opacity: 0.8; margin-top:10px;'>🔓 Desbloquea para ver tus números reales</p>", unsafe_allow_html=True)
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
    st.markdown(f'<h2 style="font-family:Syne,sans-serif;font-weight:800;margin-bottom:4px;color:{C_TEXT}">🔑 Obtén tu acceso Pro</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{C_MUTED};font-size:0.95rem;margin-bottom:24px">Desbloquea el historial ilimitado y reportes PDF al instante.</p>', unsafe_allow_html=True)
    
    # Texto de invitación limpio sin cajas rotas
    st.markdown(f'<p style="color:{C_TEXT}; font-weight:600; font-size:1.1rem; margin-top:10px; margin-bottom:15px; text-align:center;">Consigue tu código de acceso aquí 👇</p>', unsafe_allow_html=True)
    
    # Link de WhatsApp
    mensaje_wa = "¡Hola! Quiero obtener mi código de acceso Pro para PGH 🚀"
    link_wa = f"https://wa.me/56937896790?text={mensaje_wa.replace(' ', '%20')}"
    
    # Usamos un botón de link HTML directo para que tome los colores turquesa de tu CSS
    st.markdown(f'''
        <a href="{link_wa}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, {C_ACCENT2}, {C_ACCENT1}); color: white; padding: 14px 24px; border-radius: 12px; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem; text-decoration: none; transition: opacity 0.2s;">
            📲 Solicitar código por WhatsApp
        </a>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
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
    st.markdown(f'<div style="text-align:center;margin-bottom:24px"><div style="font-size:3rem">✅</div><h2 style="font-family:Syne,sans-serif;font-weight:800;color:{C_TEXT}">¡Código válido!</h2><p style="color:{C_MUTED}">Crea tu cuenta segura para activar el Pro.</p></div>', unsafe_allow_html=True)
    
    nom = st.text_input("Tu nombre completo", placeholder="Juan Pérez")
    eml = st.text_input("Tu email", placeholder="juan@gmail.com")
    # Aquí agregamos el campo para que invente su contraseña:
    pwd = st.text_input("Crea una contraseña", type="password", placeholder="••••••••")
    
    if st.button("Activar mi cuenta →", type="primary", use_container_width=True):
        if nom and eml and pwd:
            # Aquí le enviamos la contraseña (pwd) a la función que modificaste antes
            if activar_codigo(st.session_state.codigo_validado, eml, nom, pwd):
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
            st.warning("Por favor completa todos los campos, incluyendo tu nueva contraseña.")

# ── LOGIN DIRECTO ─────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "login_directo":
    st.markdown(f'<h2 style="font-family:Syne,sans-serif;font-weight:800;margin-bottom:4px;color:{C_TEXT}">👤 Iniciar sesión</h2><p style="color:{C_MUTED};margin-bottom:24px">Ingresa tus credenciales para acceder a PGH Pro.</p>', unsafe_allow_html=True)
    
    eml = st.text_input("Tu email", placeholder="juan@gmail.com")
    # Agregamos el campo de contraseña
    pwd = st.text_input("Tu contraseña", type="password", placeholder="••••••••")
    
    if st.button("Ingresar →", type="primary", use_container_width=True):
        if eml and pwd:
            # Usamos la nueva función que verifica email Y contraseña
            if validar_login(eml, pwd):
                # Si es válido, traemos su nombre para la bienvenida
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
                st.error("❌ Email o contraseña incorrectos.")
        else:
            st.warning("Por favor ingresa tu email y contraseña.")
            
    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "free"
        st.rerun()
            
# ── PRO ───────────────────────────────────────────────────────────────────────
elif st.session_state.pantalla == "pro":
    # 1. Calculamos los días apenas intenta entrar a la pantalla Pro
    dias_restantes = calcular_dias_restantes(st.session_state.usuario_email)

    # 2. EL GUARDIA DE SEGURIDAD: Si no le quedan días, bloqueamos
    if dias_restantes <= 0:
        st.markdown(f'''
            <div style="text-align:center; margin-top: 40px; margin-bottom: 24px;">
                <div style="font-size:3.5rem; margin-bottom: 10px;">⏳</div>
                <h2 style="font-family:'Syne',sans-serif; font-weight:800; color:{C_TEXT};">Tu suscripción expiró</h2>
                <p style="color:{C_MUTED}; font-size:1rem; margin-top: 10px;">
                    Tu mes de acceso a <b>PGH Pro</b> ha finalizado. Renueva ahora para recuperar tu historial guardado, seguir descargando reportes y calcular sin límites.
                </p>
            </div>
        ''', unsafe_allow_html=True)

        # Link de WhatsApp con mensaje pre-escrito
        mensaje_renovacion = "¡Hola! Mi suscripción Pro de PGH expiró y quiero renovarla 🚀"
        link_renovacion = f"https://wa.me/56937896790?text={mensaje_renovacion.replace(' ', '%20')}"

        st.markdown(f'''
            <a href="{link_renovacion}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, {C_ACCENT2}, {C_ACCENT1}); color: white; padding: 14px 24px; border-radius: 12px; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.05rem; text-decoration: none; transition: opacity 0.2s; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(28,163,158,0.2);">
                📲 Renovar PGH PRO por WhatsApp
            </a>
        ''', unsafe_allow_html=True)

        # Botón para volver a la versión gratis
        if st.button("← Volver a la versión gratuita", use_container_width=True):
            st.session_state.es_pro = False
            st.session_state.pantalla = "free"
            st.rerun()

        # MAGIA: st.stop() detiene el código aquí mismo para que no vea nada más.
        st.stop()
        
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
        st.markdown(f"<div style='font-size:0.85rem; color:#FFFFFF; margin-bottom:15px'>Base imponible: {clp(r['base_imponible'])} &middot; <span style='color:#00C853'>Tope legal (90 UF): {clp(r['tope_legal'])}</span></div>", unsafe_allow_html=True)
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
        # --- ACCIONES PRO (Guardar, PDF, Excel) ---
        c_save, c_pdf, c_xls = st.columns(3)
        with c_save:
            if st.button("💾 Guardar", type="primary", use_container_width=True):
                datos_b = {
                    "liquido": r["liquido_deseado"], "bruto": r["bruto"], "afp": r["afp"],
                    "retencion_sii": r["retencion_sii"], "base_imponible": r["base_imponible"],
                    "pago_salud": r["pago_salud"], "pago_afp": r["pago_afp"],
                    "pago_accidentes": r["pago_accidentes"], "total_cotizaciones": r["total_cotizaciones"],
                    "balance_renta": r["balance_renta"],
                }
                if guardar_boleta(st.session_state.usuario_email, datos_b):
                    st.success("¡Guardada!")
                    st.rerun()
        with c_pdf:
            st.download_button(
                label="📄 PDF",
                data=pdf_desglose(r, st.session_state.usuario_nombre, valor_uf),
                file_name=f"PGH_desglose_{date.today().strftime('%d-%m-%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with c_xls:
            # Creamos un pequeño Excel con los datos del cálculo actual
            # Convertimos el diccionario 'r' en una lista para que Pandas lo lea bien
            df_actual = pd.DataFrame([r])
            st.download_button(
                label="📊 Excel",
                data=conversion_excel(df_actual),
                file_name=f"PGH_desglose_{date.today().strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    st.divider()

    # Historial
    st.markdown('<span class="section-tag">Historial de Boletas</span>', unsafe_allow_html=True)
    
    # 1. Traer datos
    todas_las_boletas = obtener_boletas(st.session_state.usuario_email)
    
    if todas_las_boletas:
        df_full = pd.DataFrame(todas_las_boletas)
        df_full["fecha"] = pd.to_datetime(df_full["fecha"])
        
        # 2. Crear los selectores de filtro
        c1, c2 = st.columns(2)
        with c1:
            anios = sorted(df_full["fecha"].dt.year.unique(), reverse=True)
            anio_sel = st.selectbox("📅 Año", options=anios)
        with c2:
            meses_nombres = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            # Calculamos el mes actual (1 a 12) y le restamos 1 porque las listas empiezan a contar desde 0
            mes_actual = date.today().month
            mes_sel = st.selectbox("🗓️ Mes", options=list(meses_nombres.values()), index=mes_actual - 1)
            # Convertir nombre de mes a número
            mes_num = [k for k, v in meses_nombres.items() if v == mes_sel][0]

        # 3. Filtrar el DataFrame
        df = df_full[(df_full["fecha"].dt.year == anio_sel) & (df_full["fecha"].dt.month == mes_num)] # Se sobreescribe 'df' para que el resto de tu código funcione igual
        
        # Filtrado final para la tabla
        boletas = df.to_dict('records') 
        
        if not boletas:
            st.info(f"No hay boletas registradas para {mes_sel} de {anio_sel}.")
        
        # --- A partir de aquí sigue tu código original de la tabla (<tr>...) ---
    if boletas:
        df = pd.DataFrame(boletas)

          # Tabla mobile-friendly: solo columnas esenciales
        filas = ""
        for _, row in df.iterrows():
          bal = row["balance_renta"]
          color = "#00C853" if bal >= 0 else "#FF4B4B"
          icono = "🟢" if bal >= 0 else "🔴"
          # Formateamos la fecha para que solo muestre Día/Mes/Año
          fecha_limpia = row['fecha'].strftime("%d/%m/%Y") 
          
          filas += f"""<tr>
              <td>{fecha_limpia}</td>
              <td>{clp(row['liquido'])}</td>
              <td>{clp(row['bruto'])}</td>
              <td style="color:{color};font-weight:600">{icono} {clp(bal)}</td>
          </tr>"""
        st.markdown(f"""
    <div style="overflow-x:auto;border-radius:14px;border:1px solid rgba(28,163,158,0.2)">
    <table style="width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;font-size:0.88rem">
        <thead>
            <tr style="background:rgba(35,20,91,0.8);color:#9BA8B5;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px">
                <th style="padding:12px 16px;text-align:left;font-weight:600">Fecha</th>
                <th style="padding:12px 16px;text-align:right;font-weight:600">Líquido</th>
                <th style="padding:12px 16px;text-align:right;font-weight:600">Bruto</th>
                <th style="padding:12px 16px;text-align:right;font-weight:600">Balance</th>
            </tr>
        </thead>
        <tbody style="color:#FFFFFF">
            {filas}
        </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

        # Botón reporte anual
        st.markdown("<br>", unsafe_allow_html=True)
        # --- REPORTES ANUALES (PDF + EXCEL) ---
        c_anual_pdf, c_anual_xls = st.columns(2)
        
        with c_anual_pdf:
            st.download_button(
                label="📑 Reporte Anual PDF",
                data=pdf_reporte(boletas, st.session_state.usuario_nombre),
                file_name=f"PGH_Reporte_{date.today().year}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            
        with c_anual_xls:
            # Convertimos la lista de boletas filtradas a un DataFrame
            df_anual = pd.DataFrame(boletas)
            
            # Limpieza: quitamos columnas técnicas de la base de datos que al usuario no le sirven
            columnas_a_quitar = ['id', 'usuario_email', 'created_at']
            for col in columnas_a_quitar:
                if col in df_anual.columns:
                    df_anual = df_anual.drop(columns=[col])
            
            st.download_button(
                label="📈 Reporte Anual Excel",
                data=conversion_excel(df_anual),
                file_name=f"PGH_Reporte_{date.today().year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        # --- NUEVA SECCIÓN DE ELIMINAR (DIÁLOGO MODAL) ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        @st.dialog("🗑️ Eliminar una boleta")
        def modal_eliminar():
            st.markdown("<p style='font-size:0.95rem; color:#9BA8B5;'>Selecciona la boleta que deseas eliminar permanentemente de tu historial:</p>", unsafe_allow_html=True)
            opciones_borrar = {f"{b['fecha']} - Líquido: {clp(b['liquido'])}": b['id'] for b in boletas}
            
            boleta_sel = st.selectbox(
                "Boletas guardadas",
                options=list(opciones_borrar.keys()),
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Confirmar Eliminación", type="primary", use_container_width=True):
                id_a_borrar = opciones_borrar[boleta_sel]
                if eliminar_boleta(id_a_borrar):
                    st.success("✅ Boleta eliminada correctamente.")
                    st.rerun()
                else:
                    st.error("❌ Error al intentar eliminar.")

        if st.button("⚙️ Opciones de historial (Eliminar boletas)", use_container_width=True):
            modal_eliminar()
        # ----------------------------------------------------

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
            xaxis=dict(gridcolor="rgba(28,163,158,0.1)", tickfont=dict(color=C_TEXT, size=12), title="", fixedrange=False),
            yaxis=dict(gridcolor="rgba(28,163,158,0.12)", tickfont=dict(color=C_MUTED, size=11),
                       tickprefix="$", tickformat=",.0f", title="", rangemode="nonnegative", fixedrange=False),
            margin=dict(t=50, b=50, l=70, r=20),
            height=340,
            bargap=0.3,
            dragmode="pan"
        )
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        # Gráfico 2: Balance Acumulado (Estilo Semáforo - Muy fácil de entender)
        ds = df.sort_values("fecha").copy()
        ds["balance_acumulado"] = ds["balance_renta"].cumsum()
        ds["fecha_str"] = ds["fecha"].dt.strftime("%d/%b")
        
        # Asignamos colores: Verde si es positivo, Rojo si es negativo
        colores_bal = ["#00C853" if v >= 0 else "#FF4B4B" for v in ds["balance_acumulado"]]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=ds["fecha_str"],
            y=ds["balance_acumulado"],
            marker_color=colores_bal,
            text=[clp(v) for v in ds["balance_acumulado"]],
            textposition="outside",
            textfont=dict(color=C_TEXT, size=11),
        ))

        fig2.update_layout(
            title=dict(text="Mi saldo acumulado para Abril", font=dict(color=C_TEXT, size=15, family="Syne")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C_MUTED, family="DM Sans"),
            xaxis=dict(showgrid=False, tickfont=dict(color=C_TEXT)),
            yaxis=dict(gridcolor="rgba(28,163,158,0.1)", tickprefix="$", tickfont=dict(color=C_MUTED)),
            margin=dict(t=50, b=40, l=60, r=20),
            height=320,
            showlegend=False,
            dragmode=False
        )
        # Añadimos línea de equilibrio
        fig2.add_hline(y=0, line_width=2, line_color="white", opacity=0.3)
        
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    elif not todas_las_boletas:
        # Solo mostramos esto si la base de datos completa está vacía, para no duplicar el mensaje del mes.
        st.info("Aún no tienes boletas guardadas. Calcula y guarda tu primera boleta arriba. 👆")
    
    # ── PANEL DE ADMINISTRACIÓN (Versión Diálogo Pro) ──
    if st.session_state.usuario_email == "admin@gmail.com":
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<span class="section-tag" style="color:#FF4B4B">🔐 Centro de Control Admin</span>', unsafe_allow_html=True)
        
        @st.dialog("Gestión de Usuarios (Admin)")
        def modal_admin():
            st.markdown("<p style='font-size:0.95rem; color:#9BA8B5; margin-bottom: 20px;'>Lista de usuarios registrados y estado de suscripción:</p>", unsafe_allow_html=True)
            
            usuarios_lista = obtener_todos_usuarios()
            if usuarios_lista:
                for u in usuarios_lista:
                    if u['email'] == st.session_state.usuario_email:
                        continue
                    
                    with st.container():
                        c_info, c_btn = st.columns([2, 1])
                        with c_info:
                            d = calcular_dias_restantes(u['email'])
                            color_t = "#00C853" if d > 0 else "#FF4B4B"
                            st.markdown(f"**{u['nombre']}**<br><small>{u['email']}</small><br><small style='color:{color_t}; font-weight:600'>{d} días restantes</small>", unsafe_allow_html=True)
                        with c_btn:
                            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                            if st.button("Renovar", key=f"mod_ren_{u['email']}", use_container_width=True):
                                if renovar_suscripcion_usuario(u['email']):
                                    st.success(f"¡{u['nombre']} renovado!")
                                    st.rerun()
                        st.divider()
            else:
                st.info("No hay otros usuarios registrados.")

        if st.button("🔑 Abrir Panel de Renovaciones", use_container_width=True):
            modal_admin()
    
    st.divider()
    st.markdown(disclaimer(), unsafe_allow_html=True)


