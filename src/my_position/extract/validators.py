"""File validators for the extract layer."""

import hashlib
from abc import ABC
from pathlib import Path
from typing import ClassVar


class FileValidator(ABC):
    """Base validator for files.

    Subclasses add category-specific validation rules.
    """

    ALLOWED_EXTENSIONS: ClassVar[frozenset[str]] = frozenset(
        {".md", ".markdown", ".txt"}
    )

    def validate(self, path: Path) -> bool:
        """Validate that a file belongs to this category.

        Base implementation checks:
        - File exists
        - Is a regular file (not directory, symlink, etc.)
        - Has an allowed extension

        Subclasses override to add category-specific rules.

        Args:
            path: Path to the file to validate

        Returns:
            True if file passes validation, False otherwise
        """
        if not path.exists():
            return False
        if not path.is_file():
            return False
        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            return False
        return True

    @staticmethod
    def hash_file(path: Path) -> str:
        """Compute SHA-256 hash of file contents.

        Uses chunked reads to avoid loading entire file into memory.

        Args:
            path: Path to the file to hash

        Returns:
            Hexadecimal SHA-256 digest
        """
        sha256 = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(8192):  # 8 KiB chunks
                sha256.update(chunk)
        return sha256.hexdigest()


class NoteValidator(FileValidator):
    """Validator for note files.

    Notes must be ≤ 2 KiB in size.
    """

    NOTE_MAX_SIZE: ClassVar[int] = 2048  # 2 KiB

    def validate(self, path: Path) -> bool:
        """Validate note file: base checks + size constraint.

        Args:
            path: Path to the file to validate

        Returns:
            True if file passes validation, False otherwise
        """
        if not super().validate(path):
            return False
        return path.stat().st_size <= self.NOTE_MAX_SIZE


class DocumentValidator(FileValidator):
    """Validator for document files.

    Documents have no size constraint at file level.
    """

    def validate(self, path: Path) -> bool:
        """Validate document file: base checks only.

        Args:
            path: Path to the file to validate

        Returns:
            True if file passes validation, False otherwise
        """
        return super().validate(path)


class ConversationValidator(FileValidator):
    """Validator for conversation files.

    Conversations have no size constraint at file level.
    Content-aware validation (multi-speaker detection) is deferred to Stage 2.
    """

    def validate(self, path: Path) -> bool:
        """Validate conversation file: base checks only.

        Args:
            path: Path to the file to validate

        Returns:
            True if file passes validation, False otherwise
        """
        return super().validate(path)
