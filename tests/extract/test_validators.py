"""Tests for extract layer validators."""

from pathlib import Path

from my_position.extract.validators import (
    ConversationValidator,
    DocumentValidator,
    FileValidator,
    NoteValidator,
)


class TestFileValidator:
    """Tests for FileValidator base class."""

    def test_validate_common_valid_md(self, tmp_path: Path) -> None:
        """Test that .md file passes base validation."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        validator = NoteValidator()  # Any concrete subclass works
        assert validator.validate(test_file)

    def test_validate_common_invalid_extension(self, tmp_path: Path) -> None:
        """Test that .pdf file fails base validation."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        validator = NoteValidator()
        assert not validator.validate(test_file)

    def test_validate_common_nonexistent(self, tmp_path: Path) -> None:
        """Test that nonexistent file fails validation."""
        test_file = tmp_path / "nonexistent.md"

        validator = NoteValidator()
        assert not validator.validate(test_file)

    def test_validate_common_directory(self, tmp_path: Path) -> None:
        """Test that directory fails validation."""
        test_dir = tmp_path / "test.md"  # Looks like a file but is a dir
        test_dir.mkdir()

        validator = NoteValidator()
        assert not validator.validate(test_dir)

    def test_hash_file_deterministic(self, tmp_path: Path) -> None:
        """Test that hashing same content produces same hash."""
        file1 = tmp_path / "file1.md"
        file2 = tmp_path / "file2.md"
        content = "Test content\n" * 100

        file1.write_text(content)
        file2.write_text(content)

        hash1 = FileValidator.hash_file(file1)
        hash2 = FileValidator.hash_file(file2)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex is 64 chars

    def test_hash_file_differs(self, tmp_path: Path) -> None:
        """Test that different content produces different hashes."""
        file1 = tmp_path / "file1.md"
        file2 = tmp_path / "file2.md"

        file1.write_text("Content A")
        file2.write_text("Content B")

        hash1 = FileValidator.hash_file(file1)
        hash2 = FileValidator.hash_file(file2)

        assert hash1 != hash2


class TestNoteValidator:
    """Tests for NoteValidator."""

    def test_validate_note_within_limit(self, tmp_path: Path) -> None:
        """Test that file ≤ 2 KiB passes note validation."""
        test_file = tmp_path / "note.md"
        # 2048 bytes exactly
        test_file.write_text("x" * 2048)

        validator = NoteValidator()
        assert validator.validate(test_file)

    def test_validate_note_over_limit(self, tmp_path: Path) -> None:
        """Test that file > 2 KiB fails note validation."""
        test_file = tmp_path / "note.md"
        # 2049 bytes
        test_file.write_text("x" * 2049)

        validator = NoteValidator()
        assert not validator.validate(test_file)


class TestDocumentValidator:
    """Tests for DocumentValidator."""

    def test_validate_document_any_size(self, tmp_path: Path) -> None:
        """Test that both small and large .md files pass document validation."""
        small_file = tmp_path / "small.md"
        large_file = tmp_path / "large.md"

        small_file.write_text("short")
        large_file.write_text("x" * 10000)

        validator = DocumentValidator()
        assert validator.validate(small_file)
        assert validator.validate(large_file)


class TestConversationValidator:
    """Tests for ConversationValidator."""

    def test_validate_conversation_valid(self, tmp_path: Path) -> None:
        """Test that any valid .md file passes conversation validation."""
        test_file = tmp_path / "conversation.md"
        test_file.write_text("User: Hello\nAssistant: Hi!")

        validator = ConversationValidator()
        assert validator.validate(test_file)
