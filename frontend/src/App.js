import React, { useState } from 'react';
import { Container, Row, Col, Alert, Button, Navbar } from 'react-bootstrap';
import FolderSelector from './components/FolderSelector';
import DestinationFolders from './components/DestinationFolders';
import VideoCard from './components/VideoCard';
import { undoOperation } from './api/api';
import { FaUndo } from 'react-icons/fa';

function App() {
  const [sourceFolder, setSourceFolder] = useState('');
  const [videoFiles, setVideoFiles] = useState([]);
  const [destinationFolders, setDestinationFolders] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [setupComplete, setSetupComplete] = useState(false);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);

  const handleFolderSelected = (folderPath, videos) => {
    setSourceFolder(folderPath);
    setVideoFiles(videos);
    setError('');
    setSuccess(`Found ${videos.length} video files in ${folderPath}`);
    
    // If we already have destination folders set, we can consider setup complete
    if (Object.keys(destinationFolders).length > 0) {
      setSetupComplete(true);
    }
  };

  const handleFoldersSet = (folders) => {
    setDestinationFolders(folders);
    setError('');
    setSuccess('Destination folders saved successfully');
    
    // If we already have a source folder with videos, we can consider setup complete
    if (videoFiles.length > 0) {
      setSetupComplete(true);
    }
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
          <Row>
            <Col md={6}>
              <FolderSelector onFolderSelected={handleFolderSelected} />
            </Col>
            <Col md={6}>
              <DestinationFolders onFoldersSet={handleFoldersSet} />
            </Col>
          </Row>
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