# -*- coding: utf-8 -*-
"""Parent class of all of the parsers used to convert docker-compose syntax to docker commands.

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""
import os
from collections import ChainMap
from typing import Union

from ..utils import exceptions


class Parser:
    """This is the parent class of all the parsers used to parse the docker compose file. It contains common
    functions used by all of it's children class. The main on bein able to convert docker compose options and config
    into valid args.

    If we have an arguments like:

    ::

        "container_name": {"type": [str], "name": "--name"}

    Then when we receive container_name within a service it will convert that to `--name <container_name>`.

    Args:
        args (dict): Valid arguments this parser will except. It will include the type they are expected to be in i.e. a list and the name of the argument.
        config_name (str): The name of the config i.e. could be a network name or volume name.
        config_options (dict): The network option in the service (see example above).
        special_args (:obj:`dict`, optional): Defaults to empty dict. Some arguments need specific logic so we have \
            functions to create the arguments for them here.
        ignore_args (:obj:`list`, optional): Defaults to empty list. List of args to ignore, either we do not support \
            them or they are handled else where.

    Attributes:
        args (dict): Valid arguments this parser will except. It will include the type they are expected to be in i.e. a list and the name of the argument.
        config_name (str): The name of the config i.e. could be a network name or volume name.
        config_options (dict): The network option in the service (see example above).
        special_args (dict): Some arguments need specific logic so we have functions to create the arguments for \
            them here.
        ignore_args (:obj:`list` of :obj:`str`): List or args to ignore, either we do not support them or they are \
            handled else where.

    """

    def __init__(self, args: dict, config_name: str, config_options: dict, special_args=None, ignore_args=None):
        if special_args is None:
            special_args = {}

        if ignore_args is None:
            ignore_args = []

        self.args = args
        self.config_name = config_name
        self.config_options = config_options
        self.special_args = special_args
        self.ignore_args = ignore_args

    def _get_args(self) -> str:
        """Converts the list of docker compose options into a list of arguments for the various docker commands,
        such as docker run --name container1.

        Where the config options may like something like:

        ::

        {
            "labels": [
                "com.example.description=Accounting webapp",
                "com.example.department=Finance",
                "com.example.label-with-empty-value",
            ],
            "links": ["db", "db:database", "redis"],
            "network_mode": "bridge",
            "pid": "host",
            "image": "mysql:latest",
        }

        Would become;

        ::

            --label com.example.description=Accounting webapp --label com.example.department=Finance \
            --label com.example.label-with-empty-value --link db --link db:database --link redis \
            --network bridge --pid host


        Example kwargs

        ::

            {"ulimits": self._parse_ulimits, "logging": self._parse_logging}

        Logic goes as follows:

            * If the `config_key` i.e. `ulimits` is our special args list (kwargs), then we will use that specific \
                function we passed into kwargs to convert it.
            * If the key is in the ignore list skip it i.e. it is `command` we handle that logic in `ServiceParser` \
                as it needs specific ordering.
            * Else convert the current item into arguments (string).

        Args:
            kwargs: Any "extra" functions where the argument conversion logic isn't straight forward, so we need to define \
                extra specific functionality to convert it to arguments.

        Returns:
            str: The equivalent cli arguments for docker commands to the docker cli syntax.

        """
        args = ""

        for config_key, config_option in self.config_options.items():
            if config_key in self.special_args:
                get_args_func = self.special_args[config_key]
                args += get_args_func(config_option)
            elif config_key in self.ignore_args:
                continue
            else:
                args += self._get_normal_args(config_key, config_option)

        return args.strip()

    def _get_normal_args(self, config_name: str, config_value: Union[list, dict, str, bool]) -> str:
        """This gets the args back for a "normal" type where the logic is predefined and striaght forward. The
        config_value can be of many types.

        * List and dicts are treated the same; we may need multiple cli arguments for them
        * Booleans mean we just have to specify the argument i.e like a flag
        * Finally lists that should be strings need to be converted to strings

        Args:
            config_name (str): The name of the current config i.e. ``labels``.
            config_value (any): The value of the config.

        Returns:
            str: The argument as a string i.e. ``--label xxx``.

        Raises:
            IncorrectConfigException: When an incorrect key is in the wrong section of the docker-compose file.

        """
        try:
            arg = self.args[config_name]
        except KeyError as e:
            incorrect_key = e.args[0]
            raise exceptions.IncorrectConfigException(config_name=self.config_name, incorrect_key=incorrect_key)
        arg_type, name = arg["type"], arg["name"]

        arg_is_dict_or_list = set(arg_type).intersection([list, dict])
        arg_is_str = isinstance(config_value, str)

        if arg_is_dict_or_list and not arg_is_str:
            args = self._convert_list_to_args(config_value, name)
        elif bool in arg_type:
            args = f"{name} "
        else:
            if isinstance(config_value, list) and str in arg_type:
                config_value = " ".join(config_value)
            args = f"{name} {config_value} "

        return args

    def _convert_list_to_args(self, config_val: Union[list, dict], name: str) -> str:
        """Lists will become multiple arguments i.e. you can have multiple `--label` or `--extra-hosts` defined.
        So for every item in the list we just add an extra argument i.e. each label in the list adds another
        ``--label``. If the config option is a dict we will need to convert that into a list first.

        :: Example ``config_val``

            [
                "com.example.description=Accounting webapp",
                "com.example.department=Finance",
                "com.example.label-with-empty-value",
            ]

        Every kind off "iterable" list we have wether is is a dict or list of dicts needs to be converted
        in to list of strs as shown above.

        Args:
            config_val(list or dict): The config value we are converting into arguments.
            name (str): The name of the argument i.e. ``--label``.

        Returns:
            str: The list as an argument string i.e. ``--label lab1 --label lab2``.

        """
        args = ""
        if isinstance(config_val, dict):
            config_val = self._convert_dict_to_list(config_val)
        elif isinstance(config_val, list) and isinstance(config_val[0], dict):
            config_val = self._convert_list_dict_to_list(config_val)

        for item in config_val:
            args += f'{name} "{item}" '

        return args

    def _convert_dict_to_list(self, configs: dict) -> list:
        """This function will convert any dict args into list args. Sometimes in yaml files you can define
        options in multiple ways. Both are valid above, however to make our lives easier we will convert
        the top one, which is a dict into the bottom one which is a list.

        ::

        build:
            context: .
            labels:
                com.example.description: "Accounting webapp"
                com.example.department: "Finance"
                com.example.label-with-empty-value: ""

        ::

        build:
            context: .
            labels:
                - "com.example.description=Accounting webapp"
                - "com.example.department=Finance"
                - "com.example.label-with-empty-value"

        So we want to convert this:

        ::

            "config": {
                "subnet": "172.28.0.0/16"
            }

        Into this:

        ::

            "config": [
                "subnet=172.28.0.0/16"
            ]

        As when these become cli arguments we will need them in the form ``--label com.example.description=Accounting webapp``.

        Args:
            configs (dict): The configs to convert from a dict into a list.

        Returns:
            list: The config data as a list.

        """
        new_config = []
        for key, value in configs.items():
            new_config.append(f"{key}={value}")
        return new_config

    def _convert_list_dict_to_list(self, configs: dict) -> list:
        """Yaml files can define as a list of dicts however we need all lists to be strs so they can be parsed
        as args.

        For example if the config option is defined as:

        ::

            ipam:
                config:
                    - subnet: 172.28.0.0/16

        We want it to be defined as:

        ::

            ipam:
                config:
                    - subnet=172.28.0.0/1

        So we can in a config option like:

        ::

            'config': [{'subnet': '172.28.0.0/16'}]

        Into this:

        ::

            'config': ['subnet=172.28.0.0/16']

        Args:
            configs (:obj:`list` of obj:`dict`): The configs to convert from a list of dicts into a list of strs.

        Returns:
            list: The config data as a list.

        """
        new_config = []
        for item in configs:
            for key, value in item.items():
                new_config.append(f"{key}={value}")
        return new_config

    def _get_config_val(self, config: dict, config_key: str):
        """Gets the config value of a config option and if that option is a list of dicts convert into a dict.
        Sometimes options can be passed as a dict or a list of dicts. We need to make sure the config value
        returned is a dict and not a list of dicts.

        For example both of the following examples are valid.

        ::

            ipam:
                config:
                    - subnet: 172.28.0.0/16

        ::

            ipam:
                config:
                    subnet: 172.28.0.0/16

        Args:
            configs (dict): The config options such ``ipam``, where we want to get the config from.
            config_key (str): The config name we are getting from.

        Returns:
            dict: The config value .

        """
        config_val = config.get(config_key, {})
        if isinstance(config_val, list) and isinstance(config_val[0], dict):
            config_val = dict(ChainMap(*config_val))
        return config_val

    def _get_image_name(self) -> str:
        """Gets the Docker image name, if no ``image`` config option is set then we assign it a defult name. Which is
        ``<folder_name>_<service_name>``.

        Returns:
            str: The Docker image name.

        """
        dirname = os.path.basename(os.getcwd())
        default_image_name = f"{dirname}_{self.config_name}"
        image_name = self.config_options.get("image", default_image_name)
        return image_name

    def _get_container_name(self) -> str:
        """Gets the Docker container name, if no ``container`` name is set, use the default contaienr name.
        Which is ``<folder_name>_<service_name>``.

        Returns:
            str: The Docker image name.

        """
        dirname = os.path.basename(os.getcwd())
        default_container_name = f"{dirname}_{self.config_name}"
        container_name = self.config_options.get("container_name", default_container_name)
        return container_name
