"""Extract layer of the ETL pipeline.

Scans input directories for markdown files, validates them, and produces
categorized file metadata.
"""

from my_position.extract.models import (
    CategorizationResult,
    FileCategory,
    FileMetadata,
    MisplacedFile,
)
from my_position.extract.scanner import Scanner

__all__ = [
    "CategorizationResult",
    "FileCategory",
    "FileMetadata",
    "MisplacedFile",
    "Scanner",
]
