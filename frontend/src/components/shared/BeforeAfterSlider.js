import React, { useState } from 'react';
import {
  Box,
  Typography,
  Slider,
  Paper,
  Grid,
  IconButton
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown,
  CompareArrows,
  SwapHoriz
} from '@mui/icons-material';

const BeforeAfterSlider = ({ beforeData, afterData, title = "Performance Transformation" }) => {
  const [sliderValue, setSliderValue] = useState(50);

  const handleSliderChange = (event, newValue) => {
    setSliderValue(newValue);
  };

  const metrics = [
    { key: 'ctr', label: 'CTR', suffix: '%', color: '#10b981' },
    { key: 'cpc', label: 'CPC', prefix: '$', color: '#3b82f6' },
    { key: 'roas', label: 'ROAS', suffix: 'x', color: '#8b5cf6' },
    { key: 'profit', label: 'Monthly Profit', prefix: '$', color: '#f59e0b' }
  ];

  const calculateDisplayValue = (beforeValue, afterValue) => {
    const progress = sliderValue / 100;
    return beforeValue + (afterValue - beforeValue) * progress;
  };

  const formatValue = (value, prefix = '', suffix = '') => {
    if (prefix === '$' && Math.abs(value) >= 1000) {
      return `${prefix}${(value / 1000).toFixed(1)}K${suffix}`;
    }
    return `${prefix}${value.toFixed(value % 1 === 0 ? 0 : 1)}${suffix}`;
  };

  const getColorIntensity = (progress) => {
    // Interpolate between red (poor) and green (good)
    const red = Math.round(239 - (239 - 16) * progress); // From #ef4444 to #10b981
    const green = Math.round(68 + (185 - 68) * progress);
    const blue = Math.round(68 + (129 - 68) * progress);
    return `rgb(${red}, ${green}, ${blue})`;
  };

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h5" sx={{
        textAlign: 'center',
        fontWeight: 700,
        mb: 4,
        color: '#F9FAFB'
      }}>
        {title}
      </Typography>

      {/* Interactive Slider */}
      <Box sx={{ mb: 6, px: 4 }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 2
        }}>
          <Typography variant="body2" sx={{ 
            color: '#ef4444',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center'
          }}>
            <TrendingDown sx={{ mr: 1, fontSize: 18 }} />
            BEFORE
          </Typography>
          <IconButton 
            size="small"
            sx={{ color: '#C084FC' }}
            onClick={() => setSliderValue(sliderValue === 0 ? 100 : 0)}
          >
            <SwapHoriz />
          </IconButton>
          <Typography variant="body2" sx={{ 
            color: '#10b981',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center'
          }}>
            AFTER
            <TrendingUp sx={{ ml: 1, fontSize: 18 }} />
          </Typography>
        </Box>
        
        <Slider
          value={sliderValue}
          onChange={handleSliderChange}
          min={0}
          max={100}
          sx={{
            height: 8,
            '& .MuiSlider-track': {
              background: 'linear-gradient(90deg, #ef4444 0%, #10b981 100%)',
              border: 'none'
            },
            '& .MuiSlider-thumb': {
              height: 24,
              width: 24,
              backgroundColor: '#C084FC',
              border: '3px solid rgba(192, 132, 252, 0.3)',
              '&:focus, &:hover, &.Mui-active, &.Mui-focusVisible': {
                boxShadow: '0 0 0 8px rgba(192, 132, 252, 0.16)',
              },
            },
            '& .MuiSlider-rail': {
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none'
            }
          }}
        />
        
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
            Slide to see the transformation in real-time
          </Typography>
        </Box>
      </Box>

      {/* Metrics Display */}
      <Grid container spacing={3}>
        {metrics.map((metric, index) => {
          const beforeValue = beforeData[metric.key];
          const afterValue = afterData[metric.key];
          const currentValue = calculateDisplayValue(beforeValue, afterValue);
          const progress = (currentValue - beforeValue) / (afterValue - beforeValue);
          
          return (
            <Grid item xs={6} sm={3} key={metric.key}>
              <Paper sx={{
                background: `linear-gradient(135deg, ${getColorIntensity(progress)}20 0%, ${getColorIntensity(progress)}10 100%)`,
                border: `2px solid ${getColorIntensity(progress)}40`,
                borderRadius: 3,
                p: 3,
                textAlign: 'center',
                transition: 'all 0.3s ease',
                transform: `scale(${1 + progress * 0.05})`,
                '&:hover': {
                  transform: `scale(${1.05 + progress * 0.05})`
                }
              }}>
                <Typography variant="body2" sx={{
                  color: '#E5E7EB',
                  fontWeight: 600,
                  mb: 1,
                  textTransform: 'uppercase',
                  fontSize: '0.8rem'
                }}>
                  {metric.label}
                </Typography>
                
                <Typography variant="h4" sx={{
                  color: getColorIntensity(progress),
                  fontWeight: 800,
                  mb: 1,
                  fontSize: { xs: '1.5rem', sm: '2rem' }
                }}>
                  {formatValue(
                    currentValue, 
                    metric.prefix || '', 
                    metric.suffix || ''
                  )}
                </Typography>

                {/* Improvement indicator */}
                {sliderValue > 10 && (
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    mt: 1
                  }}>
                    <TrendingUp sx={{ 
                      color: '#10b981', 
                      fontSize: 16, 
                      mr: 0.5 
                    }} />
                    <Typography variant="body2" sx={{
                      color: '#10b981',
                      fontWeight: 600,
                      fontSize: '0.75rem'
                    }}>
                      +{Math.round(((afterValue - beforeValue) / beforeValue) * 100)}%
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          );
        })}
      </Grid>

      {/* Progress Message */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography variant="body1" sx={{
          color: getColorIntensity(sliderValue / 100),
          fontWeight: 600,
          fontSize: '1.1rem'
        }}>
          {sliderValue < 25 && "😞 Current underperforming state"}
          {sliderValue >= 25 && sliderValue < 50 && "📈 Starting to see improvement"}  
          {sliderValue >= 50 && sliderValue < 75 && "🚀 Significant performance gains"}
          {sliderValue >= 75 && "🎉 Optimized high-performance state"}
        </Typography>
      </Box>
    </Box>
  );
};

export default BeforeAfterSlider;