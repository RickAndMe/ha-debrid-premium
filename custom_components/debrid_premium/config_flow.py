"""Configuración: un servicio por entrada."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import prueba_clave
from .const import CONF_CLAVE, CONF_SERVICIO, DOMAIN, SERVICIOS

_LOGGER = logging.getLogger(__name__)

ESQUEMA_CLAVE = vol.Schema({vol.Required(CONF_CLAVE): str})


class DebridConfigFlow(ConfigFlow, domain=DOMAIN):
    """Alta de un servicio debrid."""

    VERSION = 1

    def _disponibles(self) -> list[str]:
        ya = {
            e.data.get(CONF_SERVICIO)
            for e in self._async_current_entries(include_ignore=False)
        }
        return [s for s in SERVICIOS if s not in ya]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        disponibles = self._disponibles()
        if not disponibles:
            return self.async_abort(reason="todos_configurados")
        return self.async_show_menu(step_id="user", menu_options=disponibles)

    async def async_step_realdebrid(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._pide_clave("realdebrid", user_input)

    async def async_step_alldebrid(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._pide_clave("alldebrid", user_input)

    async def async_step_torbox(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._pide_clave("torbox", user_input)

    async def _pide_clave(
        self, servicio: str, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        errores: dict[str, str] = {}

        if user_input is not None:
            clave = (user_input.get(CONF_CLAVE) or "").strip()
            if not clave:
                errores[CONF_CLAVE] = "clave_vacia"
            else:
                sesion = async_get_clientsession(self.hass)
                if await prueba_clave(sesion, servicio, clave):
                    await self.async_set_unique_id(servicio)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=SERVICIOS[servicio]["name"],
                        data={CONF_SERVICIO: servicio, CONF_CLAVE: clave},
                    )
                errores[CONF_CLAVE] = "clave_invalida"

        return self.async_show_form(
            step_id=servicio,
            data_schema=ESQUEMA_CLAVE,
            errors=errores,
            description_placeholders={
                "servicio": SERVICIOS[servicio]["name"],
                "donde": SERVICIOS[servicio]["token_url"],
            },
        )
