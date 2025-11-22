import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  IconButton,
  Avatar,
  Chip,
  LinearProgress,
  Fade,
  Skeleton,
  Alert,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  AutoFixHigh,
  History,
  PlayArrow,
  Add,
  ChevronRight,
  Facebook,
  Google,
  Twitter,
  LinkedIn
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../services/authContext';
import { useNavigate } from 'react-router-dom';
import metricsService from '../services/metricsService';

const ModernDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // State management
  const [selectedPlatform, setSelectedPlatform] = useState('facebook');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    totalAnalyses: 0,
    avgScore: 0,
    improvement: 0,
    activeProjects: 0
  });
  
  // Load dashboard data on mount
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Try to get metrics from API, but handle gracefully if endpoint doesn't exist
        try {
          const metrics = await metricsService.getDashboardMetrics();
          const formattedMetrics = metricsService.formatMetrics(metrics);
          
          // Update state with real data
          setDashboardData({
            totalAnalyses: formattedMetrics.adsAnalyzed || 0,
            avgScore: formattedMetrics.avgScore || 0,
            improvement: formattedMetrics.avgImprovement || 0,
            activeProjects: 0
          });
        } catch (apiError) {
          // If API endpoint doesn't exist (404), use default values without showing error
          if (apiError.response?.status === 404 || apiError.message?.includes('404')) {
            console.log('📊 Dashboard metrics endpoint not available, using defaults');
            setDashboardData({
              totalAnalyses: 0,
              avgScore: 0,
              improvement: 0,
              activeProjects: 0
            });
          } else {
            throw apiError; // Re-throw other errors
          }
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        // Only show error for non-404 issues
        setError(null); // Don't show error to user, just use defaults
      } finally {
        setIsLoading(false);
      }
    };
    
    loadDashboardData();
  }, []);

  const platforms = [
    { id: 'facebook', name: 'Facebook', icon: Facebook, color: '#1877F2' },
    { id: 'google', name: 'Google', icon: Google, color: '#4285F4' },
    { id: 'linkedin', name: 'LinkedIn', icon: LinkedIn, color: '#0A66C2' },
    { id: 'twitter', name: 'Twitter', icon: Twitter, color: '#1DA1F2' },
  ];

  const quickActions = [
    {
      title: 'Analyze New Ad',
      description: 'Get instant feedback on your ad copy',
      icon: AutoFixHigh,
      color: 'primary',
      action: () => navigate('/analysis/new')
    },
    {
      title: 'View Analytics',
      description: 'See your performance trends',
      icon: Analytics,
      color: 'success',
      action: () => navigate('/analytics')
    },
    {
      title: 'Recent History',
      description: 'Browse your past analyses',
      icon: History,
      color: 'info',
      action: () => navigate('/history')
    }
  ];

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getPlatformIcon = (platformId) => {
    const platform = platforms.find(p => p.id === platformId);
    return platform?.icon || Facebook;
  };

  const handleStartAnalysis = () => {
    // Simulate navigation delay
    setTimeout(() => {
      navigate('/analysis/new', { state: { platform: selectedPlatform } });
    }, 300);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Welcome Header - Simple & Clean */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box>
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 700, 
                  color: 'text.primary',
                  fontSize: { xs: '1.75rem', md: '2.125rem' }
                }}
              >
                Welcome back, {user?.email?.split('@')[0] || 'User'} 👋
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
                Ready to create high-performing ads?
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="large"
              onClick={handleStartAnalysis}
              sx={{
                borderRadius: 2,
                px: 3,
                py: 1.5,
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(25, 118, 210, 0.4)',
                }
              }}
            >
              Start Analyzing
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Error Alert */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        </motion.div>
      )}

      {/* Key Metrics - Clean Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
                      Analyses
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {isLoading ? <Skeleton width={60} /> : dashboardData.totalAnalyses}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
                    <Analytics />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
                      Avg Score
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {isLoading ? <Skeleton width={60} /> : dashboardData.avgScore}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'success.main', width: 48, height: 48 }}>
                    <TrendingUp />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
                      Improvement
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {isLoading ? <Skeleton width={80} /> : `+${dashboardData.improvement}%`}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'warning.main', width: 48, height: 48 }}>
                    <AutoFixHigh />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
                      Active Projects
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {isLoading ? <Skeleton width={60} /> : dashboardData.activeProjects}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'info.main', width: 48, height: 48 }}>
                    <PlayArrow />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </motion.div>

      <Grid container spacing={3}>
        {/* Quick Actions - Focused */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  {quickActions.map((action, index) => (
                    <Grid item xs={12} sm={4} key={index}>
                      <Card 
                        sx={{ 
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          border: '1px solid',
                          borderColor: 'divider',
                          '&:hover': {
                            transform: 'translateY(-4px)',
                            boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                            borderColor: `${action.color}.main`
                          }
                        }}
                        onClick={action.action}
                      >
                        <CardContent sx={{ p: 2, textAlign: 'center' }}>
                          <Avatar sx={{ bgcolor: `${action.color}.main`, mx: 'auto', mb: 2 }}>
                            <action.icon />
                          </Avatar>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                            {action.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                            {action.description}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Analyses - Simplified */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', height: 'fit-content' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Recent Analyses
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => navigate('/history')}
                    sx={{ color: 'primary.main' }}
                  >
                    <ChevronRight />
                  </IconButton>
                </Box>
                
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {dashboardData.totalAnalyses === 0 
                      ? "No analyses yet. Start analyzing!"
                      : "Recent analyses will appear here."
                    }
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/analysis/new')}
                  >
                    {dashboardData.totalAnalyses === 0 ? "Create First Analysis" : "Analyze New Ad"}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ModernDashboard;