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
  TextField,
  InputAdornment,
  IconButton,
  Skeleton,
  Chip,
  alpha
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Business as BusinessIcon,
  Schedule as ScheduleIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import CreateProjectModal from '../components/CreateProjectModal';
import {
  useProjectsWithCounts,
  useDeleteProject,
  useSearchProjects
} from '../hooks/useProjectsNew';

// ============================================================================
// ProjectCard Component
// ============================================================================

const ProjectCard = ({ project, onEdit, onDelete }) => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleCardClick = () => {
    navigate(`/projects/${project.id}`);
  };

  const handleMenuClick = (e) => {
    e.stopPropagation();
    setMenuOpen(!menuOpen);
  };

  const handleEdit = (e) => {
    e.stopPropagation();
    setMenuOpen(false);
    onEdit(project);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    setMenuOpen(false);
    onDelete(project);
  };

  return (
    <Card
      onClick={handleCardClick}
      sx={{
        height: '100%',
        cursor: 'pointer',
        position: 'relative',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 20px 60px rgba(168, 85, 247, 0.3)',
        }
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1} flex={1}>
            <FolderIcon sx={{ color: 'primary.main', fontSize: 28 }} />
            <Typography variant="h6" fontWeight={700} noWrap>
              {project.name}
            </Typography>
          </Box>
          
          <Box sx={{ position: 'relative' }}>
            <IconButton
              size="small"
              onClick={handleMenuClick}
              sx={{
                color: 'text.secondary',
                '&:hover': { color: 'primary.main' }
              }}
            >
              <MoreVertIcon />
            </IconButton>
            
            {/* Simple dropdown menu */}
            {menuOpen && (
              <Paper
                sx={{
                  position: 'absolute',
                  right: 0,
                  top: '100%',
                  mt: 0.5,
                  minWidth: 150,
                  zIndex: 10,
                  boxShadow: 4
                }}
              >
                <Box
                  onClick={handleEdit}
                  sx={{
                    p: 1.5,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  <EditIcon fontSize="small" />
                  <Typography variant="body2">Edit</Typography>
                </Box>
                <Box
                  onClick={handleDelete}
                  sx={{
                    p: 1.5,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    color: 'error.main',
                    '&:hover': { bgcolor: alpha('#ef4444', 0.1) }
                  }}
                >
                  <DeleteIcon fontSize="small" />
                  <Typography variant="body2">Delete</Typography>
                </Box>
              </Paper>
            )}
          </Box>
        </Box>

        {/* Description */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            minHeight: 40,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {project.description || 'No description provided'}
        </Typography>

        {/* Client Badge */}
        {project.client_name && (
          <Box mb={2}>
            <Chip
              icon={<BusinessIcon />}
              label={project.client_name}
              size="small"
              sx={{
                backgroundColor: alpha('#A855F7', 0.1),
                color: 'secondary.main',
                border: '1px solid',
                borderColor: alpha('#A855F7', 0.3)
              }}
            />
          </Box>
        )}

        {/* Stats */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Box display="flex" alignItems="center" gap={0.5}>
            <FolderOpenIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {project.analysisCount || 0} {project.analysisCount === 1 ? 'analysis' : 'analyses'}
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={0.5}>
            <ScheduleIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// Loading Skeleton
// ============================================================================

const ProjectCardSkeleton = () => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" mb={2}>
        <Box display="flex" alignItems="center" gap={1} flex={1}>
          <Skeleton variant="circular" width={28} height={28} />
          <Skeleton variant="text" width={150} height={28} />
        </Box>
        <Skeleton variant="circular" width={24} height={24} />
      </Box>
      <Skeleton variant="text" width="100%" height={20} sx={{ mb: 1 }} />
      <Skeleton variant="text" width="80%" height={20} sx={{ mb: 2 }} />
      <Skeleton variant="rectangular" width={100} height={24} sx={{ borderRadius: 1, mb: 2 }} />
      <Box display="flex" justifyContent="space-between">
        <Skeleton variant="text" width={80} height={20} />
        <Skeleton variant="text" width={100} height={20} />
      </Box>
    </CardContent>
  </Card>
);

// ============================================================================
// Main Component
// ============================================================================

const ProjectsListNew = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);

  // Fetch projects with counts
  const { data: projects = [], isLoading, error } = useProjectsWithCounts();
  
  // Check if we should auto-open create modal (from analysis page)
  React.useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('action') === 'create') {
      console.log('🎯 Auto-opening create project modal from URL parameter');
      setCreateModalOpen(true);
      // Clean up the URL
      window.history.replaceState({}, '', '/projects');
    }
  }, [location.search]);
  
  // Delete mutation
  const deleteProjectMutation = useDeleteProject();

  // Filter projects by search term (client-side for now)
  const filteredProjects = projects.filter(project => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      project.name.toLowerCase().includes(searchLower) ||
      project.description?.toLowerCase().includes(searchLower) ||
      project.client_name?.toLowerCase().includes(searchLower)
    );
  });

  const handleCreateProject = () => {
    setEditingProject(null);
    setCreateModalOpen(true);
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setCreateModalOpen(true);
  };

  const handleDeleteProject = async (project) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${project.name}"?\n\nThis will not delete your analyses, just unlink them from this project.`
    );
    
    if (confirmed) {
      try {
        await deleteProjectMutation.mutateAsync(project.id);
      } catch (error) {
        console.error('Error deleting project:', error);
      }
    }
  };

  const handleModalClose = () => {
    setCreateModalOpen(false);
    setEditingProject(null);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography
            variant="h4"
            fontWeight={800}
            gutterBottom
            sx={{
              background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            📁 Projects
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Organize your ad analyses by client, campaign, or category
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
          onClick={handleCreateProject}
          sx={{
            background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
            boxShadow: '0 8px 25px rgba(124, 58, 237, 0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)',
              boxShadow: '0 12px 40px rgba(192, 132, 252, 0.5)',
            }
          }}
        >
          New Project
        </Button>
      </Box>

      {/* Search Bar */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <TextField
          fullWidth
          placeholder="Search projects by name, description, or client..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
            }
          }}
        />
      </Paper>

      {/* Error State */}
      {error && (
        <Paper
          sx={{
            p: 4,
            textAlign: 'center',
            bgcolor: alpha('#ef4444', 0.1),
            border: '1px solid',
            borderColor: alpha('#ef4444', 0.3)
          }}
        >
          <Typography variant="h6" color="error.main" gutterBottom>
            Failed to load projects
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            {error.message || 'Something went wrong. Please try again.'}
          </Typography>
          <Button
            variant="outlined"
            color="error"
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </Paper>
      )}

      {/* Loading State */}
      {isLoading && (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <ProjectCardSkeleton />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Empty State */}
      {!isLoading && !error && filteredProjects.length === 0 && (
        <Paper
          sx={{
            p: 6,
            textAlign: 'center',
            background: 'linear-gradient(135deg, rgba(26, 15, 46, 0.8) 0%, rgba(15, 11, 29, 0.8) 100%)',
            border: '1px solid',
            borderColor: alpha('#A855F7', 0.2)
          }}
        >
          <FolderIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2, opacity: 0.5 }} />
          <Typography variant="h5" fontWeight={700} gutterBottom>
            {searchTerm ? 'No projects match your search' : 'No projects yet'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
            {searchTerm
              ? 'Try adjusting your search terms to find what you\'re looking for'
              : 'Create your first project to organize your ad analyses by client, campaign, or category'
            }
          </Typography>
          {!searchTerm && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              size="large"
              onClick={handleCreateProject}
              sx={{
                background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
              }}
            >
              Create Your First Project
            </Button>
          )}
        </Paper>
      )}

      {/* Projects Grid */}
      {!isLoading && !error && filteredProjects.length > 0 && (
        <>
          <Grid container spacing={3}>
            {filteredProjects.map((project) => (
              <Grid item xs={12} sm={6} md={4} key={project.id}>
                <ProjectCard
                  project={project}
                  onEdit={handleEditProject}
                  onDelete={handleDeleteProject}
                />
              </Grid>
            ))}
          </Grid>

          {/* Summary Stats */}
          <Paper sx={{ p: 3, mt: 4 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              📊 Summary
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography
                    variant="h4"
                    fontWeight={700}
                    sx={{
                      background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text'
                    }}
                  >
                    {projects.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Projects
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography
                    variant="h4"
                    fontWeight={700}
                    sx={{
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text'
                    }}
                  >
                    {projects.reduce((sum, p) => sum + (p.analysisCount || 0), 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Analyses
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography
                    variant="h4"
                    fontWeight={700}
                    sx={{
                      background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text'
                    }}
                  >
                    {Math.round(
                      projects.reduce((sum, p) => sum + (p.analysisCount || 0), 0) / 
                      Math.max(projects.length, 1)
                    )}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg per Project
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography
                    variant="h4"
                    fontWeight={700}
                    sx={{
                      background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text'
                    }}
                  >
                    {projects.filter(p => p.client_name).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    With Clients
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Tips */}
          <Paper
            sx={{
              p: 3,
              mt: 3,
              background: alpha('#A855F7', 0.05),
              border: '1px solid',
              borderColor: alpha('#A855F7', 0.2)
            }}
          >
            <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'primary.main' }}>
              💡 Pro Tips
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Use descriptive project names to easily identify campaigns later<br />
              • Add client names to quickly filter projects by client<br />
              • Click on any project card to view all its analyses and insights
            </Typography>
          </Paper>
        </>
      )}

      {/* Create/Edit Project Modal */}
      <CreateProjectModal
        open={createModalOpen}
        onClose={handleModalClose}
        project={editingProject}
      />
    </Container>
  );
};

export default ProjectsListNew;
