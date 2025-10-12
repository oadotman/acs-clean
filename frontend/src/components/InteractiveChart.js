import React, { Suspense, useState, useMemo } from 'react';
import {
  Paper,
  Box,
  Typography,
  FormControlLabel,
  Switch,
  Chip,
  CircularProgress,
  useTheme,
  ToggleButtonGroup,
  ToggleButton,
  Skeleton
} from '@mui/material';
import {
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  TrendingUp,
  Timeline
} from '@mui/icons-material';

// Lazy load chart components to reduce bundle size
const BarChart = React.lazy(() => import('recharts').then(module => ({ 
  default: module.BarChart 
})));
const LineChart = React.lazy(() => import('recharts').then(module => ({ 
  default: module.LineChart 
})));
const PieChart = React.lazy(() => import('recharts').then(module => ({ 
  default: module.PieChart 
})));
const Area = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Area 
})));
const AreaChart = React.lazy(() => import('recharts').then(module => ({ 
  default: module.AreaChart 
})));
const Cell = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Cell 
})));
const Pie = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Pie 
})));
const Bar = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Bar 
})));
const Line = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Line 
})));
const XAxis = React.lazy(() => import('recharts').then(module => ({ 
  default: module.XAxis 
})));
const YAxis = React.lazy(() => import('recharts').then(module => ({ 
  default: module.YAxis 
})));
const CartesianGrid = React.lazy(() => import('recharts').then(module => ({ 
  default: module.CartesianGrid 
})));
const Tooltip = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Tooltip 
})));
const ResponsiveContainer = React.lazy(() => import('recharts').then(module => ({ 
  default: module.ResponsiveContainer 
})));
const Legend = React.lazy(() => import('recharts').then(module => ({ 
  default: module.Legend 
})));

/**
 * Enhanced interactive chart component with lazy loading
 */
