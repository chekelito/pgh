"""
supabase_client.py
Conexión con Supabase para PGH
"""

import streamlit as st
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

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
    """Marca el código como usado y registra al usuario con contraseña encriptada."""
    supabase = get_client()
    try:
        # 1. Encriptamos la contraseña antes de hacer cualquier otra cosa
        password_encriptada = generate_password_hash(password)

        # 2. Marcar código como usado
        supabase.table("codigos").update({
            "usado": True,
            "usuario_email": email,
            "fecha_activacion": str(__import__("datetime").date.today())
        }).eq("codigo", codigo).execute()

        # 3. Registrar usuario guardando la versión segura de la contraseña
        supabase.table("usuarios").upsert({
            "email": email,
            "nombre": nombre,
            "password": password_encriptada, 
            "fecha_registro": str(__import__("datetime").date.today()),
            "codigo_usado": codigo
        }, on_conflict="email").execute()

        return True
    except Exception as e:
        print(f"Error al activar: {e}")
        return False


def validar_login(email: str, password: str) -> bool:
    """Verifica si el email existe y la contraseña coincide con el hash seguro."""
    supabase = get_client()
    try:
        # 1. Buscamos al usuario SOLO por su email para traer su contraseña encriptada
        result = supabase.table("usuarios").select("password").eq("email", email).execute()
        
        # 2. Si el usuario existe, comparamos lo que escribió con lo que está guardado
        if len(result.data) > 0:
            hash_guardado = result.data[0]["password"]
            
            # check_password_hash desencripta de forma segura y devuelve True si coinciden
            if check_password_hash(hash_guardado, password):
                return True
                
        return False
    except Exception as e:
        print(f"Error al validar login: {e}")
        return False


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
