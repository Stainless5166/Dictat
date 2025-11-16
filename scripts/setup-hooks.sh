#!/bin/bash
# Setup script for git pre-commit hooks
# This script installs and configures pre-commit hooks for code quality

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository. Please run this script from the project root."
    exit 1
fi

print_info "Setting up pre-commit hooks for Dictat project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_info "Detected Python version: $PYTHON_VERSION"

# Check if UV is installed, if not offer to install it
if ! command -v uv &> /dev/null; then
    print_warn "UV package manager not found."
    read -p "Would you like to install UV? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        print_warn "Skipping UV installation. Using pip instead."
    fi
fi

# Install pre-commit
print_info "Installing pre-commit..."
if command -v uv &> /dev/null; then
    uv pip install pre-commit
else
    pip install pre-commit
fi

# Verify pre-commit installation
if ! command -v pre-commit &> /dev/null; then
    print_error "pre-commit installation failed. Please install manually:"
    print_error "  pip install pre-commit"
    exit 1
fi

print_info "pre-commit installed successfully: $(pre-commit --version)"

# Install the git hook scripts
print_info "Installing pre-commit hooks..."
pre-commit install

# Install commit-msg hook for commitizen
print_info "Installing commit-msg hook..."
pre-commit install --hook-type commit-msg

# Create .yamllint.yaml if it doesn't exist
if [ ! -f .yamllint.yaml ]; then
    print_info "Creating .yamllint.yaml configuration..."
    cat > .yamllint.yaml <<EOF
---
extends: default

rules:
  line-length:
    max: 120
    level: warning
  indentation:
    spaces: 2
  comments:
    min-spaces-from-content: 1
  document-start: disable
  truthy:
    allowed-values: ['true', 'false', 'on', 'off']
EOF
fi

# Create pyproject.toml configuration for tools if it doesn't exist
if [ ! -f pyproject.toml ]; then
    print_info "Creating pyproject.toml with tool configurations..."
    cat > pyproject.toml <<EOF
[project]
name = "dictat"
version = "0.1.0"
description = "Medical dictation service"
requires-python = ">=3.11"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.isort]
known-third-party = ["fastapi", "pydantic", "sqlalchemy"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
follow_imports = "normal"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = ["B101", "B601"]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
pythonpath = ["."]

[tool.coverage.run]
source = ["."]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/.venv/*",
    "*/alembic/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v\$version"
version_files = [
    "pyproject.toml:version"
]
EOF
fi

# Create .markdownlint.json if it doesn't exist
if [ ! -f .markdownlint.json ]; then
    print_info "Creating .markdownlint.json configuration..."
    cat > .markdownlint.json <<EOF
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "tables": false
  },
  "MD033": false,
  "MD041": false
}
EOF
fi

# Run pre-commit on all files (optional, can be slow)
read -p "Run pre-commit on all existing files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running pre-commit on all files (this may take a while)..."
    pre-commit run --all-files || print_warn "Some hooks failed. This is normal for existing code. Fix issues and commit."
else
    print_info "Skipping initial run. Hooks will run on your next commit."
fi

print_info ""
print_info "✓ Pre-commit hooks installed successfully!"
print_info ""
print_info "Next steps:"
print_info "  1. Hooks will automatically run on 'git commit'"
print_info "  2. To run manually: pre-commit run --all-files"
print_info "  3. To update hooks: pre-commit autoupdate"
print_info "  4. To bypass hooks (not recommended): git commit --no-verify"
print_info ""
print_info "Configured hooks:"
print_info "  - Black (Python formatter)"
print_info "  - Ruff (Python linter)"
print_info "  - mypy (Python type checker)"
print_info "  - Bandit (Security scanner)"
print_info "  - Hadolint (Dockerfile linter)"
print_info "  - ShellCheck (Shell script linter)"
print_info "  - Markdownlint (Markdown linter)"
print_info "  - YAML/JSON validators"
print_info "  - Commitizen (Commit message format)"
print_info ""
print_info "For frontend (when available):"
print_info "  - ESLint (JavaScript/TypeScript linter)"
print_info "  - Prettier (Code formatter)"
print_info "  - TypeScript type checking"
print_info ""
