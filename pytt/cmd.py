import click

from pytt import parser


@click.group()
def root():
    pass


@root.command()
@click.argument("infile")
def display(infile: str):
    parser.load(infile)
