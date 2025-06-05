![GitHub release (latest by date)](https://img.shields.io/github/v/release/kgn3400/docker_status)
![GitHub all releases](https://img.shields.io/github/downloads/kgn3400/docker_status/total)
![GitHub last commit](https://img.shields.io/github/last-commit/kgn3400/docker_status)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kgn3400/docker_status)
[![Validate% with hassfest](https://github.com/kgn3400/docker_status/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/kgn3400/docker_status/actions/workflows/hassfest.yaml)

<img align="left" width="80" height="80" src="https://kgn3400.github.io/docker_status/assets/icon@2x.png" alt="App icon">

# Docker status

<br/>

The Docker status integration allows you to monitor multiple Docker and container installations. Getting the status/statistics of your
containers and images.


To enable remote access to the docker host, [check this guide](https://docs.docker.com/engine/daemon/remote-access/)

Unused images can been pruned via service __prune_images__.

## Installation

For installation instructions until the Docker status integrations is part of HACS, [see this guide](https://hacs.xyz/docs/faq/custom_repositories).

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=docker_status)
Or click
[![My Home Assistant](https://img.shields.io/badge/Home%20Assistant-%2341BDF5.svg?style=flat&logo=home-assistant&label=Add%20to%20HACS)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kgn3400&repository=docker_status&category=integration)

## Configuration

Configuration is setup via UI in Home assistant. To add one, go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations) and click the add button. Next choose the [Docker status](https://my.home-assistant.io/redirect/config_flow_start?domain=docker_status) option.

## Sensors

<img src="https://kgn3400.github.io/docker_status/assets/sensors.png" width="400" height="auto" alt="Config">
<br>

## Actions

Available actions: __prune_images__ and __update__
