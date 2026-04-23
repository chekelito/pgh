"""
app.py - PGH · Plataforma de Gestión de Honorarios
Versión Free + Pro · Diseño completo con paleta oficial
"""

import streamlit as st
import requests
import plotly.express as px
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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif}}
.stApp{{background:{C_BG};background-image:radial-gradient(ellipse 60% 50% at 10% 20%,rgba(35,20,91,0.7) 0%,transparent 70%),radial-gradient(ellipse 50% 40% at 90% 80%,rgba(2,111,110,0.35) 0%,transparent 60%)}}
.stNumberInput input,.stTextInput input{{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(28,163,158,0.25)!important;border-radius:12px!important;color:{C_TEXT}!important}}
.stSelectbox>div>div{{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(28,163,158,0.25)!important;border-radius:12px!important;color:{C_TEXT}!important}}
.stButton>button[kind="primary"]{{background:linear-gradient(135deg,{C_ACCENT2},{C_ACCENT1})!important;border:none!important;border-radius:12px!important;color:white!important;font-family:'Syne',sans-serif!important;font-weight:700!important;transition:opacity 0.2s!important}}
.stButton>button[kind="primary"]:hover{{opacity:0.88!important;transform:translateY(-1px)!important}}
.stButton>button[kind="secondary"]{{background:transparent!important;border:1px solid rgba(28,163,158,0.3)!important;border-radius:12px!important;color:{C_MUTED}!important}}
.stButton>button[kind="secondary"]:hover{{border-color:{C_ACCENT2}!important;color:{C_ACCENT2}!important}}
[data-testid="stDownloadButton"]>button{{background:rgba(28,163,158,0.12)!important;border:1px solid rgba(28,163,158,0.35)!important;border-radius:12px!important;color:{C_ACCENT2}!important;font-weight:600!important}}
hr{{border-color:rgba(28,163,158,0.15)!important}}
.stSuccess{{background:rgba(0,200,83,0.1)!important;border:1px solid rgba(0,200,83,0.3)!important;border-radius:14px!important;color:{C_TEXT}!important}}
.stError{{background:rgba(255,75,75,0.1)!important;border:1px solid rgba(255,75,75,0.3)!important;border-radius:14px!important;color:{C_TEXT}!important}}
.stInfo{{background:rgba(28,163,158,0.1)!important;border:1px solid rgba(28,163,158,0.3)!important;border-radius:14px!important;color:{C_TEXT}!important}}
.stWarning{{background:rgba(255,165,0,0.1)!important;border:1px solid rgba(255,165,0,0.3)!important;border-radius:14px!important}}
.stDataFrame{{background:rgba(35,20,91,0.3)!important;border-radius:14px!important;border:1px solid rgba(28,163,158,0.2)!important}}
.metric-card{{background:rgba(35,20,91,0.45);border:1px solid rgba(28,163,158,0.2);border-radius:14px;padding:18px;margin-bottom:8px}}
.metric-label{{font-size:0.7rem;color:{C_MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}}
.metric-value{{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;color:{C_TEXT}}}
.blurred{{filter:blur(5px);user-select:none;pointer-events:none}}
.pgh-result{{background:linear-gradient(135deg,rgba(28,163,158,0.15),rgba(2,111,110,0.1));border:1px solid rgba(28,163,158,0.4);border-radius:18px;padding:32px;text-align:center;margin-bottom:20px}}
.pgh-result-label{{font-size:0.72rem;color:{C_MUTED};text-transform:uppercase;letter-spacing:2px;margin-bottom:8px}}
.pgh-result-value{{font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;background:linear-gradient(135deg,#fff,{C_ACCENT2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-1px}}
.pgh-result-sub{{font-size:0.8rem;color:{C_MUTED};margin-top:8px}}
.pro-badge{{display:inline-block;background:linear-gradient(135deg,{C_ACCENT2},{C_ACCENT1});color:white;font-size:0.58rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:3px 10px;border-radius:99px;vertical-align:middle;margin-left:8px}}
.hero-tag{{display:inline-block;background:rgba(28,163,158,0.12);border:1px solid rgba(28,163,158,0.3);color:{C_ACCENT2};font-size:0.68rem;font-weight:500;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:99px;margin-bottom:16px}}
.section-tag{{font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{C_ACCENT2};margin-bottom:16px;display:block}}
.benefit-item{{background:rgba(28,163,158,0.08);border:1px solid rgba(28,163,158,0.15);border-radius:10px;padding:12px 14px;font-size:0.85rem;margin-bottom:8px}}
.welcome-banner{{background:linear-gradient(135deg,rgba(28,163,158,0.2),rgba(2,111,110,0.15));border:1px solid rgba(28,163,158,0.4);border-radius:16px;padding:20px 24px;margin-bottom:24px}}
.welcome-title{{font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:{C_TEXT};margin-bottom:4px}}
.welcome-sub{{font-size:0.82rem;color:{C_MUTED}}}
.uf-pill{{display:inline-flex;align-items:center;gap:6px;background:rgba(28,163,158,0.08);border:1px solid rgba(28,163,158,0.2);border-radius:99px;padding:5px 14px;font-size:0.75rem;color:{C_MUTED}}}
.pgh-card{{background:rgba(35,20,91,0.4);border:1px solid rgba(28,163,158,0.2);border-radius:20px;padding:28px;margin-bottom:20px}}
footer{{visibility:hidden}}#MainMenu{{visibility:hidden}}
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

def clp(v): return f"${v:,.0f}".replace(",",".")
def mcard(label,value,color=C_TEXT):
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="color:{color}">{value}</div></div>'


def pdf_desglose(r, nombre, valor_uf):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    T=colors.HexColor; styles=getSampleStyleSheet()
    TEAL=T("#1CA39E"); DARK=T("#160D18"); MUTED=T("#9BA8B5")
    s_sec=ParagraphStyle("s",fontName="Helvetica-Bold",fontSize=8,textColor=TEAL,spaceAfter=8,letterSpacing=2)
    s_foot=ParagraphStyle("f",fontName="Helvetica",fontSize=7.5,textColor=MUTED,alignment=TA_CENTER)
    WHITE=colors.white; LGRAY=T("#F3F4F6"); BAL=r["balance_renta"]; POS=BAL>=0
    story=[]
    lt=Table([[Paragraph(f"<b><font color='#1CA39E' size=18>PGH</font></b>",styles["Normal"]),
               Paragraph(f"<font color='#9BA8B5' size=8>Generado el {date.today().strftime('%d/%m/%Y')}</font>",
                         ParagraphStyle("r",fontName="Helvetica",fontSize=8,textColor=MUTED,alignment=TA_RIGHT))]],
             colWidths=[9*cm,8*cm])
    lt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story+=[lt]
    sub=Table([[Paragraph("<font color='#9BA8B5' size=7>PLATAFORMA DE GESTIÓN DE HONORARIOS · CHILE 2026</font>",styles["Normal"]),""]],colWidths=[9*cm,8*cm])
    story+=[sub,HRFlowable(width="100%",thickness=1,color=TEAL,spaceAfter=16,opacity=0.3)]
    story+=[Paragraph(f"<b><font size=22>Desglose de Honorarios</font></b>",styles["Normal"]),Spacer(1,4)]
    story+=[Paragraph(f"<font color='#9BA8B5' size=10>Trabajador: {nombre} · AFP: {r['afp']}</font>",styles["Normal"]),Spacer(1,16)]
    bt=Table([[Paragraph("<font color='#9BA8B5' size=8>MONTO BRUTO A BOLETEAR</font>",styles["Normal"]),
               Paragraph(f"<b><font color='#1CA39E' size=22>{clp(r['bruto'])}</font></b>",
                         ParagraphStyle("v",fontName="Helvetica-Bold",fontSize=22,textColor=TEAL,alignment=TA_RIGHT))]],
             colWidths=[9*cm,8*cm])
    bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),T("#F0FAFA")),("TOPPADDING",(0,0),(-1,-1),16),("BOTTOMPADDING",(0,0),(-1,-1),16),("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story+=[bt,Spacer(1,20),Paragraph("DESGLOSE DETALLADO",s_sec)]
    data=[["Concepto","Valor"],["Retención SII (15,25%)",clp(r["retencion_sii"])],["Sueldo líquido confirmado",clp(r["liquido_final"])],["",""],["Base Imponible (80% del bruto)",clp(r["base_imponible"])],["Tope legal (90 UF)",clp(r["tope_legal"])],["",""],["Cotización Salud (7%)",clp(r["pago_salud"])],[f"AFP {r['afp']} + SIS ({r['tasa_afp']*100:.2f}%)",clp(r["pago_afp"])],["Seguro Accidentes (0,9%)",clp(r["pago_accidentes"])],["Total Cotizaciones",clp(r["total_cotizaciones"])]]
    t=Table(data,colWidths=[11*cm,6*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),("BACKGROUND",(0,-1),(-1,-1),T("#E6F7F7")),("TEXTCOLOR",(0,-1),(-1,-1),T("#026F6E")),("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE,LGRAY]),("ALIGN",(1,0),(1,-1),"RIGHT"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),("GRID",(0,0),(-1,-1),0.5,T("#E5E7EB")),("LINEBELOW",(0,0),(-1,0),1,TEAL)]))
    story+=[t,Spacer(1,20),Paragraph("BALANCE OPERACIÓN RENTA",s_sec)]
    bc=T("#00C853") if POS else T("#FF4B4B"); bbg=T("#F0FFF4") if POS else T("#FFF5F5")
    btxt=f"{'Devolución estimada' if POS else 'Diferencia a pagar en abril'}: {clp(abs(BAL))}"
    bdesc="El SII te devolverá esta diferencia en la Operación Renta de abril." if POS else "La retención del SII no alcanza para cubrir tus cotizaciones."
    bal=Table([[Paragraph(f"<b><font size=11>{'🎉' if POS else '⚠️'} {btxt}</font></b><br/><font size=8 color='#6B7280'>{bdesc}</font>",ParagraphStyle("b",fontName="Helvetica",fontSize=10,textColor=bc,leading=16))]],colWidths=[17*cm])
    bal.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bbg),("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("LINERIGHT",(0,0),(0,-1),4,bc)]))
    story+=[bal,Spacer(1,30),HRFlowable(width="100%",thickness=0.5,color=T("#E5E7EB"),spaceAfter=10)]
    story+=[Paragraph("⚠️ Este informe es referencial. Consulta a un contador para decisiones financieras definitivas. · PGH · calculadora-pgh.streamlit.app",s_foot)]
    doc.build(story)
    return buf.getvalue()


def pdf_reporte(boletas, nombre):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    T=colors.HexColor; styles=getSampleStyleSheet()
    TEAL=T("#1CA39E"); DARK=T("#160D18"); MUTED=T("#9BA8B5"); WHITE=colors.white; LGRAY=T("#F3F4F6")
    s_sec=ParagraphStyle("s",fontName="Helvetica-Bold",fontSize=8,textColor=TEAL,spaceAfter=8,letterSpacing=2)
    s_foot=ParagraphStyle("f",fontName="Helvetica",fontSize=7.5,textColor=MUTED,alignment=TA_CENTER)
    df=pd.DataFrame(boletas); anio=date.today().year
    story=[]
    lt=Table([[Paragraph("<b><font color='#1CA39E' size=18>PGH</font></b>",styles["Normal"]),
               Paragraph(f"<font color='#9BA8B5' size=8>Reporte generado el {date.today().strftime('%d/%m/%Y')}</font>",
                         ParagraphStyle("r",fontName="Helvetica",fontSize=8,textColor=MUTED,alignment=TA_RIGHT))]],colWidths=[9*cm,8*cm])
    lt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story+=[lt,Table([[Paragraph("<font color='#9BA8B5' size=7>PLATAFORMA DE GESTIÓN DE HONORARIOS · CHILE 2026</font>",styles["Normal"]),""]],colWidths=[9*cm,8*cm])]
    story+=[HRFlowable(width="100%",thickness=1,color=TEAL,spaceAfter=16,opacity=0.3)]
    story+=[Paragraph(f"<b><font size=22>Reporte Anual {anio}</font></b>",styles["Normal"]),Spacer(1,4)]
    story+=[Paragraph(f"<font color='#9BA8B5' size=10>Trabajador: {nombre}</font>",styles["Normal"]),Spacer(1,16)]
    tb=df["bruto"].sum(); tl=df["liquido"].sum(); tc=df["total_cotizaciones"].sum(); tbal=df["balance_renta"].sum()
    rt=Table([["Total bruto boleteado","Total líquido recibido","Total cotizaciones","Balance anual"],[clp(tb),clp(tl),clp(tc),clp(tbal)]],colWidths=[4.25*cm]*4)
    rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),T("#9BA8B5")),("FONTNAME",(0,0),(-1,0),"Helvetica"),("FONTSIZE",(0,0),(-1,0),7),("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,1),(-1,1),11),("TEXTCOLOR",(0,1),(-1,1),TEAL),("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("GRID",(0,0),(-1,-1),0.5,T("#E5E7EB"))]))
    story+=[rt,Spacer(1,20),Paragraph("HISTORIAL DE BOLETAS",s_sec)]
    hd=[["Fecha","Líquido","Bruto","AFP","Total Cotiz.","Balance"]]
    rbg=[]
    for i,(_,row) in enumerate(df.iterrows()):
        hd.append([str(row["fecha"]),clp(row["liquido"]),clp(row["bruto"]),str(row["afp"]),clp(row["total_cotizaciones"]),clp(row["balance_renta"])])
        rbg.append(("BACKGROUND",(0,i+1),(-1,i+1),T("#F0FFF4") if row["balance_renta"]>=0 else T("#FFF5F5")))
    ht=Table(hd,colWidths=[2.5*cm,2.8*cm,2.8*cm,2*cm,3*cm,2.9*cm])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(1,0),(-1,-1),"RIGHT"),("ALIGN",(0,0),(0,-1),"LEFT"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),0.5,T("#E5E7EB")),("LINEBELOW",(0,0),(-1,0),1,TEAL),*rbg]))
    story+=[ht,Spacer(1,30),HRFlowable(width="100%",thickness=0.5,color=T("#E5E7EB"),spaceAfter=10)]
    story+=[Paragraph("⚠️ Este reporte es referencial. Consulta a un contador para decisiones financieras definitivas. · PGH · calculadora-pgh.streamlit.app",s_foot)]
    doc.build(story)
    return buf.getvalue()


