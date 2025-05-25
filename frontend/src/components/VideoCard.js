import React, { useState, useEffect } from 'react';
import { Card, Button, ButtonGroup, Row, Col, Image } from 'react-bootstrap';
import { getVideoScreenshots, moveFile, skipFile, prependHyphen } from '../api/api';
import { FaFolder, FaForward, FaUndo, FaMinus } from 'react-icons/fa';

const VideoCard = ({ video, destinationFolders, onOperationComplete, onError }) => {
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [screenshotsLoading, setScreenshotsLoading] = useState(true);
  const [prependHyphenBeforeMove, setPrependHyphenBeforeMove] = useState(false);

  // Load screenshots when component mounts
  useEffect(() => {
    const loadScreenshots = async () => {
      try {
        setScreenshotsLoading(true);
        const result = await getVideoScreenshots(video.path);
        if (result && result.screenshot_images) {
          setScreenshots(result.screenshot_images);
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


  const handleMoveToFolder = async (destinationPath) => {
    try {
      setLoading(true);
      await moveFile(video.path, destinationPath, prependHyphenBeforeMove);
      setLoading(false);
      onOperationComplete && onOperationComplete();
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
                src={`data:image/jpeg;base64,${screenshot}`}
                alt={`Screenshot ${index + 1}`}
                className="screenshot"
                thumbnail
              />
            ))
          ) : (
            <div className="text-center w-100 py-4">No screenshots available</div>
          )}
        </div>


        {/* Action buttons */}
        <div className="action-buttons">
          <div className="mb-3">
            <div className="d-flex align-items-center mb-2">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="prependHyphenCheck"
                  checked={prependHyphenBeforeMove}
                  onChange={(e) => setPrependHyphenBeforeMove(e.target.checked)}
                  disabled={loading}
                />
                <label className="form-check-label" htmlFor="prependHyphenCheck">
                  Prepend hyphen before moving
                </label>
              </div>
            </div>
            <div className="destination-buttons">
              {Object.entries(destinationFolders).map(([shorthand, path]) => (
                <Button
                  key={shorthand}
                  variant="outline-primary"
                  className="m-1"
                  onClick={() => handleMoveToFolder(path + '/' + video.name + video.extension)}
                  disabled={loading}
                >
                  <FaFolder className="me-1" />
                  {shorthand}
                </Button>
              ))}
            </div>
          </div>
          <div className="d-flex justify-content-end">
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
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default VideoCard;
