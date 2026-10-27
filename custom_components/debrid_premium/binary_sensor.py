"""Binario: ¿la cuenta tiene premium activo?"""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SERVICIO, DOMAIN
from .coordinator import DebridCoordinator
from .sensor import _dispositivo


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinador: DebridCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PremiumDebrid(coordinador, entry)])


class PremiumDebrid(CoordinatorEntity[DebridCoordinator], BinarySensorEntity):
    """Verdadero mientras el premium esté activo."""

    _attr_has_entity_name = True
    _attr_translation_key = "premium"
    _attr_icon = "mdi:crown"

    def __init__(self, coordinador: DebridCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinador)
        self._attr_unique_id = f"{entry.entry_id}_premium"
        self._attr_device_info = _dispositivo(entry)

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get("premium"))

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and bool(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict:
        datos = self.coordinator.data or {}
        caduca = datos.get("caduca")
        return {
            "dias_restantes": datos.get("dias_restantes"),
            "caduca": caduca.isoformat() if caduca else None,
            "tipo": datos.get("tipo_cuenta"),
        }
