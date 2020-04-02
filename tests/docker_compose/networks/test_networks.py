import pytest

from composerisation.docker_compose.networks.networks import NetworkParser


@pytest.mark.parametrize(
    "networks_data, expected_command",
    [
        (
            {"example": {"driver": "foobar", "driver_opts": {"foo": "bar", "baz": 1}, "name": "my-network"}},
            ['docker network create --driver foobar --opt "foo=bar" --opt "baz=1" --name my-network example'],
        ),
        (
            {
                "network1": {"internal": True},
                "network2": {
                    "labels": [
                        "com.example.description=Financial transaction network",
                        "com.example.department=Finance",
                        "com.example.label-with-empty-value",
                    ]
                },
            },
            [
                "docker network create --internal network1",
                'docker network create --label "com.example.description=Financial transaction network"'
                ' --label "com.example.department=Finance" --label "com.example.label-with-empty-value" network2',
            ],
        ),
        (
            {"network2": {"ipam": {"driver": "default", "config": {"subnet": "172.28.0.0/16"}}}},
            ["docker network create --ipam-driver default --ipam-opt subnet=172.28.0.0/16 network2"],
        ),
        (
            {"network2": {"ipam": {"driver": "default", "config": [{"subnet": "172.28.0.0/16"}]}}},
            ["docker network create --ipam-driver default --ipam-opt subnet=172.28.0.0/16 network2"],
        ),
    ],
)
def test_get_start_networks_command(networks_data, expected_command):
    commands = []
    for name, config in networks_data.items():
        networks = NetworkParser(network_name=name, network_config=config)
        command = networks.get_start_command()
        commands.append(command)
    assert commands == expected_command


@pytest.mark.parametrize(
    "networks_data, expected_command",
    [
        (
            {
                "network1": {"internal": True},
                "network2": {
                    "labels": [
                        "com.example.description=Financial transaction network",
                        "com.example.department=Finance",
                        "com.example.label-with-empty-value",
                    ]
                },
            },
            ["docker network rm network1", "docker network rm network2",],
        ),
        (
            {"network2": {"ipam": {"driver": "default", "config": {"subnet": "172.28.0.0/16"}}}},
            ["docker network rm network2"],
        ),
    ],
)
def test_get_delete_network_commands(networks_data, expected_command):
    commands = []
    for name, config in networks_data.items():
        networks = NetworkParser(network_name=name, network_config=config)
        command = networks.get_delete_command()
        commands.append(command)
    assert commands == expected_command
