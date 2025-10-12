import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
  Grid,
  Divider
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  Search,
  Add,
  History
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';

const AnalysisHistory = () => {
  const { user, subscription } = useAuth();
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 2 }}>
          <History color="primary" sx={{ fontSize: 40 }} />
          Analysis History
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track and review all your ad copy analyses
        </Typography>
      </Box>

      {/* Empty State */}
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
          No analysis history yet
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 500, mx: 'auto' }}>
          You haven't analyzed any ad copy yet. Start your first analysis to see detailed performance insights, 
          AI-powered suggestions, and track your improvements over time.
        </Typography>

        <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
          <Button
            variant="contained"
            size="large"
            startIcon={<Add />}
            component={RouterLink}
            to="/analyze"
            sx={{ 
              px: 4, 
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600
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
      </Paper>

      {/* What you'll see section */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h6" gutterBottom fontWeight={600} textAlign="center" sx={{ mb: 4 }}>
          🎯 What You'll See Here Once You Start Analyzing
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <Search color="primary" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Detailed Analysis Reports
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View comprehensive scores for clarity, persuasion, emotional impact, and platform optimization
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <TrendingUp color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Performance Tracking
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Track your improvement over time and see which strategies work best for your campaigns
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <Analytics color="warning" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  AI-Powered Insights
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Get actionable recommendations and alternative copy suggestions to boost conversion rates
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Account Info */}
      <Paper sx={{ mt: 6, p: 4, bgcolor: 'grey.50' }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Ready to optimize your ad copy?
            </Typography>
            <Typography variant="body1" color="text.secondary">
              You're currently on the <strong>{subscription?.subscription_tier?.toUpperCase() || 'FREE'}</strong> plan. 
              {subscription?.subscription_tier === 'free' && ' You can analyze up to 5 ads per month.'}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} textAlign={{ xs: 'left', md: 'right' }}>
            <Box display="flex" gap={2} flexDirection={{ xs: 'column', sm: 'row' }}>
              <Button
                variant="contained"
                component={RouterLink}
                to="/analyze"
                startIcon={<Add />}
              >
                Start Analysis
              </Button>
              <Button
                variant="outlined"
                component={RouterLink}
                to="/pricing"
              >
                View Plans
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default AnalysisHistory;
