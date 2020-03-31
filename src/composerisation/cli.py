import logging
import os
import sys

import click
import yaml

from composerisation.docker_compose.networks.networks import NetworkParser
from composerisation.docker_compose.services.services import ServicesParser
from composerisation.docker_compose.volumes.volumes import VolumeParser

from .utils import exceptions

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-i",
    "--input-file",
    type=click.File("r"),
    default=sys.stdin,
    required=True,
    help="Path to file to convert from docker-compose to Docker.",
)
@click.option(
    "--log-level",
    "-l",
    default="DEBUG",
    type=click.Choice(["DEBUG", "INFO", "ERROR", "CRITICAL"]),
    help="Log level for the script.",
)
def cli(input_file: str, log_level: str) -> list:
    """Converts docker-compose files to Docker comamnds."""
    logger.setLevel(log_level)
    docker_compose = get_docker_compose(input_file)

    try:
        start_commands = get_docker_start_commands(docker_compose)
        delete_commands = get_docker_delete_commands(docker_compose)
    except exceptions.IncorrectConfigException as e:
        error_message = f"Invalid key {e.incorrect_key} in {e.config_name}"
        logger.error(error_message)
        click.echo(error_message, err=True)
        sys.exit(1)

    commands = ["# Start Commands: ", ""] + start_commands + ["", "# Delete Commands: ", ""] + delete_commands
    click.echo("\n".join(commands))


def get_docker_compose(input_file: click.File) -> dict:
    """Gets the contents of the docker-compose file after it's been parsed by PyYaml. If the file cannot be opened or
    parsed i.e. incorrect yaml. Then it will throw an error and exit.

    Args:
        input_file (click.File): An file object (docker-compose).

    Returns:
        dict: Contents of the docker-compose file.

    """
    logger.info(f"Opening docker-compose file")
    try:
        data = "".join(sys.stdin.readlines()) if input_file.name == "<stdin>" else input_file.read()
        docker_compose = yaml.load(data, Loader=yaml.SafeLoader)
    except yaml.YAMLError as e:
        error_message = f"Invalid yaml file, {input_file.name}."
        logger.error(f"error_message, {e}")
        click.echo(error_message, err=True)
        sys.exit(1)

    logger.info(f"Retrieved docker compose data")
    return docker_compose


def get_docker_start_commands(docker_compose: dict) -> list:
    """Gets all the Docker cli commands required to start your containers, this includes creating docker volumes,
    networks and running images.

    Args:
        docker_compose (dict): The contents of the docker-compose file.

    Returns:
        list: Of Docker cli commands to create the same environment as created by docker-compose.

    """
    logger.info(f"Converting docker-compose to commands required to start your docker container.")
    start_commands = []
    default_name = os.path.basename(os.getcwd())
    default_network_name = f"{default_name}_network"
    networks_data = docker_compose.get("networks", {})
    networks_data[default_network_name] = {"driver": "bridge"}

    logger.info(f"Converting 'networks' sections to docker cli commands.")
    for name, config in networks_data.items():
        networks = NetworkParser(network_name=name, network_config=config)
        command = networks.get_start_command()
        start_commands.append(command)

    logger.info(f"Converting 'volumes' sections to docker cli commands.")
    volumes_data = docker_compose.get("volumes", {})
    for name, config in volumes_data.items():
        volume = VolumeParser(volume_name=name, volume_config=config)
        command = volume.get_start_command()
        start_commands.append(command)

    logger.info(f"Converting 'services' sections to docker cli commands.")
    services_data = docker_compose.get("services", {})
    for name, option in services_data.items():
        if "networks" not in option:
            option["network_mode"] = default_network_name

        service = ServicesParser(service_name=name, service_options=option)
        command = service.get_start_command()
        start_commands += command

    return start_commands


def get_docker_delete_commands(docker_compose: dict) -> list:
    """Gets all the Docker cli commands required to stop your containers.

    Args:
        docker_compose (dict): The contents of the docker-compose file.

    Returns:
        list: Of Docker cli commands to stop the running containers remove them and also the network they are \
            connect to.

    """
    logger.info(f"Converting docker-compose to commands required to delete your docker container.")
    delete_commands = []
    networks_data = docker_compose.get("networks", {})
    default_name = os.path.basename(os.getcwd())
    default_network_name = f"{default_name}_network"
    networks_data[default_network_name] = {"driver": "bridge", "name": default_network_name}

    logger.info(f"Converting 'networks' sections to docker cli commands.")
    for name, config in networks_data.items():
        networks = NetworkParser(network_name=name, network_config=config)
        command = networks.get_delete_command()
        delete_commands.append(command)

    logger.info(f"Converting 'services' sections to docker cli commands.")
    services_data = docker_compose.get("services", {})
    for name, option in services_data.items():
        if "networks" not in option:
            option["network_mode"] = default_network_name

        service = ServicesParser(service_name=name, service_options=option)
        command = service.get_delete_command()
        delete_commands += command

    return delete_commands


if __name__ == "__main__":
    cli(sys.argv[1:])
