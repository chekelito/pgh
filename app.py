"""
app.py
Interfaz Streamlit para la Calculadora de Sueldo Inverso PGH (2026)
"""

import streamlit as st
import requests
from datetime import date
from calculadora import calcular_sueldo_inverso, obtener_afps, TASA_RETENCION_SII

# ─── Configuración de página ─────────────────────────────────────────────────
st.set_page_config(
    page_title="PGH · Calculadora de Honorarios",
    page_icon="💼",
    layout="centered",
)

# ─── Estilos ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 0.5rem;
    }
    .metric-label { font-size: 0.8rem; color: #6c757d; margin-bottom: 2px; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #212529; }
    .balance-positivo { color: #198754; }
    .balance-negativo { color: #dc3545; }
    .tag {
        display: inline-block;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 99px;
        font-weight: 600;
    }
    .tag-verde { background: #d1e7dd; color: #0f5132; }
    .tag-rojo  { background: #f8d7da; color: #842029; }
</style>
""", unsafe_allow_html=True)


# ─── Obtener valor UF ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def obtener_uf() -> float:
    """Obtiene el valor de la UF desde mindicador.cl. Fallback: valor hardcodeado."""
    try:
        hoy = date.today().strftime("%d-%m-%Y")
        r = requests.get(
            f"https://mindicador.cl/api/uf/{hoy}",
            timeout=5,
        )
        data = r.json()
        return float(data["serie"][0]["valor"])
    except Exception:
        return 40013.88   # Fallback UF conocida


# ─── Encabezado ──────────────────────────────────────────────────────────────
st.title("💼 Calculadora de Honorarios")
st.caption("Plataforma de Gestión de Honorarios · Normativa chilena 2026")
st.divider()

# ─── Sidebar con parámetros ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Parámetros")

    liquido = st.number_input(
        "💵 Sueldo líquido que quiero recibir (CLP)",
        min_value=10_000,
        max_value=50_000_000,
        value=500_000,
        step=10_000,
        format="%d",
    )

    afp_seleccionada = st.selectbox(
        "🏦 AFP",
        options=obtener_afps(),
        index=0,
    )

    valor_uf = obtener_uf()
    st.metric(
        "📊 Valor UF hoy",
        f"${valor_uf:,.2f}",
        help="Obtenido desde mindicador.cl · Se actualiza cada hora",
    )

    st.divider()
    st.caption(f"Retención SII 2026: **{TASA_RETENCION_SII*100:.2f}%**")
    st.caption("Base imponible: **80% del bruto**")
    st.caption("Tope cotizaciones: **90 UF**")


# ─── Cálculo ─────────────────────────────────────────────────────────────────
resultado = calcular_sueldo_inverso(
    liquido_deseado=float(liquido),
    afp=afp_seleccionada,
    valor_uf=valor_uf,
)


def clp(valor: float) -> str:
    """Formatea un número como moneda chilena."""
    return f"${valor:,.0f}".replace(",", ".")


# ─── Sección 1: Boleta ───────────────────────────────────────────────────────
st.subheader("📄 Boleta de Honorarios")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Monto bruto a boletear</div>
        <div class="metric-value">{clp(resultado['bruto'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Retención SII (15,25%)</div>
        <div class="metric-value">{clp(resultado['retencion_sii'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Líquido que recibirás ✓</div>
        <div class="metric-value">{clp(resultado['liquido_final'])}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Sección 2: Cotizaciones ─────────────────────────────────────────────────
st.subheader("🧾 Cotizaciones Obligatorias")
st.caption(f"Base imponible: {clp(resultado['base_imponible'])} · Tope legal (90 UF): {clp(resultado['tope_legal'])}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Salud (7%)</div>
        <div class="metric-value">{clp(resultado['pago_salud'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">AFP + SIS ({resultado['tasa_afp']*100:.2f}%)</div>
        <div class="metric-value">{clp(resultado['pago_afp'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Acc. Trabajo (0,9%)</div>
        <div class="metric-value">{clp(resultado['pago_accidentes'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total cotizaciones</div>
        <div class="metric-value">{clp(resultado['total_cotizaciones'])}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Sección 3: Balance Renta ────────────────────────────────────────────────
st.subheader("⚖️ Balance Operación Renta (Abril)")

balance = resultado["balance_renta"]
es_positivo = balance >= 0

if es_positivo:
    st.success(f"""
    **🎉 Devolución estimada: {clp(balance)}**

    La retención del SII ({clp(resultado['retencion_sii'])}) supera tus cotizaciones obligatorias.
    El SII te devolverá aproximadamente esta diferencia en la Operación Renta de abril.
    """)
else:
    st.error(f"""
    **⚠️ Diferencia a pagar en abril: {clp(abs(balance))}**

    La retención del SII ({clp(resultado['retencion_sii'])}) **no alcanza** para cubrir tus
    cotizaciones obligatorias ({clp(resultado['total_cotizaciones'])}). Deberás pagar esta
    diferencia en la Operación Renta de abril.
    """)

# ─── Resumen expandible ──────────────────────────────────────────────────────
with st.expander("📋 Ver resumen completo"):
    resumen = {
        "Líquido deseado":       clp(resultado["liquido_deseado"]),
        "Bruto a boletear":      clp(resultado["bruto"]),
        "Retención SII (15,25%)":clp(resultado["retencion_sii"]),
        "Líquido final":         clp(resultado["liquido_final"]),
        "---": "---",
        "Valor UF":              clp(valor_uf),
        "Tope legal (90 UF)":    clp(resultado["tope_legal"]),
        "Base imponible (80%)":  clp(resultado["base_imponible"]),
        "----": "---",
        "AFP seleccionada":      afp_seleccionada,
        f"AFP+SIS ({resultado['tasa_afp']*100:.2f}%)": clp(resultado["pago_afp"]),
        "Salud (7%)":            clp(resultado["pago_salud"]),
        "Acc. Trabajo (0,9%)":   clp(resultado["pago_accidentes"]),
        "Total cotizaciones":    clp(resultado["total_cotizaciones"]),
        "-----": "---",
        "Balance Renta":         clp(balance) + (" (devolución)" if es_positivo else " (a pagar)"),
    }
    for k, v in resumen.items():
        if v == "---":
            st.divider()
        else:
            col_a, col_b = st.columns([2, 1])
            col_a.write(k)
            col_b.write(f"**{v}**")

st.divider()
st.caption("⚠️ Esta calculadora es una estimación referencial. Consulta a un contador para decisiones financieras definitivas.")
