"""Tests for main module."""

from io import StringIO
from unittest.mock import patch

from my_position.main import main


def test_main_no_args_shows_help() -> None:
    """Test main function with no args shows help."""
    with patch("sys.stdout", new=StringIO()) as mock_stdout:
        with patch("sys.argv", ["my-position"]):
            main()

        output = mock_stdout.getvalue()
        assert "my-position" in output.lower()
        assert "synthesize" in output.lower() or "extract" in output.lower()
