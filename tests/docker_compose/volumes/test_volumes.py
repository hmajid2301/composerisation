import pytest

from composerisation.docker_compose.volumes.volumes import VolumeParser


@pytest.mark.parametrize(
    "volumes_data, expected_command",
    [
        (
            {
                "example": {
                    "driver": "foobar",
                    "driver_opts": {
                        "type": "nfs",
                        "o": "addr=10.40.0.199,nolock,soft,rw example",
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
            [
                "docker volume create --driver foobar --opt 'type=nfs' --opt 'o=addr=10.40.0.199,nolock,soft,rw example'"
                " --opt 'device=:/docker/example' --label 'com.example.description=Database volume'"
                " --label 'com.example.department=IT/Ops' --label 'com.example.label-with-empty-value'"
                " --name my-app-data example"
            ],
        ),
    ],
)
def test_get_volumes_command(volumes_data, expected_command):
    commands = []
    for name, config in volumes_data.items():
        volume = VolumeParser(volume_name=name, volume_config=config)
        command = volume.get_start_command()
        commands.append(command)
    assert commands == expected_command
