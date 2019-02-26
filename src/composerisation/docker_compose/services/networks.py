# -*- coding: utf-8 -*-
"""This module creates the network commands from the network option within services.

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""

from ..parser import Parser


class ServiceNetworkParser(Parser):
    """This class converts network in docker-compose services into `docker network` connect commands.
    For example given the below yaml definition (docker-compose.yml).

    ::

        services:
            app:
                image: nginx:alpine
                networks:
                    app_net:
                        ipv4_address: 172.16.238.10

    Once parsed it will look something like:

    ::

        {
            "app_net": {
                "ipv4_address": "172.16.238.10",
            }
        },

    We generate the following command:

    ::

        docker network connect --ip 172.16.238.10 app_net example_app

    Args:
        service_name (str): The name of the container to attach the network to.
        network_name (str): The name of the network (from config).
        network_config (dict): The network option in the service (see example above).

    Attributes:
        service_name (str): The name of the container to attach the network to.

    """

    def __init__(self, service_name: str, network_name: str, network_config: dict):
        self.service_name = service_name
        args = {
            "aliases": {"type": [list], "name": "--alias"},
            "driver": {"type": [str], "name": "--driver-opt"},
            "ipv4_address": {"type": [str], "name": "--ip"},
            "ipv6_address": {"type": [str], "name": "--ip6"},
        }
        super().__init__(args=args, config_name=network_name, config_options=network_config)

    def get_command(self) -> list:
        """Converts the docker compose syntax to normal docker commands. For each network defined in the services
        we generate one `docker network connect` command.

        Returns:
            list: A list of `docker network connect` commands to connect a network to the container.

        """
        args = self._get_args()
        network_command = f"docker network connect {args} {self.config_name} {self.service_name}"
        return network_command
