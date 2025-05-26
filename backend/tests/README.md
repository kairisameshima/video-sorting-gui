# Tests for Video Sorting GUI Backend

This directory contains tests for the backend services of the Video Sorting GUI application.

## Running Tests

To run all tests:

```bash
cd backend
python -m pytest
```

To run tests with verbose output:

```bash
cd backend
python -m pytest -v
```

To run a specific test file:

```bash
cd backend
python -m pytest tests/test_file_service.py -v
```

## Test Coverage

### File Service Tests

The `test_file_service.py` file contains tests for the file service module, which handles file operations such as moving, renaming, and skipping files.

#### `get_unique_filename` Function Tests

- `test_destination_does_not_exist`: Tests that the function returns the original destination when the destination file doesn't exist.
- `test_destination_exists_no_similar_files`: Tests that the function generates a unique filename with "_1" suffix when the destination file exists but no similar files exist.
- `test_destination_exists_with_similar_files`: Tests that the function generates a unique filename with the next available number suffix when the destination file exists and similar files exist.
- `test_destination_with_existing_number_suffix`: Tests that the function handles destinations that already have a "_n" suffix.
- `test_non_sequential_numbers`: Tests that the function correctly finds the highest number in existing files with non-sequential numbers.

#### `move_file` Function Tests

- `test_move_file_with_conflict`: Tests moving a file when a file with the same name exists at the destination. Also verifies that the logs reflect the new name that fixed the conflict.
- `test_move_file_with_prepend_hyphen_and_conflict`: Tests moving a file with prepend_hyphen when a file with the same name exists. Also verifies that the logs reflect both the hyphen prefix and the new name that fixed the conflict.

#### `prepend_hyphen` Function Tests

- `test_prepend_hyphen_with_conflict`: Tests prepending a hyphen when a file with the same name exists. Also verifies that the logs reflect the new name that fixed the conflict.

#### `undo_last_operation` Function Tests

- `test_undo_move_with_conflict`: Tests undoing a move operation when a file with the same name exists at the original location. Also verifies that the logs reflect the new name that fixed the conflict.

## Test Results

All tests are passing, confirming that the file name conflict resolution logic is working correctly. The implementation handles various scenarios, including:

- When a file with the same name exists at the destination, a unique filename with "_n" suffix is generated.
- When a file with the same name exists and prepend_hyphen is used, a unique filename with "-" prefix and "_n" suffix is generated.
- When undoing operations, filename conflicts are handled correctly.

The tests also verify that the logs correctly reflect any new names that fixed name conflicts. For each operation that results in a filename conflict, the logs include messages like:
- "File with the same name exists, using unique name: file_3.txt"
- "File with the same name exists at original location, using unique name: file_1.txt"

This ensures that users can review the logs to understand what happened when files were renamed due to conflicts.
