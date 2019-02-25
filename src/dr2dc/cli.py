import click


@click.command()
@click.option('-o', '--output', required=True, help="Path where to store output file.")
def cli(output):
    pass