import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  IconButton,
  Chip,
  Skeleton,
  alpha,
  Divider
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  RemoveCircleOutline as RemoveIcon,
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
  Devices as DevicesIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import CreateProjectModal from '../components/CreateProjectModal';
import {
  useProjectWithInsights,
  useDeleteProject,
  useRemoveAnalysisFromProject
} from '../hooks/useProjectsNew';

// ============================================================================
// Analysis Card Component
// ============================================================================

const AnalysisCard = ({ analysis, projectId, onRemove }) => {
  const navigate = useNavigate();

  const getScoreBadgeColor = (score) => {
    if (score >= 80) return { bg: alpha('#10b981', 0.1), color: '#10b981', border: alpha('#10b981', 0.3) };
    if (score >= 60) return { bg: alpha('#f59e0b', 0.1), color: '#f59e0b', border: alpha('#f59e0b', 0.3) };
    return { bg: alpha('#ef4444', 0.1), color: '#ef4444', border: alpha('#ef4444', 0.3) };
  };

  const scoreColors = getScoreBadgeColor(analysis.overall_score);

  return (
    <Card
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4
        }
      }}
      onClick={() => navigate(`/results/${analysis.id}`)}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Typography variant="h6" fontWeight={600} noWrap>
              {analysis.headline || 'Untitled Analysis'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}
            </Typography>
          </Box>
          
          {/* Score Badge */}
          <Chip
            label={`${Math.round(analysis.overall_score || 0)}`}
            size="small"
            sx={{
              fontWeight: 700,
              backgroundColor: scoreColors.bg,
              color: scoreColors.color,
              border: '1px solid',
              borderColor: scoreColors.border
            }}
          />
        </Box>

        {/* Body Text Preview */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            minHeight: 40
          }}
        >
          {analysis.body_text}
        </Typography>

        {/* Platform & Scores */}
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Chip
            label={analysis.platform}
            size="small"
            variant="outlined"
            sx={{ textTransform: 'capitalize' }}
          />
          
          <Box display="flex" gap={1}>
            <Button
              size="small"
              variant="outlined"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/results/${analysis.id}`);
              }}
            >
              View
            </Button>
            <Button
              size="small"
              color="error"
              startIcon={<RemoveIcon />}
              onClick={(e) => {
                e.stopPropagation();
                onRemove(analysis);
              }}
            >
              Remove
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// Insights Card Component
// ============================================================================

const InsightsCard = ({ insights, project }) => {
  const navigate = useNavigate();

  if (!insights || insights.totalAnalyses === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          📊 Project Insights
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Add analyses to this project to see insights
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        📊 Project Insights
      </Typography>
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Average Score */}
        <Grid item xs={12} md={4}>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              background: alpha('#A855F7', 0.05),
              border: '1px solid',
              borderColor: alpha('#A855F7', 0.2)
            }}
          >
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <TrendingUpIcon sx={{ color: 'primary.main' }} />
              <Typography variant="subtitle2" fontWeight={600}>
                Average Score
              </Typography>
            </Box>
            <Typography variant="h4" fontWeight={700} color="primary.main">
              {Math.round(insights.averageImprovement)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Across {insights.totalAnalyses} {insights.totalAnalyses === 1 ? 'analysis' : 'analyses'}
            </Typography>
          </Box>
        </Grid>

        {/* Most Used Platform */}
        <Grid item xs={12} md={4}>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              background: alpha('#10b981', 0.05),
              border: '1px solid',
              borderColor: alpha('#10b981', 0.2)
            }}
          >
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <DevicesIcon sx={{ color: '#10b981' }} />
              <Typography variant="subtitle2" fontWeight={600}>
                Most Used Platform
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight={700} sx={{ color: '#10b981', textTransform: 'capitalize' }}>
              {insights.mostUsedPlatform || 'N/A'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {insights.platformCounts[insights.mostUsedPlatform] || 0} / {insights.totalAnalyses} analyses
            </Typography>
          </Box>
        </Grid>

        {/* Best Performing */}
        <Grid item xs={12} md={4}>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              background: alpha('#f59e0b', 0.05),
              border: '1px solid',
              borderColor: alpha('#f59e0b', 0.2),
              cursor: insights.bestPerformingId ? 'pointer' : 'default',
              '&:hover': insights.bestPerformingId ? {
                background: alpha('#f59e0b', 0.1)
              } : {}
            }}
            onClick={() => {
              if (insights.bestPerformingId) {
                navigate(`/results/${insights.bestPerformingId}`);
              }
            }}
          >
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <TrophyIcon sx={{ color: '#f59e0b' }} />
              <Typography variant="subtitle2" fontWeight={600}>
                Best Performing
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight={700} sx={{ color: '#f59e0b' }}>
              {Math.round(insights.bestPerformingScore)}
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: '-webkit-box',
                WebkitLineClamp: 1,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
            >
              {insights.bestPerformingName}
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

// ============================================================================
// Main Component
// ============================================================================

const ProjectDetailNew = () => {
  const navigate = useNavigate();
  const { id: projectId } = useParams();
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Fetch project with insights
  const { data, isLoading, error } = useProjectWithInsights(projectId);
  const project = data?.project;
  const analyses = data?.analyses || [];
  const insights = data?.insights;

  // Mutations
  const deleteProjectMutation = useDeleteProject();
  const removeAnalysisMutation = useRemoveAnalysisFromProject();

  const handleEdit = () => {
    setMenuOpen(false);
    setEditModalOpen(true);
  };

  const handleDelete = async () => {
    setMenuOpen(false);
    const confirmed = window.confirm(
      `Are you sure you want to delete "${project?.name}"?\n\nThis will not delete your analyses, just unlink them from this project.`
    );

    if (confirmed) {
      try {
        await deleteProjectMutation.mutateAsync(projectId);
        navigate('/projects');
      } catch (error) {
        console.error('Error deleting project:', error);
      }
    }
  };

  const handleRemoveAnalysis = async (analysis) => {
    const confirmed = window.confirm(
      `Remove "${analysis.headline}" from this project?\n\nThe analysis won't be deleted, just unlinked.`
    );

    if (confirmed) {
      try {
        await removeAnalysisMutation.mutateAsync({
          analysisId: analysis.id,
          projectId: projectId
        });
      } catch (error) {
        console.error('Error removing analysis:', error);
      }
    }
  };

  // Loading State
  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 3 }} />
        <Skeleton variant="rectangular" height={200} sx={{ mb: 3, borderRadius: 3 }} />
        <Grid container spacing={3}>
          {[...Array(3)].map((_, i) => (
            <Grid item xs={12} md={4} key={i}>
              <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  // Error State
  if (error || !project) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
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
            Project Not Found
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            This project doesn't exist or you don't have access to it.
          </Typography>
          <Button variant="outlined" onClick={() => navigate('/projects')}>
            Back to Projects
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Breadcrumb */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/projects')}
        sx={{ mb: 3, color: 'text.secondary' }}
      >
        Back to Projects
      </Button>

      {/* Project Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
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
              {project.name}
            </Typography>
            
            {project.description && (
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {project.description}
              </Typography>
            )}

            <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
              {project.client_name && (
                <Chip
                  label={`Client: ${project.client_name}`}
                  color="primary"
                  variant="outlined"
                />
              )}
              <Typography variant="caption" color="text.secondary">
                Created {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                • {analyses.length} {analyses.length === 1 ? 'analysis' : 'analyses'}
              </Typography>
            </Box>
          </Box>

          {/* More Menu */}
          <Box sx={{ position: 'relative' }}>
            <IconButton
              onClick={() => setMenuOpen(!menuOpen)}
              sx={{
                color: 'text.secondary',
                '&:hover': { color: 'primary.main' }
              }}
            >
              <MoreVertIcon />
            </IconButton>

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
                  <Typography variant="body2">Edit Project</Typography>
                </Box>
                <Divider />
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
                  <Typography variant="body2">Delete Project</Typography>
                </Box>
              </Paper>
            )}
          </Box>
        </Box>
      </Paper>

      {/* Add Analysis Button */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6" fontWeight={600}>
          Analyses ({analyses.length})
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate(`/analysis/new?projectId=${projectId}`)}
          sx={{
            background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
          }}
        >
          Add Analysis
        </Button>
      </Box>

      {/* Insights Section */}
      <InsightsCard insights={insights} project={project} />

      {/* Analyses List */}
      {analyses.length === 0 ? (
        <Paper
          sx={{
            p: 6,
            mt: 3,
            textAlign: 'center',
            background: alpha('#A855F7', 0.05),
            border: '1px solid',
            borderColor: alpha('#A855F7', 0.2)
          }}
        >
          <AssessmentIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2, opacity: 0.5 }} />
          <Typography variant="h6" fontWeight={600} gutterBottom>
            No analyses yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Add your first analysis to this project to start tracking performance
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate(`/analysis/new?projectId=${projectId}`)}
          >
            Add First Analysis
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          {analyses.map((analysis) => (
            <Grid item xs={12} md={6} key={analysis.id}>
              <AnalysisCard
                analysis={analysis}
                projectId={projectId}
                onRemove={handleRemoveAnalysis}
              />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Edit Project Modal */}
      <CreateProjectModal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        project={project}
      />
    </Container>
  );
};

export default ProjectDetailNew;
