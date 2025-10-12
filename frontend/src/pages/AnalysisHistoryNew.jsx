import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Skeleton,
  Alert,
  Select,
  FormControl,
  InputLabel,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  Search as SearchIcon,
  Add,
  History,
  FilterList,
  Folder,
  MoreVert,
  Facebook,
  Instagram,
  LinkedIn,
  Twitter,
  Google,
  MusicNote,
  Assessment,
  CalendarToday,
  Delete,
  AddCircleOutline
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabaseClientClean';
import { useProjectsWithCounts, useAddAnalysisToProject } from '../hooks/useProjectsNew';

// Platform config for icons and colors
const platformConfig = {
  facebook: { icon: Facebook, color: '#1877F2', label: 'Facebook' },
  instagram: { icon: Instagram, color: '#E4405F', label: 'Instagram' },
  google: { icon: Google, color: '#4285F4', label: 'Google Ads' },
  linkedin: { icon: LinkedIn, color: '#0A66C2', label: 'LinkedIn' },
  twitter: { icon: Twitter, color: '#1DA1F2', label: 'Twitter/X' },
  tiktok: { icon: MusicNote, color: '#FF0050', label: 'TikTok' }
};

// Analysis Card Component
const AnalysisCard = ({ analysis, projects, onAddToProject, onDelete }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [projectMenuAnchor, setProjectMenuAnchor] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const platform = platformConfig[analysis.platform?.toLowerCase()] || {
    icon: Analytics,
    color: '#666',
    label: analysis.platform
  };

  const PlatformIcon = platform.icon;

  const handleCardClick = () => {
    // Navigate to analysis results page
    console.log('🔍 Navigating to analysis results:', analysis.id);
    navigate(`/results/${analysis.id}`);
  };

  const handleMenuOpen = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProjectMenuOpen = (event) => {
    event.stopPropagation();
    setProjectMenuAnchor(event.currentTarget);
  };

  const handleProjectMenuClose = () => {
    setProjectMenuAnchor(null);
  };

  const handleAddToProject = (projectId) => {
    onAddToProject(analysis.id, projectId);
    handleProjectMenuClose();
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = () => {
    onDelete(analysis.id);
    setDeleteDialogOpen(false);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  return (
    <Card
      onClick={handleCardClick}
      sx={{
        cursor: 'pointer',
        height: '100%',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4
        }
      }}
    >
      <CardContent>
        {/* Header with platform and menu */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <PlatformIcon sx={{ color: platform.color, fontSize: 24 }} />
            <Typography variant="body2" color="text.secondary">
              {platform.label}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleMenuOpen}>
            <MoreVert />
          </IconButton>
        </Box>

        {/* Project Badge */}
        {analysis.projects && (
          <Box mb={2}>
            <Chip
              icon={<Folder />}
              label={analysis.projects.name}
              size="small"
              variant="outlined"
              sx={{ borderColor: 'primary.main', color: 'primary.main' }}
            />
          </Box>
        )}

        {/* Headline */}
        <Typography
          variant="h6"
          gutterBottom
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            minHeight: '3em'
          }}
        >
          {analysis.headline || 'Untitled Ad'}
        </Typography>

        {/* Body preview */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            mb: 2,
            minHeight: '2.5em'
          }}
        >
          {analysis.body_text}
        </Typography>

        {/* Scores */}
        <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
          <Chip
            label={`Overall: ${analysis.overall_score || 0}/100`}
            size="small"
            color={getScoreColor(analysis.overall_score)}
          />
          {analysis.cta && (
            <Chip
              label={`CTA: ${analysis.cta}`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>

        {/* Date */}
        <Box display="flex" alignItems="center" gap={0.5}>
          <CalendarToday sx={{ fontSize: 14, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            {formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}
          </Typography>
        </Box>

        {/* Dropdown Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => {
            console.log('🔍 Menu: Navigating to analysis results:', analysis.id);
            navigate(`/results/${analysis.id}`);
            handleMenuClose();
          }}>
            <Assessment sx={{ mr: 1, fontSize: 20 }} />
            View Details
          </MenuItem>
          {!analysis.project_id && (
            <MenuItem onClick={handleProjectMenuOpen}>
              <AddCircleOutline sx={{ mr: 1, fontSize: 20 }} />
              Add to Project
            </MenuItem>
          )}
          <MenuItem onClick={handleDeleteClick}>
            <Delete sx={{ mr: 1, fontSize: 20 }} />
            Delete
          </MenuItem>
        </Menu>

        {/* Project Selection Menu */}
        <Menu
          anchorEl={projectMenuAnchor}
          open={Boolean(projectMenuAnchor)}
          onClose={handleProjectMenuClose}
        >
          <MenuItem disabled>
            <Typography variant="body2" fontWeight={600}>
              Select Project
            </Typography>
          </MenuItem>
          {projects?.map(project => (
            <MenuItem
              key={project.id}
              onClick={() => handleAddToProject(project.id)}
            >
              <Folder sx={{ mr: 1, fontSize: 20, color: 'primary.main' }} />
              {project.name}
              {project.client_name && (
                <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                  ({project.client_name})
                </Typography>
              )}
            </MenuItem>
          ))}
        </Menu>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
          <DialogTitle>Delete Analysis</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete this analysis? This action cannot be undone.
              <br /><br />
              <strong>Analysis:</strong> {analysis.headline || 'Untitled Ad'}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel}>Cancel</Button>
            <Button onClick={handleDeleteConfirm} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

// Main Component
const AnalysisHistoryNew = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [projectFilter, setProjectFilter] = useState('all');

  // Fetch analyses
  const { data: analyses = [], isLoading, error } = useQuery({
    queryKey: ['analyses', user?.id],
    queryFn: async () => {
      if (!user?.id) {
      console.log('🔍 History: No user ID available');
        return [];
      }
      
      console.log('📅 History: Fetching analyses for user:', user.id);
      console.log('📅 History: User object details:', {
        id: user.id,
        email: user.email,
        aud: user.aud,
        role: user.role,
        created_at: user.created_at
      });
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .select(`
          *,
          projects (
            id,
            name,
            client_name
          )
        `)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      console.log('📅 History: Query result:', { data, error, count: data?.length });
      
      // Additional debug: Try to count total analyses in table (to test if RLS is the issue)
      try {
        const { count: totalCount } = await supabase
          .from('ad_analyses')
          .select('*', { count: 'exact', head: true });
        console.log('📅 History: Total analyses in database:', totalCount);
      } catch (countError) {
        console.error('📅 History: Error counting total analyses:', countError);
      }

      if (error) {
        console.error('Error fetching analyses:', error);
        throw error;
      }

      return data || [];
    },
    enabled: !!user?.id
  });

  // Fetch projects for filter and add-to-project
  const { data: projects = [] } = useProjectsWithCounts();
  
  // Mutation to add analysis to project
  const addToProjectMutation = useAddAnalysisToProject();
  
  // Mutation to delete analysis
  const deleteAnalysisMutation = useMutation({
    mutationFn: async (analysisId) => {
      const { error } = await supabase
        .from('ad_analyses')
        .delete()
        .eq('id', analysisId)
        .eq('user_id', user?.id); // Extra safety check
      
      if (error) {
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['analyses', user?.id]);
      toast.success('Analysis deleted successfully');
    },
    onError: (error) => {
      console.error('Error deleting analysis:', error);
      toast.error('Failed to delete analysis');
    }
  });

  const handleAddToProject = async (analysisId, projectId) => {
    try {
      await addToProjectMutation.mutateAsync({
        analysisId,
        projectId,
        userId: user?.id
      });
      toast.success('Analysis added to project');
    } catch (error) {
      console.error('Error adding to project:', error);
      toast.error('Failed to add to project');
    }
  };

  const handleDeleteAnalysis = async (analysisId) => {
    try {
      await deleteAnalysisMutation.mutateAsync(analysisId);
    } catch (error) {
      // Error handling is done in the mutation
    }
  };

  // Filter analyses
  const filteredAnalyses = analyses.filter(analysis => {
    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      if (!analysis.headline?.toLowerCase().includes(search) &&
          !analysis.body_text?.toLowerCase().includes(search) &&
          !analysis.cta?.toLowerCase().includes(search)) {
        return false;
      }
    }

    // Platform filter
    if (platformFilter !== 'all' && analysis.platform !== platformFilter) {
      return false;
    }

    // Project filter
    if (projectFilter !== 'all') {
      if (projectFilter === 'unassigned' && analysis.project_id) {
        return false;
      }
      if (projectFilter !== 'unassigned' && analysis.project_id !== projectFilter) {
        return false;
      }
    }

    return true;
  });

  // Debug logging
  console.log('📅 History: Component state:', { 
    isLoading, 
    error: error?.message, 
    analysesCount: analyses?.length,
    filteredCount: filteredAnalyses?.length,
    userID: user?.id,
    hasUser: !!user,
    userEmail: user?.email,
    userObject: user
  });

  // Loading state
  if (isLoading) {
    console.log('📅 History: Rendering loading state');
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Skeleton variant="rectangular" height={250} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load analysis history. Please try again later.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 2 }}>
            <History color="primary" sx={{ fontSize: 40 }} />
            Analysis History
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            component={RouterLink}
            to="/analysis/new"
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            New Analysis
          </Button>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Track and review all your ad copy analyses
        </Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search analyses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Platform</InputLabel>
              <Select
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value)}
                label="Platform"
              >
                <MenuItem value="all">All Platforms</MenuItem>
                {Object.entries(platformConfig).map(([key, config]) => (
                  <MenuItem key={key} value={key}>
                    {config.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Project</InputLabel>
              <Select
                value={projectFilter}
                onChange={(e) => setProjectFilter(e.target.value)}
                label="Project"
              >
                <MenuItem value="all">All Projects</MenuItem>
                <MenuItem value="unassigned">Unassigned</MenuItem>
                {projects.map(project => (
                  <MenuItem key={project.id} value={project.id}>
                    {project.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Typography variant="body2" color="text.secondary">
              {filteredAnalyses.length} {filteredAnalyses.length === 1 ? 'analysis' : 'analyses'}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Analyses Grid or Empty State */}
      {(() => {
        if (filteredAnalyses.length === 0) {
          console.log('📅 History: Showing empty state - no filteredAnalyses', {
            filteredAnalysesLength: filteredAnalyses?.length,
            rawAnalysesLength: analyses?.length,
            searchTerm,
            platformFilter,
            projectFilter,
            userId: user?.id
          });
        }
        return null;
      })()}
      {filteredAnalyses.length > 0 ? (
        <Grid container spacing={3}>
          {filteredAnalyses.map(analysis => (
            <Grid item xs={12} md={6} lg={4} key={analysis.id}>
              <AnalysisCard
                analysis={analysis}
                projects={projects}
                onAddToProject={handleAddToProject}
                onDelete={handleDeleteAnalysis}
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper
          sx={{
            p: 6,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            border: '1px solid',
            borderColor: 'grey.200'
          }}
        >
          <Analytics sx={{ fontSize: 80, color: 'primary.main', mb: 3 }} />
          
          <Typography variant="h5" gutterBottom fontWeight={600}>
            {searchTerm || platformFilter !== 'all' || projectFilter !== 'all'
              ? 'No analyses match your filters'
              : 'No analysis history yet'}
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 500, mx: 'auto' }}>
            {searchTerm || platformFilter !== 'all' || projectFilter !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Start your first analysis to see detailed performance insights and AI-powered suggestions'}
          </Typography>

          {(!searchTerm && platformFilter === 'all' && projectFilter === 'all') && (
            <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
              <Button
                variant="contained"
                size="large"
                startIcon={<Add />}
                component={RouterLink}
                to="/analysis/new"
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                }}
              >
                Analyze Your First Ad
              </Button>
              
              <Button
                variant="outlined"
                size="large"
                startIcon={<TrendingUp />}
                component={RouterLink}
                to="/dashboard"
                sx={{ px: 4, py: 1.5 }}
              >
                View Dashboard
              </Button>
            </Box>
          )}
        </Paper>
      )}
    </Container>
  );
};

export default AnalysisHistoryNew;