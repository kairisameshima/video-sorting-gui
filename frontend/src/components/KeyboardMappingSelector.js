import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Table, Modal, InputGroup } from 'react-bootstrap';
import { defaultKeyboardMappings } from '../keyboardMappings';

const KeyboardMappingSelector = ({ onMappingSelected }) => {
  const [selectedMapping, setSelectedMapping] = useState('default');
  const [customMapping, setCustomMapping] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingMapping, setEditingMapping] = useState(null);
  const [editingKey, setEditingKey] = useState('');
  const [editingAction, setEditingAction] = useState('');

  useEffect(() => {
    // Initialize with default mapping
    const initialMapping = { ...defaultKeyboardMappings[selectedMapping] };
    setCustomMapping(initialMapping);
    onMappingSelected(initialMapping);
  }, []);

  const handleMappingChange = (e) => {
    const newMapping = e.target.value;
    setSelectedMapping(newMapping);
    const mappingConfig = { ...defaultKeyboardMappings[newMapping] };
    setCustomMapping(mappingConfig);
    onMappingSelected(mappingConfig);
  };

  const handleEditMapping = (type, key, action) => {
    setEditingMapping(type);
    setEditingKey(key);
    setEditingAction(action);
    setShowEditModal(true);
  };

  const handleSaveEdit = () => {
    if (!editingKey || !editingAction) return;

    const updatedMapping = { ...customMapping };
    if (editingMapping === 'moveToFolder') {
      updatedMapping.mappings.moveToFolder[editingKey] = editingAction;
    } else {
      updatedMapping.mappings.actions[editingKey] = editingAction;
    }

    setCustomMapping(updatedMapping);
    onMappingSelected(updatedMapping);
    setShowEditModal(false);
  };

  return (
    <Card className="keyboard-mapping-selector mb-3">
      <Card.Body>
        <Card.Title>Keyboard Mapping Configuration</Card.Title>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Select Keyboard Mapping</Form.Label>
            <Form.Select
              value={selectedMapping}
              onChange={handleMappingChange}
            >
              {Object.entries(defaultKeyboardMappings).map(([key, config]) => (
                <option key={key} value={key}>
                  {config.name} - {config.description}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </Form>

        {customMapping && (
          <>
            <h5 className="mt-4">Folder Shortcuts</h5>
            <Table striped bordered hover size="sm">
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Folder</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(customMapping.mappings.moveToFolder).map(([key, folder]) => (
                  <tr key={key}>
                    <td>{key}</td>
                    <td>{folder}</td>
                    <td>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => handleEditMapping('moveToFolder', key, folder)}
                      >
                        Edit
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>

            <h5 className="mt-4">Action Shortcuts</h5>
            <Table striped bordered hover size="sm">
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Action</th>
                  <th>Edit</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(customMapping.mappings.actions).map(([key, action]) => (
                  <tr key={key}>
                    <td>{key}</td>
                    <td>{action}</td>
                    <td>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => handleEditMapping('actions', key, action)}
                      >
                        Edit
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </>
        )}

        <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Edit Keyboard Mapping</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Key</Form.Label>
                <Form.Control
                  type="text"
                  value={editingKey}
                  onChange={(e) => setEditingKey(e.target.value)}
                  placeholder="Enter key (e.g., 'a', 'shift+b')"
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>
                  {editingMapping === 'moveToFolder' ? 'Folder' : 'Action'}
                </Form.Label>
                <Form.Control
                  type="text"
                  value={editingAction}
                  onChange={(e) => setEditingAction(e.target.value)}
                  placeholder={
                    editingMapping === 'moveToFolder'
                      ? "Enter folder name"
                      : "Enter action name"
                  }
                />
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowEditModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveEdit}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      </Card.Body>
    </Card>
  );
};

export default KeyboardMappingSelector; 