const InteractiveChart = ({
  title,
  data = [],
  type = 'bar',
  height = 300,
  loading = false,
  error = null,
  showLegend = true,
  showGrid = true,
  colors = ['#2563eb', '#7c3aed', '#f59e0b', '#10b981', '#ef4444'],
  ...props
}) => {
  const theme = useTheme();
  const [chartType, setChartType] = useState(type);
  const [legendVisible, setLegendVisible] = useState(showLegend);
  const [gridVisible, setGridVisible] = useState(showGrid);

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Paper
          sx={{
            p: 2,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            maxWidth: 250
          }}
        >
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
            {label}
          </Typography>
          {payload.map((entry, index) => (
            <Box key={index} display="flex" alignItems="center" gap={1} sx={{ mb: 0.5 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: entry.color
                }}
              />
              <Typography variant="body2" sx={{ flex: 1 }}>
                {entry.name}: <strong>{entry.value}</strong>
              </Typography>
            </Box>
          ))}
        </Paper>
      );
    }
    return null;
  };

  // Chart type options
  const chartTypes = [
    { value: 'bar', icon: BarChartIcon, label: 'Bar Chart' },
    { value: 'line', icon: TrendingUp, label: 'Line Chart' },
    { value: 'area', icon: Timeline, label: 'Area Chart' },
    { value: 'pie', icon: PieChartIcon, label: 'Pie Chart' }
  ];

  // Memoized chart rendering
  const renderChart = useMemo(() => {
    if (!data || data.length === 0) return null;

    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 20 }
    };

    switch (chartType) {
      case 'bar':
        return (
          <BarChart {...commonProps}>
            {gridVisible && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
            <XAxis 
              dataKey="month" 
              stroke={theme.palette.text.secondary}
              fontSize="12"
            />
            <YAxis 
              stroke={theme.palette.text.secondary}
              fontSize="12"
            />
            <Tooltip content={<CustomTooltip />} />
            {legendVisible && <Legend />}
            <Bar 
              dataKey="analyses" 
              fill={colors[0]}
              name="Analyses"
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="avg_score" 
              fill={colors[1]}
              name="Avg Score"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        );

      case 'line':
        return (
          <LineChart {...commonProps}>
            {gridVisible && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
            <XAxis 
              dataKey="month" 
              stroke={theme.palette.text.secondary}
              fontSize="12"
            />
            <YAxis 
              stroke={theme.palette.text.secondary}
              fontSize="12"
            />
            <Tooltip content={<CustomTooltip />} />
            {legendVisible && <Legend />}
            <Line 
              type="monotone" 
              dataKey="analyses" 
              stroke={colors[0]}
              strokeWidth={3}
              dot={{ fill: colors[0], strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: colors[0], strokeWidth: 2, fill: 'white' }}
              name="Analyses"
            />
            <Line 
              type="monotone" 
              dataKey="avg_score" 
              stroke={colors[1]}
              strokeWidth={3}
              dot={{ fill: colors[1], strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: colors[1], strokeWidth: 2, fill: 'white' }}
              name="Avg Score"
            />
          </LineChart>
        );

      case 'area':
        return (
          <AreaChart {...commonProps}>
            {gridVisible && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
            <XAxis 
              dataKey="month" 
              stroke={theme.palette.text.secondary}
              fontSize="12"
            />
            <YAxis 
              stroke={theme.palette.text.secondary}
              fontSize="12"
            />
            <Tooltip content={<CustomTooltip />} />
            {legendVisible && <Legend />}
            <Area
              type="monotone"
              dataKey="analyses"
              stackId="1"
              stroke={colors[0]}
              fill={`${colors[0]}40`}
              name="Analyses"
            />
            <Area
              type="monotone"
              dataKey="avg_score"
              stackId="2"
              stroke={colors[1]}
              fill={`${colors[1]}40`}
              name="Avg Score"
            />
          </AreaChart>
        );

      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="analyses"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            {legendVisible && <Legend />}
          </PieChart>
        );

      default:
        return null;
    }
  }, [chartType, data, theme, colors, gridVisible, legendVisible]);

  // Loading skeleton
  const ChartSkeleton = () => (
    <Box sx={{ p: 3 }}>
      <Skeleton variant="rectangular" width="100%" height={height} sx={{ borderRadius: 2 }} />
    </Box>
  );

  return (
    <Paper sx={{ overflow: 'hidden', ...props.sx }}>
      {/* Chart Header */}
      <Box
        sx={{
          p: 3,
          pb: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'grey.50'
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight={600}>
            {title}
          </Typography>
          {data && data.length > 0 && (
            <Chip
              label={`${data.length} data points`}
              size="small"
              variant="outlined"
              color="primary"
            />
          )}
        </Box>

        {/* Chart Controls */}
        <Box display="flex" flexWrap="wrap" gap={2} alignItems="center">
          {/* Chart Type Selector */}
          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={(event, newType) => {
              if (newType !== null) {
                setChartType(newType);
              }
            }}
            size="small"
          >
            {chartTypes.map((type) => (
              <ToggleButton key={type.value} value={type.value} sx={{ px: 2 }}>
                <type.icon sx={{ fontSize: '1rem', mr: 0.5 }} />
                {type.label}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>

          {/* Display Options */}
          <Box display="flex" gap={1}>
            <FormControlLabel
              control={
                <Switch
                  checked={legendVisible}
                  onChange={(e) => setLegendVisible(e.target.checked)}
                  size="small"
                />
              }
              label="Legend"
              sx={{ fontSize: '0.875rem' }}
            />
            {chartType !== 'pie' && (
              <FormControlLabel
                control={
                  <Switch
                    checked={gridVisible}
                    onChange={(e) => setGridVisible(e.target.checked)}
                    size="small"
                  />
                }
                label="Grid"
                sx={{ fontSize: '0.875rem' }}
              />
            )}
          </Box>
        </Box>
      </Box>

      {/* Chart Content */}
      <Box sx={{ position: 'relative', minHeight: height }}>
        {loading ? (
          <ChartSkeleton />
        ) : error ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height,
              color: 'text.secondary'
            }}
          >
            <Typography variant="body2">Error loading chart data</Typography>
            <Typography variant="caption">{error.message}</Typography>
          </Box>
        ) : !data || data.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height,
              color: 'text.secondary'
            }}
          >
            <Typography variant="body2">No data available</Typography>
            <Typography variant="caption">Data will appear here once available</Typography>
          </Box>
        ) : (
          <Box sx={{ p: 3 }}>
            <Suspense fallback={<ChartSkeleton />}>
              <ResponsiveContainer width="100%" height={height}>
                {renderChart}
              </ResponsiveContainer>
            </Suspense>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default InteractiveChart;
