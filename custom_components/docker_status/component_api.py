"""Component api."""

from dataclasses import dataclass
from functools import partial

import docker
from docker import errors
from docker.models.containers import Container
from docker.models.images import Image
from docker.models.volumes import Volume

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_DOCKER_ENGINE_URL,
    CONF_DOCKER_ENV_SENSOR_NAME,
    CONF_SENSORS,
    LOGGER,
    SENSOR_CONTAINERS_CPU_PERCENT,
    SENSOR_CONTAINERS_MEMORY_USAGE,
    SENSOR_CONTAINERS_RUNNING,
    SENSOR_CONTAINERS_STOPPED,
    SENSOR_IMAGES,
    SENSOR_IMAGES_DANGLING,
    SENSOR_IMAGES_UNUSED,
    SENSOR_VOLUMES,
    SENSOR_VOLUMES_UNUSED,
)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class DockerData:
    """Docker data."""

    def __init__(self, sensor_name: str, engine_url: str) -> None:
        """Docker data."""
        self.sensor_name: str = sensor_name
        self.engine_url: str = engine_url

        self.client: docker.DockerClient
        self.values: dict[str, int | float] = {}
        self.values_uom: dict[str, str] = {}


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class ComponentApi:
    """Docker status interface."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Component api."""
        self.hass = hass
        self.entry: ConfigEntry = entry
        self.coordinator: DataUpdateCoordinator
        self.client: docker.DockerClient
        self.first_time: bool = True
        self.env_sensors: dict[str, DockerData] = {}

    # ------------------------------------------------------------------
    async def async_update(self) -> None:
        """Update."""

        if self.first_time:
            await self.async_init()

        self.first_time = False

        await self.update_sensors_date()

    # ------------------------------------------------------------------
    async def update_sensors_date(self) -> None:
        """Update data."""

        def convert_bytes_to(byte_count: int) -> tuple[float, str]:
            """Konverterer bytes til MB eller GB baseret på størrelsen."""
            units: list[str] = ["B", "KB", "MB", "GB"]
            size: float = float(byte_count)

            for unit in units:
                if size < 1024:
                    return (size, unit)
                size /= 1024
            return (size, "B")

        for env_sensor in self.env_sensors.values():
            # -- Containers
            env_sensor.values[SENSOR_CONTAINERS_RUNNING] = 0
            env_sensor.values[SENSOR_CONTAINERS_STOPPED] = 0
            cpu_percent = 0.0
            memory_usage_bytes: int = 0

            containers: list[Container] = await self.hass.async_add_executor_job(
                env_sensor.client.containers.list, True
            )  # type: ignore

            for container in containers:
                if container.status != "running":
                    env_sensor.values[SENSOR_CONTAINERS_STOPPED] += 1
                    continue

                env_sensor.values[SENSOR_CONTAINERS_RUNNING] += 1

                stats = await self.hass.async_add_executor_job(
                    partial(container.stats, decode=False, stream=False)
                )

                cpu_delta = float(
                    stats["cpu_stats"]["cpu_usage"]["total_usage"]
                ) - float(stats["precpu_stats"]["cpu_usage"]["total_usage"])
                system_cpu_delta = float(
                    stats["cpu_stats"]["system_cpu_usage"]
                ) - float(stats["precpu_stats"]["system_cpu_usage"])

                if system_cpu_delta > 0.0 and cpu_delta > 0.0:
                    cpu_percent += (
                        (cpu_delta / system_cpu_delta)
                        #      * float(len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]))
                        * 100.0
                    )

                memory_usage_bytes += stats["memory_stats"]["usage"]

            env_sensor.values[SENSOR_CONTAINERS_CPU_PERCENT] = round(cpu_percent, 2)
            env_sensor.values_uom[SENSOR_CONTAINERS_CPU_PERCENT] = "%"

            memory_usage, uom = convert_bytes_to(memory_usage_bytes)

            env_sensor.values[SENSOR_CONTAINERS_MEMORY_USAGE] = round(memory_usage, 2)
            env_sensor.values_uom[SENSOR_CONTAINERS_MEMORY_USAGE] = uom

            # -- images
            images: list[Image] = await self.hass.async_add_executor_job(
                env_sensor.client.images.list
            )  # type: ignore

            env_sensor.values[SENSOR_IMAGES] = len(images)
            env_sensor.values[SENSOR_IMAGES_DANGLING] = len(
                await self.hass.async_add_executor_job(
                    env_sensor.client.images.list, None, False, {"dangling": True}
                )
            )

            tmp_count: int = 0

            for image in images:
                for container in containers:
                    if image.id == container.attrs.get("Image", ""):  # type: ignore
                        tmp_count += 1

            env_sensor.values[SENSOR_IMAGES_UNUSED] = (
                env_sensor.values[SENSOR_IMAGES] - tmp_count
            )

            # -- Volumes

            volumes: list[Volume] = await self.hass.async_add_executor_job(
                env_sensor.client.volumes.list
            )  # type: ignore

            env_sensor.values[SENSOR_VOLUMES] = len(volumes)

            tmp_count: int = 0

            for volume in volumes:
                volume_is_used = False

                for container in containers:
                    for mount in container.attrs["Mounts"]:  # type:ignore
                        if (
                            mount.get("Type", "") == "volume"
                            and mount.get("Name", "") == volume.name
                        ):
                            tmp_count += 1
                            volume_is_used = True
                            break
                    if volume_is_used:
                        break

            env_sensor.values[SENSOR_VOLUMES_UNUSED] = (
                env_sensor.values[SENSOR_VOLUMES] - tmp_count
            )

    # ------------------------------------------------------------------
    async def async_init(self) -> None:
        """Init."""
        config = dict(self.entry.options)

        for sensor in config[CONF_SENSORS]:
            tmp_data = DockerData(
                sensor.get(CONF_DOCKER_ENV_SENSOR_NAME),
                sensor.get(CONF_DOCKER_ENGINE_URL),
            )

            try:
                tmp_data.client = await self.hass.async_add_executor_job(
                    docker.DockerClient, tmp_data.engine_url
                )
            except errors.DockerException:
                LOGGER.exception("Error creating docker client")

            self.env_sensors[tmp_data.sensor_name] = tmp_data

    # ------------------------------------------------------------------
    def get_value(self, env_sensor_name: str, sensor_type: str) -> int | float:
        """Get value."""
        return self.env_sensors[env_sensor_name].values.get(sensor_type, 0)

    # ------------------------------------------------------------------
    def get_value_uom(self, env_sensor_name: str, sensor_type: str) -> str | None:
        """Get value unit of measurement."""
        return self.env_sensors[env_sensor_name].values_uom.get(sensor_type, None)

    # ------------------------------------------------------------------
    def get_value_sum(self, sensor_type: str) -> int | float:
        """Get value sum."""

        tmp_sum: int | float = 0

        for sensor in self.env_sensors.values():
            tmp_sum += sensor.values.get(sensor_type, 0)

        return tmp_sum

    # ------------------------------------------------------------------
    def get_value_sum_uom(self, sensor_type: str) -> str | None:
        """Get value sum."""

        for sensor in self.env_sensors.values():
            if sensor.values.get(sensor_type, None) is not None:
                return sensor.values_uom.get(sensor_type, None)

        return None
