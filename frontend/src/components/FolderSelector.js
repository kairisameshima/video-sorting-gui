import React, { useState, useRef, useEffect } from 'react';
import { Form, Button, Alert, Card, InputGroup, Dropdown } from 'react-bootstrap';
import { setSourceFolder, getCommonDirectories } from '../api/api';

const FolderSelector = ({ onFolderSelected }) => {
  const [folderPath, setFolderPath] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [directories, setDirectories] = useState([]);
  const [loadingDirectories, setLoadingDirectories] = useState(false);
  const fileInputRef = useRef(null);

  // Fetch common directories when component mounts
  useEffect(() => {
    const fetchDirectories = async () => {
      try {
        setLoadingDirectories(true);
        const dirs = await getCommonDirectories();
        setDirectories(dirs);
      } catch (err) {
        console.error('Error fetching directories:', err);
        setError('Failed to load directories. Please enter a path manually.');
      } finally {
        setLoadingDirectories(false);
      }
    };

    fetchDirectories();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!folderPath.trim()) {
      setError('Please enter a folder path');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const videoFiles = await setSourceFolder(folderPath);
      onFolderSelected(folderPath, videoFiles);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error setting source folder');
    } finally {
      setLoading(false);
    }
  };

  const handleFolderSelect = () => {
    fileInputRef.current.click();
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      // Get the folder path from the first file's webkitRelativePath
      // This gives us the folder name and the relative path within that folder
      const folderName = files[0].webkitRelativePath.split('/')[0];

      // For security reasons, browsers don't provide the full system path
      // We'll use the folder name as the path, which the backend will resolve
      // If you need the full path, you'll need to use a native app or Electron
      setFolderPath(folderName);

      // Auto-submit the form after selecting a folder
      setTimeout(() => {
        handleSubmit(new Event('submit'));
      }, 100);
    }
  };

  return (
    <Card className="folder-selector">
      <Card.Body>
        <Card.Title>Select Source Folder</Card.Title>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Folder Path</Form.Label>
            <InputGroup>
              <Form.Control
                type="text"
                placeholder="Enter the full path to the folder containing videos"
                value={folderPath}
                onChange={(e) => setFolderPath(e.target.value)}
                disabled={loading}
              />
              <Dropdown>
                <Dropdown.Toggle 
                  variant="outline-secondary" 
                  id="dropdown-folders"
                  disabled={loading || loadingDirectories}
                >
                  {loadingDirectories ? 'Loading...' : 'Select Folder'}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  {directories.map((dir, index) => (
                    <Dropdown.Item 
                      key={index} 
                      onClick={() => {
                        setFolderPath(dir.path);
                        // Auto-submit after selecting a directory
                        setTimeout(() => {
                          handleSubmit(new Event('submit'));
                        }, 100);
                      }}
                    >
                      {dir.path}
                    </Dropdown.Item>
                  ))}
                </Dropdown.Menu>
              </Dropdown>
              <Button 
                variant="outline-secondary" 
                onClick={handleFolderSelect}
                disabled={loading}
              >
                Browse...
              </Button>
              <input
                type="file"
                ref={fileInputRef}
                webkitdirectory="true"
                directory="true"
                style={{ display: 'none' }}
                onChange={handleFileInputChange}
              />
            </InputGroup>
            <Form.Text className="text-muted">
              Enter the full path to the folder containing the videos you want to sort, select from common folders, or click "Browse..." to select a folder.
            </Form.Text>
          </Form.Group>

          {error && <Alert variant="danger">{error}</Alert>}

          <Button variant="primary" type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Load Videos'}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default FolderSelector;
