import pytest

from composerisation.docker_compose.services.services import ServicesParser


@pytest.mark.parametrize(
    "service_data, expected_command",
    [
        ({}, []),
        (
            {
                "web_server": {
                    "container_name": "nginx",
                    "build": {"context": ".", "dockerfile": "docker/nginx/Dockerfile"},
                    "ports": ["80:80"],
                    "depends_on": ["app"],
                },
                "app": {
                    "container_name": "flask",
                    "restart": "always",
                    "build": {"context": ".", "dockerfile": "docker/flask/Dockerfile"},
                    "env_file": "docker/database.conf",
                    "expose": [8080],
                    "depends_on": ["database"],
                },
                "database": {
                    "container_name": "postgres",
                    "image": "postgres:latest",
                    "env_file": "docker/database.conf",
                    "ports": ["5432:5432"],
                    "volumes": ["db_volume:/var/lib/postgresql"],
                },
            },
            [
                "docker build --file docker/nginx/Dockerfile --tag composerisation_web_server .",
                "docker run --name nginx --publish '80:80' --detach composerisation_web_server",
                "docker build --file docker/flask/Dockerfile --tag composerisation_app .",
                "docker run --name flask --restart always --env-file docker/database.conf --expose '8080'"
                " --detach composerisation_app",
                "docker run --name postgres --env-file docker/database.conf --publish '5432:5432'"
                " --volume 'db_volume:/var/lib/postgresql' --detach postgres:latest",
            ],
        ),
        (
            {
                "database": {
                    "container_name": "postgres",
                    "image": "postgres:latest",
                    "env_file": "docker/database.conf",
                    "ports": ["5432:5432"],
                    "volumes": ["db_volume:/var/lib/postgresql"],
                    "init": True,
                }
            },
            [
                "docker run --name postgres --env-file docker/database.conf --publish '5432:5432'"
                " --volume 'db_volume:/var/lib/postgresql' --init --detach postgres:latest"
            ],
        ),
        (
            {
                "service1": {
                    "cap_add": ["ALL"],
                    "cap_drop": ["NET_ADMIN", "SYS_ADMIN"],
                    "cgroup_parent": "m-executor-abcd",
                    "image": "postgres:latest",
                }
            },
            [
                "docker run --cap-add 'ALL' --cap-drop 'NET_ADMIN' --cap-drop 'SYS_ADMIN' --cgroup-parent "
                "m-executor-abcd --name composerisation_service1 --detach postgres:latest"
            ],
        ),
        (
            {
                "service2": {
                    "device": ["/dev/ttyUSB0:/dev/ttyUSB0"],
                    "dns": ["127.0.0.1"],
                    "image": "postgres:latest",
                    "dns_search": "example.com",
                }
            },
            [
                "docker run --device '/dev/ttyUSB0:/dev/ttyUSB0' --dns '127.0.0.1' --dns-search example.com"
                " --name composerisation_service2 --detach postgres:latest"
            ],
        ),
        (
            {
                "service2": {
                    "device": ["/dev/ttyUSB0:/dev/ttyUSB0"],
                    "dns": "127.0.0.1",
                    "image": "postgres:latest",
                    "dns_search": ["example.com"],
                }
            },
            [
                "docker run --device '/dev/ttyUSB0:/dev/ttyUSB0' --dns 127.0.0.1 --dns-search 'example.com'"
                " --name composerisation_service2 --detach postgres:latest"
            ],
        ),
        (
            {
                "service2": {
                    "env_file": "data/data.conf",
                    "entrypoint": ["php", "-d", "memory_limit=-1", "vendor/bin/phpunit"],
                    "image": "postgres:latest",
                }
            },
            [
                "docker run --env-file data/data.conf --entrypoint php -d memory_limit=-1 vendor/bin/phpunit"
                " --name composerisation_service2 --detach postgres:latest"
            ],
        ),
        (
            {
                "service2": {
                    "env_file": ["data/data.conf", "other_data.conf"],
                    "environment": ["RACK_ENV=development"],
                    "image": "postgres:latest",
                }
            },
            [
                "docker run --env-file 'data/data.conf' --env-file 'other_data.conf' --environment"
                " 'RACK_ENV=development' --name composerisation_service2 --detach postgres:latest"
            ],
        ),
        (
            {
                "service2": {
                    "extra_hosts": ["somehost:162.242.195.82", "otherhost:50.31.209.229"],
                    "init": True,
                    "isolation": "process",
                    "image": "postgres:latest",
                }
            },
            [
                "docker run --add-host 'somehost:162.242.195.82' --add-host 'otherhost:50.31.209.229' --init"
                " --isolation process --name composerisation_service2 --detach postgres:latest"
            ],
        ),
        (
            {
                "example": {
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
            },
            [
                "docker run --label 'com.example.description=Accounting webapp' --label 'com.example.department=Finance'"
                " --label 'com.example.label-with-empty-value' --link 'db' --link 'db:database' --link 'redis'"
                " --network bridge --pid host --name composerisation_example --detach mysql:latest"
            ],
        ),
        (
            {
                "example": {
                    "labels": [
                        {"com.example.description": "Accounting webapp"},
                        {"com.example.department": "Finance"},
                        {"com.example.label-with-empty-value": ""},
                    ],
                    "links": ["db", "db:database", "redis"],
                    "network_mode": "bridge",
                    "pid": "host",
                    "image": "mysql:latest",
                }
            },
            [
                "docker run --label 'com.example.description=Accounting webapp' --label 'com.example.department=Finance'"
                " --label 'com.example.label-with-empty-value=' --link 'db' --link 'db:database' --link 'redis'"
                " --network bridge --pid host --name composerisation_example --detach mysql:latest"
            ],
        ),
        (
            {
                "example2": {
                    "security_opt": ["label:user:USER", "label:role:ROLE"],
                    "stop_grace_period": "1s",
                    "stop_signal": "SIGUSR1",
                    "sysctls": {"net.core.somaxconn": 1024, "net.ipv4.tcp_syncookies": 0},
                    "image": "mysql:latest",
                }
            },
            [
                "docker run --security-opt 'label:user:USER' --security-opt 'label:role:ROLE' --stop-timeout 1s"
                " --stop-signal SIGUSR1 --sysctl 'net.core.somaxconn=1024' --sysctl 'net.ipv4.tcp_syncookies=0'"
                " --name composerisation_example2 --detach mysql:latest"
            ],
        ),
        (
            {
                "example2": {
                    "tmpfs": ["/run", "/tmp"],
                    "ulimits": {"nproc": 65535, "nofile": {"soft": 20000, "hard": 40000}},
                    "userns_mode": "host",
                    "image": "mysql:latest",
                }
            },
            [
                "docker run --tmpfs '/run' --tmpfs '/tmp' --ulimit nproc=65535 --ulimit nofile=20000:40000"
                " --userns host --name composerisation_example2 --detach mysql:latest"
            ],
        ),
        (
            {
                "example2": {
                    "logging": {"driver": "json-file", "options": {"max-size": "1k", "max-file": "3"}},
                    "image": "mysql:latest",
                }
            },
            [
                "docker run --log-driver json-file --log-opt max-size=1k --log-opt max-file=3"
                " --name composerisation_example2 --detach mysql:latest"
            ],
        ),
        (
            {"example2": {"image": "mysql:latest", "command": ["/bin/bash", "tail", "-f", "log.log"]}},
            ["docker run  --name composerisation_example2 --detach mysql:latest '/bin/bash tail -f log.log'"],
        ),
        (
            {
                "example2": {
                    "networks": {
                        "some-network": {
                            "driver": "default",
                            "aliases": ["alias1", "alias2"],
                            "ipv4_address": "172.16.238.10",
                            "ipv6_address": "2001:3984:3989::10",
                        },
                        "other-network": {"aliases": ["alias"]},
                    },
                    "image": "mysql:latest",
                }
            },
            [
                "docker run  --name composerisation_example2 --detach mysql:latest",
                "docker network connect --driver-opt default --alias 'alias1' --alias 'alias2'"
                " --ip 172.16.238.10 --ip6 2001:3984:3989::10 some-network composerisation_example2",
                "docker network connect --alias 'alias' other-network composerisation_example2",
            ],
        ),
    ],
)
def test_get_add_service_command(service_data, expected_command):
    commands = []
    for name, option in service_data.items():
        service = ServicesParser(service_name=name, service_options=option)
        command = service.get_start_command()
        commands += command
    assert commands == expected_command


@pytest.mark.parametrize(
    "service_data, expected_command",
    [
        ({}, []),
        (
            {
                "web_server": {
                    "container_name": "nginx",
                    "build": {"context": ".", "dockerfile": "docker/nginx/Dockerfile"},
                    "ports": ["80:80"],
                    "depends_on": ["app"],
                },
                "app": {
                    "container_name": "flask",
                    "restart": "always",
                    "build": {"context": ".", "dockerfile": "docker/flask/Dockerfile"},
                    "env_file": "docker/database.conf",
                    "expose": [8080],
                    "depends_on": ["database"],
                },
                "database": {
                    "container_name": "postgres",
                    "image": "postgres:latest",
                    "env_file": "docker/database.conf",
                    "ports": ["5432:5432"],
                    "volumes": ["db_volume:/var/lib/postgresql"],
                },
            },
            [
                "docker stop nginx",
                "docker rm nginx",
                "docker stop flask",
                "docker rm flask",
                "docker stop postgres",
                "docker rm postgres",
            ],
        ),
        (
            {
                "service1": {
                    "cap_add": ["ALL"],
                    "cap_drop": ["NET_ADMIN", "SYS_ADMIN"],
                    "cgroup_parent": "m-executor-abcd",
                    "image": "postgres:latest",
                }
            },
            ["docker stop composerisation_service1", "docker rm composerisation_service1"],
        ),
        (
            {
                "service2": {
                    "device": ["/dev/ttyUSB0:/dev/ttyUSB0"],
                    "dns": ["127.0.0.1"],
                    "image": "postgres:latest",
                    "dns_search": "example.com",
                }
            },
            ["docker stop composerisation_service2", "docker rm composerisation_service2"],
        ),
    ],
)
def test_get_service_delete_command(service_data, expected_command):
    commands = []
    for name, option in service_data.items():
        service = ServicesParser(service_name=name, service_options=option)
        command = service.get_delete_command()
        commands += command
    assert commands == expected_command
