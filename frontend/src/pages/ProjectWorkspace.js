import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  Card,
  CardContent,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Save as SaveIcon,
  Settings as SettingsIcon,
  Visibility as PreviewIcon,
  Share as ShareIcon,
  ContentCopy as CopyIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import StartIcon from '../components/icons/StartIcon';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import sharedWorkflowService from '../services/sharedWorkflowService';
import CopyInputForm from '../components/shared/CopyInputForm';
import { ErrorMessage } from '../components/ui';
import AnalysisToolsSelector from '../components/shared/AnalysisToolsSelector';
import { DEFAULT_ENABLED_TOOLS } from '../constants/analysisTools';
import { useSettings } from '../contexts/SettingsContext';

const ProjectWorkspace = () => {
  const navigate = useNavigate();
  const { projectId } = useParams(); // For editing existing projects
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [project, setProject] = useState(null);
  const { showAdvancedSettings } = useSettings();

  const { control, handleSubmit, formState: { errors }, watch, setValue, reset } = useForm({
    defaultValues: {
      projectName: '',
      description: '',
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: '',
      target_audience: '',
      enabledTools: DEFAULT_ENABLED_TOOLS,
      autoAnalyze: true,
      tags: [],
      customTag: ''
    }
  });

  const watchedTools = watch('enabledTools');
  const watchedAutoAnalyze = watch('autoAnalyze');

  // Load existing project if editing
  useEffect(() => {
    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const projectData = await sharedWorkflowService.getProject(projectId);
      setProject(projectData);
      
      // Populate form with existing data
      reset({
        projectName: projectData.project_name,
        description: projectData.description || '',
        headline: projectData.headline,
        body_text: projectData.body_text,
        cta: projectData.cta,
        platform: projectData.platform,
        industry: projectData.industry || '',
        target_audience: projectData.target_audience || '',
        enabledTools: projectData.enabled_tools || DEFAULT_ENABLED_TOOLS,
        autoAnalyze: projectData.auto_chain_analysis ?? true,
        tags: projectData.tags || []
      });
    } catch (error) {
      console.error('Failed to load project:', error);
      setError(error);
      toast.error('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data, action = 'save') => {
    const isAnalyzing = action === 'analyze';
    setLoading(isAnalyzing);
    setSaving(!isAnalyzing);
    setError(null);
    
    try {
      const projectData = {
        projectName: data.projectName || 'Untitled Project',
        description: data.description,
        headline: data.headline,
        bodyText: data.body_text,
        cta: data.cta,
        platform: data.platform,
        industry: data.industry,
        targetAudience: data.target_audience,
        enabledTools: data.enabledTools,
        autoAnalyze: isAnalyzing ? true : data.autoAnalyze,
        tags: data.tags
      };

      let response;
      
      if (projectId) {
        // Update existing project
        response = await sharedWorkflowService.updateProject(projectId, projectData);
        if (isAnalyzing) {
          await sharedWorkflowService.startAnalysis(projectId, data.enabledTools, true);
        }
        toast.success(isAnalyzing ? 'Analysis started!' : 'Project updated!');
      } else {
        // Create new project
        response = await sharedWorkflowService.createProject({
          ...projectData,
          autoAnalyze: isAnalyzing
        });
        toast.success(isAnalyzing ? 'Project created and analysis started!' : 'Project saved!');
      }

      const resultProjectId = response.project_id || response.id;
      
      if (isAnalyzing) {
        // Navigate to unified results dashboard
        navigate(`/project/${resultProjectId}/results`);
      } else if (!projectId) {
        // Navigate to the new project workspace
        navigate(`/project/${resultProjectId}/workspace`);
      }
    } catch (error) {
      console.error('Project operation failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Operation failed';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setLoading(false);
      setSaving(false);
    }
  };

  const handleSave = (data) => onSubmit(data, 'save');
  const handleSaveAndAnalyze = (data) => onSubmit(data, 'analyze');

  const addTag = () => {
    const customTag = watch('customTag');
    if (customTag && !watch('tags').includes(customTag)) {
      const currentTags = watch('tags');
      setValue('tags', [...currentTags, customTag]);
      setValue('customTag', '');
    }
  };

  const removeTag = (tagToRemove) => {
    const currentTags = watch('tags');
    setValue('tags', currentTags.filter(tag => tag !== tagToRemove));
  };

  // availableTools moved to constants/analysisTools.js

  if (loading && !project) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress size={48} sx={{ mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Loading project...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header Section */}
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          mb: 3,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography 
          variant="h3" 
          gutterBottom 
          sx={{ 
            fontWeight: 800,
            mb: 2,
            letterSpacing: '-0.02em'
          }}
        >
          🚀 {projectId ? 'Edit Project' : 'Create Ad Copy Project'}
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            opacity: 0.9,
            fontWeight: 400,
            maxWidth: 800,
            mx: 'auto'
          }}
        >
          {projectId 
            ? 'Update your ad copy and rerun analysis tools to get fresh insights'
            : 'Create your ad copy once and run it through all analysis tools automatically. No more copying and pasting!'
          }
        </Typography>
      </Paper>

      {/* Info Alert */}
      {!projectId && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>How it works:</strong> Enter your ad copy below, select which analysis tools to run, 
            and we'll process it through all selected tools automatically. You can view all results 
            in a unified dashboard without re-entering your copy.
          </Typography>
        </Alert>
      )}

      <form onSubmit={handleSubmit(handleSave)}>
        <Grid container spacing={4}>
          {/* Project Metadata */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                📋 Project Information
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Controller
                    name="projectName"
                    control={control}
                    rules={{ required: 'Project name is required' }}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Project Name"
                        fullWidth
                        required
                        error={!!errors.projectName}
                        helperText={errors.projectName?.message || "Give your project a memorable name"}
                        placeholder="e.g., Q4 Health Supplement Campaign"
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {project && (
                      <>
                        <Tooltip title="Share Project">
                          <IconButton color="primary">
                            <ShareIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Duplicate Project">
                          <IconButton color="primary">
                            <CopyIcon />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <Controller
                    name="description"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Description (Optional)"
                        fullWidth
                        multiline
                        rows={2}
                        placeholder="Brief description of this campaign or project goals..."
                      />
                    )}
                  />
                </Grid>

                {/* Tags */}
                <Grid item xs={12}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                      Tags (Optional)
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                      {watch('tags').map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          onDelete={() => removeTag(tag)}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                      <Controller
                        name="customTag"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Add tag"
                            size="small"
                            sx={{ minWidth: 200 }}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault();
                                addTag();
                              }
                            }}
                          />
                        )}
                      />
                      <Button onClick={addTag} variant="outlined" size="small">
                        Add
                      </Button>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Ad Copy Content */}
          <Grid item xs={12}>
            <CopyInputForm
              control={control}
              errors={errors}
              title="📝 Ad Copy Content"
              subtitle="This content will be analyzed by all selected tools automatically"
            />
          </Grid>

          {/* Analysis Tools Configuration */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <AnalysisToolsSelector
                watch={watch}
                setValue={setValue}
                subtitle="Select which analysis tools to run on your ad copy. All selected tools will process your content automatically."
              />
            </Paper>
          </Grid>

          {/* Action Buttons */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                <Button
                  type="submit"
                  variant="outlined"
                  size="large"
                  disabled={saving || loading}
                  startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                  sx={{ minWidth: 180 }}
                >
                  {saving ? 'Saving...' : (projectId ? 'Update Project' : 'Save Project')}
                </Button>

                <Button
                  onClick={handleSubmit(handleSaveAndAnalyze)}
                  variant="contained"
                  size="large"
                  disabled={loading || saving || watchedTools.length === 0}
                  startIcon={loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : <StartIcon />}
                  sx={{ 
                    minWidth: 220,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                    }
                  }}
                >
                  {loading ? 'Starting Analysis...' : 'Save & Analyze Now'}
                </Button>

                {project && (
                  <Button
                    onClick={() => navigate(`/project/${projectId}/results`)}
                    variant="outlined"
                    size="large"
                    startIcon={<PreviewIcon />}
                    sx={{ minWidth: 180 }}
                  >
                    View Results
                  </Button>
                )}
              </Box>

              {watchedTools.length === 0 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Please select at least one analysis tool to proceed.
                </Alert>
              )}
            </Paper>
          </Grid>
        </Grid>
      </form>

      {/* Error Display */}
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage
            variant="inline"
            title="Operation Failed"
            message={error.message}
            error={error}
            onRetry={() => setError(null)}
            showActions={false}
          />
        </Box>
      )}
    </Container>
  );
};

export default ProjectWorkspace;
