from click.testing import CliRunner
from flask import Flask, jsonify, request, render_template
from composerisation.cli import cli

app = Flask(__name__, static_url_path="", static_folder="static", template_folder="static")

bash = open("static/content/bash.txt").read()
usage = open("static/content/usage.txt").read()
yaml = open("static/content/yaml.txt").read()


@app.route("/")
def main():
    print(request.script_root)
    return render_template("index.html", usage=usage, yaml=yaml, bash=bash)


@app.route("/docker/compose", methods=["POST"])
def docker_compose_to_docker_cli():
    data = request.get_json()
    docker_compose_data = data["docker_compose"]
    runner = CliRunner()
    result = runner.invoke(cli, args=["-l", "DEBUG"], input=docker_compose_data)
    response = {"docker_cli": result.stdout}
    return jsonify(response)


if __name__ == "__main__":
    app.run()
