import React from 'react';
import {
  Paper,
  Typography,
  Grid,
  Slider,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  Box,
  Checkbox,
  FormGroup,
  Divider,
  Tooltip,
  IconButton
} from '@mui/material';
import { Help as HelpIcon, AutoAwesome } from '@mui/icons-material';

/**
 * Reusable component for configuring ad copy variation generation options
 * Can be embedded in forms, modals, or sidebars across different input methods
 */
const VariationOptionsCard = ({
  options,
  onChange,
  title = "⚙️ Variation Options",
  variant = "outlined",
  sx = {},
  compact = false,
  showAdvanced = true
}) => {
  const handleOptionChange = (field, value) => {
    onChange({
      ...options,
      [field]: value
    });
  };

  const handleFocusAreaToggle = (areaId) => {
    const currentAreas = options.focusAreas || [];
    const newAreas = currentAreas.includes(areaId)
      ? currentAreas.filter(id => id !== areaId)
      : [...currentAreas, areaId];
    
    handleOptionChange('focusAreas', newAreas);
  };

  const markSliderValue = compact ? [
    { value: 1, label: '1' },
    { value: 3, label: '3' },
    { value: 5, label: '5' },
    { value: 8, label: '8' }
  ] : [
    { value: 1, label: '1' },
    { value: 2, label: '2' },
    { value: 3, label: '3' },
    { value: 4, label: '4' },
    { value: 5, label: '5' },
    { value: 6, label: '6' },
    { value: 7, label: '7' },
    { value: 8, label: '8' }
  ];

  return (
    <Paper 
      variant={variant} 
      sx={{ 
        p: compact ? 2 : 3,
        backgroundColor: 'rgba(245, 158, 11, 0.02)',
        border: '1px solid rgba(245, 158, 11, 0.1)',
        ...sx 
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: compact ? 2 : 3 }}>
        <AutoAwesome sx={{ color: 'warning.main' }} />
        <Typography 
          variant={compact ? "subtitle1" : "h6"} 
          sx={{ 
            fontWeight: 600,
            color: 'warning.main',
            flex: 1
          }}
        >
          {title}
        </Typography>
        <Tooltip title="Configure how many variations to generate and their style">
          <IconButton size="small">
            <HelpIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      <Grid container spacing={compact ? 2 : 3}>
        {/* Number of Variations */}
        <Grid item xs={12} sm={compact ? 12 : 6}>
          <Typography gutterBottom sx={{ fontWeight: 500, mb: 1 }}>
            Number of Variations: {options.numVariations || 3}
          </Typography>
          <Slider
            value={options.numVariations || 3}
            onChange={(_, value) => handleOptionChange('numVariations', value)}
            min={1}
            max={8}
            step={1}
            marks={markSliderValue}
            valueLabelDisplay="auto"
            sx={{
              '& .MuiSlider-markLabel': {
                fontSize: '0.75rem'
              }
            }}
          />
        </Grid>

        {/* Tone Selection */}
        <Grid item xs={12} sm={compact ? 12 : 6}>
          <FormControl fullWidth size={compact ? "small" : "medium"}>
            <InputLabel sx={{ fontWeight: 500 }}>Tone of Voice</InputLabel>
            <Select
              value={options.tone || 'professional'}
              label="Tone of Voice"
              onChange={(e) => handleOptionChange('tone', e.target.value)}
            >
              <MenuItem value="professional">Professional</MenuItem>
              <MenuItem value="casual">Casual</MenuItem>
              <MenuItem value="friendly">Friendly</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
              <MenuItem value="playful">Playful</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Quick Options */}
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mb: 1 }}>
            Quick Options
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: compact ? 'column' : 'row', gap: compact ? 0.5 : 2 }}>
            <FormControlLabel
              control={
                <Switch 
                  checked={options.includeEmojis || false}
                  onChange={(e) => handleOptionChange('includeEmojis', e.target.checked)}
                  size={compact ? "small" : "medium"}
                />
              }
              label="Include Emojis"
              sx={{ fontSize: compact ? '0.875rem' : '1rem' }}
            />
            <FormControlLabel
              control={
                <Switch 
                  checked={options.includeUrgency || false}
                  onChange={(e) => handleOptionChange('includeUrgency', e.target.checked)}
                  size={compact ? "small" : "medium"}
                />
              }
              label="Add Urgency"
              sx={{ fontSize: compact ? '0.875rem' : '1rem' }}
            />
            <FormControlLabel
              control={
                <Switch 
                  checked={options.includeStats || false}
                  onChange={(e) => handleOptionChange('includeStats', e.target.checked)}
                  size={compact ? "small" : "medium"}
                />
              }
              label="Include Stats"
              sx={{ fontSize: compact ? '0.875rem' : '1rem' }}
            />
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default VariationOptionsCard;
