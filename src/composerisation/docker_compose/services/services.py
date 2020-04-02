# -*- coding: utf-8 -*-
"""This module creates the all the commands related to the services this includes building images, running the
images and connecting networks.

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""

from ..parser import Parser
from .build import ServiceBuildParser
from .networks import ServiceNetworkParser


class ServicesParser(Parser):
    """This class converts service in docker-compose services into various docker commands.
    For example given the below yaml definition (docker-compose.yml).

    ::

        services:
            webapp:
                build:
                    context: ./dir
                    dockerfile: Dockerfile-alternate
                container_name: MyContainer
                networks:
                    app_net:
                        ipv4_address: 172.16.238.10

    Once parsed it will look something like:

    ::

        "webapp": {
            "build":{
                "context": "./dir",
                "dockerfile": "Dockerfile-alternate",
            },
            "container_name": MyContainer,
            "networks": {
                "app_net": {
                    "ipv4_address": "172.16.238.10",
                }
            }
        },

    We generate the following command:

    ::

        docker build --file Dockerfile-alternate --tag composerisation_webapp ./dir
        docker run --name MyContainer --detach composerisation_webapp
        docker network connect --ip 172.16.238.10 app_net composerisation_webapp

    Following config options are ignored:

    - configs
    - credential_spec
    - depends_on
    - deploy
    - external_links
    - healthcheck
    - secrets
    - volume (long syntax)

    Args:
        service_name (str): The service name.
        service_options (dict): The service config options.

    """

    def __init__(self, service_name: str, service_options: dict):
        args = {
            "cap_add": {"type": [list], "name": "--cap-add"},
            "cap_drop": {"type": [list], "name": "--cap-drop"},
            "cgroup_parent": {"type": [str], "name": "--cgroup-parent"},
            "container_name": {"type": [str], "name": "--name"},
            "device": {"type": [list], "name": "--device"},
            "dns": {"type": [list, str], "name": "--dns"},
            "dns_search": {"type": [list, str], "name": "--dns-search"},
            "entrypoint": {"type": [str], "name": "--entrypoint"},
            "env_file": {"type": [list, str], "name": "--env-file"},
            "environment": {"type": [list, dict], "name": "--environment"},
            "expose": {"type": [list], "name": "--expose"},
            "extra_hosts": {"type": [list], "name": "--add-host"},
            "init": {"type": [bool], "name": "--init"},
            "isolation": {"type": [str], "name": "--isolation"},
            "labels": {"type": [list], "name": "--label"},
            "links": {"type": [list], "name": "--link"},
            "network_mode": {"type": [str], "name": "--network"},
            "pid": {"type": [str], "name": "--pid"},
            "ports": {"type": [list], "name": "--publish"},
            "restart": {"type": [str], "name": "--restart"},
            "security_opt": {"type": [list], "name": "--security-opt"},
            "stop_grace_period": {"type": [str], "name": "--stop-timeout"},
            "stop_signal": {"type": [str], "name": "--stop-signal"},
            "sysctls": {"type": [list, dict], "name": "--sysctl"},
            "tmpfs": {"type": [list], "name": "--tmpfs"},
            "userns_mode": {"type": [str], "name": "--userns"},
            "volumes": {"type": [list], "name": "--volume"},
        }
        special_args = {"ulimits": self._parse_ulimits, "logging": self._parse_logging}
        ignore_args = [
            "build",
            "command",
            "configs",
            "credential_spec",
            "depends_on",
            "deploy",
            "external_links",
            "healthcheck",
            "networks",
            "image",
            "secrets",
        ]
        super().__init__(
            args=args,
            config_name=service_name,
            config_options=service_options,
            special_args=special_args,
            ignore_args=ignore_args,
        )

    def get_start_command(self) -> list:
        """This function returns a list of all the commands you will need to recreate the docker-compose service
        using the docker cli. Each item in the list is a docker command you can run. They should be in the
        order they are presented in, for example you need to build a container before you can run it.

        For each service you will always get a `docker run` command you may also get a `docker build` and a
        `docker network` depending on what config options are set within that service (build/networking).

        Returns:
            list: A list of commands required by the services this includes `docker build`, `docker run` and \
                `docker network connect`.

        """
        service_commands = []
        image_name = self._get_image_name()
        container_name = self._get_container_name()

        if "build" in self.config_options:
            build_config = self.config_options["build"]
            build = ServiceBuildParser(service_name=image_name, build_config=build_config)
            build_command = build.get_command()
            service_commands.append(build_command)

        run_command = self._add_run_command(container_name, image_name)
        service_commands.append(run_command)

        if "networks" in self.config_options:
            networks_config = self.config_options["networks"]
            for name, config in networks_config.items():
                network = ServiceNetworkParser(service_name=container_name, network_name=name, network_config=config)
                network_command = network.get_command()
                service_commands.append(network_command)
        return service_commands

    def _add_run_command(self, container_name: str, image_name: str) -> str:
        """This function will get the equivalent `docker run` command for a given service config in docker compose.
        Including the args required. If a name is not specified the container will be named after the service.

        Args:
            container_name (str): What to call the container once it's running.
            image_name (str): The name of the image we will run.

        Returns:
            str: The `docker run` commands for the given `service_options`. This will start our docker image and run \
                it.

        """
        args = self._get_args()
        if "container_name" not in self.config_options:
            args += f" --name {container_name}"

        command = self.config_options.get("command", "")
        if isinstance(command, list):
            command = " ".join(command)
            command = f'"{command}"'

        run_command = f"docker run {args} --detach {image_name} {command}".strip()
        return run_command

    def get_delete_command(self) -> list:
        """This function returns the a list of commands to remove the docker container from your system.

        Returns:
            list: Of commands required to remove a running docker contianer.

        """
        container_name = self._get_container_name()
        stop_command = f"docker stop {container_name}"
        remove_command = f"docker rm {container_name}"
        return [stop_command, remove_command]

    def _parse_ulimits(self, ulimits: dict) -> str:
        """For parsing any `ulimits` options with in docker-compose the logic for this is a bit more complicated as
        compared with normal args. The key and value parsed can be of any value and they can also define hard & soft
        values.This function will get passed to the `_get_args()` function as `kwargs`.

        Example `ulimits` config option below.

        ::

            {"nproc": 65535, "nofile": {"soft": 20000, "hard": 40000}}

        Example arguments returned.

        ::

            --ulimit nproc=65535 --ulimit nofile=20000:40000

        Args:
            ulimits (dict): The ulimits config options (see example above).

        Returns:
            str: The equivalent cli arguments for docker commands for `ulimits` option in docker-compose.

        """
        ulimit_args = ""
        for name, value in ulimits.items():
            if isinstance(value, dict):
                soft, hard = value["soft"], value["hard"]
                ulimit = f"--ulimit {name}={soft}:{hard} "
            else:
                ulimit = f"--ulimit {name}={value} "
            ulimit_args += ulimit

        return ulimit_args

    def _parse_logging(self, logging: dict) -> str:
        """For parsing any `logging` options with in docker-compose the logic for this is a bit more complicated as
        compared with normal args. We need to parse the `logging` object. For example it can contain a driving logger
        and then extra logging options where the key and value can be "anything". This function will get passed to the
        `_get_args()` function as `kwargs`.

        Example `logging` config option below.

        ::

            {"driver": "json-file", "options": {"max-size": "1k", "max-file": "3"}}


        Example arguments returned.

        ::

            --log-driver json-file --log-opt max-size=1k --log-opt max-file=3

        Args:
            logging (dict): The logging config options (see example above).

        Returns:
            str: The equivalent cli arguments for docker commands for `logging` option in docker-compose.

        """
        logging_args = ""
        driver = logging.get("driver", "")
        logging_args += f"--log-driver {driver} "
        logging_opts = self._get_config_val(config=logging, config_key="options")

        for name, value in logging_opts.items():
            logging_args += f"--log-opt {name}={value} "

        return logging_args
