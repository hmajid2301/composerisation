# -*- coding: utf-8 -*-
"""This module creates the all the commands related to the volumes for docker-compose.

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""

from ..parser import Parser


class VolumeParser(Parser):
    """This class converts service in docker-compose volumes into ``docker volume`` commands.
    For example given the below yaml definition (docker-compose.yml).

    ::

    example:
        driver: foobar
        driver_opts:
            type: nfs
            o: addr=10.40.0.199,nolock,soft,rw
            device: ":/docker/example"
        labels:
            - com.example.description=Database volume
            - com.example.department=IT/Ops
            - com.example.label-with-empty-value
        name: my-app-data


    Once parsed it will look something like:

    ::

        {
            "example": {
                "driver": "foobar",
                "driver_opts": {
                    "type": "nfs",
                    "o": "addr=10.40.0.199,nolock,soft,rw",
                    "device": ":/docker/example",
                },
                "labels": [
                    "com.example.description=Database volume",
                    "com.example.department=IT/Ops",
                    "com.example.label-with-empty-value",
                ],
                "name": "my-app-data",
            }
        },

    We generate the following command:

    ::

        docker volume create --driver foobar --opt type=nfs --opt 'o=addr=10.40.0.199,nolock,soft,rw example' \
        --opt 'device=:/docker/example' --label 'com.example.description=Database volume' \
        --label 'com.example.department=IT/Ops' --label 'com.example.label-with-empty-value' \
        --name my-app-data example

    Args:
        volume_config (dict): The volumes config options (see above).

    """

    def __init__(self, volume_name: str, volume_config: dict):
        args = {
            "driver": {"type": [str], "name": "--driver"},
            "driver_opts": {"type": [list, dict], "name": "--opt"},
            "labels": {"type": [list, dict], "name": "--label"},
            "name": {"type": [str], "name": "--name"},
        }
        super().__init__(args=args, config_name=volume_name, config_options=volume_config)

    def get_start_command(self) -> list:
        """Converts the docker compose syntax to normal docker commands. The command will create volumes that can be
        attached to container. If the volume has been created externally we don't need the comamnd
        hence we skip it.

        Returns:
            str: The volume create Docker command.

        """
        args = ""
        if self.config_options and "external" not in self.config_options:
            args = self._get_args()

        volume_command = f"docker volume create {args} {self.config_name}"
        return volume_command
