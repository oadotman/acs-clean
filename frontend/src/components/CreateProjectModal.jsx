import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  CircularProgress,
  alpha
} from '@mui/material';
import {
  Close as CloseIcon,
  Folder as FolderIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useCreateProject, useUpdateProject } from '../hooks/useProjectsNew';

/**
 * CreateProjectModal - Modal for creating or editing projects
 * 
 * Props:
 * - open: boolean - Whether modal is open
 * - onClose: function - Callback when modal closes
 * - project: object (optional) - If provided, modal is in edit mode
 * - onSuccess: function (optional) - Callback when project is successfully created/updated
 */
const CreateProjectModal = ({ open, onClose, project, onSuccess }) => {
  const navigate = useNavigate();
  const isEditMode = !!project;

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    client_name: ''
  });
  const [errors, setErrors] = useState({});

  // Mutations
  const createMutation = useCreateProject();
  const updateMutation = useUpdateProject();

  // Initialize form data when project changes
  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name || '',
        description: project.description || '',
        client_name: project.client_name || ''
      });
    } else {
      setFormData({
        name: '',
        description: '',
        client_name: ''
      });
    }
    setErrors({});
  }, [project, open]);

  const handleChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    // Clear error for this field when user types
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Name is required
    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    } else if (formData.name.trim().length < 3) {
      newErrors.name = 'Project name must be at least 3 characters';
    } else if (formData.name.trim().length > 255) {
      newErrors.name = 'Project name must be less than 255 characters';
    }

    // Description validation (optional but has max length)
    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description must be less than 1000 characters';
    }

    // Client name validation (optional but has max length)
    if (formData.client_name && formData.client_name.length > 255) {
      newErrors.client_name = 'Client name must be less than 255 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      console.log('❌ Form validation failed');
      return;
    }

    console.log('📝 Form validation passed, submitting...');

    try {
      if (isEditMode) {
        console.log('✏️ Updating project:', project.id);
        // Update existing project
        const updatedProject = await updateMutation.mutateAsync({
          projectId: project.id,
          updates: {
            name: formData.name.trim(),
            description: formData.description.trim() || null,
            client_name: formData.client_name.trim() || null
          }
        });
        console.log('✅ Project updated successfully');
        onClose();
      } else {
        console.log('➕ Creating new project with data:', {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          client_name: formData.client_name.trim() || null
        });
        // Create new project
        const newProject = await createMutation.mutateAsync({
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          client_name: formData.client_name.trim() || null
        });
        console.log('✅ Project created, navigating to:', `/projects/${newProject.id}`);
        
        // Call onSuccess if provided (used by NewAnalysis page)
        if (onSuccess && typeof onSuccess === 'function') {
        console.log('🎯 Calling onSuccess callback with project:', newProject);
          onSuccess(newProject);
        }
        
        // Check if we should return to analysis page
        const returnToAnalysis = sessionStorage.getItem('returnToAnalysis');
        if (returnToAnalysis === 'true') {
          console.log('🔙 Returning to analysis page with new project:', newProject.id);
          sessionStorage.setItem('selectedProjectId', newProject.id);
          navigate('/analysis/new');
        } else {
          onClose();
          
          // Only navigate to project detail if not in a selection context (no onSuccess handler)
          if (!onSuccess) {
            navigate(`/projects/${newProject.id}`);
          }
        }
      }
    } catch (error) {
      console.error('💥 Error in handleSubmit:', {
        message: error.message,
        stack: error.stack,
        fullError: error
      });
      // Error toast is already shown by the mutation hook
    }
  };

  const handleClose = () => {
    if (!createMutation.isLoading && !updateMutation.isLoading) {
      onClose();
    }
  };

  const isLoading = createMutation.isLoading || updateMutation.isLoading;
  
  // Debug: Log when modal opens
  React.useEffect(() => {
    if (open) {
      console.log('📝 CreateProjectModal opened, isEditMode:', isEditMode);
    }
  }, [open, isEditMode]);

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      sx={{
        zIndex: 9999 // Ensure it appears on top
      }}
      PaperProps={{
        sx: {
          borderRadius: 3,
          background: 'linear-gradient(135deg, #1A0F2E 0%, #0F0B1D 100%)',
          border: '1px solid',
          borderColor: alpha('#A855F7', 0.2)
        }
      }}
    >
      {/* Title */}
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1.5}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: alpha('#A855F7', 0.1),
                border: '1px solid',
                borderColor: alpha('#A855F7', 0.3)
              }}
            >
              <FolderIcon sx={{ color: 'primary.main', fontSize: 28 }} />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                {isEditMode ? 'Edit Project' : 'Create New Project'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isEditMode ? 'Update project details' : 'Organize your ad analyses'}
              </Typography>
            </Box>
          </Box>
          <IconButton
            onClick={handleClose}
            disabled={isLoading}
            sx={{
              color: 'text.secondary',
              '&:hover': { color: 'text.primary' }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      {/* Content */}
      <DialogContent sx={{ pt: 3 }}>
        <Box component="form" onSubmit={handleSubmit}>
          {/* Project Name */}
          <TextField
            fullWidth
            label="Project Name"
            required
            value={formData.name}
            onChange={handleChange('name')}
            error={!!errors.name}
            helperText={errors.name || 'e.g., Q1 2025 Campaign, Nike Spring Launch'}
            disabled={isLoading}
            autoFocus
            sx={{ mb: 3 }}
          />

          {/* Description */}
          <TextField
            fullWidth
            label="Description (Optional)"
            multiline
            rows={3}
            value={formData.description}
            onChange={handleChange('description')}
            error={!!errors.description}
            helperText={errors.description || 'Brief description of this project'}
            disabled={isLoading}
            sx={{ mb: 3 }}
          />

          {/* Client Name */}
          <TextField
            fullWidth
            label="Client Name (Optional)"
            value={formData.client_name}
            onChange={handleChange('client_name')}
            error={!!errors.client_name}
            helperText={errors.client_name || 'e.g., Nike, Adidas, Acme Inc.'}
            disabled={isLoading}
          />
        </Box>
      </DialogContent>

      {/* Actions */}
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={handleClose}
          disabled={isLoading}
          sx={{
            color: 'text.secondary',
            '&:hover': { bgcolor: alpha('#fff', 0.05) }
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isLoading}
          startIcon={isLoading && <CircularProgress size={16} />}
          sx={{
            background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
            minWidth: 120,
            '&:hover': {
              background: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)',
            },
            '&.Mui-disabled': {
              background: alpha('#A855F7', 0.3),
              color: alpha('#fff', 0.5)
            }
          }}
        >
          {isLoading ? 'Saving...' : isEditMode ? 'Update Project' : 'Create Project'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateProjectModal;
