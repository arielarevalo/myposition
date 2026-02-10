"""Scanner for extracting and categorizing files from input directory."""

from pathlib import Path

from my_position.extract.models import (
    CATEGORY_DIRS,
    CategorizationResult,
    FileCategory,
    FileMetadata,
    MisplacedFile,
)
from my_position.extract.validators import (
    ConversationValidator,
    DocumentValidator,
    FileValidator,
    NoteValidator,
)


class Scanner:
    """Scans input directory and categorizes files based on validation rules."""

    def __init__(self, input_dir: Path) -> None:
        """Initialize scanner with input directory.

        Args:
            input_dir: Path to directory containing category subdirectories

        Raises:
            ValueError: If input_dir doesn't exist or isn't a directory
        """
        self.input_dir = input_dir.resolve()
        if not self.input_dir.exists():
            msg = f"Input directory does not exist: {input_dir}"
            raise ValueError(msg)
        if not self.input_dir.is_dir():
            msg = f"Input path is not a directory: {input_dir}"
            raise ValueError(msg)

        # Initialize validators for each category
        self._validators: dict[FileCategory, FileValidator] = {
            FileCategory.NOTE: NoteValidator(),
            FileCategory.DOCUMENT: DocumentValidator(),
            FileCategory.CONVERSATION: ConversationValidator(),
        }

    def scan(self) -> CategorizationResult:
        """Scan input directory and categorize files.

        Returns:
            CategorizationResult with categorized files, misplaced files,
            duplicates, and ignored files
        """
        # Temporary collections during scanning
        categorized: dict[FileCategory, set[FileMetadata]] = {
            FileCategory.CONVERSATION: set(),
            FileCategory.NOTE: set(),
            FileCategory.DOCUMENT: set(),
        }
        misplaced: list[MisplacedFile] = []
        ignored: list[Path] = []

        # Scan each category subdirectory
        for dir_name, category in CATEGORY_DIRS.items():
            subdir = self.input_dir / dir_name
            if not subdir.exists() or not subdir.is_dir():
                continue

            # Iterate over files (non-recursive)
            for file_path in subdir.iterdir():
                if not file_path.is_file():
                    continue

                # Try validating with the expected category validator
                validator = self._validators[category]
                if validator.validate(file_path):
                    # Success: hash file and create metadata
                    content_hash = FileValidator.hash_file(file_path)
                    metadata = FileMetadata(
                        path=file_path,
                        category=category,
                        size=file_path.stat().st_size,
                        content_hash=content_hash,
                    )
                    categorized[category].add(metadata)
                else:
                    # Failed: try other validators
                    suggestions = self._find_alternate_category(file_path, category)
                    if suggestions:
                        # Exactly one alternate category passed
                        # (or multiple, we just pick the first)
                        suggested = suggestions[0]
                        misplaced.append(
                            MisplacedFile(
                                path=file_path,
                                placed_in=category,
                                suggested=suggested,
                            )
                        )
                    else:
                        # No alternate categories passed
                        ignored.append(file_path)

        # Deduplicate by content hash
        deduped, duplicates = self._deduplicate(categorized)

        return CategorizationResult(
            conversations=frozenset(deduped[FileCategory.CONVERSATION]),
            notes=frozenset(deduped[FileCategory.NOTE]),
            documents=frozenset(deduped[FileCategory.DOCUMENT]),
            misplaced=misplaced,
            duplicates=duplicates,
            ignored=ignored,
        )

    def _find_alternate_category(
        self, path: Path, skip_category: FileCategory
    ) -> list[FileCategory]:
        """Find alternate categories that would accept this file.

        Args:
            path: File to validate
            skip_category: Category to skip (the one it was placed in)

        Returns:
            List of categories that pass validation (may be empty)
        """
        suggestions = []
        for category, validator in self._validators.items():
            if category == skip_category:
                continue
            if validator.validate(path):
                suggestions.append(category)
        return suggestions

    def _deduplicate(
        self, categorized: dict[FileCategory, set[FileMetadata]]
    ) -> tuple[dict[FileCategory, set[FileMetadata]], list[Path]]:
        """Deduplicate files across categories by content hash.

        Priority order: CONVERSATION > DOCUMENT > NOTE (first wins).

        Args:
            categorized: Dict of category to FileMetadata sets

        Returns:
            Tuple of (deduplicated categorized dict, list of duplicate paths)
        """
        seen_hashes: dict[str, FileMetadata] = {}
        duplicates: list[Path] = []
        deduped: dict[FileCategory, set[FileMetadata]] = {
            FileCategory.CONVERSATION: set(),
            FileCategory.NOTE: set(),
            FileCategory.DOCUMENT: set(),
        }

        # Process in priority order
        priority_order = [
            FileCategory.CONVERSATION,
            FileCategory.DOCUMENT,
            FileCategory.NOTE,
        ]

        for category in priority_order:
            for metadata in categorized[category]:
                if metadata.content_hash in seen_hashes:
                    # Duplicate detected
                    duplicates.append(metadata.path)
                else:
                    # First occurrence
                    seen_hashes[metadata.content_hash] = metadata
                    deduped[category].add(metadata)

        return deduped, duplicates
