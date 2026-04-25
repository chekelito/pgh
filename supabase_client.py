"""
supabase_client.py
Conexión con Supabase para PGH
"""

import streamlit as st
from supabase import create_client, Client

def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def verificar_codigo(codigo: str) -> bool:
    """Verifica si el código existe y no ha sido usado."""
    supabase = get_client()
    result = supabase.table("codigos").select("*").eq("codigo", codigo).eq("usado", False).execute()
    return len(result.data) > 0


def activar_codigo(codigo: str, email: str, nombre: str) -> bool:
    """Marca el código como usado y registra al usuario."""
    supabase = get_client()
    try:
        # Marcar código como usado
        supabase.table("codigos").update({
            "usado": True,
            "usuario_email": email,
            "fecha_activacion": str(__import__("datetime").date.today())
        }).eq("codigo", codigo).execute()

        # Registrar usuario
        supabase.table("usuarios").insert({
            "email": email,
            "nombre": nombre,
            "fecha_registro": str(__import__("datetime").date.today()),
            "codigo_usado": codigo
        }).execute()

        return True
    except Exception:
        return False


def es_usuario_pro(email: str) -> bool:
    """Verifica si el email tiene acceso Pro."""
    supabase = get_client()
    result = supabase.table("usuarios").select("*").eq("email", email).execute()
    return len(result.data) > 0


def guardar_boleta(email: str, datos: dict) -> bool:
    """Guarda una boleta en el historial del usuario."""
    supabase = get_client()
    try:
        supabase.table("boletas").insert({
            "usuario_email": email,
            "fecha": str(__import__("datetime").date.today()),
            **datos
        }).execute()
        return True
    except Exception:
        return False


def obtener_boletas(email: str) -> list:
    """Obtiene el historial de boletas de un usuario."""
    supabase = get_client()
    result = supabase.table("boletas").select("*").eq("usuario_email", email).order("created_at", desc=True).execute()
    return result.data

def eliminar_boleta(boleta_id: int) -> bool:
    """Elimina una boleta por su ID."""
    supabase = get_client()
    try:
        supabase.table("boletas").delete().eq("id", boleta_id).execute()
        return True
    except Exception:
        return False
