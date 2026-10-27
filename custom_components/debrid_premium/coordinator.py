"""Coordinador: uno por servicio configurado."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import CONSULTAS
from .const import CONF_CLAVE, CONF_SERVICIO, DOMAIN, INTERVALO

_LOGGER = logging.getLogger(__name__)


class DebridCoordinator(DataUpdateCoordinator[dict]):
    """Consulta un servicio debrid una vez al día."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.servicio = entry.data[CONF_SERVICIO]
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.servicio}",
            update_interval=timedelta(minutes=INTERVALO),
        )
        self._clave = entry.data[CONF_CLAVE]
        self._sesion = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        return await CONSULTAS[self.servicio](self._sesion, self._clave)
