import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions for video sorting operations
export const setSourceFolder = async (folderPath) => {
  try {
    const response = await api.post('/source-folder', { path: folderPath });
    return response.data;
  } catch (error) {
    console.error('Error setting source folder:', error);
    throw error;
  }
};

export const setDestinationFolders = async (foldersMap) => {
  try {
    const response = await api.post('/destination-folders', { folders: foldersMap });
    return response.data;
  } catch (error) {
    console.error('Error setting destination folders:', error);
    throw error;
  }
};

export const moveFile = async (sourcePath, destinationPath, prependHyphenFirst = false) => {
  try {
    const response = await api.post('/move-file', {
      source_path: sourcePath,
      destination_path: destinationPath,
      operation_type: 'move',
      prepend_hyphen_first: prependHyphenFirst,
    });
    return response.data;
  } catch (error) {
    console.error('Error moving file:', error);
    throw error;
  }
};

export const skipFile = async (filePath) => {
  try {
    const response = await api.post('/skip-file', {
      source_path: filePath,
      operation_type: 'skip',
    });
    return response.data;
  } catch (error) {
    console.error('Error skipping file:', error);
    throw error;
  }
};

export const prependHyphen = async (filePath) => {
  try {
    const response = await api.post('/prepend-hyphen', {
      source_path: filePath,
      operation_type: 'rename',
    });
    return response.data;
  } catch (error) {
    console.error('Error prepending hyphen:', error);
    throw error;
  }
};

export const undoOperation = async () => {
  try {
    const response = await api.post('/undo');
    return response.data;
  } catch (error) {
    console.error('Error undoing operation:', error);
    throw error;
  }
};


export const getVideoScreenshots = async (videoPath, numScreenshots = 3) => {
  try {
    const response = await api.post('/screenshots', null, {
      params: {
        video_path: videoPath,
        num_screenshots: numScreenshots,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error getting video screenshots:', error);
    throw error;
  }
};

export const getCommonDirectories = async () => {
  try {
    const response = await api.get('/common-directories');
    return response.data;
  } catch (error) {
    console.error('Error getting common directories:', error);
    throw error;
  }
};

export const openVideoInNativePlayer = async (filePath) => {
  try {
    const response = await api.post('/open-video', null, {
      params: {
        file_path: filePath,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error opening video in native player:', error);
    throw error;
  }
};

export default api;
