import pytest

from composerisation.docker_compose.services.build import ServiceBuildParser


@pytest.mark.parametrize(
    "service_name, build_data, expected_command",
    [
        (
            "build2",
            {
                "args": {"buildno": 1, "gitcommithash": "cdc3b19"},
                "cache_from": ["alpine:latest", "corp/web_app:3.14"],
                "shm_size": "2gb",
            },
            (
                "docker build --build-arg 'buildno=1' --build-arg 'gitcommithash=cdc3b19' --cache-from 'alpine:latest'"
                " --cache-from 'corp/web_app:3.14' --shm-size 2gb --tag build2 ."
            ),
        ),
        (
            "build1",
            {
                "context": "./dir",
                "dockerfile": "Dockerfile-alternate",
                "args": {"buildno": 1},
                "shm_size": 10000000,
                "labels": [
                    "com.example.description=Accounting webapp",
                    "com.example.department=Finance",
                    "com.example.label-with-empty-value",
                ],
                "target": "prod",
            },
            (
                "docker build --file Dockerfile-alternate --build-arg 'buildno=1' --shm-size 10000000"
                " --label 'com.example.description=Accounting webapp' --label 'com.example.department=Finance'"
                " --label 'com.example.label-with-empty-value' --target prod --tag build1 ./dir"
            ),
        ),
        (
            "build",
            {
                "cache_from": ["alpine:latest", "corp/web_app:3.14"],
                "args": {"buildno": 1, "gitcommithash": "cdc3b19"},
                "labels": {
                    "com.example.description": "Accounting webapp",
                    "com.example.department": "Finance",
                    "com.example.label-with-empty-value": "",
                },
            },
            (
                "docker build --cache-from 'alpine:latest' --cache-from 'corp/web_app:3.14' --build-arg 'buildno=1' --build-arg 'gitcommithash=cdc3b19'"
                " --label 'com.example.description=Accounting webapp' --label 'com.example.department=Finance'"
                " --label 'com.example.label-with-empty-value=' --tag build ."
            ),
        ),
    ],
)
def test_get_build_command(service_name, build_data, expected_command):
    build = ServiceBuildParser(service_name=service_name, build_config=build_data)
    command = build.get_command()
    assert command == expected_command
