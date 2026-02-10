"""Main entry point for my-position CLI."""

from my_position.cli import CLI


def main() -> None:
    """Run the CLI."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
