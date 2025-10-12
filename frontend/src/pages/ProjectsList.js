import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Box,
  Chip,
  Avatar,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
  Alert,
  Stack,
  Divider,
  CircularProgress,
  Skeleton
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Article as DraftIcon,
  Folder as FolderIcon
} from '@mui/icons-material';
import StartIcon from '../components/icons/StartIcon';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import { 
  useProjects,
  useDeleteProject,
  useRunAnalysis,
  useProjectSearch,
  useRefreshProjects 
} from '../hooks/useProjects';
import { useDebounce } from '../hooks/useDebounce';
import toast from 'react-hot-toast';

const ProjectCard = ({ project, onEdit, onDelete, onRunAnalysis, isDeleting = false, isRunningAnalysis = false }) => {
  const [menuAnchor, setMenuAnchor] = useState(null);
  const navigate = useNavigate();

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: 'success.main', fontSize: '1.2rem' }} />;
      case 'analyzing':
        return <ScheduleIcon sx={{ color: 'primary.main', fontSize: '1.2rem' }} />;
      case 'draft':
        return <DraftIcon sx={{ color: 'warning.main', fontSize: '1.2rem' }} />;
      default:
        return <FolderIcon sx={{ color: 'info.main', fontSize: '1.2rem' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'analyzing': return 'primary';
      case 'draft': return 'warning';
      default: return 'info';
    }
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        }
      }}
      onClick={() => navigate(`/project/${project.id}/results`)}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1} flex={1}>
            {getStatusIcon(project.status)}
            <Typography variant="h6" fontWeight={600} noWrap>
              {project.name}
            </Typography>
          </Box>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setMenuAnchor(e.currentTarget);
            }}
          >
            <MoreVertIcon />
          </IconButton>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
          {project.description || 'No description provided'}
        </Typography>

        <Box display="flex" gap={1} mb={2} flexWrap="wrap">
          <Chip 
            label={project.status} 
            color={getStatusColor(project.status)} 
            size="small"
            variant="outlined"
          />
          <Chip 
            label={project.platform} 
            size="small" 
            variant="outlined"
          />
          <Chip 
            label={`${project.toolsCount} tools`}
            size="small"
            variant="outlined"
            color="primary"
          />
        </Box>

        {project.progress !== undefined && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
              <Typography variant="caption" color="text.secondary">
                Analysis Progress
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {project.progress}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={project.progress} 
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>
        )}

        <Box display="flex" gap={1} mt={2}>
          <Button
            size="small"
            variant="outlined"
            startIcon={<ViewIcon />}
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/project/${project.id}/results`);
            }}
          >
            View
          </Button>
          <Button
            size="small"
            variant="contained"
            startIcon={isRunningAnalysis ? <CircularProgress size={16} /> : <StartIcon />}
            onClick={(e) => {
              e.stopPropagation();
              onRunAnalysis(project);
            }}
            disabled={project.status === 'analyzing' || isRunningAnalysis}
          >
            {isRunningAnalysis ? 'Starting...' : project.status === 'analyzing' ? 'Running...' : 'Analyze'}
          </Button>
        </Box>

        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={() => setMenuAnchor(null)}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem onClick={() => { onEdit(project); setMenuAnchor(null); }}>
            <EditIcon sx={{ mr: 1 }} fontSize="small" />
            Edit Project
          </MenuItem>
          <MenuItem onClick={() => { navigate(`/project/${project.id}/results`); setMenuAnchor(null); }}>
            <ViewIcon sx={{ mr: 1 }} fontSize="small" />
            View Results
          </MenuItem>
          <MenuItem 
            onClick={() => { onRunAnalysis(project); setMenuAnchor(null); }}
            disabled={project.status === 'analyzing'}
          >
            <StartIcon sx={{ mr: 1 }} fontSize="small" />
            Run Analysis
          </MenuItem>
          <Divider />
          <MenuItem 
            onClick={() => { onDelete(project); setMenuAnchor(null); }} 
            sx={{ color: 'error.main' }}
            disabled={isDeleting}
          >
            {isDeleting ? <CircularProgress size={16} sx={{ mr: 1 }} /> : <DeleteIcon sx={{ mr: 1 }} fontSize="small" />}
            {isDeleting ? 'Deleting...' : 'Delete Project'}
          </MenuItem>
        </Menu>
      </CardContent>
    </Card>
  );
};

const ProjectsList = () => {
  const { user, subscription } = useAuth();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Debounce search term to avoid too many API calls
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  
  // Fetch projects based on search and filter
  const { 
    data: projects = [], 
    isLoading, 
    error, 
    refetch 
  } = useProjectSearch(debouncedSearchTerm, statusFilter, {
    enabled: !!user?.id
  });
  
  // Mutation hooks
  const deleteProjectMutation = useDeleteProject();
  const runAnalysisMutation = useRunAnalysis();
  const refreshProjects = useRefreshProjects();

  // Calculate status counts from current projects
  const statusCounts = {
    all: projects.length,
    completed: projects.filter(p => p.status === 'completed').length,
    analyzing: projects.filter(p => p.status === 'analyzing').length,
    draft: projects.filter(p => p.status === 'draft').length
  };

  const handleEdit = (project) => {
    navigate(`/project/${project.id}/workspace`);
  };

  const handleDelete = async (project) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${project.name}"? This action cannot be undone.`
    );
    
    if (confirmed) {
      try {
        await deleteProjectMutation.mutateAsync(project.id);
        toast.success(`Project "${project.name}" deleted successfully`);
      } catch (error) {
        console.error('Error deleting project:', error);
        toast.error('Failed to delete project');
      }
    }
  };

  const handleRunAnalysis = async (project) => {
    try {
      await runAnalysisMutation.mutateAsync(project.id);
      toast.success(`Analysis started for "${project.name}"`);
      // Optionally navigate to results page
      // navigate(`/project/${project.id}/results`);
    } catch (error) {
      console.error('Error running analysis:', error);
      toast.error('Failed to start analysis');
    }
  };

  const handleRefresh = () => {
    refreshProjects();
  };

  const handleTabChange = (event, newValue) => {
    setStatusFilter(newValue);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            📁 All Projects
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your ad copy analysis projects and track their progress
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
          component={RouterLink}
          to="/project/new/workspace"
          sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
            }
          }}
        >
          Create New Project
        </Button>
      </Box>

      {/* Search and Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <TextField
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 300, flex: 1 }}
          />
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => alert('Advanced filters coming soon!')}
          >
            More Filters
          </Button>
        </Box>

        {/* Status Tabs */}
        <Tabs 
          value={statusFilter} 
          onChange={handleTabChange} 
          sx={{ mt: 2, borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            label={`All (${statusCounts.all})`} 
            value="all" 
          />
          <Tab 
            label={`Completed (${statusCounts.completed})`} 
            value="completed" 
          />
          <Tab 
            label={`Analyzing (${statusCounts.analyzing})`} 
            value="analyzing" 
          />
          <Tab 
            label={`Draft (${statusCounts.draft})`} 
            value="draft" 
          />
        </Tabs>
      </Paper>

      {/* Error state */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Failed to load projects
          </Typography>
          <Typography variant="body2">
            {error.message || 'Something went wrong. Please try again.'}
          </Typography>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={handleRefresh}
            sx={{ mt: 1 }}
          >
            Retry
          </Button>
        </Alert>
      )}

      {/* Projects Grid */}
      {isLoading ? (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box display="flex" alignItems="center" gap={1} flex={1}>
                      <Skeleton variant="circular" width={24} height={24} />
                      <Skeleton variant="text" width={150} height={28} />
                    </Box>
                    <Skeleton variant="circular" width={24} height={24} />
                  </Box>
                  <Skeleton variant="text" width="100%" height={20} sx={{ mb: 1 }} />
                  <Skeleton variant="text" width="80%" height={20} sx={{ mb: 2 }} />
                  <Box display="flex" gap={1} mb={2}>
                    <Skeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 1 }} />
                    <Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 1 }} />
                    <Skeleton variant="rectangular" width={50} height={24} sx={{ borderRadius: 1 }} />
                  </Box>
                  <Skeleton variant="rectangular" width="100%" height={6} sx={{ borderRadius: 3, mb: 2 }} />
                  <Box display="flex" gap={1}>
                    <Skeleton variant="rectangular" width={70} height={32} sx={{ borderRadius: 1 }} />
                    <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : projects.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <FolderIcon sx={{ fontSize: 64, color: 'grey.300', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            {searchTerm || statusFilter !== 'all' ? 'No projects match your criteria' : 'No projects found'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {searchTerm || statusFilter !== 'all'
              ? 'Try adjusting your search terms or filters'
              : 'Create your first project to get started with ad copy analysis'
            }
          </Typography>
          {!searchTerm && statusFilter === 'all' && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              component={RouterLink}
              to="/project/new/workspace"
              size="large"
            >
              Create Your First Project
            </Button>
          )}
        </Paper>
      ) : (
        <>
          <Grid container spacing={3}>
            {projects.map((project) => (
              <Grid item xs={12} sm={6} md={4} key={project.id}>
                <ProjectCard
                  project={project}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onRunAnalysis={handleRunAnalysis}
                  isDeleting={deleteProjectMutation.isLoading && deleteProjectMutation.variables === project.id}
                  isRunningAnalysis={runAnalysisMutation.isLoading && runAnalysisMutation.variables === project.id}
                />
              </Grid>
            ))}
          </Grid>

          {/* Summary Stats */}
          <Paper sx={{ p: 3, mt: 4 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              📊 Project Summary
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="primary.main">
                    {projects.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Projects
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="success.main">
                    {statusCounts.completed}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completed
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="primary.main">
                    {statusCounts.analyzing}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    In Progress
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="warning.main">
                    {statusCounts.draft}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Drafts
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </>
      )}

      {/* Tips */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          💡 Pro Tips for Managing Projects
        </Typography>
        <Typography variant="body2">
          • Use descriptive project names to easily identify campaigns later
          • Run analyses regularly to track performance improvements
          • Organize projects by platform or campaign type using tags
        </Typography>
      </Alert>
    </Container>
  );
};

export default ProjectsList;
