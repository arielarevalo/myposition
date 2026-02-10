# my-position

[![CI](https://github.com/arielarevalo/my-position/actions/workflows/ci.yml/badge.svg)](https://github.com/arielarevalo/my-position/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Synthesize your positions on topics from conversations, notes, and documents.**

A CLI tool that processes your Markdown conversations, notes, and documents to identify topics, model your positions, and generate encyclopedia-like position entries. Think of it as creating a personal encyclopedia of your views, automatically derived from your writings.

## Features

- **Markdown Ingestion**: Process conversation logs, notes, and documents in Markdown format
- **Topic Modeling**: Automatically identify and cluster topics from your content
- **Position Synthesis**: Generate coherent position statements from fragmented discussions
- **Encyclopedia-Style Output**: Create structured, encyclopedia-like entries for each topic
- **Extensible Connectors**: Designed to integrate with external services (Slack, Notion, etc.) via separate connector libraries

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/arielarevalo/my-position.git
cd my-position

# Install dependencies
uv sync
```

## Usage

```bash
# Display usage information
uv run my-position

# Ingest Markdown files (coming soon)
uv run my-position ingest ./notes/*.md

# Synthesize positions (coming soon)
uv run my-position synthesize --topic "software-architecture"

# Export positions (coming soon)
uv run my-position export --format markdown --output positions.md
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=my_position --cov-report=html

# Run specific test file
uv run pytest tests/test_main.py
```

### Code Quality

```bash
# Lint and auto-fix
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type check
uvx ty check

# Run all checks
uv run ruff check --fix . && uv run ruff format . && uvx ty check && uv run pytest
```

### CI/CD

The project uses GitHub Actions for continuous integration:
- Automated testing on push and pull requests
- Linting with ruff
- Type checking with ty
- Code coverage reporting

## Architecture

```
my-position/
├── src/
│   └── my_position/           # Main package
│       ├── __init__.py
│       ├── main.py            # CLI entry point
│       ├── cli.py             # CLI implementation
│       ├── extract/           # ETL: Extract layer
│       │   ├── __init__.py
│       │   ├── models.py      # Data models
│       │   ├── validators.py  # File validators
│       │   └── scanner.py     # Directory scanner
│       ├── transform/         # ETL: Transform layer (future)
│       └── load/              # ETL: Load layer (future)
├── tests/                     # Test suite
│   ├── extract/               # Extract layer tests
│   ├── test_cli.py            # CLI tests
│   ├── test_e2e.py            # End-to-end tests
│   └── conftest.py
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI
└── pyproject.toml             # Project config & dependencies
```

### ETL Pipeline

**Extract**: Scan input directories for `conversations/`, `notes/`, and `documents/` subdirectories. Validate files based on extension and size constraints. Produce categorized file metadata with content hashes for deduplication.

**Transform** (future): Topic modeling identifies themes and clusters related content.

**Load** (future): Export encyclopedia-style position entries in various formats.

### Data Flow

1. **Input**: Markdown files containing conversations, notes, or documents
2. **Processing**: Topic modeling identifies themes and clusters related content
3. **Synthesis**: Position synthesis generates coherent statements from fragmented discussions
4. **Output**: Encyclopedia-style position entries in various formats

### External Connectors

Service-specific connectors (Slack, Notion, Obsidian, etc.) will be maintained in separate repositories to keep the core library lightweight and focused. This follows a plugin architecture where connectors implement a standard interface.

## Roadmap

- [ ] **Phase 1**: File extraction and parsing
  - [x] **Stage 1**: File extraction & file-level validation (CLI integration)
  - [ ] **Stage 2**: Content-aware validation (speaker detection, structure analysis)
  - [ ] **Stage 3**: Markdown parsing & content extraction
- [ ] **Phase 2**: Topic modeling engine (TF-IDF, clustering)
- [ ] **Phase 3**: Position synthesis from clustered content
- [ ] **Phase 4**: Export formats (Markdown, JSON, HTML)
- [ ] **Phase 5**: Connector framework and reference implementations

## Contributing

Contributions are welcome! This is an open-source project under active development.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and ensure tests pass
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Standards

- All code must have type hints
- Tests required for new features (80% coverage minimum)
- Follow existing code style (enforced by ruff)
- Update documentation for user-facing changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Status

**Work in Progress**: This project is in early development. The core infrastructure is in place, but feature implementation is ongoing. Check the [Roadmap](#roadmap) for current progress.
