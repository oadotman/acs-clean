/**
 * Shared Workflow Adapter
 * This component wraps existing tools to make them compatible with the shared workflow system
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Visibility as ViewResultsIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ToolIntegration } from '../../services/sharedWorkflowService';
import toast from 'react-hot-toast';

const SharedWorkflowAdapter = ({ 
  children, 
  toolName, 
  toolDisplayName,
  onResultSubmit,
  showProjectHeader = true 
}) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const projectId = searchParams.get('project');
  const isWorkflowMode = !!projectId;

  useEffect(() => {
    if (isWorkflowMode) {
      loadProjectData();
    }
  }, [projectId]);

  const loadProjectData = async () => {
    try {
      setLoading(true);
      const projectData = await ToolIntegration.getProjectAdCopy(projectId);
      setProject(projectData);
    } catch (error) {
      console.error('Failed to load project data:', error);
      setError(error);
      toast.error('Failed to load project data');
    } finally {
      setLoading(false);
    }
  };

  const handleResultSubmit = async (result) => {
    if (!isWorkflowMode) {
      // Standard mode - just call the original handler
      if (onResultSubmit) {
        onResultSubmit(result);
      }
      return;
    }

    try {
      // Workflow mode - submit result to shared system
      let submitResult;
      
      switch (toolName) {
        case 'compliance':
          submitResult = await ToolIntegration.submitComplianceResult(projectId, result);
          break;
        case 'legal':
          submitResult = await ToolIntegration.submitLegalResult(projectId, result);
          break;
        case 'brand_voice':
          submitResult = await ToolIntegration.submitBrandVoiceResult(projectId, result);
          break;
        case 'psychology':
          submitResult = await ToolIntegration.submitPsychologyResult(projectId, result);
          break;
        default:
          throw new Error(`Unknown tool: ${toolName}`);
      }

      toast.success('Results saved to project!');
      
      if (onResultSubmit) {
        onResultSubmit(result);
      }
      
      // Optionally navigate to unified results
      const shouldNavigateToResults = window.confirm(
        'Results saved! Would you like to view all project results now?'
      );
      
      if (shouldNavigateToResults) {
        navigate(`/project/${projectId}/results`);
      }
      
    } catch (error) {
      console.error('Failed to submit results:', error);
      toast.error('Failed to save results to project');
      
      // Still call the original handler as fallback
      if (onResultSubmit) {
        onResultSubmit(result);
      }
    }
  };

  const handleBackToProject = () => {
    navigate(`/project/${projectId}/results`);
  };

  const handleEditProject = () => {
    navigate(`/project/${projectId}/workspace`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading project data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        Failed to load project data: {error.message}
        <Button onClick={() => navigate('/projects')} sx={{ ml: 2 }}>
          Back to Projects
        </Button>
      </Alert>
    );
  }

  return (
    <Box>
      {/* Project Header (only shown in workflow mode) */}
      {isWorkflowMode && showProjectHeader && project && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'primary.50' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  🚀 Project Workflow Mode
                </Typography>
                <Chip label="Shared Analysis" color="primary" size="small" />
              </Box>
              <Typography variant="body2" color="textSecondary">
                Running {toolDisplayName} on project ad copy. Results will be saved automatically.
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<EditIcon />}
                onClick={handleEditProject}
              >
                Edit Project
              </Button>
              <Button
                variant="outlined"
                size="small"
                startIcon={<ViewResultsIcon />}
                onClick={handleBackToProject}
              >
                View All Results
              </Button>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Project Ad Copy Display */}
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
                Ad Copy Being Analyzed:
              </Typography>
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  Headline: <span style={{ fontWeight: 400 }}>{project.headline}</span>
                </Typography>
              </Box>
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  Body: <span style={{ fontWeight: 400 }}>{project.body_text}</span>
                </Typography>
              </Box>
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  CTA: <span style={{ fontWeight: 400 }}>{project.cta}</span>
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip label={project.platform} size="small" variant="outlined" />
                {project.industry && (
                  <Chip label={project.industry} size="small" variant="outlined" />
                )}
              </Box>
            </CardContent>
          </Card>
        </Paper>
      )}

      {/* Workflow Mode Alert for Standalone Tool Usage */}
      {!isWorkflowMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>💡 Tip:</strong> Use the new{' '}
            <Button 
              size="small" 
              onClick={() => navigate('/project/new/workspace')}
              sx={{ mx: 0.5, minWidth: 'auto', p: 0, textDecoration: 'underline' }}
            >
              Project Workflow
            </Button>
            {' '}to analyze your ad copy with multiple tools automatically, without re-entering content.
          </Typography>
        </Alert>
      )}

      {/* Original Tool Content */}
      {React.cloneElement(children, {
        onSubmit: handleResultSubmit,
        initialData: isWorkflowMode ? project : undefined,
        workflowMode: isWorkflowMode,
        projectId: projectId
      })}
    </Box>
  );
};

export default SharedWorkflowAdapter;
