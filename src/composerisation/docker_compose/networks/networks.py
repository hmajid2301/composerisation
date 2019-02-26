# -*- coding: utf-8 -*-
"""This module creates the all the commands related to the network for docker-compose.

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""

from ..parser import Parser


class NetworkParser(Parser):
    """This class converts service in docker-compose volumes into ``docker network`` commands.
    For example given the below yaml definition (docker-compose.yml).

    ::

        example:
            driver: foobar
            driver_opts:
                foo: bar
                baz: 1
            name: my-network

    Once parsed it will look something like:

    ::

        {"example": {"driver": "foobar", "driver_opts": {"foo": "bar", "baz": 1}, "name": "my-network",}},


    We generate the following command:

    ::

    docker network create --driver foobar --opt 'foo=bar' --opt 'baz=1' --name my-network example

    Following config options are ignored:

    - enable_ipv6

    Args:
        network_name (str): The name of the network (from config).
        network_config (dict): The network option in the service (see example above).

    """

    def __init__(self, network_name: str, network_config: dict):
        self.network_name = network_name
        args = {
            "driver": {"type": [str], "name": "--driver"},
            "driver_opts": {"type": [list, dict], "name": "--opt"},
            "attachable": {"type": [bool], "name": "--attachable"},
            "internal": {"type": [bool], "name": "--internal"},
            "external": {"type": [bool], "name": "--external"},
            "labels": {"type": [list, dict], "name": "--label"},
            "name": {"type": [str], "name": "--name"},
        }
        special_args = {
            "ipam": self._parse_ipam,
        }
        ignore_args = ["enable_ipv6"]

        super().__init__(
            args=args,
            config_name=network_name,
            config_options=network_config,
            special_args=special_args,
            ignore_args=ignore_args,
        )

    def get_start_command(self) -> str:
        """Converts the docker compose syntax to normal docker commands. The command will create networks that can be
        attached to container.

        Returns:
            list: A list of volume create commands.

        """
        args = self._get_args()
        network_command = f"docker network create {args} {self.network_name}"
        return network_command

    def get_delete_command(self) -> str:
        """This function returns the command required to delete the network.

        Returns:
            str: Docker command to delete the network.

        """
        network_command = f"docker network rm {self.network_name}"
        return network_command

    def _parse_ipam(self, ipam: dict) -> str:
        """For parsing any ``ipam`` options with in docker-compose the logic for this is a bit more complicated as
        compared with normal args. We need to parse the ``ipam` object. This function will get passed to the
        `_get_args()` function as `kwargs`.

        Example ``ipam`` config option below.

        ::

            {
                "ipam": {"driver": "default", "config": {"subnet": "172.28.0.0/16"}}
            }

        Example arguments returned.

        ::

            --ipam-driver default --ipam-opt subnet=172.28.0.0./16

        Args:
            ipam (dict): The ipam config options (see example above).

        Returns:
            str: The equivalent cli arguments for docker commands for ``ipam`` option in docker-compose networks.

        """
        ipam_args = ""
        driver = ipam.get("driver", "")
        if driver:
            ipam_args += f"--ipam-driver {driver} "
        ipam_opts = self._get_config_val(config=ipam, config_key="config")

        for name, value in ipam_opts.items():
            ipam_args += f"--ipam-opt {name}={value} "

        return ipam_args
