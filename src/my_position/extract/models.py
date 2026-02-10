"""Data models for the extract layer."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileCategory(Enum):
    """File categories, ordered by deduplication priority (highest first)."""

    CONVERSATION = "conversations"
    DOCUMENT = "documents"
    NOTE = "notes"


# Mapping from directory names to categories
CATEGORY_DIRS: dict[str, FileCategory] = {
    category.value: category for category in FileCategory
}


@dataclass(frozen=True)
class FileMetadata:
    """Metadata for a validated file."""

    path: Path
    category: FileCategory
    size: int
    content_hash: str  # SHA-256 hex digest


@dataclass(frozen=True)
class MisplacedFile:
    """A file that failed validation for its directory but passed for another."""

    path: Path
    placed_in: FileCategory
    suggested: FileCategory


@dataclass
class CategorizationResult:
    """Result of scanning and categorizing files in an input directory."""

    conversations: frozenset[FileMetadata]
    notes: frozenset[FileMetadata]
    documents: frozenset[FileMetadata]
    misplaced: list[MisplacedFile]
    duplicates: list[Path]
    ignored: list[Path]
