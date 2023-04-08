"""Support for Docker status."""
from __future__ import annotations

from homeassistant.components.sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .component_api import ComponentApi
from .const import (
    CONF_DOCKER_BASE_NAME,
    CONF_DOCKER_ENGINE_URL,
    CONF_DOCKER_ENV_SENSOR_NAME,
    CONF_SENSORS,
    DOCKER_SENSORS,
    DOCKER_SENSORS_SUM,
    DOMAIN,
)
from .entity import ComponentEntity


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Entry for Docker status setup."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    component_api: ComponentApi = hass.data[DOMAIN][entry.entry_id]["component_api"]

    sensors = []

    config = dict(entry.options)

    for sensor in config[CONF_SENSORS]:
        for docker_sensor in DOCKER_SENSORS:
            sensors.append(
                DockerSensor(
                    coordinator,
                    entry,
                    component_api,
                    sensor[CONF_DOCKER_ENV_SENSOR_NAME],
                    docker_sensor,
                    sensor[CONF_DOCKER_ENGINE_URL],
                    sensor[CONF_UNIQUE_ID],
                )
            )

    # -- Sum sensors
    for docker_sensor in DOCKER_SENSORS_SUM:
        sensors.append(
            DockerSensorSum(
                coordinator,
                entry,
                component_api,
                config[CONF_DOCKER_BASE_NAME],
                docker_sensor,
                config[CONF_UNIQUE_ID],
            )
        )

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class DockerSensor(ComponentEntity, SensorEntity):
    """Sensor class Docker."""

    # ------------------------------------------------------
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        component_api: ComponentApi,
        sensor_env_name: str,
        sensor_type: str,
        sensor_engine_url: str,
        sensor_unigue_id: str,
    ) -> None:
        """Docker sensor."""
        super().__init__(coordinator, entry)

        self.component_api = component_api
        self.coordinator = coordinator
        self.env_name = sensor_env_name
        self.sensor_type: str = sensor_type
        self.engine_url = sensor_engine_url
        self._unique_id = sensor_unigue_id

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name."""
        return f"{self.env_name} {self.sensor_type}"

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        """Icon."""
        return "mdi:docker"

    # ------------------------------------------------------
    @property
    def native_value(self) -> int | float | None:
        """Native value."""
        return self.component_api.get_value(self.env_name, self.sensor_type)

    # ------------------------------------------------------
    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit the value is expressed in."""
        return self.component_api.get_value_uom(self.env_name, self.sensor_type)

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes."""
        attr: dict = {}

        return attr

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
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


# ------------------------------------------------------
# ------------------------------------------------------
class DockerSensorSum(ComponentEntity, SensorEntity):
    """Sensor class Docker sum."""

    # ------------------------------------------------------
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        component_api: ComponentApi,
        sensor_name: str,
        sensor_type: str,
        sensor_unigue_id: str,
    ) -> None:
        """Docker sensor sum."""
        super().__init__(coordinator, entry)

        self.component_api = component_api
        self.coordinator = coordinator
        self._name = sensor_name
        self.sensor_type: str = sensor_type
        self.sensor_unique_id = sensor_unigue_id

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name."""
        return f"{self._name} {self.sensor_type} sum"

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        """Icon."""
        return "mdi:docker"

    # ------------------------------------------------------
    @property
    def native_value(self) -> int | float | None:
        """Native value."""
        return self.component_api.get_value_sum(self.sensor_type)

    # ------------------------------------------------------
    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit the value is expressed in."""
        return self.component_api.get_value_sum_uom(self.sensor_type)

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes."""
        attr: dict = {}

        return attr

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id."""
        return self.sensor_unique_id + self.sensor_type

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
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
