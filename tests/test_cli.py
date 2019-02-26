import pytest

from composerisation.cli import cli


@pytest.mark.parametrize(
    "args, expected_output",
    [
        (["-i", "tests/data/1.yml"], open("tests/data/1.txt").read()),
        (["-i", "tests/data/2.yml"], open("tests/data/2.txt").read()),
    ],
)
def test_success(runner, args, expected_output):
    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert result.stdout == expected_output


@pytest.mark.parametrize(
    "args, expected_output",
    [
        (["-i", "tests/data/invalid_option.yml"], "Invalid key context in web_server\n"),
        (["-i", "tests/data/invalid_yaml.yml"], "Invalid yaml file, tests/data/invalid_yaml.yml.\n",),
    ],
)
def test_fail(runner, args, expected_output):
    result = runner.invoke(cli, args)
    assert result.exit_code == 1
    assert result.stdout == expected_output
