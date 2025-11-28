"""Support for Docker status."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CommonConfigEntry
from .component_api import ComponentApi
from .const import (
    BINARY_SENSOR_CONNECTED,
    CONF_DOCKER_BASE_NAME,
    CONF_DOCKER_BASE_NAME_USE_IN_SENSOR_NAME,
    CONF_DOCKER_ENGINE_URL,
    CONF_DOCKER_ENV_SENSOR_NAME,
    CONF_SENSORS,
    TRANSLATION_KEY,
)
from .entity import ComponentEntity


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CommonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Entry for Docker status setup."""
    sensors = []

    config = dict(entry.options)

    sensors.extend(
        DockerBinarySensor(
            hass,
            entry,
            config.get(CONF_DOCKER_BASE_NAME, ""),
            sensor[CONF_DOCKER_ENV_SENSOR_NAME],
            BINARY_SENSOR_CONNECTED,
            sensor[CONF_DOCKER_ENGINE_URL],
            sensor[CONF_UNIQUE_ID],
        )
        for sensor in config[CONF_SENSORS]
    )

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class DockerBinarySensor(ComponentEntity, BinarySensorEntity):
    """Binary Sensor class Docker."""

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: CommonConfigEntry,
        docker_base_name: str,
        sensor_env_name: str,
        sensor_type: str,
        sensor_engine_url: str,
        sensor_unigue_id: str,
    ) -> None:
        """Docker sensor."""
        super().__init__(entry.runtime_data.coordinator, entry)

        self.hass: HomeAssistant = hass
        self.component_api: ComponentApi = entry.runtime_data.component_api
        self.coordinator = entry.runtime_data.coordinator
        self.entry: CommonConfigEntry = entry
        self.docker_base_name = docker_base_name
        self.env_name = sensor_env_name
        self.sensor_type: str = sensor_type
        self.engine_url = sensor_engine_url
        self._unique_id = sensor_unigue_id

        self.translation_key = TRANSLATION_KEY

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name."""

        return (
            f"{self.docker_base_name} {self.env_name} - Status"
            if self.entry.options.get(CONF_DOCKER_BASE_NAME_USE_IN_SENSOR_NAME, False)
            else f"{self.env_name} - Status"
        )

    # --------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """Get the state."""

        return self.component_api.get_value(self.env_name, self.sensor_type, False)

    # ------------------------------------------------------
    @property
    def device_class(self):
        """Device class."""
        return "connectivity"

    # # ------------------------------------------------------
    # @property
    # def native_unit_of_measurement(self) -> str | None:
    #     """Return the unit the value is expressed in."""
    #     return self.component_api.get_value_uom(self.env_name, self.sensor_type)

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id."""
        return self._unique_id + self.sensor_type

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""

        await super().async_added_to_hass()

        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
