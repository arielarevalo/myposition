"""Integration tests for CLI."""

from io import StringIO
from pathlib import Path
from unittest.mock import patch

from my_position.cli import CLI


class TestCLI:
    """Integration tests for CLI."""

    def test_extract_command_help(self) -> None:
        """Test that extract --help prints usage."""
        cli = CLI()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            try:
                cli.run(["extract", "--help"])
            except SystemExit:
                pass  # argparse calls sys.exit after --help

            output = mock_stdout.getvalue()
            assert "extract" in output.lower()
            assert "input_dir" in output.lower()

    def test_extract_reports_summary(self, tmp_path: Path) -> None:
        """Test that extract prints file count summary."""
        # Create simple test structure
        (tmp_path / "conversations").mkdir()
        (tmp_path / "notes").mkdir()

        (tmp_path / "conversations" / "chat.md").write_text("User: Hi")
        (tmp_path / "notes" / "idea.md").write_text("Idea")

        cli = CLI()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            with patch("builtins.input", return_value="n"):  # Skip any prompts
                cli.run(["extract", str(tmp_path)])

            output = mock_stdout.getvalue()
            assert "conversations:" in output
            assert "notes:" in output
            assert "1 files" in output or "1  files" in output  # Account for spacing

    def test_extract_reports_misplaced(self, tmp_path: Path) -> None:
        """Test that misplaced files are reported."""
        (tmp_path / "notes").mkdir()

        # 3 KiB file in notes/ (over limit)
        large = tmp_path / "notes" / "large.md"
        large.write_text("x" * 3000)

        cli = CLI()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            with patch("builtins.input", return_value="n"):  # Skip move prompt
                cli.run(["extract", str(tmp_path)])

            output = mock_stdout.getvalue()
            assert "Misplaced" in output or "misplaced" in output
            assert "large.md" in output

    def test_extract_reports_ignored(self, tmp_path: Path) -> None:
        """Test that ignored files are reported."""
        (tmp_path / "notes").mkdir()

        pdf = tmp_path / "notes" / "doc.pdf"
        pdf.write_bytes(b"fake")

        cli = CLI()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            cli.run(["extract", str(tmp_path)])

            output = mock_stdout.getvalue()
            assert "Ignored" in output or "ignored" in output
            assert "doc.pdf" in output
