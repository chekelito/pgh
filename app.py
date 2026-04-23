"""
app.py
PGH · Plataforma de Gestión de Honorarios
Versión Free + Pro · Diseño completo con paleta oficial
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from calculadora import calcular_sueldo_inverso, obtener_afps
from supabase_client import (
    verificar_codigo, activar_codigo, es_usuario_pro,
    guardar_boleta, obtener_boletas,
)

st.set_page_config(page_title="PGH · Calculadora de Honorarios", page_icon="📊", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
.stApp {
    background: #160D18;
    background-image:
        radial-gradient(ellipse 60% 50% at 10% 20%, rgba(35,20,91,0.7) 0%, transparent 70%),
        radial-gradient(ellipse 50% 40% at 90% 80%, rgba(2,111,110,0.35) 0%, transparent 60%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 760px; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; color: #FFFFFF; }
.pgh-card { background: rgba(35,20,91,0.35); backdrop-filter: blur(20px); border: 1px solid rgba(28,163,158,0.2); border-radius: 20px; padding: 28px; margin-bottom: 16px; }
.metric-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(28,163,158,0.2); border-radius: 14px; padding: 16px; margin-bottom: 8px; }
.metric-label { font-size: 0.72rem; color: #9BA8B5; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700; color: #FFFFFF; }
.metric-value.accent { color: #1CA39E; }
.result-hero { background: linear-gradient(135deg, rgba(28,163,158,0.15), rgba(2,111,110,0.1)); border: 1px solid rgba(28,163,158,0.4); border-radius: 18px; padding: 32px; text-align: center; margin-bottom: 20px; }
.result-label { font-size: 0.72rem; color: #9BA8B5; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
.result-value { font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #1CA39E 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; line-height: 1; }
.result-sub { font-size: 0.82rem; color: #9BA8B5; margin-top: 8px; }
.blurred-value { filter: blur(5px); user-select: none; font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #9BA8B5; }
.pro-badge { display: inline-block; background: linear-gradient(135deg, #1CA39E, #026F6E); color: white; font-size: 0.58rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 3px 10px; border-radius: 99px; vertical-align: middle; margin-left: 8px; }
.hero-tag { display: inline-block; background: rgba(28,163,158,0.12); border: 1px solid rgba(28,163,158,0.3); color: #1CA39E; font-size: 0.68rem; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; padding: 5px 14px; border-radius: 99px; margin-bottom: 16px; }
.uf-pill { display: inline-flex; align-items: center; gap: 7px; background: rgba(28,163,158,0.08); border: 1px solid rgba(28,163,158,0.2); border-radius: 99px; padding: 5px 14px; font-size: 0.75rem; color: #9BA8B5; }
.section-title { font-family: 'Syne', sans-serif; font-size: 0.68rem; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: #9BA8B5; margin: 24px 0 12px; }
.welcome-banner { background: linear-gradient(135deg, rgba(28,163,158,0.2), rgba(2,111,110,0.15)); border: 1px solid rgba(28,163,158,0.4); border-radius: 14px; padding: 18px 22px; margin-bottom: 24px; }
.welcome-banner h3 { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; margin-bottom: 3px; }
.welcome-banner p { font-size: 0.82rem; color: #9BA8B5; margin: 0; }
.logo-text { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #1CA39E, #026F6E); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.logo-sub { font-size: 0.6rem; color: #9BA8B5; letter-spacing: 2px; text-transform: uppercase; }
.benefit-item { background: rgba(28,163,158,0.07); border: 1px solid rgba(28,163,158,0.15); border-radius: 12px; padding: 13px 16px; font-size: 0.85rem; margin-bottom: 8px; }
.precio-box { text-align: center; padding: 20px; background: rgba(28,163,158,0.08); border: 1px solid rgba(28,163,158,0.25); border-radius: 16px; margin: 20px 0; }
.precio-valor { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #1CA39E, #026F6E); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.precio-sub { font-size: 0.78rem; color: #9BA8B5; margin-top: 4px; }
div[data-baseweb="input"] > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(28,163,158,0.25) !important; border-radius: 12px !important; }
div[data-baseweb="select"] > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(28,163,158,0.25) !important; border-radius: 12px !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #1CA39E, #026F6E) !important; border: none !important; border-radius: 12px !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; }
.stButton > button[kind="secondary"] { background: transparent !important; border: 1px solid rgba(28,163,158,0.3) !important; border-radius: 12px !important; color: #9BA8B5 !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def obtener_uf() -> float:
    try:
        hoy = date.today().strftime("%d-%m-%Y")
        r = requests.get(f"https://mindicador.cl/api/uf/{hoy}", timeout=5)
        return float(r.json()["serie"][0]["valor"])
    except Exception:
        return 40013.88

def clp(v: float) -> str:
    return f"${v:,.0f}".replace(",", ".")


def generar_pdf_desglose(r: dict, nombre: str, valor_uf: float) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    CA = colors.HexColor("#1CA39E"); CD = colors.HexColor("#160D18"); CS = colors.HexColor("#23145B")
    CM = colors.HexColor("#09456C"); CMT = colors.HexColor("#9BA8B5"); CW = colors.white
    CSU = colors.HexColor("#00C853"); CDG = colors.HexColor("#FF4B4B")
    sty = getSampleStyleSheet()
    ss = ParagraphStyle("s", fontName="Helvetica", fontSize=8, textColor=CMT, spaceAfter=2)
    sc = ParagraphStyle("c", fontName="Helvetica", fontSize=8, textColor=CMT, alignment=TA_CENTER)
    sn = ParagraphStyle("n", fontName="Helvetica", fontSize=9, textColor=CW, spaceAfter=4)
    sb = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=8, textColor=CA, spaceAfter=8, letterSpacing=1.5)
    story = []
    ht = Table([[
        Paragraph("<b><font color='#1CA39E' size='22'>PGH</font></b>", sty["Normal"]),
        Paragraph(f"<font color='#9BA8B5' size='7'>PLATAFORMA DE GESTIÓN DE HONORARIOS<br/>Informe: {date.today().strftime('%d/%m/%Y')}</font>",
                  ParagraphStyle("r", fontName="Helvetica", fontSize=7, textColor=CMT, alignment=TA_RIGHT))
    ]], colWidths=[9*cm, 8*cm])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CS),("BOX",(0,0),(-1,-1),0.5,CA),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [ht, Spacer(1,0.4*cm), Paragraph("DESGLOSE DE HONORARIOS", sb),
              Paragraph(f"Profesional: <b>{nombre}</b> · AFP: <b>{r['afp']}</b> · UF: <b>{clp(valor_uf)}</b>", sn),
              Spacer(1,0.3*cm)]
    bt = Table([[Paragraph("<font color='#9BA8B5' size='8'>MONTO A BOLETEAR</font>", sty["Normal"]),
                 Paragraph(f"<font color='#1CA39E' size='20'><b>{clp(r['bruto'])}</b></font>", sty["Normal"])]],
               colWidths=[8*cm,9*cm])
    bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CS),("BOX",(0,0),(-1,-1),1,CA),
        ("TOPPADDING",(0,0),(-1,-1),16),("BOTTOMPADDING",(0,0),(-1,-1),16),
        ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [bt, Spacer(1,0.4*cm), Paragraph("DESGLOSE COMPLETO", sb)]
    td = [["Concepto","Valor"],
          ["Líquido deseado", clp(r["liquido_deseado"])],
          ["Retención SII (15,25%)", clp(r["retencion_sii"])],
          ["Líquido final confirmado", clp(r["liquido_final"])],
          ["Base imponible (80%)", clp(r["base_imponible"])],
          ["Tope legal (90 UF)", clp(r["tope_legal"])],
          ["Salud (7%)", clp(r["pago_salud"])],
          [f"AFP + SIS ({r['tasa_afp']*100:.2f}%)", clp(r["pago_afp"])],
          ["Accidentes (0,9%)", clp(r["pago_accidentes"])],
          ["TOTAL COTIZACIONES", clp(r["total_cotizaciones"])]]
    t = Table(td, colWidths=[12*cm,5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),CM),("TEXTCOLOR",(0,0),(-1,0),CW),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),("TEXTCOLOR",(0,1),(-1,-1),CW),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#1A0E1F"),colors.HexColor("#160D18")]),
        ("ALIGN",(1,0),(1,-1),"RIGHT"),("FONTNAME",(0,9),(-1,9),"Helvetica-Bold"),("TEXTCOLOR",(0,9),(-1,9),CA),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("BOX",(0,0),(-1,-1),0.5,CA),("LINEBELOW",(0,0),(-1,0),0.5,CA),("LINEBELOW",(0,-1),(-1,-1),0.5,CA)]))
    story += [t, Spacer(1,0.4*cm), Paragraph("BALANCE OPERACIÓN RENTA", sb)]
    balance = r["balance_renta"]
    bc = CSU if balance >= 0 else CDG
    bi = "DEVOLUCIÓN ESTIMADA" if balance >= 0 else "DIFERENCIA A PAGAR EN ABRIL"
    bm = "El SII te devolverá esta diferencia en la Operación Renta de abril." if balance >= 0 \
         else "La retención no alcanza. Deberás pagar esta diferencia en abril."
    bgt = colors.HexColor("#0D1A0D") if balance >= 0 else colors.HexColor("#1A0D0D")
    balt = Table([[Paragraph(f"<font color='{'#00C853' if balance>=0 else '#FF4B4B'}' size='9'><b>{bi}</b></font>", sty["Normal"])],
                  [Paragraph(f"<font color='{'#00C853' if balance>=0 else '#FF4B4B'}' size='14'><b>{clp(abs(balance))}</b></font>", sty["Normal"])],
                  [Paragraph(f"<font color='#9BA8B5' size='8'>{bm}</font>", sty["Normal"])]],
                 colWidths=[17*cm])
    balt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bgt),("BOX",(0,0),(-1,-1),0.8,bc),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story += [balt, Spacer(1,0.8*cm),
              HRFlowable(width="100%", thickness=0.5, color=CA, spaceAfter=8),
              Paragraph("⚠️ Este informe es referencial. Consulta a un contador para decisiones financieras definitivas. · PGH Chile 2026", sc)]
    doc.build(story)
    return buf.getvalue()


def generar_pdf_reporte(boletas: list, nombre: str, email: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    CA = colors.HexColor("#1CA39E"); CD = colors.HexColor("#160D18"); CS = colors.HexColor("#23145B")
    CM = colors.HexColor("#09456C"); CMT = colors.HexColor("#9BA8B5"); CW = colors.white
    CSU = colors.HexColor("#00C853"); CDG = colors.HexColor("#FF4B4B")
    sty = getSampleStyleSheet()
    sc = ParagraphStyle("c", fontName="Helvetica", fontSize=8, textColor=CMT, alignment=TA_CENTER)
    sn = ParagraphStyle("n", fontName="Helvetica", fontSize=9, textColor=CW, spaceAfter=4)
    sb = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=8, textColor=CA, spaceAfter=8, letterSpacing=1.5)
    story = []
    ht = Table([[
        Paragraph("<b><font color='#1CA39E' size='22'>PGH</font></b>", sty["Normal"]),
        Paragraph(f"<font color='#9BA8B5' size='7'>PLATAFORMA DE GESTIÓN DE HONORARIOS<br/>Reporte anual: {date.today().strftime('%d/%m/%Y')}</font>",
                  ParagraphStyle("r", fontName="Helvetica", fontSize=7, textColor=CMT, alignment=TA_RIGHT))
    ]], colWidths=[9*cm, 8*cm])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CS),("BOX",(0,0),(-1,-1),0.5,CA),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [ht, Spacer(1,0.4*cm), Paragraph("REPORTE ANUAL DE HONORARIOS", sb),
              Paragraph(f"Profesional: <b>{nombre}</b> · {email}", sn), Spacer(1,0.3*cm)]
    df = pd.DataFrame(boletas)
    res = [["TOTAL BRUTO","TOTAL LÍQUIDO","TOTAL COTIZACIONES","BALANCE TOTAL"],
           [clp(df["bruto"].sum()), clp(df["liquido"].sum()), clp(df["total_cotizaciones"].sum()), clp(df["balance_renta"].sum())]]
    rt = Table(res, colWidths=[4.25*cm]*4)
    rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),CM),("BACKGROUND",(0,1),(-1,1),CS),
        ("TEXTCOLOR",(0,0),(-1,-1),CW),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9),
        ("BOX",(0,0),(-1,-1),0.5,CA),("INNERGRID",(0,0),(-1,-1),0.3,CM)]))
    story += [rt, Spacer(1,0.4*cm), Paragraph("HISTORIAL DE BOLETAS", sb)]
    hd = [["Fecha","Líquido","Bruto","AFP","Total Cotiz.","Balance"]]
    for b in boletas:
        hd.append([b["fecha"], clp(b["liquido"]), clp(b["bruto"]), b["afp"],
                   clp(b["total_cotizaciones"]), clp(b["balance_renta"])])
    hs = [("BACKGROUND",(0,0),(-1,0),CM),("TEXTCOLOR",(0,0),(-1,0),CW),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
          ("FONTSIZE",(0,0),(-1,-1),7),("TEXTCOLOR",(0,1),(-1,-1),CW),
          ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#1A0E1F"),CD]),
          ("ALIGN",(1,0),(-1,-1),"RIGHT"),("ALIGN",(0,0),(0,-1),"LEFT"),
          ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
          ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
          ("BOX",(0,0),(-1,-1),0.5,CA),("LINEBELOW",(0,0),(-1,0),0.5,CA)]
    for i, b in enumerate(boletas, 1):
        hs.append(("TEXTCOLOR",(5,i),(5,i), CSU if b["balance_renta"] >= 0 else CDG))
    ht2 = Table(hd, colWidths=[2.5*cm,2.8*cm,2.8*cm,2*cm,3*cm,2.9*cm])
    ht2.setStyle(TableStyle(hs))
    story += [ht2, Spacer(1,0.8*cm),
              HRFlowable(width="100%", thickness=0.5, color=CA, spaceAfter=8),
              Paragraph("⚠️ Este informe es referencial. Consulta a un contador para decisiones financieras definitivas. · PGH Chile 2026", sc)]
    doc.build(story)
    return buf.getvalue()


defaults = {"pantalla":"free","usuario_email":None,"usuario_nombre":None,"es_pro":False,
            "resultado":None,"codigo_validado":None,"mostrar_bienvenida":False}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

valor_uf = obtener_uf()

# HEADER
col_logo, col_uf, col_btn = st.columns([3, 2, 1.2])
with col_logo:
    st.markdown('<div><div class="logo-text">📊 PGH</div><div class="logo-sub">Gestión de Honorarios · Chile 2026</div></div>', unsafe_allow_html=True)
with col_uf:
    st.markdown(f'<div style="padding-top:8px"><div class="uf-pill"><span style="width:6px;height:6px;border-radius:50%;background:#1CA39E;display:inline-block"></span>UF: {clp(valor_uf)}</div></div>', unsafe_allow_html=True)
with col_btn:
    if st.session_state.es_pro:
        if st.button("Salir", use_container_width=True):
            for k, v in defaults.items(): st.session_state[k] = v
            st.rerun()
    else:
        if st.button("Iniciar sesión", use_container_width=True):
            st.session_state.pantalla = "login_directo"; st.rerun()

st.markdown("<hr style='border:none;border-top:1px solid rgba(28,163,158,0.2);margin:12px 0 24px'>", unsafe_allow_html=True)

if st.session_state.pantalla in ["free", "pro"]:
    c1, c2 = st.columns(2)
    with c1:
        liquido = st.number_input("💵 Líquido que quiero recibir", min_value=10_000, max_value=50_000_000, value=500_000, step=10_000, format="%d")
    with c2:
        afp = st.selectbox("🏦 AFP", options=obtener_afps())
    if st.button("Calcular →", type="primary", use_container_width=True):
        st.session_state.resultado = calcular_sueldo_inverso(float(liquido), afp, valor_uf)

# FREE
if st.session_state.pantalla == "free":
    if st.session_state.resultado:
        r = st.session_state.resultado
        st.markdown(f'<div class="result-hero"><div class="result-label">Debes boletear</div><div class="result-value">{clp(r["bruto"])}</div><div class="result-sub">Para recibir {clp(r["liquido_deseado"])} líquidos</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔒 Vista previa desglose</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        for col,lbl in zip([c1,c2,c3],["Retención SII","Total cotizaciones","Balance Renta"]):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="blurred-value">$██████</div></div>', unsafe_allow_html=True)
        if st.button("Ver desglose completo 🔓", use_container_width=True):
            st.session_state.pantalla = "vista_previa"; st.rerun()

elif st.session_state.pantalla == "vista_previa":
    st.markdown('<div style="text-align:center;margin-bottom:24px"><div class="hero-tag">Versión Pro</div><h2 style="font-family:\'Syne\',sans-serif;font-size:1.8rem;font-weight:800;margin:8px 0">Desbloquea el desglose completo</h2><p style="color:#9BA8B5">Gestiona tus honorarios como un profesional</p></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col,lbl in zip([c1,c2,c3],["Retención SII (15,25%)","Base imponible (80%)","Salud (7%)"]):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="blurred-value">$██████</div></div>', unsafe_allow_html=True)
    c4,c5,c6 = st.columns(3)
    for col,lbl in zip([c4,c5,c6],["AFP + SIS","Accidentes (0,9%)","Balance Renta"]):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="blurred-value">{"🔴 $██████" if lbl=="Balance Renta" else "$██████"}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='margin:16px 0 8px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="benefit-item">✅ Desglose completo de cotizaciones</div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-item">✅ Balance Renta con alerta roja/verde</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="benefit-item">✅ Historial de todas tus boletas</div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-item">✅ Gráficos de ingresos y balance</div>', unsafe_allow_html=True)
    st.markdown('<div class="precio-box"><div class="precio-valor">$2.990</div><div class="precio-sub">por mes · Cancela cuando quieras</div></div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Quiero el Pro 🔓", type="primary", use_container_width=True):
            st.session_state.pantalla = "compra"; st.rerun()
    with c2:
        if st.button("← Volver", use_container_width=True):
            st.session_state.pantalla = "free"; st.rerun()

elif st.session_state.pantalla == "compra":
    st.markdown('<div class="hero-tag">Obtén tu acceso</div><h2 style="font-family:\'Syne\',sans-serif;font-size:1.6rem;font-weight:800;margin:8px 0 20px">3 pasos simples</h2>', unsafe_allow_html=True)
    st.markdown('<div class="pgh-card"><div class="metric-label" style="margin-bottom:16px">Instrucciones de pago</div><p style="margin-bottom:10px"><b>1️⃣ Transfiere $2.990</b></p><p style="color:#9BA8B5;font-size:0.88rem;margin-bottom:3px">• Banco: BancoEstado (Cuenta RUT)</p><p style="color:#9BA8B5;font-size:0.88rem;margin-bottom:3px">• RUT: 21.553.061-2</p><p style="color:#9BA8B5;font-size:0.88rem;margin-bottom:16px">• Nombre: Exequiel Zambrano</p><p style="margin-bottom:10px"><b>2️⃣ Envía el comprobante</b></p><p style="color:#9BA8B5;font-size:0.88rem;margin-bottom:16px">• 📲 WhatsApp: +56 9 5222 2772</p><p><b>3️⃣ Recibe tu código en minutos</b></p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">¿Ya tienes tu código?</div>', unsafe_allow_html=True)
    codigo_input = st.text_input("Código de acceso", placeholder="PGH-PRO-XXXX").strip().upper()
    if st.button("Activar Pro ✅", type="primary", use_container_width=True):
        if codigo_input:
            if verificar_codigo(codigo_input):
                st.session_state.codigo_validado = codigo_input; st.session_state.pantalla = "activacion"; st.rerun()
            else:
                st.error("❌ Código incorrecto o ya utilizado.")
        else: st.warning("Por favor ingresa un código.")
    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "vista_previa"; st.rerun()

elif st.session_state.pantalla == "activacion":
    st.success("✅ ¡Código válido! Crea tu cuenta para activar el Pro.")
    nombre_input = st.text_input("Tu nombre completo", placeholder="Juan Pérez")
    email_input  = st.text_input("Tu email", placeholder="juan@gmail.com")
    if st.button("Activar mi cuenta Pro 🚀", type="primary", use_container_width=True):
        if nombre_input and email_input:
            if activar_codigo(st.session_state.codigo_validado, email_input, nombre_input):
                st.session_state.es_pro = True; st.session_state.usuario_email = email_input
                st.session_state.usuario_nombre = nombre_input; st.session_state.mostrar_bienvenida = True
                st.session_state.pantalla = "pro"; st.rerun()
            else: st.error("Error al activar. Contáctanos por WhatsApp.")
        else: st.warning("Por favor completa todos los campos.")

elif st.session_state.pantalla == "login_directo":
    st.markdown('<h2 style="font-family:\'Syne\',sans-serif;font-size:1.5rem;font-weight:800;margin-bottom:20px">Iniciar sesión</h2>', unsafe_allow_html=True)
    email_login = st.text_input("Tu email", placeholder="juan@gmail.com")
    if st.button("Ingresar →", type="primary", use_container_width=True):
        if email_login:
            if es_usuario_pro(email_login):
                from supabase_client import get_client
                result = get_client().table("usuarios").select("nombre").eq("email", email_login).execute()
                nombre = result.data[0]["nombre"] if result.data else email_login
                st.session_state.es_pro = True; st.session_state.usuario_email = email_login
                st.session_state.usuario_nombre = nombre; st.session_state.mostrar_bienvenida = True
                st.session_state.pantalla = "pro"; st.rerun()
            else:
                st.error("❌ No encontramos una cuenta Pro con ese email.")
        else: st.warning("Por favor ingresa tu email.")
    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "free"; st.rerun()

elif st.session_state.pantalla == "pro":
    nombre_corto = st.session_state.usuario_nombre.split()[0]
    if st.session_state.mostrar_bienvenida:
        st.markdown(f'<div class="welcome-banner"><h3>👋 ¡Bienvenido de vuelta, {nombre_corto}!</h3><p>Tu cuenta Pro está activa. Aquí tienes todo lo que necesitas.</p></div>', unsafe_allow_html=True)
        st.session_state.mostrar_bienvenida = False
    st.markdown(f'<h2 style="font-family:\'Syne\',sans-serif;font-size:1.3rem;font-weight:800;margin-bottom:4px">{nombre_corto} <span class="pro-badge">PRO</span></h2><p style="color:#9BA8B5;font-size:0.8rem;margin-bottom:24px">{st.session_state.usuario_email}</p>', unsafe_allow_html=True)

    if st.session_state.resultado:
        r = st.session_state.resultado
        st.markdown('<div class="section-title">📄 Boleta de honorarios</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-hero"><div class="result-label">Bruto a boletear</div><div class="result-value">{clp(r["bruto"])}</div><div class="result-sub">Recibirás {clp(r["liquido_deseado"])} líquidos · Retención SII: {clp(r["retencion_sii"])}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧾 Cotizaciones obligatorias</div>', unsafe_allow_html=True)
        st.caption(f"Base imponible: {clp(r['base_imponible'])} · Tope legal 90 UF: {clp(r['tope_legal'])}")
        c1,c2,c3,c4 = st.columns(4)
        for col,(lbl,val,acc) in zip([c1,c2,c3,c4],[
            ("Salud (7%)",r["pago_salud"],False),
            (f"AFP+SIS ({r['tasa_afp']*100:.2f}%)",r["pago_afp"],False),
            ("Accidentes (0,9%)",r["pago_accidentes"],False),
            ("Total cotizaciones",r["total_cotizaciones"],True)]):
            with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {"accent" if acc else ""}">{clp(val)}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚖️ Balance Operación Renta</div>', unsafe_allow_html=True)
        balance = r["balance_renta"]
        if balance >= 0: st.success(f"**🎉 Devolución estimada: {clp(balance)}**\n\nEl SII te devolverá esta diferencia en abril.")
        else: st.error(f"**⚠️ Diferencia a pagar en abril: {clp(abs(balance))}**\n\nLa retención no alcanza para cubrir tus cotizaciones.")
        cg, cd = st.columns(2)
        with cg:
            if st.button("💾 Guardar boleta", type="primary", use_container_width=True):
                datos = {k:r[k] for k in ["bruto","afp","retencion_sii","base_imponible","pago_salud","pago_afp","pago_accidentes","total_cotizaciones","balance_renta"]}
                datos["liquido"] = r["liquido_deseado"]
                if guardar_boleta(st.session_state.usuario_email, datos): st.success("✅ Boleta guardada.")
                else: st.error("Error al guardar.")
        with cd:
            st.download_button(label="📄 Descargar desglose PDF",
                data=generar_pdf_desglose(r, st.session_state.usuario_nombre, valor_uf),
                file_name=f"pgh_desglose_{date.today().strftime('%d%m%Y')}.pdf",
                mime="application/pdf", use_container_width=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(28,163,158,0.15);margin:28px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Historial de boletas</div>', unsafe_allow_html=True)
    boletas = obtener_boletas(st.session_state.usuario_email)

    if boletas:
        df = pd.DataFrame(boletas)
        dm = df[["fecha","liquido","bruto","afp","total_cotizaciones","balance_renta"]].copy()
        dm.columns = ["Fecha","Líquido","Bruto","AFP","Total Cotiz.","Balance Renta"]
        for col in ["Líquido","Bruto","Total Cotiz.","Balance Renta"]: dm[col] = dm[col].apply(clp)
        st.dataframe(dm, hide_index=True, use_container_width=True)

        st.markdown('<div class="section-title">📊 Gráficos</div>', unsafe_allow_html=True)
        df["fecha"] = pd.to_datetime(df["fecha"])
        dfm = df.groupby(df["fecha"].dt.strftime("%b %Y"))["bruto"].sum().reset_index()
        dfm.columns = ["Mes","Bruto"]
        fig1 = go.Figure(go.Bar(x=dfm["Mes"], y=dfm["Bruto"],
            marker=dict(color=dfm["Bruto"], colorscale=[[0,"#026F6E"],[1,"#1CA39E"]], line=dict(color="rgba(28,163,158,0.5)",width=1)),
            text=[clp(v) for v in dfm["Bruto"]], textposition="outside", textfont=dict(color="#9BA8B5",size=11)))
        fig1.update_layout(title=dict(text="Ingresos brutos por mes",font=dict(color="#FFFFFF",size=14),x=0),
            paper_bgcolor="rgba(35,20,91,0.3)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9BA8B5",family="DM Sans"),
            xaxis=dict(gridcolor="rgba(28,163,158,0.1)",tickfont=dict(color="#9BA8B5")),
            yaxis=dict(gridcolor="rgba(28,163,158,0.1)",tickfont=dict(color="#9BA8B5"),tickformat="$,.0f"),
            margin=dict(l=20,r=20,t=40,b=20),height=320)
        st.plotly_chart(fig1, use_container_width=True)

        dfs = df.sort_values("fecha").copy()
        dfs["balance_acumulado"] = dfs["balance_renta"].cumsum()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dfs["fecha"], y=dfs["balance_acumulado"],
            mode="lines+markers", line=dict(color="#1CA39E",width=2.5),
            marker=dict(color="#1CA39E",size=7,line=dict(color="#026F6E",width=1.5)),
            fill="tozeroy", fillcolor="rgba(28,163,158,0.08)"))
        fig2.add_hline(y=0, line_dash="dash", line_color="rgba(255,75,75,0.5)", line_width=1)
        fig2.update_layout(title=dict(text="Balance acumulado en el año",font=dict(color="#FFFFFF",size=14),x=0),
            paper_bgcolor="rgba(35,20,91,0.3)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9BA8B5",family="DM Sans"),
            xaxis=dict(gridcolor="rgba(28,163,158,0.1)",tickfont=dict(color="#9BA8B5")),
            yaxis=dict(gridcolor="rgba(28,163,158,0.1)",tickfont=dict(color="#9BA8B5"),tickformat="$,.0f"),
            margin=dict(l=20,r=20,t=40,b=20),height=320,showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(label="📊 Descargar reporte anual completo PDF",
            data=generar_pdf_reporte(boletas, st.session_state.usuario_nombre, st.session_state.usuario_email),
            file_name=f"pgh_reporte_anual_{date.today().year}.pdf",
            mime="application/pdf", use_container_width=True, type="primary")
    else:
        st.info("Aún no tienes boletas guardadas. Calcula y guarda tu primera boleta arriba. 👆")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(28,163,158,0.15);margin:28px 0'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#9BA8B5;font-size:0.72rem'>⚠️ Esta calculadora es referencial. Consulta a un contador para decisiones financieras definitivas.</p>", unsafe_allow_html=True)
