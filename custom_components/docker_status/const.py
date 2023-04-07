"""Constants for Scrape integration."""
from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__name__)

DOMAIN = "docker_status"
DOMAIN_NAME = "Docker status"
DEFAULT_SCAN_INTERVAL = 1
DEFAULT_CHECK_FOR_UPDATED_IMAGES = 6


CONF_DOCKER_BASE_NAME = "docker_base_name"
CONF_DOCKER_ENGINE_URL = "docker_engine_url"
CONF_DOCKER_ENV_SENSOR_NAME = "docker_env_sensor_name"
CONF_CHECK_FOR_UPDATED_IMAGES_HOURS = "check_for_updated_images_hours"
CONF_INDEX = "index"
CONF_SENSORS = "sensors"
CONF_CHECK_FOR_IMAGES_UPDATES = "check_for_images_updates"

SENSOR_CONTAINERS_RUNNING = "Containers running"
SENSOR_CONTAINERS_STOPPED = "Containers stopped"
SENSOR_IMAGES = "Images"
SENSOR_IMAGES_UNUSED = "Images unused"
SENSOR_IMAGES_DANGLING = "Images dangling"
SENSOR_VOLUMES = "Volumes"
SENSOR_VOLUMES_UNUSED = "Volumes unused"

DOCKER_SENSORS = [
    SENSOR_CONTAINERS_RUNNING,
    SENSOR_CONTAINERS_STOPPED,
    SENSOR_IMAGES,
    SENSOR_IMAGES_UNUSED,
    SENSOR_IMAGES_DANGLING,
    SENSOR_VOLUMES,
    SENSOR_VOLUMES_UNUSED,
]
