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


def activar_codigo(codigo: str, email: str, nombre: str, password: str) -> bool:
    """Marca el código como usado y registra al usuario con contraseña."""
    supabase = get_client()
    try:
        # Marcar código como usado
        supabase.table("codigos").update({
            "usado": True,
            "usuario_email": email,
            "fecha_activacion": str(__import__("datetime").date.today())
        }).eq("codigo", codigo).execute()

        # Registrar o Actualizar usuario (Upsert) con contraseña
        supabase.table("usuarios").upsert({
            "email": email,
            "nombre": nombre,
            "password": password,
            "fecha_registro": str(__import__("datetime").date.today()),
            "codigo_usado": codigo
        }, on_conflict="email").execute()

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def validar_login(email: str, password: str) -> bool:
    """Verifica si el email existe y la contraseña es correcta."""
    supabase = get_client()
    result = supabase.table("usuarios").select("*").eq("email", email).eq("password", password).execute()
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

def eliminar_boleta(boleta_id) -> bool:
    """Elimina una boleta del historial usando su ID."""
    supabase = get_client()
    try:
        supabase.table("boletas").delete().eq("id", boleta_id).execute()
        return True
    except Exception:
        return False

def obtener_todos_usuarios():
    """Trae la lista de todos los usuarios para el panel de admin."""
    supabase = get_client()
    res = supabase.table("usuarios").select("*").order("fecha_registro", desc=True).execute()
    return res.data

def renovar_suscripcion_usuario(email):
    """Actualiza la fecha de registro a hoy para reiniciar los 30 días."""
    supabase = get_client()
    try:
        supabase.table("usuarios").update({
            "fecha_registro": str(__import__("datetime").date.today())
        }).eq("email", email).execute()
        return True
    except Exception:
        return False
