import pytest

from composerisation.docker_compose.services.networks import ServiceNetworkParser


@pytest.mark.parametrize(
    "service_name, networks_data, expected_command",
    [
        (
            "container1",
            {
                "some-network": {
                    "driver": "default",
                    "aliases": ["alias1", "alias2"],
                    "ipv4_address": "172.16.238.10",
                    "ipv6_address": "2001:3984:3989::10",
                },
                "other-network": {"aliases": ["alias"]},
            },
            [
                'docker network connect --driver-opt default --alias "alias1" --alias "alias2"'
                " --ip 172.16.238.10 --ip6 2001:3984:3989::10 some-network container1",
                'docker network connect --alias "alias" other-network container1',
            ],
        ),
        (
            "container1",
            {"some-network": {"driver": "default", "aliases": ["alias1", "alias2"], "ipv4_address": "172.16.238.10"}},
            [
                'docker network connect --driver-opt default --alias "alias1" --alias "alias2"'
                " --ip 172.16.238.10 some-network container1"
            ],
        ),
    ],
)
def test_get_network_command(service_name, networks_data, expected_command):
    commands = []
    for name, config in networks_data.items():
        network = ServiceNetworkParser(service_name=service_name, network_name=name, network_config=config)
        command = network.get_command()
        commands.append(command)
    assert commands == expected_command
