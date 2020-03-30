.. image:: https://gitlab.com/hmajid2301/composerisation/badges/master/pipeline.svg
   :target: https://gitlab.com/hmajid2301/composerisation
   :alt: Pipeline Status

.. image:: https://gitlab.com/hmajid2301/composerisation/badges/master/coverage.svg
   :target: https://gitlab.com/hmajid2301/composerisation
   :alt: Coverage

.. image:: https://img.shields.io/pypi/l/composerisation.svg
   :target: https://pypi.org/project/composerisation/
   :alt: PyPI Project License

.. image:: https://img.shields.io/pypi/v/composerisation.svg
   :target: https://pypi.org/project/composerisation/
   :alt: PyPI Project Version


composerisation
===============

A CLI tool used to convert between docker-compose to normal Docker CLI commands.

Usage
-----

.. code-block:: bash

  pip install composerisation
  composerisation --help

Usage: composerisation [OPTIONS]

  Converts docker-compose files to Docker comamnds.

Options:
  -i, --input-file TEXT           Path to file to convert from docker-compose
                                  to Docker.  [required]

  -l, --log-level [DEBUG|INFO|ERROR|CRITICAL]
                                  Log level for the script.
  --help                          Show this message and exit

.. code-block:: bash

  $ composerisation -i docker-compose.yml

Docker
------

You can also use the docker image to convert between docker-compose and Docker cli.

.. code-block :: bash

  docker run -v ${PWD}/docker-compose.yml:/app/docker-compose.yml composerisation

Supported Command
=================

We support all commands specified in the docker-compose reference file version 3.7
`here <https://docs.docker.com/compose/compose-file/#reference-and-guidelines>_`.
Besides from the config options defined below.

Services
--------

Unsupported config options:

- configs
- credential_spec
- depends_on
- deploy
- external_links
- healthcheck
- secrets
- volume (long syntax)

Networks
--------

Unsupported config options:

- enable_ipv6

Future Features
===============

- Convert between Docker cli commands to docker-compose
- Add ``docker pull``, when using images

Changelog
=========

You can find the `changelog here <https://gitlab.com/hmajid2301/composerisation/blob/master/CHANGELOG.md>`_.

credit: https://www.kissclipart.com/docker-compose-clipart-docker-software-deployment-hy6g1u/

Appendix
========

- docker-compose example taken from `here <https://github.com/DataDog/docker-compose-example>_`
- Editable code area from `wales <https://jsfiddle.net/wales/2azkLnad/>_`
