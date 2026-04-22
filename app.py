"""
app.py
Interfaz Streamlit para PGH - Plataforma de Gestión de Honorarios
Versión Free + Pro con Supabase
"""

import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from datetime import date
from calculadora import calcular_sueldo_inverso, obtener_afps, TASA_RETENCION_SII
from supabase_client import (
    verificar_codigo,
    activar_codigo,
    es_usuario_pro,
    guardar_boleta,
    obtener_boletas,
)

# ─── Configuración de página ─────────────────────────────────────────────────
st.set_page_config(
    page_title="PGH · Calculadora de Honorarios",
    page_icon="💼",
    layout="centered",
)

# ─── Estilos ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 0.5rem;
    }
    .metric-label { font-size: 0.8rem; color: #6c757d; margin-bottom: 2px; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #212529; }
    .blurred { filter: blur(6px); user-select: none; pointer-events: none; }
    .pro-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ─── Obtener valor UF ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def obtener_uf() -> float:
    try:
        hoy = date.today().strftime("%d-%m-%Y")
        r = requests.get(f"https://mindicador.cl/api/uf/{hoy}", timeout=5)
        return float(r.json()["serie"][0]["valor"])
    except Exception:
        return 40013.88


def clp(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


# ─── Estado de sesión ─────────────────────────────────────────────────────────
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "free"
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = None
if "usuario_nombre" not in st.session_state:
    st.session_state.usuario_nombre = None
if "es_pro" not in st.session_state:
    st.session_state.es_pro = False
if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "codigo_validado" not in st.session_state:
    st.session_state.codigo_validado = None


# ─── Header ───────────────────────────────────────────────────────────────────
col_titulo, col_login = st.columns([3, 1])
with col_titulo:
    st.markdown("## 💼 PGH · Calculadora de Honorarios")
with col_login:
    if st.session_state.es_pro:
        st.markdown(f"👤 **{st.session_state.usuario_nombre.split()[0]}**")
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.es_pro = False
            st.session_state.usuario_email = None
            st.session_state.usuario_nombre = None
            st.session_state.pantalla = "free"
            st.rerun()
    else:
        if st.button("Iniciar sesión", use_container_width=True):
            st.session_state.pantalla = "login_directo"
            st.rerun()

st.divider()

# ─── Inputs comunes ───────────────────────────────────────────────────────────
valor_uf = obtener_uf()

if st.session_state.pantalla in ["free", "pro"]:
    col1, col2 = st.columns(2)
    with col1:
        liquido = st.number_input(
            "💵 ¿Cuánto quieres recibir líquido?",
            min_value=10_000,
            max_value=50_000_000,
            value=500_000,
            step=10_000,
            format="%d",
        )
    with col2:
        afp = st.selectbox("🏦 AFP", options=obtener_afps())

    if st.button("Calcular", type="primary", use_container_width=True):
        st.session_state.resultado = calcular_sueldo_inverso(
            liquido_deseado=float(liquido),
            afp=afp,
            valor_uf=valor_uf,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA FREE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.pantalla == "free":

    if st.session_state.resultado:
        r = st.session_state.resultado
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Debes boletear</div>
            <div class="metric-value">{clp(r['bruto'])}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🔒 ¿Quieres ver el desglose completo?")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card blurred">
                <div class="metric-label">Retención SII</div>
                <div class="metric-value">$██████</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card blurred">
                <div class="metric-label">Total cotizaciones</div>
                <div class="metric-value">$██████</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card blurred">
                <div class="metric-label">Balance Renta</div>
                <div class="metric-value">🔴 $██████</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Ver desglose completo 🔓", use_container_width=True):
            st.session_state.pantalla = "vista_previa"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA VISTA PREVIA PRO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pantalla == "vista_previa":

    st.markdown("## 🚀 Desbloquea el desglose completo")
    st.markdown("*Gestiona tus honorarios como un profesional*")
    st.markdown("---")

    st.markdown("#### Vista previa")
    data_preview = {
        "Concepto": [
            "Retención SII (15,25%)",
            "Base imponible (80%)",
            "Salud (7%)",
            "AFP + SIS",
            "Accidentes (0,9%)",
            "Total cotizaciones",
            "Balance Operación Renta",
        ],
        "Valor": ["$██████"] * 7,
    }
    df_preview = pd.DataFrame(data_preview)
    st.dataframe(df_preview, hide_index=True, use_container_width=True)
    st.caption("🔓 Desbloquea para ver tus números reales")

    st.markdown("---")
    st.markdown("#### ✅ Con la versión Pro obtienes:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - ✅ Desglose completo de cotizaciones
        - ✅ Balance Operación Renta con alerta
        - ✅ Historial de todas tus boletas
        """)
    with col2:
        st.markdown("""
        - ✅ Gráfico de ingresos por mes
        - ✅ Gráfico de balance acumulado
        - ✅ Acceso desde cualquier dispositivo
        """)

    st.markdown("### 💰 $2.990 / mes")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Quiero el Pro 🔓", type="primary", use_container_width=True):
            st.session_state.pantalla = "compra"
            st.rerun()
    with col2:
        if st.button("← Volver", use_container_width=True):
            st.session_state.pantalla = "free"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA INSTRUCCIONES DE COMPRA
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pantalla == "compra":

    st.markdown("## 🔑 Obtén tu acceso Pro")
    st.markdown("---")

    st.markdown("""
    ### 3 pasos simples:

    **1️⃣ Transfiere $2.990**
    - Banco: *(tu banco)*
    - RUT: *(tu RUT)*
    - Nombre: *(tu nombre)*

    **2️⃣ Envía el comprobante**
    - 📲 WhatsApp: *(tu número)*

    **3️⃣ Recibe tu código en menos de 24 horas**
    """)

    st.markdown("---")
    st.markdown("#### ¿Ya tienes tu código?")

    codigo_input = st.text_input(
        "Ingresa tu código de acceso",
        placeholder="PGH-PRO-XXXX",
    ).strip().upper()

    if st.button("Activar Pro ✅", type="primary", use_container_width=True):
        if codigo_input:
            if verificar_codigo(codigo_input):
                st.session_state.codigo_validado = codigo_input
                st.session_state.pantalla = "activacion"
                st.rerun()
            else:
                st.error("❌ Código incorrecto o ya utilizado. Verifica e intenta de nuevo.")
        else:
            st.warning("Por favor ingresa un código.")

    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "vista_previa"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA ACTIVACIÓN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pantalla == "activacion":

    st.markdown("## ✅ ¡Código válido!")
    st.markdown("Ingresa tus datos para activar tu cuenta Pro y acceder sin código la próxima vez.")
    st.markdown("---")

    nombre_input = st.text_input("Tu nombre", placeholder="Juan Pérez")
    email_input = st.text_input("Tu email", placeholder="juan@gmail.com")

    if st.button("Activar mi cuenta Pro 🚀", type="primary", use_container_width=True):
        if nombre_input and email_input:
            if activar_codigo(st.session_state.codigo_validado, email_input, nombre_input):
                st.session_state.es_pro = True
                st.session_state.usuario_email = email_input
                st.session_state.usuario_nombre = nombre_input
                st.session_state.pantalla = "pro"
                st.rerun()
            else:
                st.error("Hubo un error al activar tu cuenta. Contáctanos por WhatsApp.")
        else:
            st.warning("Por favor completa todos los campos.")

# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA LOGIN DIRECTO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pantalla == "login_directo":

    st.markdown("## 👤 Iniciar sesión")
    st.markdown("---")

    email_login = st.text_input("Tu email", placeholder="juan@gmail.com")

    if st.button("Ingresar", type="primary", use_container_width=True):
        if email_login:
            if es_usuario_pro(email_login):
                from supabase_client import get_client
                result = get_client().table("usuarios").select("nombre").eq("email", email_login).execute()
                nombre = result.data[0]["nombre"] if result.data else email_login
                st.session_state.es_pro = True
                st.session_state.usuario_email = email_login
                st.session_state.usuario_nombre = nombre
                st.session_state.pantalla = "pro"
                st.rerun()
            else:
                st.error("❌ No encontramos una cuenta Pro con ese email.")
                st.info("¿Aún no tienes el Pro? Vuelve a la calculadora y haz clic en 'Ver desglose completo'.")
        else:
            st.warning("Por favor ingresa tu email.")

    if st.button("← Volver", use_container_width=True):
        st.session_state.pantalla = "free"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA PRO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pantalla == "pro":

    st.markdown(f"### Bienvenido, {st.session_state.usuario_nombre.split()[0]} 👋 <span class='pro-badge'>PRO</span>", unsafe_allow_html=True)
    st.divider()

    if st.session_state.resultado:
        r = st.session_state.resultado

        st.subheader("📄 Boleta de Honorarios")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Bruto a boletear</div>
                <div class="metric-value">{clp(r['bruto'])}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Retención SII (15,25%)</div>
                <div class="metric-value">{clp(r['retencion_sii'])}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Líquido que recibirás ✓</div>
                <div class="metric-value">{clp(r['liquido_final'])}</div>
            </div>""", unsafe_allow_html=True)

        st.subheader("🧾 Cotizaciones Obligatorias")
        st.caption(f"Base imponible: {clp(r['base_imponible'])} · Tope legal (90 UF): {clp(r['tope_legal'])}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Salud (7%)</div>
                <div class="metric-value">{clp(r['pago_salud'])}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">AFP+SIS ({r['tasa_afp']*100:.2f}%)</div>
                <div class="metric-value">{clp(r['pago_afp'])}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Accidentes (0,9%)</div>
                <div class="metric-value">{clp(r['pago_accidentes'])}</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Total cotizaciones</div>
                <div class="metric-value">{clp(r['total_cotizaciones'])}</div>
            </div>""", unsafe_allow_html=True)

        st.subheader("⚖️ Balance Operación Renta")
        balance = r["balance_renta"]
        if balance >= 0:
            st.success(f"**🎉 Devolución estimada: {clp(balance)}**\n\nEl SII te devolverá esta diferencia en abril.")
        else:
            st.error(f"**⚠️ Diferencia a pagar en abril: {clp(abs(balance))}**\n\nLa retención no alcanza para cubrir tus cotizaciones.")

        if st.button("💾 Guardar boleta", type="primary"):
            datos = {
                "liquido": r["liquido_deseado"],
                "bruto": r["bruto"],
                "afp": r["afp"],
                "retencion_sii": r["retencion_sii"],
                "base_imponible": r["base_imponible"],
                "pago_salud": r["pago_salud"],
                "pago_afp": r["pago_afp"],
                "pago_accidentes": r["pago_accidentes"],
                "total_cotizaciones": r["total_cotizaciones"],
                "balance_renta": r["balance_renta"],
            }
            if guardar_boleta(st.session_state.usuario_email, datos):
                st.success("✅ Boleta guardada en tu historial.")
            else:
                st.error("Error al guardar. Intenta de nuevo.")

    st.divider()

    # ── Historial ─────────────────────────────────────────────────────────────
    st.subheader("📋 Historial de Boletas")
    boletas = obtener_boletas(st.session_state.usuario_email)

    if boletas:
        df = pd.DataFrame(boletas)
        df_mostrar = df[["fecha", "liquido", "bruto", "afp", "total_cotizaciones", "balance_renta"]].copy()
        df_mostrar.columns = ["Fecha", "Líquido", "Bruto", "AFP", "Total Cotiz.", "Balance Renta"]
        for col in ["Líquido", "Bruto", "Total Cotiz.", "Balance Renta"]:
            df_mostrar[col] = df_mostrar[col].apply(lambda x: clp(x))
        st.dataframe(df_mostrar, hide_index=True, use_container_width=True)

        st.divider()

        # ── Gráficos ──────────────────────────────────────────────────────────
        st.subheader("📊 Gráficos")

        df["fecha"] = pd.to_datetime(df["fecha"])
        df["mes"] = df["fecha"].dt.strftime("%b %Y")

        df_mes = df.groupby("mes")["bruto"].sum().reset_index()
        fig1 = px.bar(
            df_mes,
            x="mes",
            y="bruto",
            title="Ingresos brutos por mes",
            labels={"mes": "Mes", "bruto": "Bruto ($)"},
            color_discrete_sequence=["#667eea"],
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

        df_sorted = df.sort_values("fecha")
        df_sorted["balance_acumulado"] = df_sorted["balance_renta"].cumsum()
        fig2 = px.line(
            df_sorted,
            x="fecha",
            y="balance_acumulado",
            title="Balance acumulado en el año",
            labels={"fecha": "Fecha", "balance_acumulado": "Balance acumulado ($)"},
            color_discrete_sequence=["#764ba2"],
        )
        fig2.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Aún no tienes boletas guardadas. Calcula y guarda tu primera boleta arriba. 👆")

    st.divider()
    st.caption("⚠️ Esta calculadora es referencial. Consulta a un contador para decisiones financieras definitivas.")
