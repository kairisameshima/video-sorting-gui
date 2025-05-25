import React, { useState, useEffect } from 'react';
import { Form, Button, Alert, Card, Row, Col } from 'react-bootstrap';
import { setDestinationFolders } from '../api/api';
import { defaultSortingPatterns } from '../sortingPatterns';

const DestinationFolders = ({ onFoldersSet }) => {
  const [folders, setFolders] = useState([
    { shorthand: '', path: '' },
    { shorthand: '', path: '' }
  ]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const loadDefaultPatterns = () => {
    const defaultFolders = Object.entries(defaultSortingPatterns).map(([shorthand, path]) => ({
      shorthand,
      path
    }));
    setFolders(defaultFolders);
  };

  // Load default patterns when component mounts
  useEffect(() => {
    loadDefaultPatterns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAddFolder = () => {
    setFolders([...folders, { shorthand: '', path: '' }]);
  };

  const handleRemoveFolder = (index) => {
    if (folders.length <= 1) return;
    const newFolders = [...folders];
    newFolders.splice(index, 1);
    setFolders(newFolders);
  };

  const handleFolderChange = (index, field, value) => {
    const newFolders = [...folders];
    newFolders[index][field] = value;
    setFolders(newFolders);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate folders
    const invalidFolders = folders.filter(
      folder => !folder.shorthand.trim() || !folder.path.trim()
    );

    if (invalidFolders.length > 0) {
      setError('All folders must have both a shorthand and a path');
      return;
    }

    // Check for duplicate shorthands
    const shorthands = folders.map(folder => folder.shorthand.trim());
    if (new Set(shorthands).size !== shorthands.length) {
      setError('Folder shorthands must be unique');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Convert to the format expected by the API
      const foldersMap = {};
      folders.forEach(folder => {
        foldersMap[folder.shorthand.trim()] = folder.path.trim();
      });

      await setDestinationFolders(foldersMap);
      onFoldersSet(foldersMap);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error setting destination folders');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="destination-folders">
      <Card.Body>
        <Card.Title>Define Destination Folders</Card.Title>
        <Form onSubmit={handleSubmit}>
          {folders.map((folder, index) => (
            <Row key={index} className="mb-3">
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Shorthand</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="e.g., A, B, C"
                    value={folder.shorthand}
                    onChange={(e) => handleFolderChange(index, 'shorthand', e.target.value)}
                    disabled={loading}
                  />
                </Form.Group>
              </Col>
              <Col md={8}>
                <Form.Group>
                  <Form.Label>Folder Path</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter the full path to the destination folder"
                    value={folder.path}
                    onChange={(e) => handleFolderChange(index, 'path', e.target.value)}
                    disabled={loading}
                  />
                </Form.Group>
              </Col>
              <Col md={1} className="d-flex align-items-end">
                <Button 
                  variant="outline-danger" 
                  onClick={() => handleRemoveFolder(index)}
                  disabled={folders.length <= 1 || loading}
                  className="mb-2"
                >
                  &times;
                </Button>
              </Col>
            </Row>
          ))}

          <div className="d-flex mb-3">
            <Button 
              variant="outline-secondary" 
              onClick={handleAddFolder} 
              className="me-2"
              disabled={loading}
            >
              Add Folder
            </Button>
            <Button 
              variant="outline-primary" 
              onClick={loadDefaultPatterns} 
              disabled={loading}
            >
              Load Default Patterns
            </Button>
          </div>

          {error && <Alert variant="danger">{error}</Alert>}

          <div className="d-grid gap-2">
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Destination Folders'}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default DestinationFolders;
