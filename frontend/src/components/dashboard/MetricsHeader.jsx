import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  alpha,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  Assessment,
  Speed,
  Star
} from '@mui/icons-material';

const MetricCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  trend, 
  subtitle,
  isPercentage = false,
  isLoading = false,
  index = 0
}) => {
  const theme = useTheme();
  
  const trendColor = trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'default';
  const TrendIcon = trend === 'up' ? TrendingUp : TrendingDown;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
    >
      <Card
        elevation={1}
        sx={{
          height: '100%',
          borderRadius: 3,
          border: `1px solid ${theme.palette.divider}`,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            boxShadow: 4,
            transform: 'translateY(-2px)',
          }
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography 
                variant="body2" 
                color="text.secondary" 
                fontWeight={500}
                sx={{ mb: 1 }}
              >
                {title}
              </Typography>
              
              {isLoading ? (
                <LinearProgress sx={{ height: 6, borderRadius: 3, mb: 1 }} />
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                  <Typography 
                    variant="h3" 
                    fontWeight={700}
                    color="text.primary"
                  >
                    <CountUp
                      end={value}
                      duration={1.5}
                      decimals={isPercentage ? 1 : 0}
                      suffix={isPercentage ? '%' : ''}
                      separator=","
                    />
                  </Typography>
                  
                  {change !== undefined && change !== null && (
                    <Chip
                      icon={<TrendIcon sx={{ fontSize: '0.875rem' }} />}
                      label={`${change > 0 ? '+' : ''}${change}%`}
                      size="small"
                      color={trendColor}
                      variant="outlined"
                      sx={{
                        height: 22,
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        '& .MuiChip-icon': {
                          fontSize: '0.875rem'
                        }
                      }}
                    />
                  )}
                </Box>
              )}
              
              {subtitle && (
                <Typography 
                  variant="caption" 
                  color="text.secondary"
                  sx={{ display: 'block', mt: 0.5 }}
                >
                  {subtitle}
                </Typography>
              )}
            </Box>
            
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main
              }}
            >
              <Icon sx={{ fontSize: 24 }} />
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const MetricsHeader = ({ 
  metrics = null,
  isLoading = false
}) => {
  // Use default values if metrics is null or loading
  const displayMetrics = metrics || {
    adsAnalyzed: 0,
    adsAnalyzedChange: 0,
    avgImprovement: 0,
    avgImprovementChange: 0,
    avgScore: 0,
    avgScoreChange: 0,
    topPerforming: 0,
    topPerformingChange: 0
  };
  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography 
          variant="h5" 
          fontWeight={700}
          color="text.primary"
          gutterBottom
        >
          Dashboard Overview
        </Typography>
        <Typography 
          variant="body2" 
          color="text.secondary"
        >
          Your ad performance metrics this month
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Ads Analyzed"
            value={displayMetrics.adsAnalyzed}
            change={displayMetrics.adsAnalyzedChange}
            trend={displayMetrics.adsAnalyzedChange > 0 ? 'up' : 'down'}
            icon={Assessment}
            subtitle="This month"
            isLoading={isLoading}
            index={0}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Avg Improvement"
            value={displayMetrics.avgImprovement}
            change={displayMetrics.avgImprovementChange}
            trend={displayMetrics.avgImprovementChange > 0 ? 'up' : 'down'}
            icon={TrendingUp}
            subtitle="Score points gained"
            isPercentage={true}
            isLoading={isLoading}
            index={1}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Average Score"
            value={displayMetrics.avgScore}
            change={displayMetrics.avgScoreChange}
            trend={displayMetrics.avgScoreChange > 0 ? 'up' : 'down'}
            icon={Speed}
            subtitle="Across all platforms"
            isLoading={isLoading}
            index={2}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Top Performing"
            value={displayMetrics.topPerforming}
            change={displayMetrics.topPerformingChange}
            trend={displayMetrics.topPerformingChange > 0 ? 'up' : 'down'}
            icon={Star}
            subtitle="Highest score"
            isLoading={isLoading}
            index={3}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default MetricsHeader;