# Estado
defs={"pantalla":"free","usuario_email":None,"usuario_nombre":None,"es_pro":False,"resultado":None,"codigo_validado":None,"mostrar_bienvenida":False}
for k,v in defs.items():
    if k not in st.session_state: st.session_state[k]=v

valor_uf=obtener_uf()

# HEADER
c1,c2,c3=st.columns([3,2,1])
with c1:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:4px 0">
    <div style="width:42px;height:42px;background:linear-gradient(135deg,{C_SURFACE},{C_MID});border:1px solid rgba(28,163,158,0.4);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.2rem">📈</div>
    <div><div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:800;background:linear-gradient(135deg,{C_ACCENT2},{C_ACCENT1});-webkit-background-clip:text;-webkit-text-fill-color:transparent">PGH</div>
    <div style="font-size:0.55rem;color:{C_MUTED};letter-spacing:1.5px;text-transform:uppercase">Gestión de Honorarios</div></div></div>""",unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="padding-top:10px"><div class="uf-pill"><span style="width:6px;height:6px;border-radius:50%;background:{C_ACCENT2};display:inline-block;animation:pulse 2s infinite"></span>UF hoy: {clp(valor_uf)}</div></div>',unsafe_allow_html=True)
with c3:
    if st.session_state.es_pro:
        if st.button("Salir",use_container_width=True): 
            for k,v in defs.items(): st.session_state[k]=v
            st.rerun()
    else:
        if st.button("Ingresar",use_container_width=True):
            st.session_state.pantalla="login_directo"; st.rerun()

st.divider()

# INPUTS COMUNES
if st.session_state.pantalla in ["free","pro"]:
    if st.session_state.es_pro and st.session_state.mostrar_bienvenida:
        n=st.session_state.usuario_nombre.split()[0]
        st.markdown(f'<div class="welcome-banner"><div class="welcome-title">¡Bienvenido de vuelta, {n}! 👋</div><div class="welcome-sub">Tienes acceso completo a todas las funciones Pro.</div></div>',unsafe_allow_html=True)
        st.session_state.mostrar_bienvenida=False
    if st.session_state.es_pro:
        st.markdown(f'<div style="margin-bottom:12px"><span style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700">{st.session_state.usuario_nombre.split()[0]}</span><span class="pro-badge">PRO</span></div>',unsafe_allow_html=True)
    st.markdown('<span class="section-tag">Calculadora</span>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: liquido=st.number_input("💵 Líquido que quiero recibir",min_value=10_000,max_value=50_000_000,value=500_000,step=10_000,format="%d")
    with c2: afp=st.selectbox("🏦 AFP",options=obtener_afps())
    if st.button("Calcular →",type="primary",use_container_width=True):
        st.session_state.resultado=calcular_sueldo_inverso(float(liquido),afp,valor_uf)

# FREE
if st.session_state.pantalla=="free":
    if st.session_state.resultado:
        r=st.session_state.resultado
        st.markdown(f'<div class="pgh-result"><div class="pgh-result-label">Debes boletear</div><div class="pgh-result-value">{clp(r["bruto"])}</div><div class="pgh-result-sub">Para recibir {clp(r["liquido_final"])} líquidos</div></div>',unsafe_allow_html=True)
        st.markdown('<span class="section-tag">¿Quieres saber más?</span>',unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown('<div class="metric-card blurred"><div class="metric-label">Retención SII</div><div class="metric-value">$██████</div></div>',unsafe_allow_html=True)
        with c2: st.markdown('<div class="metric-card blurred"><div class="metric-label">Total cotizaciones</div><div class="metric-value">$██████</div></div>',unsafe_allow_html=True)
        with c3: st.markdown('<div class="metric-card blurred"><div class="metric-label">Balance Renta</div><div class="metric-value">🔴 $██████</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Ver desglose completo 🔓",use_container_width=True):
            st.session_state.pantalla="vista_previa"; st.rerun()

# VISTA PREVIA
elif st.session_state.pantalla=="vista_previa":
    st.markdown(f'<div style="text-align:center;margin-bottom:8px"><div class="hero-tag">Versión Pro</div><h2 style="font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;margin:8px 0">Desbloquea el desglose completo</h2><p style="color:{C_MUTED};font-size:0.9rem">Gestiona tus honorarios como un profesional</p></div>',unsafe_allow_html=True)
    st.divider()
    st.markdown('<span class="section-tag">Vista previa</span>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    items=[("Retención SII (15,25%)","$██████"),("Base Imponible (80%)","$██████"),("Total cotizaciones","$██████"),("Salud (7%)","$██████"),("AFP + SIS","$██████"),("Balance Renta","🔴 $██████")]
    for i,(lbl,val) in enumerate(items):
        with [c1,c2,c3][i%3]: st.markdown(f'<div class="metric-card blurred"><div class="metric-label">{lbl}</div><div class="metric-value">{val}</div></div>',unsafe_allow_html=True)
    st.caption("🔓 Desbloquea para ver tus números reales")
    st.divider()
    st.markdown('<span class="section-tag">¿Qué incluye el Pro?</span>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        for b in ["✅ Desglose completo de cotizaciones","✅ Balance Operación Renta con alerta","✅ Historial de todas tus boletas"]:
            st.markdown(f'<div class="benefit-item">{b}</div>',unsafe_allow_html=True)
    with c2:
        for b in ["✅ Gráfico de ingresos por mes","✅ Gráfico de balance acumulado","✅ Descarga tus informes en PDF"]:
            st.markdown(f'<div class="benefit-item">{b}</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin:24px 0 8px"><div style="font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,{C_ACCENT2},{C_ACCENT1});-webkit-background-clip:text;-webkit-text-fill-color:transparent">$2.990</div><div style="color:{C_MUTED};font-size:0.8rem">por mes · Cancela cuando quieras</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if st.button("Quiero el Pro 🔓",type="primary",use_container_width=True):
            st.session_state.pantalla="compra"; st.rerun()
    with c2:
        if st.button("← Volver",use_container_width=True):
            st.session_state.pantalla="free"; st.rerun()

# COMPRA
elif st.session_state.pantalla=="compra":
    st.markdown(f'<h2 style="font-family:Syne,sans-serif;font-weight:800;margin-bottom:4px">🔑 Obtén tu acceso Pro</h2><p style="color:{C_MUTED};font-size:0.9rem;margin-bottom:24px">3 pasos simples para activar tu cuenta</p>',unsafe_allow_html=True)
    st.markdown(f'<div class="pgh-card"><span class="section-tag">Instrucciones</span><p><b>1️⃣ Transfiere $2.990</b></p><ul style="color:{C_MUTED};font-size:0.9rem;margin:8px 0 16px 16px;line-height:1.8"><li>Banco: BancoEstado (Cuenta RUT)</li><li>RUT: 21.553.061-2</li><li>Nombre: Exequiel Zambrano</li></ul><p><b>2️⃣ Envía el comprobante</b></p><p style="color:{C_MUTED};font-size:0.9rem;margin:8px 0 16px 16px">📲 WhatsApp: +56 9 5222 2772</p><p><b>3️⃣ Recibe tu código en minutos</b></p></div>',unsafe_allow_html=True)
    st.divider()
    st.markdown('<span class="section-tag">¿Ya tienes tu código?</span>',unsafe_allow_html=True)
    cod=st.text_input("Código de acceso",placeholder="PGH-PRO-XXXX",label_visibility="collapsed").strip().upper()
    if st.button("Activar Pro ✅",type="primary",use_container_width=True):
        if cod:
            if verificar_codigo(cod):
                st.session_state.codigo_validado=cod; st.session_state.pantalla="activacion"; st.rerun()
            else: st.error("❌ Código incorrecto o ya utilizado.")
        else: st.warning("Por favor ingresa tu código.")
    if st.button("← Volver",use_container_width=True):
        st.session_state.pantalla="vista_previa"; st.rerun()

# ACTIVACIÓN
elif st.session_state.pantalla=="activacion":
    st.markdown(f'<div style="text-align:center;margin-bottom:24px"><div style="font-size:3rem">✅</div><h2 style="font-family:Syne,sans-serif;font-weight:800">¡Código válido!</h2><p style="color:{C_MUTED}">Ingresa tus datos para activar tu cuenta.</p></div>',unsafe_allow_html=True)
    nom=st.text_input("Tu nombre completo",placeholder="Juan Pérez")
    eml=st.text_input("Tu email",placeholder="juan@gmail.com")
    if st.button("Activar mi cuenta Pro 🚀",type="primary",use_container_width=True):
        if nom and eml:
            if activar_codigo(st.session_state.codigo_validado,eml,nom):
                st.session_state.es_pro=True; st.session_state.usuario_email=eml
                st.session_state.usuario_nombre=nom; st.session_state.mostrar_bienvenida=True
                st.session_state.pantalla="pro"; st.rerun()
            else: st.error("Error al activar. Contáctanos por WhatsApp.")
        else: st.warning("Por favor completa todos los campos.")

# LOGIN DIRECTO
elif st.session_state.pantalla=="login_directo":
    st.markdown(f'<h2 style="font-family:Syne,sans-serif;font-weight:800;margin-bottom:4px">👤 Iniciar sesión</h2><p style="color:{C_MUTED};margin-bottom:24px">Ingresa tu email para acceder a tu cuenta Pro.</p>',unsafe_allow_html=True)
    eml=st.text_input("Tu email",placeholder="juan@gmail.com")
    if st.button("Ingresar →",type="primary",use_container_width=True):
        if eml:
            if es_usuario_pro(eml):
                from supabase_client import get_client
                res=get_client().table("usuarios").select("nombre").eq("email",eml).execute()
                nom=res.data[0]["nombre"] if res.data else eml
                st.session_state.es_pro=True; st.session_state.usuario_email=eml
                st.session_state.usuario_nombre=nom; st.session_state.mostrar_bienvenida=True
                st.session_state.pantalla="pro"; st.rerun()
            else:
                st.error("❌ No encontramos una cuenta Pro con ese email.")
                st.info("¿Aún no tienes el Pro? Vuelve y haz clic en 'Ver desglose completo'.")
        else: st.warning("Por favor ingresa tu email.")
    if st.button("← Volver",use_container_width=True):
        st.session_state.pantalla="free"; st.rerun()

# PRO
elif st.session_state.pantalla=="pro":
    if st.session_state.mostrar_bienvenida:
        n=st.session_state.usuario_nombre.split()[0]
        st.markdown(f'<div class="welcome-banner"><div class="welcome-title">¡Bienvenido de vuelta, {n}! 👋</div><div class="welcome-sub">Tienes acceso completo a todas las funciones Pro.</div></div>',unsafe_allow_html=True)
        st.session_state.mostrar_bienvenida=False

    if st.session_state.resultado:
        r=st.session_state.resultado
        st.markdown(f'<div class="pgh-result"><div class="pgh-result-label">Monto bruto a boletear</div><div class="pgh-result-value">{clp(r["bruto"])}</div><div class="pgh-result-sub">Recibirás {clp(r["liquido_final"])} líquidos · Retención SII: {clp(r["retencion_sii"])}</div></div>',unsafe_allow_html=True)
        st.markdown('<span class="section-tag">Cotizaciones Obligatorias</span>',unsafe_allow_html=True)
        st.caption(f"Base imponible: {clp(r['base_imponible'])} · Tope legal (90 UF): {clp(r['tope_legal'])}")
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("Salud (7%)",clp(r['pago_salud'])),unsafe_allow_html=True)
        with c2: st.markdown(mcard(f"AFP+SIS ({r['tasa_afp']*100:.2f}%)",clp(r['pago_afp'])),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Accidentes (0,9%)",clp(r['pago_accidentes'])),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Total cotizaciones",clp(r['total_cotizaciones']),C_ACCENT2),unsafe_allow_html=True)
        st.markdown('<span class="section-tag" style="margin-top:12px;display:block">Balance Operación Renta</span>',unsafe_allow_html=True)
        bal=r["balance_renta"]
        if bal>=0: st.success(f"**🎉 Devolución estimada: {clp(bal)}**\n\nEl SII te devolverá esta diferencia en la Operación Renta de abril.")
        else: st.error(f"**⚠️ Diferencia a pagar en abril: {clp(abs(bal))}**\n\nLa retención no alcanza para cubrir tus cotizaciones obligatorias.")
        st.markdown("<br>",unsafe_allow_html=True)
        cg,cp=st.columns(2)
        with cg:
            if st.button("💾 Guardar boleta",type="primary",use_container_width=True):
                datos={"liquido":r["liquido_deseado"],"bruto":r["bruto"],"afp":r["afp"],"retencion_sii":r["retencion_sii"],"base_imponible":r["base_imponible"],"pago_salud":r["pago_salud"],"pago_afp":r["pago_afp"],"pago_accidentes":r["pago_accidentes"],"total_cotizaciones":r["total_cotizaciones"],"balance_renta":r["balance_renta"]}
                if guardar_boleta(st.session_state.usuario_email,datos): st.success("✅ Boleta guardada."); st.rerun()
                else: st.error("Error al guardar.")
        with cp:
            st.download_button(label="📄 Descargar desglose PDF",data=pdf_desglose(r,st.session_state.usuario_nombre,valor_uf),file_name=f"PGH_desglose_{date.today().strftime('%d-%m-%Y')}.pdf",mime="application/pdf",use_container_width=True)

    st.divider()
    st.markdown('<span class="section-tag">Historial de Boletas</span>',unsafe_allow_html=True)
    boletas=obtener_boletas(st.session_state.usuario_email)

    if boletas:
        df=pd.DataFrame(boletas)
        dm=df[["fecha","liquido","bruto","afp","total_cotizaciones","balance_renta"]].copy()
        dm.columns=["Fecha","Líquido","Bruto","AFP","Total Cotiz.","Balance Renta"]
        for col in ["Líquido","Bruto","Total Cotiz.","Balance Renta"]: dm[col]=dm[col].apply(lambda x:clp(x))
        st.dataframe(dm,hide_index=True,use_container_width=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.download_button(label="📊 Descargar reporte anual PDF",data=pdf_reporte(boletas,st.session_state.usuario_nombre),file_name=f"PGH_reporte_anual_{date.today().year}.pdf",mime="application/pdf",use_container_width=True)
        st.divider()
        st.markdown('<span class="section-tag">Gráficos</span>',unsafe_allow_html=True)
        df["fecha"]=pd.to_datetime(df["fecha"])
        dm2=df.groupby(df["fecha"].dt.strftime("%b %Y"))["bruto"].sum().reset_index()
        dm2.columns=["Mes","Bruto"]
        fig1=go.Figure()
        fig1.add_trace(go.Bar(x=dm2["Mes"],y=dm2["Bruto"],marker=dict(color=dm2["Bruto"],colorscale=[[0,"#026F6E"],[1,"#1CA39E"]],line=dict(width=0)),text=[clp(v) for v in dm2["Bruto"]],textposition="outside",textfont=dict(color="#9BA8B5",size=11)))
        fig1.update_layout(title=dict(text="📊 Ingresos brutos por mes",font=dict(color="#FFFFFF",size=14,family="Syne")),paper_bgcolor="rgba(35,20,91,0.4)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9BA8B5",family="DM Sans"),xaxis=dict(gridcolor="rgba(28,163,158,0.1)"),yaxis=dict(gridcolor="rgba(28,163,158,0.1)",tickprefix="$",tickformat=",.0f"),margin=dict(t=50,b=40,l=60,r=20),height=320)
        st.plotly_chart(fig1,use_container_width=True)
        ds=df.sort_values("fecha"); ds["balance_acumulado"]=ds["balance_renta"].cumsum()
        fig2=go.Figure()
        fig2.add_hline(y=0,line_dash="dash",line_color="rgba(255,255,255,0.2)",line_width=1)
        fig2.add_trace(go.Scatter(x=ds["fecha"],y=ds["balance_acumulado"],mode="lines+markers",line=dict(color="#1CA39E",width=3),marker=dict(color="#1CA39E",size=8,line=dict(color="#160D18",width=2)),fill="tozeroy",fillcolor="rgba(28,163,158,0.1)",text=[clp(v) for v in ds["balance_acumulado"]],hovertemplate="%{text}<extra></extra>"))
        fig2.update_layout(title=dict(text="📈 Balance acumulado en el año",font=dict(color="#FFFFFF",size=14,family="Syne")),paper_bgcolor="rgba(35,20,91,0.4)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9BA8B5",family="DM Sans"),xaxis=dict(gridcolor="rgba(28,163,158,0.1)"),yaxis=dict(gridcolor="rgba(28,163,158,0.1)",tickprefix="$",tickformat=",.0f"),margin=dict(t=50,b=40,l=60,r=20),height=320,showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)
    else:
        st.info("Aún no tienes boletas guardadas. Calcula y guarda tu primera boleta arriba. 👆")

    st.divider()
    st.markdown(f'<p style="text-align:center;color:{C_MUTED};font-size:0.75rem">⚠️ Esta calculadora es referencial. Consulta a un contador para decisiones financieras definitivas.</p>',unsafe_allow_html=True)
