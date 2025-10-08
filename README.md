# Test Deduplication Tool

A command-line tool for identifying and removing duplicate test functions across Python files while preserving all formatting, comments, and whitespace.

## Description

This tool helps you refactor test suites by:
- Extracting all test functions (those starting with `test_`) from two Python files
- Comparing them side-by-side interactively
- Removing equivalent tests from one file while maintaining exact formatting using LibCST
- Generating a cleaned version of your test file

Perfect for consolidating test suites, removing redundant tests, or merging test files.

## Installation

### From source

```bash
# Clone or navigate to the repository
cd refactor-toolbox

# Install in development mode
pip install -e .
```

### Requirements
- Python >= 3.8
- libcst

## Usage

### Basic Command

```bash
test-dedup <file1.py> <file2.py>
```

This will:
1. Extract all `test_*` functions from both files
2. Show you each common test side-by-side
3. Ask if they're equivalent (respond with `y` or `n`)
4. Generate `<file1>_cleaned.py` with equivalent tests removed

### With Custom Output Path

```bash
test-dedup file1.py file2.py -o output.py
```

### Recommended Workflow

**Step 1: Commit your current state**
```bash
git add tests/test_module.py
git commit -m "Before deduplication"
```

**Step 2: Run the deduplication tool**
```bash
test-dedup tests/test_module.py tests/test_other.py
```

The tool will interactively show you each test pair:
```
============================================================
TEST: test_addition
============================================================

--- FROM tests/test_module.py ---
def test_addition():
    assert 1 + 1 == 2

--- FROM tests/test_other.py ---
def test_addition():
    assert 1 + 1 == 2

Are these equivalent? (y/n): y
✓ Marked 'test_addition' as equivalent
```

**Step 3: Review the changes**

Option A - Compare files directly:
```bash
# Using git diff
git diff tests/test_module.py tests/test_module_cleaned.py

# Or use diff
diff tests/test_module.py tests/test_module_cleaned.py
```

Option B - Use PyCharm's visual diff:
1. Right-click on `test_module.py` in Project view
2. Select **Compare With...**
3. Choose `test_module_cleaned.py`
4. Review changes in the side-by-side diff viewer

**Step 4: Apply changes if satisfied**

Replace the original with the cleaned version:
```bash
cp tests/test_module_cleaned.py tests/test_module.py
```

**Step 5: Review with version control**
```bash
git diff tests/test_module.py
```

This shows exactly what was removed from your original file.

**Step 6: Commit the changes**
```bash
git add tests/test_module.py
git commit -m "Remove duplicate tests identified in test_other.py"
```

### Command-Line Options

```
positional arguments:
  file1                 First Python file containing test functions (will be cleaned)
  file2                 Second Python file to compare against

options:
  -h, --help            Show help message
  -o OUTPUT, --output OUTPUT
                        Output file path (default: <file1>_cleaned.py)
```

## Examples

### Example 1: Basic deduplication
```bash
test-dedup tests/test_api.py tests/test_legacy_api.py
# Creates: tests/test_api_cleaned.py
```

### Example 2: Custom output location
```bash
test-dedup tests/old_tests.py tests/new_tests.py -o tests/consolidated.py
```

### Example 3: Full workflow with git
```bash
# Save current state
git commit -am "Before test deduplication"

# Run deduplication
test-dedup tests/test_main.py tests/test_backup.py

# Review changes
git diff tests/test_main.py tests/test_main_cleaned.py

# Apply if satisfied
mv tests/test_main_cleaned.py tests/test_main.py

# Final review
git diff

# Commit
git commit -am "Removed duplicate tests"
```

## Features

- **Format Preservation**: Uses LibCST to maintain exact formatting, indentation, comments, and whitespace
- **Interactive Comparison**: See tests side-by-side before deciding if they're equivalent
- **Safe by Default**: Creates new files instead of overwriting originals
- **Git-Friendly**: Designed to work seamlessly with version control workflows

## Notes

- Only functions starting with `test_` are considered
- Both standalone functions and methods within classes are detected
- The tool compares tests by name first, then shows you the implementation
- Original files are never modified automatically - you control when to apply changes

## License

MIT License