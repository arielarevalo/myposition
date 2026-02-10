"""End-to-end tests using subprocess."""

import subprocess
from pathlib import Path


class TestE2E:
    """End-to-end tests."""

    def test_extract_end_to_end(self, tmp_path: Path) -> None:
        """Test full extract command via direct venv python invocation."""
        # Create test structure
        (tmp_path / "conversations").mkdir()
        (tmp_path / "notes").mkdir()
        (tmp_path / "documents").mkdir()

        (tmp_path / "conversations" / "chat.md").write_text("User: Hello")
        (tmp_path / "notes" / "idea.md").write_text("Quick note")
        (tmp_path / "documents" / "essay.md").write_text("# Essay\n" + "x" * 3000)

        # Run command via venv python to avoid uv cache permission issues
        result = subprocess.run(
            [".venv/bin/python3", "-m", "my_position.main", "extract", str(tmp_path)],
            capture_output=True,
            text=True,
            check=False,
            cwd="/Users/ariel/workspace/my-position",
        )

        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "conversations:" in result.stdout
        assert "notes:" in result.stdout
        assert "documents:" in result.stdout
        assert "1 files" in result.stdout or "1  files" in result.stdout
