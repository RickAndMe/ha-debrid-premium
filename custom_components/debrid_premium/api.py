"""Consultas a las APIs de los servicios debrid."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import SERVICIOS, TIMEOUT


async def _pide(sesion, url: str, clave: str) -> dict:
    """GET autenticado con Bearer."""
    cabeceras = {
        "Authorization": f"Bearer {clave}",
        "Accept": "application/json",
        "User-Agent": "hermes-debrid-premium/1.0",
    }
    try:
        async with asyncio.timeout(TIMEOUT):
            async with sesion.get(url, headers=cabeceras) as resp:
                if resp.status in (401, 403):
                    raise UpdateFailed("la clave ha sido rechazada")
                if resp.status != 200:
                    raise UpdateFailed(f"respuesta HTTP {resp.status}")
                return await resp.json(content_type=None)
    except asyncio.TimeoutError as err:
        raise UpdateFailed("la API no respondió a tiempo") from err


def _fecha(valor) -> datetime | None:
    """ISO 8601 o epoch -> datetime con zona."""
    if not valor:
        return None
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(float(valor), tz=timezone.utc)
    try:
        fecha = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        return fecha if fecha.tzinfo else fecha.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _dias(fecha: datetime | None) -> int:
    if fecha is None:
        return 0
    return max(0, (fecha - datetime.now(timezone.utc)).days)


async def lee_realdebrid(sesion, clave: str) -> dict:
    datos = await _pide(sesion, SERVICIOS["realdebrid"]["url"], clave)
    tipo = str(datos.get("type") or "").lower()
    segundos = int(datos.get("premium") or 0)
    caduca = _fecha(datos.get("expiration"))
    return {
        "premium": tipo == "premium" and segundos > 0,
        "dias_restantes": _dias(caduca) if caduca else max(0, segundos // 86400),
        "caduca": caduca,
        "puntos": datos.get("points"),
        "usuario": datos.get("username"),
        "tipo_cuenta": tipo or "desconocido",
    }


async def lee_alldebrid(sesion, clave: str) -> dict:
    crudo = await _pide(sesion, SERVICIOS["alldebrid"]["url"], clave)
    usuario = ((crudo.get("data") or {}).get("user")) or {}
    caduca = _fecha(usuario.get("premiumUntil"))
    if usuario.get("isTrial"):
        tipo = "prueba"
    elif usuario.get("isSubscribed"):
        tipo = "suscripción"
    elif usuario.get("isPremium"):
        tipo = "premium"
    else:
        tipo = "gratis"
    return {
        "premium": bool(usuario.get("isPremium")),
        "dias_restantes": _dias(caduca),
        "caduca": caduca,
        "puntos": usuario.get("fidelityPoints"),
        "usuario": usuario.get("username"),
        "tipo_cuenta": tipo,
    }


async def lee_torbox(sesion, clave: str) -> dict:
    crudo = await _pide(sesion, SERVICIOS["torbox"]["url"], clave)
    datos = crudo.get("data") or {}
    if isinstance(datos, list):
        datos = datos[0] if datos else {}
    caduca = _fecha(datos.get("premium_expires_at"))
    return {
        "premium": bool(datos.get("is_subscribed")),
        "dias_restantes": _dias(caduca),
        "caduca": caduca,
        "usuario": datos.get("email") or datos.get("customer") or datos.get("username"),
        "tipo_cuenta": str(datos.get("plan") or "desconocido"),
    }


CONSULTAS = {
    "realdebrid": lee_realdebrid,
    "alldebrid": lee_alldebrid,
    "torbox": lee_torbox,
}


async def prueba_clave(sesion, servicio: str, clave: str) -> bool:
    """True si la clave responde 200 en la API del servicio."""
    try:
        await _pide(sesion, SERVICIOS[servicio]["url"], clave)
        return True
    except Exception:  # noqa: BLE001
        return False
