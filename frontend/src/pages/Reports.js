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
  Chip
} from '@mui/material';
import {
  Assessment,
  BarChart,
  TrendingUp,
  Speed,
  Analytics,
  Add,
  Insights
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../services/authContext';

const Reports = () => {
  const { user, subscription } = useAuth();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Assessment color="primary" sx={{ fontSize: 40 }} />
          Reports & Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Get insights and performance analytics for your ad copy campaigns
        </Typography>
      </Box>

      {/* Empty State */}
      <Paper 
        sx={{ 
          p: 6, 
          textAlign: 'center', 
          background: 'linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%)',
          border: '1px solid',
          borderColor: 'success.200'
        }}
      >
        <BarChart sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
        
        <Typography variant="h5" gutterBottom fontWeight={600}>
          No reports available yet
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
          Reports and analytics will appear here once you've completed some ad analyses. 
          You'll get detailed insights including performance trends, score improvements, 
          platform comparisons, and optimization recommendations.
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
            Create Your First Analysis
          </Button>
          
          <Button
            variant="outlined"
            size="large"
            startIcon={<TrendingUp />}
            component={RouterLink}
            to="/dashboard"
            sx={{ px: 4, py: 1.5 }}
          >
            Back to Dashboard
          </Button>
        </Box>
      </Paper>

      {/* What reports will show */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h6" gutterBottom fontWeight={600} textAlign="center" sx={{ mb: 4 }}>
          📊 Analytics & Reports You'll Get
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <TrendingUp color="primary" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Performance Trends
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Track your ad performance over time with detailed charts showing score improvements and campaign success rates
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <Speed color="warning" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Score Breakdowns
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Detailed analysis of clarity, persuasion, emotion, and CTA effectiveness across all your campaigns
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <Analytics color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Platform Insights
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Compare performance across Facebook, Google, Instagram, and other platforms to optimize your strategy
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Sample metrics preview */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h6" gutterBottom fontWeight={600} textAlign="center" sx={{ mb: 4 }}>
          📈 Sample Metrics You'll Track
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="h4" color="primary.main" fontWeight={700}>
                --
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Analyses
              </Typography>
            </Card>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="h4" color="success.main" fontWeight={700}>
                --%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Improvement
              </Typography>
            </Card>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="h4" color="warning.main" fontWeight={700}>
                --
              </Typography>
              <Typography variant="body2" color="text.secondary">
                High Scores
              </Typography>
            </Card>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Card sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="h4" color="info.main" fontWeight={700}>
                --
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Platforms Used
              </Typography>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Account status */}
      <Paper sx={{ mt: 6, p: 4, bgcolor: 'grey.50' }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Start generating powerful insights today
            </Typography>
            <Typography variant="body1" color="text.secondary">
              You're on the <Chip label={subscription?.subscription_tier?.toUpperCase() || 'FREE'} size="small" color="primary" /> plan. 
              Complete your first analysis to unlock detailed reports and performance tracking.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} textAlign={{ xs: 'left', md: 'right' }}>
            <Box display="flex" gap={2} flexDirection={{ xs: 'column', sm: 'row' }}>
              <Button
                variant="contained"
                component={RouterLink}
                to="/analyze"
                startIcon={<Insights />}
              >
                Analyze Ad Copy
              </Button>
              <Button
                variant="outlined"
                component={RouterLink}
                to="/pricing"
              >
                Upgrade Plan
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default Reports;
