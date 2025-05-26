import os
import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import logging

# Add the parent directory to sys.path to import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.file_service import get_unique_filename, move_file, prepend_hyphen, undo_last_operation, operation_history, logger


class TestGetUniqueFilename:
    """Tests for the get_unique_filename function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_destination_does_not_exist(self, temp_dir):
        """Test when the destination file doesn't exist."""
        destination = temp_dir / "file.txt"
        result = get_unique_filename(destination)
        assert result == destination
        assert str(result) == str(destination)

    def test_destination_exists_no_similar_files(self, temp_dir):
        """Test when the destination file exists but no similar files exist."""
        # Create the destination file
        destination = temp_dir / "file.txt"
        destination.touch()

        # Create some unrelated files
        (temp_dir / "other.txt").touch()
        (temp_dir / "another.txt").touch()

        result = get_unique_filename(destination)
        assert result != destination
        assert result.name == "file_1.txt"
        assert result.parent == destination.parent

    def test_destination_exists_with_similar_files(self, temp_dir):
        """Test when the destination file exists and similar files exist."""
        # Create the destination file and similar files
        destination = temp_dir / "file.txt"
        destination.touch()
        (temp_dir / "file_1.txt").touch()
        (temp_dir / "file_2.txt").touch()

        result = get_unique_filename(destination)
        assert result != destination
        assert result.name == "file_3.txt"
        assert result.parent == destination.parent

    def test_destination_with_existing_number_suffix(self, temp_dir):
        """Test when the destination file already has a _n suffix."""
        # Create the destination file with a _n suffix
        destination = temp_dir / "file_1.txt"
        destination.touch()
        (temp_dir / "file.txt").touch()
        (temp_dir / "file_2.txt").touch()

        result = get_unique_filename(destination)
        assert result != destination
        assert result.name == "file_3.txt"
        assert result.parent == destination.parent

    def test_non_sequential_numbers(self, temp_dir):
        """Test when the existing files have non-sequential numbers."""
        # Create files with non-sequential numbers
        destination = temp_dir / "file.txt"
        destination.touch()
        (temp_dir / "file_1.txt").touch()
        (temp_dir / "file_5.txt").touch()
        (temp_dir / "file_10.txt").touch()

        result = get_unique_filename(destination)
        assert result != destination
        assert result.name == "file_11.txt"
        assert result.parent == destination.parent


class TestMoveFile:
    """Tests for the move_file function with filename conflicts."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def setup_files(self, temp_dir):
        """Set up test files."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Create source file
        source_file = source_dir / "file.txt"
        with open(source_file, "w") as f:
            f.write("test content")

        # Create destination files
        (dest_dir / "file.txt").touch()
        (dest_dir / "file_1.txt").touch()
        (dest_dir / "file_2.txt").touch()

        return {
            "source_dir": source_dir,
            "dest_dir": dest_dir,
            "source_file": source_file
        }

    @pytest.mark.asyncio
    async def test_move_file_with_conflict(self, setup_files, caplog):
        """Test moving a file when a file with the same name exists at the destination."""
        source_file = setup_files["source_file"]
        dest_dir = setup_files["dest_dir"]
        dest_file = dest_dir / "file.txt"

        # Clear operation history before test
        operation_history.clear()

        # Set log level to capture INFO messages
        caplog.set_level(logging.INFO)

        result = await move_file(str(source_file), str(dest_file))

        assert result.success
        assert not source_file.exists()
        assert (dest_dir / "file_3.txt").exists()
        assert "file_3.txt" in result.message

        # Verify log message for file name conflict
        assert "File with the same name exists, using unique name: file_3.txt" in caplog.text

    @pytest.mark.asyncio
    async def test_move_file_with_prepend_hyphen_and_conflict(self, setup_files, caplog):
        """Test moving a file with prepend_hyphen when a file with the same name exists."""
        source_file = setup_files["source_file"]
        dest_dir = setup_files["dest_dir"]
        dest_file = dest_dir / "file.txt"

        # Create a file with hyphen
        (dest_dir / "-file.txt").touch()

        # Clear operation history before test
        operation_history.clear()

        # Set log level to capture INFO messages
        caplog.set_level(logging.INFO)

        result = await move_file(str(source_file), str(dest_file), prepend_hyphen_first=True)

        assert result.success
        assert not source_file.exists()
        assert (dest_dir / "-file_1.txt").exists()
        assert "-file_1.txt" in result.message

        # Verify log messages for prepend hyphen and file name conflict
        assert "Will prepend hyphen before moving: -file.txt" in caplog.text
        assert "File with the same name exists, using unique name: -file_1.txt" in caplog.text


class TestPrependHyphen:
    """Tests for the prepend_hyphen function with filename conflicts."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def setup_files(self, temp_dir):
        """Set up test files."""
        # Create test file
        test_file = temp_dir / "file.txt"
        with open(test_file, "w") as f:
            f.write("test content")

        # Create files with hyphen
        (temp_dir / "-file.txt").touch()
        (temp_dir / "-file_1.txt").touch()

        return {
            "temp_dir": temp_dir,
            "test_file": test_file
        }

    def test_prepend_hyphen_with_conflict(self, setup_files, caplog):
        """Test prepending a hyphen when a file with the same name exists."""
        test_file = setup_files["test_file"]

        # Clear operation history before test
        operation_history.clear()

        # Set log level to capture INFO messages
        caplog.set_level(logging.INFO)

        result = prepend_hyphen(str(test_file))

        assert result.success
        assert not test_file.exists()
        assert (test_file.parent / "-file_2.txt").exists()
        assert "-file_2.txt" in result.message

        # Verify log messages for file name conflict
        assert "File with the same name exists, using unique name: -file_2.txt" in caplog.text
        assert "Renaming file: file.txt -> -file_2.txt" in caplog.text
        assert "File renamed successfully: file.txt -> -file_2.txt" in caplog.text


class TestUndoLastOperation:
    """Tests for the undo_last_operation function with filename conflicts."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def setup_files(self, temp_dir):
        """Set up test files."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Create source file
        source_file = source_dir / "file.txt"
        with open(source_file, "w") as f:
            f.write("test content")

        return {
            "source_dir": source_dir,
            "dest_dir": dest_dir,
            "source_file": source_file
        }

    @pytest.mark.asyncio
    async def test_undo_move_with_conflict(self, setup_files, caplog):
        """Test undoing a move operation when a file with the same name exists at the original location."""
        source_file = setup_files["source_file"]
        dest_dir = setup_files["dest_dir"]
        dest_file = dest_dir / "moved_file.txt"

        # Clear operation history before test
        operation_history.clear()

        # Move the file
        await move_file(str(source_file), str(dest_file))

        # Create a new file at the original location
        with open(source_file, "w") as f:
            f.write("new content")

        # Clear caplog before undo operation
        caplog.clear()

        # Set log level to capture INFO messages
        caplog.set_level(logging.INFO)

        # Undo the move
        result = undo_last_operation()

        assert result.success
        assert not dest_file.exists()
        assert source_file.exists()  # Original file still exists
        assert (setup_files["source_dir"] / "file_1.txt").exists()  # New file with _1 suffix
        assert "file_1.txt" in result.message

        # Verify log messages for file name conflict during undo
        assert "File with the same name exists at original location, using unique name: file_1.txt" in caplog.text
        assert "Undoing move:" in caplog.text
        assert "File moved back successfully:" in caplog.text
