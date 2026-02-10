"""Tests for Scanner class."""

from pathlib import Path

import pytest

from my_position.extract import FileCategory, Scanner


class TestScanner:
    """Tests for Scanner class."""

    def test_scan_empty_dir(self, tmp_path: Path) -> None:
        """Test scanning directory with no category subdirs returns empty result."""
        scanner = Scanner(tmp_path)
        result = scanner.scan()

        assert len(result.conversations) == 0
        assert len(result.notes) == 0
        assert len(result.documents) == 0
        assert len(result.misplaced) == 0
        assert len(result.ignored) == 0
        assert len(result.duplicates) == 0

    def test_scan_valid_files(self, tmp_path: Path) -> None:
        """Test that valid files are correctly categorized."""
        # Create subdirs and files
        (tmp_path / "conversations").mkdir()
        (tmp_path / "notes").mkdir()
        (tmp_path / "documents").mkdir()

        conv_file = tmp_path / "conversations" / "chat.md"
        conv_file.write_text("User: Hi\nAssistant: Hello")

        note_file = tmp_path / "notes" / "idea.md"
        note_file.write_text("Quick idea")  # Small file

        doc_file = tmp_path / "documents" / "essay.md"
        doc_file.write_text("# Essay\n" + "content " * 500)  # Large file

        scanner = Scanner(tmp_path)
        result = scanner.scan()

        assert len(result.conversations) == 1
        assert len(result.notes) == 1
        assert len(result.documents) == 1
        assert len(result.misplaced) == 0
        assert len(result.ignored) == 0

    def test_scan_misplaced_note(self, tmp_path: Path) -> None:
        """Test that oversized file in notes/ is flagged as misplaced."""
        (tmp_path / "notes").mkdir()

        # Create a 3 KiB file in notes/ (over the 2 KiB limit)
        large_note = tmp_path / "notes" / "large.md"
        large_note.write_text("x" * 3000)

        scanner = Scanner(tmp_path)
        result = scanner.scan()

        assert len(result.notes) == 0
        assert len(result.misplaced) == 1

        misplaced = result.misplaced[0]
        assert misplaced.path == large_note
        assert misplaced.placed_in == FileCategory.NOTE
        # Could be suggested as DOCUMENT or CONVERSATION (both accept any size)
        assert misplaced.suggested in {FileCategory.DOCUMENT, FileCategory.CONVERSATION}

    def test_scan_ignored_file(self, tmp_path: Path) -> None:
        """Test that invalid file (.pdf) is ignored."""
        (tmp_path / "notes").mkdir()

        pdf_file = tmp_path / "notes" / "diagram.pdf"
        pdf_file.write_bytes(b"fake pdf")

        scanner = Scanner(tmp_path)
        result = scanner.scan()

        assert len(result.notes) == 0
        assert len(result.ignored) == 1
        assert result.ignored[0] == pdf_file

    def test_scan_extra_subdirs_ignored(self, tmp_path: Path) -> None:
        """Test that extra subdirectories are silently skipped."""
        (tmp_path / "notes").mkdir()
        (tmp_path / "extras").mkdir()  # Not a category dir

        note = tmp_path / "notes" / "note.md"
        note.write_text("note")

        extra = tmp_path / "extras" / "extra.md"
        extra.write_text("extra")

        scanner = Scanner(tmp_path)
        result = scanner.scan()

        assert len(result.notes) == 1
        # extra.md should not appear anywhere in the results
        all_paths = [m.path for m in result.notes] + result.ignored
        assert extra not in all_paths

    def test_scan_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test that nonexistent input dir raises ValueError."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(ValueError, match="does not exist"):
            Scanner(nonexistent)

    def test_scan_deduplicates_by_hash(self, tmp_path: Path) -> None:
        """Test that identical files are deduplicated."""
        (tmp_path / "conversations").mkdir()
        (tmp_path / "documents").mkdir()

        # Create two identical files in different dirs
        content = "Identical content\n" * 100

        file1 = tmp_path / "conversations" / "original.md"
        file1.write_text(content)

        file2 = tmp_path / "documents" / "copy.md"
        file2.write_text(content)

        scanner = Scanner(tmp_path)
        result = scanner.scan()

        # Only first occurrence should be kept
        assert len(result.conversations) == 1
        assert len(result.documents) == 0
        assert len(result.duplicates) == 1
        assert result.duplicates[0] == file2

    def test_scan_dedup_priority(self, tmp_path: Path) -> None:
        """Test that deduplication priority is CONVERSATION > DOCUMENT > NOTE."""
        (tmp_path / "conversations").mkdir()
        (tmp_path / "notes").mkdir()

        content = "Same content"

        conv_file = tmp_path / "conversations" / "conv.md"
        conv_file.write_text(content)

        note_file = tmp_path / "notes" / "note.md"
        note_file.write_text(content)

        scanner = Scanner(tmp_path)
        result = scanner.scan()

        # Conversation should win
        assert len(result.conversations) == 1
        assert len(result.notes) == 0
        assert len(result.duplicates) == 1
        assert result.duplicates[0] == note_file
