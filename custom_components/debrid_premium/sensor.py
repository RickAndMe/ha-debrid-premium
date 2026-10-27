"""Sensores por servicio: días que quedan, caducidad y puntos."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SERVICIO, DOMAIN, SERVICIOS
from .coordinator import DebridCoordinator


@dataclass(frozen=True, kw_only=True)
class SensorDebrid(SensorEntityDescription):
    """Descripción de un sensor debrid."""


DIAS = SensorDebrid(
    key="dias_restantes",
    translation_key="dias_restantes",
    icon="mdi:calendar-clock",
    native_unit_of_measurement="d",
    suggested_display_precision=0,
)
CADUCA = SensorDebrid(
    key="caduca",
    translation_key="caduca",
    icon="mdi:calendar-end",
    device_class=SensorDeviceClass.TIMESTAMP,
)
PUNTOS = SensorDebrid(
    key="puntos",
    translation_key="puntos",
    icon="mdi:star-circle-outline",
)


def _dispositivo(entry: ConfigEntry) -> DeviceInfo:
    servicio = entry.data[CONF_SERVICIO]
    info = SERVICIOS[servicio]
    return DeviceInfo(
        identifiers={(DOMAIN, servicio)},
        name=info["name"],
        manufacturer=info["name"],
        model="Cuenta premium",
        entry_type=DeviceEntryType.SERVICE,
        configuration_url=info["account_url"],
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Solo los sensores que ese servicio sabe dar."""
    coordinador: DebridCoordinator = hass.data[DOMAIN][entry.entry_id]
    servicio = entry.data[CONF_SERVICIO]
    descripciones = [DIAS, CADUCA]
    if SERVICIOS[servicio].get("puntos"):
        descripciones.append(PUNTOS)

    async_add_entities(
        SensorServicio(coordinador, entry, d) for d in descripciones
    )


class SensorServicio(CoordinatorEntity[DebridCoordinator], SensorEntity):
    """Un dato de la cuenta debrid."""

    _attr_has_entity_name = True
    entity_description: SensorDebrid

    def __init__(
        self,
        coordinador: DebridCoordinator,
        entry: ConfigEntry,
        descripcion: SensorDebrid,
    ) -> None:
        super().__init__(coordinador)
        self.entity_description = descripcion
        self._attr_unique_id = f"{entry.entry_id}_{descripcion.key}"
        self._attr_device_info = _dispositivo(entry)

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self.entity_description.key)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and bool(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict:
        datos = self.coordinator.data or {}
        atributos: dict = {}
        if datos.get("usuario"):
            atributos["cuenta"] = datos["usuario"]
        if datos.get("tipo_cuenta"):
            atributos["tipo"] = datos["tipo_cuenta"]
        if datos.get("premium") is not None:
            atributos["premium"] = datos["premium"]
        return atributos
