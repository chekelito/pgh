"""
calculadora.py
Lógica de negocio de la Calculadora de Sueldo Inverso para PGH (2026)
Basada en normativa chilena vigente.
"""

# ─── Tasas fijas 2026 ────────────────────────────────────────────────────────
TASA_RETENCION_SII = 0.1525      # Retención SII boletas de honorarios 2026
TASA_SALUD         = 0.07        # Cotización obligatoria salud (Fonasa)
TASA_ACCIDENTES    = 0.009       # Seguro Social de Accidentes del Trabajo
PORCENTAJE_BASE    = 0.80        # Base imponible = 80% del bruto
TOPES_UF           = 90          # Tope legal cotizaciones (90 UF)

# ─── Tabla de AFPs (tasa total independiente, incluye SIS 1,54%) ─────────────
AFPS = {
    "Uno":      0.1200,
    "Modelo":   0.1212,
    "PlanVital":0.1270,
    "Habitat":  0.1281,
    "Capital":  0.1298,
    "Cuprum":   0.1298,
    "Provida":  0.1299,
}


def calcular_sueldo_inverso(
    liquido_deseado: float,
    afp: str,
    valor_uf: float,
) -> dict:
    """
    Dado un sueldo líquido deseado, calcula todos los montos relevantes
    para un trabajador independiente (PGH) en Chile.

    Args:
        liquido_deseado: Monto neto que el trabajador quiere recibir (CLP).
        afp:             Nombre de la AFP seleccionada.
        valor_uf:        Valor de la UF en CLP (se obtiene externamente).

    Returns:
        Dict con todos los valores calculados.
    """
    if afp not in AFPS:
        raise ValueError(f"AFP '{afp}' no reconocida. Opciones: {list(AFPS.keys())}")
    if liquido_deseado <= 0:
        raise ValueError("El sueldo líquido debe ser mayor a 0.")
    if valor_uf <= 0:
        raise ValueError("El valor de la UF debe ser mayor a 0.")

    tasa_afp = AFPS[afp]

    # 1. Bruto a boletear
    bruto = liquido_deseado / (1 - TASA_RETENCION_SII)

    # 2. Retención SII
    retencion_sii = bruto * TASA_RETENCION_SII

    # 3. Confirmación líquido
    liquido_final = bruto - retencion_sii

    # 4. Tope legal (90 UF)
    tope_legal = valor_uf * TOPES_UF

    # 5. Base imponible (80% del bruto, con tope de 90 UF)
    base_imponible = min(bruto * PORCENTAJE_BASE, tope_legal)

    # 6. Cotizaciones obligatorias
    pago_salud     = base_imponible * TASA_SALUD
    pago_afp       = base_imponible * tasa_afp
    pago_accidentes= base_imponible * TASA_ACCIDENTES
    total_cotizaciones = pago_salud + pago_afp + pago_accidentes

    # 7. Balance Operación Renta
    # Positivo → SII devolverá en abril
    # Negativo → deberás pagar la diferencia en abril
    balance_renta = retencion_sii - total_cotizaciones

    return {
        # Inputs
        "liquido_deseado":    liquido_deseado,
        "afp":                afp,
        "tasa_afp":           tasa_afp,
        "valor_uf":           valor_uf,
        # Bruto
        "bruto":              bruto,
        "retencion_sii":      retencion_sii,
        "liquido_final":      liquido_final,
        # Base
        "tope_legal":         tope_legal,
        "base_imponible":     base_imponible,
        # Cotizaciones
        "pago_salud":         pago_salud,
        "pago_afp":           pago_afp,
        "pago_accidentes":    pago_accidentes,
        "total_cotizaciones": total_cotizaciones,
        # Balance
        "balance_renta":      balance_renta,
    }


def obtener_afps() -> list[str]:
    """Retorna la lista de AFPs disponibles."""
    return list(AFPS.keys())
