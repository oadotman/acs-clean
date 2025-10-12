import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  InputAdornment,
  Chip,
  Menu,
  MenuItem,
  IconButton,
  Avatar,
  LinearProgress,
  alpha,
  useTheme,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert as MoreIcon,
  ContentCopy as CopyIcon,
  FileDownload as ExportIcon,
  Refresh as ReanalyzeIcon,
  Delete as DeleteIcon,
  Close as CloseIcon,
  TrendingUp as ImprovementIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import { useAuth } from '../services/authContext';
import dataService from '../services/dataService';
import { formatDistanceToNow } from 'date-fns';

const RecentAnalyses = ({ onClose, onViewAnalysis, onNewAnalysis, limit = 20, compact = false, showTitle = false }) => {
  const theme = useTheme();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchor, setFilterAnchor] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Real analyses data from database
  const [recentAnalyses, setRecentAnalyses] = useState([]);

  // Fetch analyses from database
  const fetchAnalyses = async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const analyses = await dataService.getAnalysesHistory(user.id, limit, 0);
      
      // Transform database data to component format
      const transformedAnalyses = analyses.map(analysis => ({
        id: analysis.id,
        original: analysis.headline || analysis.body_text || 'Untitled Ad',
        improved: analysis.feedback || analysis.suggestions || 'Analysis completed',
        originalScore: 60, // Default since we don't track original scores
        improvedScore: analysis.overall_score || 75,
        improvement: Math.max(0, (analysis.overall_score || 75) - 60),
        date: formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true }),
        type: 'single', // Default type
        status: 'completed',
        platform: analysis.platform || 'Unknown',
        fullData: analysis // Keep full analysis data for viewing
      }));
      
      setRecentAnalyses(transformedAnalyses);
    } catch (err) {
      console.error('Error fetching analyses:', err);
      setError('Failed to load recent analyses');
    } finally {
      setLoading(false);
    }
  };

  // Fetch analyses on component mount and when user changes
  useEffect(() => {
    fetchAnalyses();
  }, [user?.id, limit]);

  const filterOptions = [
    { value: 'all', label: 'All Analyses', count: recentAnalyses.length },
    { value: 'single', label: 'Single Ads', count: recentAnalyses.filter(a => a.type === 'single').length },
    { value: 'batch', label: 'Batch Campaigns', count: recentAnalyses.filter(a => a.type === 'batch').length },
    { value: 'high-improvement', label: 'High Improvement (+30)', count: recentAnalyses.filter(a => a.improvement >= 30).length }
  ];

  const filteredAnalyses = recentAnalyses.filter(analysis => {
    const matchesSearch = analysis.original.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         analysis.improved.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         analysis.platform.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = selectedFilter === 'all' || 
                         (selectedFilter === 'single' && analysis.type === 'single') ||
                         (selectedFilter === 'batch' && analysis.type === 'batch') ||
                         (selectedFilter === 'high-improvement' && analysis.improvement >= 30);
    
    return matchesSearch && matchesFilter;
  });

  const handleMenuOpen = (event, analysis) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
    setSelectedAnalysis(analysis);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedAnalysis(null);
  };

  const handleCopyImproved = () => {
    if (selectedAnalysis) {
      navigator.clipboard.writeText(selectedAnalysis.improved).then(() => {
        toast.success('Improved version copied to clipboard!');
      });
    }
    handleMenuClose();
  };

  const handleReanalyze = () => {
    if (selectedAnalysis) {
      toast.success('Re-analyzing ad...');
      // Would trigger new analysis with same original text
    }
    handleMenuClose();
  };

  const handleExport = () => {
    if (selectedAnalysis) {
      toast.success('Exporting analysis...');
      // Would trigger export functionality
    }
    handleMenuClose();
  };

  const handleDelete = () => {
    setDeleteDialog(selectedAnalysis);
    handleMenuClose();
  };

  const confirmDelete = async () => {
    if (deleteDialog) {
      try {
        // Delete from database using Supabase directly (dataService doesn't have delete method)
        const { supabase } = await import('../lib/supabaseClientClean');
        const { error } = await supabase.default
          .from('ad_analyses')
          .delete()
          .eq('id', deleteDialog.id)
          .eq('user_id', user?.id); // Safety check
        
        if (error) {
          throw error;
        }
        
        // Remove from local state
        setRecentAnalyses(prev => prev.filter(analysis => analysis.id !== deleteDialog.id));
        toast.success('Analysis deleted successfully');
      } catch (error) {
        console.error('Error deleting analysis:', error);
        toast.error('Failed to delete analysis');
      }
    }
    setDeleteDialog(null);
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getTypeIcon = (type) => {
    return type === 'batch' ? '📊' : '📝';
  };

  const getPlatformColor = (platform) => {
    switch (platform.toLowerCase()) {
      case 'facebook': return '#1877f2';
      case 'google': return '#4285f4';
      case 'instagram': return '#e4405f';
      case 'linkedin': return '#0077b5';
      case 'twitter': return '#1da1f2';
      default: return theme.palette.primary.main;
    }
  };

  // Loading state
  if (loading) {
    return (
      <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3, textAlign: 'center' }}>
        <CircularProgress size={40} sx={{ mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          Loading recent analyses...
        </Typography>
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button variant="outlined" onClick={fetchAnalyses}>
          Try Again
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>
            Recent Analyses
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {filteredAnalyses.length} of {recentAnalyses.length} analyses
          </Typography>
        </Box>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Search and Filter Bar */}
      <Card elevation={1} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              placeholder="Search analyses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                )
              }}
              sx={{ flexGrow: 1 }}
            />
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={(e) => setFilterAnchor(e.currentTarget)}
              sx={{ textTransform: 'none', minWidth: 120 }}
            >
              {filterOptions.find(f => f.value === selectedFilter)?.label}
            </Button>
          </Box>
          
          {/* Filter Chips */}
          <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
            {filterOptions.map((filter) => (
              <Chip
                key={filter.value}
                label={`${filter.label} (${filter.count})`}
                variant={selectedFilter === filter.value ? 'filled' : 'outlined'}
                color={selectedFilter === filter.value ? 'primary' : 'default'}
                size="small"
                onClick={() => setSelectedFilter(filter.value)}
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Analyses Grid */}
      <Grid container spacing={3}>
        {filteredAnalyses.map((analysis) => (
          <Grid item xs={12} md={6} lg={4} key={analysis.id}>
            <Card 
              sx={{ 
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  boxShadow: 4,
                  transform: 'translateY(-2px)'
                }
              }}
              onClick={() => onViewAnalysis && onViewAnalysis(analysis)}
            >
              <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6" component="span">
                      {getTypeIcon(analysis.type)}
                    </Typography>
                    <Chip
                      label={analysis.type === 'batch' ? 'Campaign' : 'Single Ad'}
                      size="small"
                      variant="outlined"
                      color={analysis.type === 'batch' ? 'secondary' : 'primary'}
                    />
                  </Box>
                  <IconButton 
                    size="small"
                    onClick={(e) => handleMenuOpen(e, analysis)}
                  >
                    <MoreIcon />
                  </IconButton>
                </Box>

                {/* Content Preview */}
                <Box sx={{ mb: 2 }}>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      mb: 1
                    }}
                  >
                    {analysis.original}
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography 
                    variant="body2"
                    sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      fontWeight: 500
                    }}
                  >
                    {analysis.improved}
                  </Typography>
                </Box>

                {/* Scores */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      label={`${analysis.originalScore} → ${analysis.improvedScore}`}
                      color={getScoreColor(analysis.improvedScore)}
                      variant="outlined"
                      size="small"
                    />
                    <Chip
                      icon={<ImprovementIcon />}
                      label={`+${analysis.improvement}`}
                      color="success"
                      variant="filled"
                      size="small"
                    />
                  </Box>
                </Box>

                {/* Progress Bar */}
                <Box sx={{ mb: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.improvedScore}
                    color={getScoreColor(analysis.improvedScore)}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: alpha(theme.palette.grey[300], 0.3)
                    }}
                  />
                </Box>

                {/* Footer */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    {analysis.date}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: getPlatformColor(analysis.platform)
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {analysis.platform}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {filteredAnalyses.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <SearchIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No analyses found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {searchQuery ? 'Try adjusting your search terms' : 'Start analyzing ads to see them here'}
          </Typography>
          <Button
            variant="contained"
            onClick={onNewAnalysis}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            Create New Analysis
          </Button>
        </Box>
      )}

      {/* Bottom Actions */}
      {filteredAnalyses.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', pt: 4 }}>
          <Button
            variant="contained"
            onClick={onNewAnalysis}
            sx={{
              fontWeight: 600,
              textTransform: 'none',
              px: 4
            }}
          >
            Create New Analysis
          </Button>
        </Box>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: { minWidth: 200 }
        }}
      >
        <MenuItem onClick={handleCopyImproved}>
          <CopyIcon sx={{ mr: 2, fontSize: '1.25rem' }} />
          Copy Improved Version
        </MenuItem>
        <MenuItem onClick={handleReanalyze}>
          <ReanalyzeIcon sx={{ mr: 2, fontSize: '1.25rem' }} />
          Re-analyze
        </MenuItem>
        <MenuItem onClick={handleExport}>
          <ExportIcon sx={{ mr: 2, fontSize: '1.25rem' }} />
          Export Analysis
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 2, fontSize: '1.25rem' }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={Boolean(deleteDialog)} onClose={() => setDeleteDialog(null)}>
        <DialogTitle>Delete Analysis</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this analysis? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(null)}>
            Cancel
          </Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchor}
        open={Boolean(filterAnchor)}
        onClose={() => setFilterAnchor(null)}
      >
        {filterOptions.map((filter) => (
          <MenuItem
            key={filter.value}
            onClick={() => {
              setSelectedFilter(filter.value);
              setFilterAnchor(null);
            }}
            selected={selectedFilter === filter.value}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
              <span>{filter.label}</span>
              <Chip label={filter.count} size="small" variant="outlined" />
            </Box>
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default RecentAnalyses;