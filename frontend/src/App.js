import React, { useState } from 'react';
import { Container, Row, Col, Alert, Button, Navbar } from 'react-bootstrap';
import FolderSelector from './components/FolderSelector';
import DestinationFolders from './components/DestinationFolders';
import VideoCard from './components/VideoCard';
import KeyboardMappingSelector from './components/KeyboardMappingSelector';
import { undoOperation } from './api/api';
import { FaUndo } from 'react-icons/fa';
import { defaultSortingPatterns } from './sortingPatterns';

function App() {
  const [sourceFolder, setSourceFolder] = useState('');
  const [videoFiles, setVideoFiles] = useState([]);
  const [destinationFolders, setDestinationFolders] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [setupComplete, setSetupComplete] = useState(false);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [keyboardMapping, setKeyboardMapping] = useState(null);

  const handleFolderSelected = (folderPath, videos) => {
    setSourceFolder(folderPath);
    setVideoFiles(videos);
    setError('');
    setSuccess(`Found ${videos.length} video files in ${folderPath}`);

    // If we already have destination folders set, use them
    // Otherwise, use the default sorting patterns
    if (Object.keys(destinationFolders).length === 0) {
      setDestinationFolders(defaultSortingPatterns);
    }
  };

  const handleFoldersSet = (folders) => {
    setDestinationFolders(folders);
    setError('');
    setSuccess('Destination folders saved successfully');
  };

  const handleKeyboardMappingSelected = (mapping) => {
    setKeyboardMapping(mapping);
    setError('');
    setSuccess('Keyboard mapping updated successfully');
  };

  const handleSetupComplete = () => {
    if (!sourceFolder) {
      setError('Please select a source folder');
      return;
    }
    if (Object.keys(destinationFolders).length === 0) {
      setError('Please configure destination folders');
      return;
    }
    if (!keyboardMapping) {
      setError('Please select a keyboard mapping');
      return;
    }
    setSetupComplete(true);
  };

  const handleOperationComplete = () => {
    setSuccess('Operation completed successfully');

    // Move to the next video
    if (currentVideoIndex < videoFiles.length - 1) {
      setCurrentVideoIndex(currentVideoIndex + 1);
    } else {
      setSuccess('All videos processed!');
    }
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setSuccess('');
  };

  const handleUndo = async () => {
    try {
      const result = await undoOperation();
      if (result) {
        setSuccess('Operation undone successfully');
        // Refresh the video list if needed
      } else {
        setSuccess('No operations to undo');
      }
    } catch (error) {
      setError(`Error undoing operation: ${error.message}`);
    }
  };

  const currentVideo = videoFiles[currentVideoIndex];

  return (
    <div className="App">
      <Navbar bg="dark" variant="dark" className="app-header">
        <Container>
          <Navbar.Brand className="app-title">Video Sorting GUI</Navbar.Brand>
        </Container>
      </Navbar>

      <Container className="mt-4">
        {error && (
          <Alert variant="danger" onClose={() => setError('')} dismissible>
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success" onClose={() => setSuccess('')} dismissible>
            {success}
          </Alert>
        )}

        {!setupComplete ? (
          <>
            <Row>
              <Col md={6}>
                <FolderSelector onFolderSelected={handleFolderSelected} />
              </Col>
              <Col md={6}>
                <DestinationFolders onFoldersSet={handleFoldersSet} />
              </Col>
            </Row>
            <Row className="mt-3">
              <Col md={12}>
                <KeyboardMappingSelector onMappingSelected={handleKeyboardMappingSelected} />
              </Col>
            </Row>
            <Row className="mt-3">
              <Col className="text-center">
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={handleSetupComplete}
                  disabled={!sourceFolder || Object.keys(destinationFolders).length === 0 || !keyboardMapping}
                >
                  Start Sorting
                </Button>
              </Col>
            </Row>
          </>
        ) : (
          <div>
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h2>Sorting Videos</h2>
              <Button variant="outline-secondary" onClick={handleUndo}>
                <FaUndo className="me-1" /> Undo Last Operation
              </Button>
            </div>

            <div className="mb-3">
              <strong>Source Folder:</strong> {sourceFolder}
            </div>

            <div className="mb-3">
              <strong>Progress:</strong> {currentVideoIndex + 1} of {videoFiles.length} videos
            </div>

            {currentVideo && (
              <VideoCard
                video={currentVideo}
                destinationFolders={destinationFolders}
                onOperationComplete={handleOperationComplete}
                onError={handleError}
                keyboardMapping={keyboardMapping}
              />
            )}
          </div>
        )}
      </Container>

      <footer className="app-footer">
        <Container>
          <p>Video Sorting GUI - A tool for sorting and organizing video files</p>
        </Container>
      </footer>
    </div>
  );
}

export default App;
