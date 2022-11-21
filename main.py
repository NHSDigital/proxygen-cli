import click

from proxygen_cli.dot_proxygen import directory
from proxygen_cli import auth


@click.group()
def main():
    directory()
    token = auth.access_token()
    print(token)
    pass


@main.command()
def configure():
    print("configure")
    pass

if __name__ == "__main__":
    main()
