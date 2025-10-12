import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Divider,
  Button,
  Stack,
  Paper,
  LinearProgress,
  Tooltip,
  IconButton,
  Alert
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Favorite as FavoriteIcon,
  Insights as InsightsIcon,
  Lightbulb as LightbulbIcon,
  Assessment as AssessmentIcon,
  CompareArrows as CompareArrowsIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  Legend
} from 'recharts';
import { motion } from 'framer-motion';

const CreativeAnalytics = ({ 
  analyticsData = null, 
  timeRange = '30d',
  onTimeRangeChange,
  platform = 'all'
}) => {
  const [selectedMetric, setSelectedMetric] = useState('performance');
  const [selectedTimeRange, setSelectedTimeRange] = useState(timeRange);

  // Mock analytics data - in production this would come from your backend
  const mockAnalyticsData = useMemo(() => ({
    creativity_performance: [
      { creativity: 1, performance: 65, samples: 15 },
      { creativity: 2, performance: 68, samples: 23 },
      { creativity: 3, performance: 72, samples: 34 },
      { creativity: 4, performance: 75, samples: 45 },
      { creativity: 5, performance: 78, samples: 56 },
      { creativity: 6, performance: 82, samples: 67 },
      { creativity: 7, performance: 85, samples: 43 },
      { creativity: 8, performance: 87, samples: 32 },
      { creativity: 9, performance: 83, samples: 21 },
      { creativity: 10, performance: 79, samples: 12 }
    ],
    emotion_performance: [
      { emotion: 'inspiring', performance: 82, conversion: 3.4, engagement: 4.2 },
      { emotion: 'urgent', performance: 85, conversion: 4.1, engagement: 3.8 },
      { emotion: 'trust_building', performance: 78, conversion: 3.8, engagement: 3.5 },
      { emotion: 'aspirational', performance: 80, conversion: 3.2, engagement: 4.5 },
      { emotion: 'problem_solving', performance: 83, conversion: 4.0, engagement: 3.9 },
      { emotion: 'excitement', performance: 86, conversion: 3.6, engagement: 4.8 },
      { emotion: 'fomo', performance: 88, conversion: 4.3, engagement: 4.1 },
      { emotion: 'curiosity', performance: 81, conversion: 3.5, engagement: 4.3 },
      { emotion: 'confidence', performance: 77, conversion: 3.7, engagement: 3.6 },
      { emotion: 'comfort', performance: 75, conversion: 3.3, engagement: 3.4 }
    ],
    urgency_trends: [
      { urgency: 0, ctr: 2.1, conversion: 2.8, bounce: 65 },
      { urgency: 1, ctr: 2.3, conversion: 3.0, bounce: 62 },
      { urgency: 2, ctr: 2.6, conversion: 3.2, bounce: 58 },
      { urgency: 3, ctr: 2.9, conversion: 3.5, bounce: 55 },
      { urgency: 4, ctr: 3.2, conversion: 3.7, bounce: 52 },
      { urgency: 5, ctr: 3.5, conversion: 4.0, bounce: 48 },
      { urgency: 6, ctr: 3.8, conversion: 4.2, bounce: 45 },
      { urgency: 7, ctr: 4.1, conversion: 4.5, bounce: 42 },
      { urgency: 8, ctr: 4.3, conversion: 4.3, bounce: 40 },
      { urgency: 9, ctr: 4.0, conversion: 3.9, bounce: 38 },
      { urgency: 10, ctr: 3.7, conversion: 3.5, bounce: 35 }
    ],
    platform_performance: {
      facebook: { creativity: 6.2, urgency: 5.8, top_emotion: 'trust_building', performance: 79 },
      instagram: { creativity: 7.1, urgency: 4.3, top_emotion: 'aspirational', performance: 82 },
      linkedin: { creativity: 4.5, urgency: 3.2, top_emotion: 'problem_solving', performance: 76 },
      twitter: { creativity: 7.3, urgency: 6.1, top_emotion: 'excitement', performance: 84 },
      tiktok: { creativity: 8.9, urgency: 3.8, top_emotion: 'curiosity', performance: 87 },
      google: { creativity: 5.4, urgency: 7.2, top_emotion: 'urgent', performance: 81 }
    },
    optimization_opportunities: [
      {
        type: 'creativity',
        current: 5.2,
        recommended: 6.8,
        potential_lift: '+12%',
        confidence: 'High',
        description: 'Your current creativity levels are conservative. Testing higher creativity could improve engagement.'
      },
      {
        type: 'emotion',
        current: 'trust_building',
        recommended: 'excitement',
        potential_lift: '+8%',
        confidence: 'Medium',
        description: 'Excitement-based emotions show 8% better performance for your audience segment.'
      },
      {
        type: 'urgency',
        current: 4.1,
        recommended: 6.5,
        potential_lift: '+15%',
        confidence: 'High',
        description: 'Higher urgency levels correlate with better conversion rates in your industry.'
      }
    ],
    cliche_impact: {
      with_cliches: { performance: 72, engagement: 3.2, bounce_rate: 58 },
      without_cliches: { performance: 84, engagement: 4.1, bounce_rate: 45 },
      improvement: { performance: '+16.7%', engagement: '+28.1%', bounce_rate: '-22.4%' }
    }
  }), []);

  const data = analyticsData || mockAnalyticsData;

  const MetricCard = ({ title, value, change, icon, color = 'primary' }) => (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent sx={{ textAlign: 'center', py: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
          {icon}
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 600, color: `${color}.main`, mb: 1 }}>
          {value}
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
          {title}
        </Typography>
        {change && (
          <Chip
            label={change}
            size="small"
            color={change.startsWith('+') ? 'success' : 'error'}
            variant="outlined"
          />
        )}
      </CardContent>
    </Card>
  );

  const CreativityPerformanceChart = () => (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <PsychologyIcon color="primary" />
          Creativity vs Performance
          <Tooltip title="How different creativity levels affect ad performance">
            <InfoIcon fontSize="small" color="action" />
          </Tooltip>
        </Typography>
        
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart data={data.creativity_performance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="creativity" 
              domain={[0, 10]}
              label={{ value: 'Creativity Level', position: 'insideBottom', offset: -10 }}
            />
            <YAxis 
              domain={[60, 90]}
              label={{ value: 'Performance Score', angle: -90, position: 'insideLeft' }}
            />
            <RechartsTooltip
              formatter={(value, name) => [
                `${value}${name === 'performance' ? '%' : ''}`,
                name === 'performance' ? 'Performance' : 'Samples'
              ]}
              labelFormatter={(creativity) => `Creativity Level: ${creativity}`}
            />
            <Scatter dataKey="performance" fill="#1976d2" />
          </ScatterChart>
        </ResponsiveContainer>
        
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Insight:</strong> Creativity levels 6-8 show the highest performance scores. 
            Consider testing in this range for optimal results.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );

  const EmotionPerformanceChart = () => (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <FavoriteIcon color="error" />
          Emotion Performance Analysis
        </Typography>
        
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.emotion_performance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="emotion" 
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
            <RechartsTooltip />
            <Bar dataKey="performance" fill="#1976d2" name="Performance" />
            <Bar dataKey="conversion" fill="#f57c00" name="Conversion Rate" />
            <Bar dataKey="engagement" fill="#388e3c" name="Engagement" />
          </BarChart>
        </ResponsiveContainer>
        
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          Performance scores are normalized. Higher bars indicate better results.
        </Typography>
      </CardContent>
    </Card>
  );

  const UrgencyTrendsChart = () => (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <SpeedIcon color="secondary" />
          Urgency Level Impact
        </Typography>
        
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.urgency_trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="urgency" 
              label={{ value: 'Urgency Level', position: 'insideBottom', offset: -10 }}
            />
            <YAxis label={{ value: 'Rate (%)', angle: -90, position: 'insideLeft' }} />
            <RechartsTooltip />
            <Line 
              type="monotone" 
              dataKey="ctr" 
              stroke="#1976d2" 
              strokeWidth={2}
              name="Click-through Rate"
            />
            <Line 
              type="monotone" 
              dataKey="conversion" 
              stroke="#f57c00" 
              strokeWidth={2}
              name="Conversion Rate"
            />
            <Legend />
          </LineChart>
        </ResponsiveContainer>
        
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Sweet Spot:</strong> Urgency levels 6-8 show optimal conversion rates 
            while maintaining good click-through rates.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );

  const PlatformOptimizationTable = () => (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <AssessmentIcon color="primary" />
          Platform-Specific Insights
        </Typography>
        
        <Grid container spacing={2}>
          {Object.entries(data.platform_performance).map(([platform, metrics]) => (
            <Grid item xs={12} sm={6} md={4} key={platform}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1, textTransform: 'capitalize' }}>
                  {platform}
                </Typography>
                
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="textSecondary">Avg Creativity</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {metrics.creativity}/10
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="textSecondary">Avg Urgency</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {metrics.urgency}/10
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="textSecondary">Top Emotion</Typography>
                    <Chip 
                      label={metrics.top_emotion.replace('_', ' ')}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="textSecondary">Performance</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {metrics.performance}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={metrics.performance}
                        sx={{ width: 40, height: 6 }}
                      />
                    </Box>
                  </Box>
                </Stack>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  const OptimizationRecommendations = () => (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <LightbulbIcon color="warning" />
          Optimization Recommendations
        </Typography>
        
        <Stack spacing={2}>
          {data.optimization_opportunities.map((opportunity, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2, 
                  backgroundColor: 'rgba(255, 193, 7, 0.05)',
                  border: '1px solid rgba(255, 193, 7, 0.2)'
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                      {opportunity.type} Optimization
                    </Typography>
                    <Chip 
                      label={opportunity.confidence}
                      size="small"
                      color={opportunity.confidence === 'High' ? 'success' : 'warning'}
                      variant="outlined"
                    />
                  </Box>
                  <Chip 
                    label={opportunity.potential_lift}
                    size="small"
                    color="success"
                    sx={{ fontWeight: 600 }}
                  />
                </Box>
                
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {opportunity.description}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Typography variant="caption" color="textSecondary">
                    Current: <strong>{opportunity.current}</strong>
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    →
                  </Typography>
                  <Typography variant="caption" color="success.main">
                    Recommended: <strong>{opportunity.recommended}</strong>
                  </Typography>
                </Box>
              </Paper>
            </motion.div>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );

  const ClicheImpactAnalysis = () => (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <CompareArrowsIcon color="primary" />
          Cliché Filtering Impact
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={6}>
            <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 1 }}>
                With Clichés
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'error.main', mb: 1 }}>
                {data.cliche_impact.with_cliches.performance}%
              </Typography>
              <Typography variant="body2" color="textSecondary">Performance</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6}>
            <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 1 }}>
                Without Clichés
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main', mb: 1 }}>
                {data.cliche_impact.without_cliches.performance}%
              </Typography>
              <Typography variant="body2" color="textSecondary">Performance</Typography>
            </Paper>
          </Grid>
        </Grid>
        
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Impact:</strong> Filtering clichés improves performance by{' '}
            <strong>{data.cliche_impact.improvement.performance}</strong> and engagement by{' '}
            <strong>{data.cliche_impact.improvement.engagement}</strong>.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          <InsightsIcon />
          Creative Analytics
          <Chip label="Phase 4 & 5" size="small" color="primary" variant="outlined" />
        </Typography>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={selectedTimeRange}
            label="Time Range"
            onChange={(e) => {
              setSelectedTimeRange(e.target.value);
              onTimeRangeChange && onTimeRangeChange(e.target.value);
            }}
          >
            <MenuItem value="7d">Last 7 days</MenuItem>
            <MenuItem value="30d">Last 30 days</MenuItem>
            <MenuItem value="90d">Last 90 days</MenuItem>
            <MenuItem value="1y">Last year</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="Avg Performance"
            value="82%"
            change="+5.2%"
            icon={<TrendingUpIcon sx={{ fontSize: 32 }} color="primary" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="Optimal Creativity"
            value="6.8/10"
            change="+1.2"
            icon={<PsychologyIcon sx={{ fontSize: 32 }} color="secondary" />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="Top Emotion"
            value="FOMO"
            change="+12%"
            icon={<FavoriteIcon sx={{ fontSize: 32 }} color="error" />}
            color="error"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="Cliché Impact"
            value="+16.7%"
            change="Performance"
            icon={<CheckCircleIcon sx={{ fontSize: 32 }} color="success" />}
            color="success"
          />
        </Grid>
      </Grid>
      
      {/* Main Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <CreativityPerformanceChart />
        </Grid>
        <Grid item xs={12} lg={4}>
          <ClicheImpactAnalysis />
        </Grid>
      </Grid>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={6}>
          <EmotionPerformanceChart />
        </Grid>
        <Grid item xs={12} lg={6}>
          <UrgencyTrendsChart />
        </Grid>
      </Grid>
      
      {/* Platform Analysis */}
      <PlatformOptimizationTable />
      
      {/* Recommendations */}
      <Box sx={{ mt: 4 }}>
        <OptimizationRecommendations />
      </Box>
    </Box>
  );
};

export default CreativeAnalytics;