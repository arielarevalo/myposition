"""Command-line interface for my-position."""

import argparse
import sys
from pathlib import Path

from my_position.extract import Scanner


class CLI:
    """Command-line interface using argparse."""

    def __init__(self) -> None:
        """Initialize CLI with argument parser."""
        self.parser = argparse.ArgumentParser(
            prog="my-position",
            description="Synthesize positions from conversations, notes, and documents",
        )
        subparsers = self.parser.add_subparsers(
            dest="command", help="Available commands"
        )

        # Extract subcommand
        extract_parser = subparsers.add_parser(
            "extract",
            help="Extract and categorize files from input directory",
        )
        extract_parser.add_argument(
            "input_dir",
            type=Path,
            help="Directory containing conversations/, notes/, and documents/ subdirectories",
        )

    def run(self, args: list[str] | None = None) -> None:
        """Run CLI with given arguments.

        Args:
            args: Command-line arguments. If None, uses sys.argv[1:]
        """
        parsed_args = self.parser.parse_args(args)

        if parsed_args.command == "extract":
            self._handle_extract(parsed_args)
        else:
            # No command specified, show help
            self.parser.print_help()

    def _handle_extract(self, args: argparse.Namespace) -> None:
        """Handle extract subcommand.

        Args:
            args: Parsed command-line arguments
        """
        try:
            scanner = Scanner(args.input_dir)
            result = scanner.scan()

            # Print summary
            print(f"\nScanning {args.input_dir} ...\n")
            print(f"  conversations:  {len(result.conversations):>3} files")
            print(f"  notes:          {len(result.notes):>3} files")
            print(f"  documents:      {len(result.documents):>3} files")

            # Report misplaced files
            if result.misplaced:
                print(f"\n⚠ Misplaced files ({len(result.misplaced)}):\n")
                for misplaced in result.misplaced:
                    # Get file size for display
                    size_kb = misplaced.path.stat().st_size / 1024
                    print(
                        f"  {misplaced.path.relative_to(args.input_dir)} "
                        f"({size_kb:.1f} KiB) → suggested: {misplaced.suggested.value}/"
                    )
                    response = input("  Move? [y/n/a(ll)/s(kip all)]: ").strip().lower()

                    if response in {"a", "all"}:
                        # Move all remaining
                        self._move_all_misplaced(result.misplaced, args.input_dir)
                        break
                    elif response in {"s", "skip"}:
                        # Skip all remaining
                        print("  Skipping all.")
                        break
                    elif response in {"y", "yes"}:
                        # Move this file
                        self._move_file(
                            misplaced.path,
                            args.input_dir / misplaced.suggested.value,
                        )

            # Report duplicates
            if result.duplicates:
                print(f"\n⚠ Duplicates ({len(result.duplicates)}):\n")
                for dup_path in result.duplicates:
                    print(f"  {dup_path.relative_to(args.input_dir)}")

            # Report ignored files
            if result.ignored:
                print(f"\n✗ Ignored ({len(result.ignored)}):\n")
                for ignored_path in result.ignored:
                    print(f"  {ignored_path.relative_to(args.input_dir)}")

            print()  # Final newline

        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def _move_file(self, source: Path, dest_dir: Path) -> None:
        """Move a file to a new directory.

        Args:
            source: Source file path
            dest_dir: Destination directory
        """
        dest_path = dest_dir / source.name
        source.rename(dest_path)
        print(f"  ✓ Moved to {dest_path}")

    def _move_all_misplaced(
        self, misplaced_files: list, input_dir: Path
    ) -> None:
        """Move all misplaced files to their suggested directories.

        Args:
            misplaced_files: List of MisplacedFile objects
            input_dir: Input directory (for dest path construction)
        """
        for misplaced in misplaced_files:
            dest_dir = input_dir / misplaced.suggested.value
            self._move_file(misplaced.path, dest_dir)
