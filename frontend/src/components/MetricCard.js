import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  HelpOutline as HelpIcon
} from '@mui/icons-material';

/**
 * Reusable MetricCard component with performance color coding and trend indicators
 * 
 * @param {Object} props
 * @param {string} props.title - Card title
 * @param {number|string} props.value - Main metric value
 * @param {string} props.subtitle - Supporting text below value
 * @param {React.ElementType} props.icon - Material-UI icon component
 * @param {'primary'|'secondary'|'success'|'warning'|'error'} props.color - Color theme
 * @param {Object} props.trend - Trend data {value: number, direction: 'up'|'down'|'flat'}
 * @param {string} props.chipLabel - Optional chip/badge label
 * @param {'small'|'medium'|'large'} props.size - Card size variant
 * @param {boolean} props.loading - Loading state
 * @param {string} props.tooltip - Help tooltip text
 * @param {function} props.onClick - Click handler
 */
const MetricCard = ({
  title,
  value,
  subtitle,
  icon: IconComponent,
  color = 'primary',
  trend,
  chipLabel,
  size = 'medium',
  loading = false,
  tooltip,
  onClick,
  ...props
}) => {
  const theme = useTheme();

  // Color mapping for performance tiers
  const getColorConfig = (colorKey) => {
    const configs = {
      primary: {
        main: theme.palette.primary.main,
        light: theme.palette.primary.light,
        bg: 'rgba(37, 99, 235, 0.1)',
      },
      secondary: {
        main: theme.palette.secondary.main,
        light: theme.palette.secondary.light,
        bg: 'rgba(124, 58, 237, 0.1)',
      },
      success: {
        main: theme.palette.success.main,
        light: theme.palette.success.light,
        bg: 'rgba(16, 185, 129, 0.1)',
      },
      warning: {
        main: theme.palette.warning.main,
        light: theme.palette.warning.light,
        bg: 'rgba(245, 158, 11, 0.1)',
      },
      error: {
        main: theme.palette.error.main,
        light: theme.palette.error.light,
        bg: 'rgba(239, 68, 68, 0.1)',
      },
    };
    return configs[colorKey] || configs.primary;
  };

  const colorConfig = getColorConfig(color);

  // Trend icon and color
  const getTrendConfig = (trendData) => {
    if (!trendData) return null;
    
    const { direction, value: trendValue } = trendData;
    const configs = {
      up: {
        icon: TrendingUpIcon,
        color: theme.palette.success.main,
        symbol: '▲',
      },
      down: {
        icon: TrendingDownIcon,
        color: theme.palette.error.main,
        symbol: '▼',
      },
      flat: {
        icon: TrendingFlatIcon,
        color: theme.palette.text.secondary,
        symbol: '●',
      },
    };
    
    return {
      ...configs[direction],
      value: trendValue,
    };
  };

  const trendConfig = getTrendConfig(trend);

  // Size configurations
  const sizeConfig = {
    small: {
      iconSize: 32,
      valueSize: 'h4',
      cardPadding: 2,
    },
    medium: {
      iconSize: 40,
      valueSize: 'h3',
      cardPadding: 3,
    },
    large: {
      iconSize: 48,
      valueSize: 'h2',
      cardPadding: 4,
    },
  };

  const config = sizeConfig[size];

  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'visible',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease-in-out',
        background: `linear-gradient(135deg, ${colorConfig.bg} 0%, rgba(255, 255, 255, 0.9) 100%)`,
        border: `1px solid ${colorConfig.bg}`,
        '&:hover': onClick ? {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
          '& .metric-icon': {
            transform: 'scale(1.1)',
          },
        } : {},
        ...props.sx,
      }}
      onClick={onClick}
    >
      <CardContent sx={{ p: config.cardPadding }}>
        {/* Header with icon and chip */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box
            className="metric-icon"
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: config.iconSize,
              height: config.iconSize,
              borderRadius: '50%',
              bgcolor: colorConfig.main,
              color: 'white',
              transition: 'all 0.3s ease-in-out',
              boxShadow: `0 4px 20px ${colorConfig.main}30`,
            }}
          >
            {loading ? (
              <CircularProgress size={config.iconSize * 0.6} color="inherit" />
            ) : (
              <IconComponent sx={{ fontSize: config.iconSize * 0.6 }} />
            )}
          </Box>
          
          <Box display="flex" alignItems="center" gap={1}>
            {chipLabel && (
              <Chip
                label={chipLabel}
                size="small"
                variant="outlined"
                color={color}
                sx={{
                  height: 24,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}
              />
            )}
            {tooltip && (
              <Tooltip title={tooltip} placement="top">
                <HelpIcon sx={{ fontSize: '1rem', color: 'text.secondary', cursor: 'help' }} />
              </Tooltip>
            )}
          </Box>
        </Box>

        {/* Title */}
        <Typography 
          variant="h6" 
          color="text.secondary" 
          fontWeight={500}
          gutterBottom
          sx={{ mb: 1 }}
        >
          {title}
        </Typography>

        {/* Main Value with Trend */}
        <Box display="flex" alignItems="baseline" gap={1} mb={1}>
          <Typography 
            variant={config.valueSize} 
            color={colorConfig.main} 
            fontWeight="bold"
            sx={{ lineHeight: 1.2 }}
          >
            {loading ? '...' : value}
          </Typography>
          
          {trendConfig && !loading && (
            <Box display="flex" alignItems="center" gap={0.5}>
              <Box
                component="span"
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  color: trendConfig.color,
                  fontSize: '0.875rem',
                  fontWeight: 600,
                }}
              >
                {trendConfig.symbol} {Math.abs(trendConfig.value)}%
              </Box>
            </Box>
          )}
        </Box>

        {/* Subtitle */}
        <Typography 
          variant="body2" 
          color="text.secondary"
          sx={{ lineHeight: 1.4 }}
        >
          {subtitle}
        </Typography>

        {/* Performance Bar (optional) */}
        {trend?.showProgress && (
          <Box 
            sx={{ 
              mt: 2, 
              height: 4, 
              bgcolor: 'grey.200', 
              borderRadius: 2,
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            <Box
              sx={{
                height: '100%',
                width: `${Math.min(Math.max(trend.value || 0, 0), 100)}%`,
                bgcolor: trendConfig?.color || colorConfig.main,
                borderRadius: 2,
                transition: 'width 0.8s ease-in-out',
              }}
            />
          </Box>
        )}
      </CardContent>

      {/* Decorative gradient overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: 60,
          height: 60,
          background: `radial-gradient(circle at center, ${colorConfig.main}15 0%, transparent 70%)`,
          borderRadius: '50%',
          transform: 'translate(20px, -20px)',
          pointerEvents: 'none',
        }}
      />
    </Card>
  );
};

export default MetricCard;
