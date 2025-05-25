import React, { useState, useEffect } from 'react';
import { Card, Button, ButtonGroup, ProgressBar, Row, Col, Image } from 'react-bootstrap';
import { getVideoScreenshots, moveFile, skipFile, prependHyphen, getOperationProgress } from '../api/api';
import { FaFolder, FaForward, FaUndo, FaMinus } from 'react-icons/fa';

const VideoCard = ({ video, destinationFolders, onOperationComplete, onError }) => {
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [screenshotsLoading, setScreenshotsLoading] = useState(true);
  const [operationId, setOperationId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [operationStatus, setOperationStatus] = useState(null);

  // Load screenshots when component mounts
  useEffect(() => {
    const loadScreenshots = async () => {
      try {
        setScreenshotsLoading(true);
        const result = await getVideoScreenshots(video.path);
        if (result && result.screenshot_paths) {
          setScreenshots(result.screenshot_paths);
        }
      } catch (error) {
        console.error('Error loading screenshots:', error);
        onError && onError(`Error loading screenshots: ${error.message}`);
      } finally {
        setScreenshotsLoading(false);
      }
    };

    loadScreenshots();
  }, [video.path, onError]);

  // Poll for progress updates when an operation is in progress
  useEffect(() => {
    let interval;
    
    if (operationId) {
      interval = setInterval(async () => {
        try {
          const progressData = await getOperationProgress(operationId);
          if (progressData) {
            setProgress(progressData.progress * 100);
            setOperationStatus(progressData.status);
            
            if (progressData.status === 'completed' || progressData.status === 'failed') {
              clearInterval(interval);
              setLoading(false);
              
              if (progressData.status === 'completed') {
                onOperationComplete && onOperationComplete();
              } else {
                onError && onError(progressData.message || 'Operation failed');
              }
            }
          }
        } catch (error) {
          console.error('Error fetching progress:', error);
          clearInterval(interval);
          setLoading(false);
          onError && onError(`Error tracking progress: ${error.message}`);
        }
      }, 500);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [operationId, onOperationComplete, onError]);

  const handleMoveToFolder = async (destinationPath) => {
    try {
      setLoading(true);
      const result = await moveFile(video.path, destinationPath);
      if (result && result.operation) {
        // Extract operation ID from the result if available
        const opId = result.operation.operation_id || 'unknown';
        setOperationId(opId);
      } else {
        setLoading(false);
        onOperationComplete && onOperationComplete();
      }
    } catch (error) {
      console.error('Error moving file:', error);
      setLoading(false);
      onError && onError(`Error moving file: ${error.message}`);
    }
  };

  const handleSkip = async () => {
    try {
      setLoading(true);
      await skipFile(video.path);
      setLoading(false);
      onOperationComplete && onOperationComplete();
    } catch (error) {
      console.error('Error skipping file:', error);
      setLoading(false);
      onError && onError(`Error skipping file: ${error.message}`);
    }
  };

  const handlePrependHyphen = async () => {
    try {
      setLoading(true);
      await prependHyphen(video.path);
      setLoading(false);
      onOperationComplete && onOperationComplete();
    } catch (error) {
      console.error('Error prepending hyphen:', error);
      setLoading(false);
      onError && onError(`Error prepending hyphen: ${error.message}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="video-card">
      <Card.Body>
        <Card.Title>{video.name}{video.extension}</Card.Title>
        <Card.Subtitle className="mb-2 text-muted">
          {formatFileSize(video.size)}
        </Card.Subtitle>
        
        {/* Screenshots */}
        <div className="screenshots-container">
          {screenshotsLoading ? (
            <div className="text-center w-100 py-4">Loading screenshots...</div>
          ) : screenshots.length > 0 ? (
            screenshots.map((screenshot, index) => (
              <Image 
                key={index}
                src={`/static/${screenshot.split('/').pop()}`}
                alt={`Screenshot ${index + 1}`}
                className="screenshot"
                thumbnail
              />
            ))
          ) : (
            <div className="text-center w-100 py-4">No screenshots available</div>
          )}
        </div>
        
        {/* Progress bar */}
        {loading && (
          <div className="progress-container">
            <ProgressBar 
              now={progress} 
              label={`${Math.round(progress)}%`} 
              variant={operationStatus === 'failed' ? 'danger' : 'primary'} 
            />
          </div>
        )}
        
        {/* Action buttons */}
        <div className="action-buttons">
          <Row>
            <Col>
              <ButtonGroup className="me-2">
                {Object.entries(destinationFolders).map(([shorthand, path]) => (
                  <Button
                    key={shorthand}
                    variant="outline-primary"
                    onClick={() => handleMoveToFolder(path + '/' + video.name + video.extension)}
                    disabled={loading}
                  >
                    <FaFolder className="me-1" />
                    {shorthand}
                  </Button>
                ))}
              </ButtonGroup>
            </Col>
            <Col xs="auto">
              <ButtonGroup>
                <Button
                  variant="outline-secondary"
                  onClick={handleSkip}
                  disabled={loading}
                  title="Skip this file"
                >
                  <FaForward />
                </Button>
                <Button
                  variant="outline-secondary"
                  onClick={handlePrependHyphen}
                  disabled={loading}
                  title="Prepend hyphen to filename"
                >
                  <FaMinus />
                </Button>
              </ButtonGroup>
            </Col>
          </Row>
        </div>
      </Card.Body>
    </Card>
  );
};

export default VideoCard;