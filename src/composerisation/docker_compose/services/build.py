# -*- coding: utf-8 -*-
"""This module creates the build commands from the build option within services.

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""

from ..parser import Parser


class ServiceBuildParser(Parser):
    """This class converts build in docker-compose services into `docker build` commands.
    For example given the below yaml definition (docker-compose.yml).

    ::

        services:
            webapp:
                build:
                    context: ./dir
                    dockerfile: Dockerfile-alternate
                    args:
                        buildno: 1

    Once parsed it will look something like:

    ::

        {
            "context": "./dir",
            "dockerfile": "Dockerfile-alternate",
            "args": {"buildno": 1},
        },

    We generate the following command:

    ::

        docker build --f Dockerfile-alternate --build-arg buildno=1 --tag build2 ./dir"

    Args:
        service_name (str): The name (tag) of the image when created.
        build_config (dict): The build option in the service (see example above).

    """

    def __init__(self, service_name: str, build_config: dict):
        args = {
            "args": {"type": [list, dict], "name": "--build-arg"},
            "dockerfile": {"type": [str], "name": "--file"},
            "cache_from": {"type": [list, dict], "name": "--cache-from"},
            "labels": {"type": [list, dict], "name": "--label"},
            "shm_size": {"type": [str], "name": "--shm-size"},
            "target": {"type": [str], "name": "--target"},
        }
        ignore_args = ["context"]
        super().__init__(args=args, config_name=service_name, config_options=build_config, ignore_args=ignore_args)

    def get_command(self) -> str:
        """Converts the docker compose syntax to normal docker commands. The command will build a docker image.

        Returns:
            str: The docker build command, to build the docker image.

        """
        args = self._get_args()
        context = self.config_options.get("context", ".")
        build_command = f"docker build {args} --tag {self.config_name} {context}"
        return build_command
