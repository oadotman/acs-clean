import React, { useState, useEffect } from 'react';
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
} from '@mui/material';

const EditableAdForm = ({ 
  initialValues = {},
  onUpdate,
  showPlatform = true, 
  showIndustry = true,
  showTargetAudience = true,
}) => {
  const [values, setValues] = useState({
    headline: '',
    body_text: '',
    cta: '',
    platform: 'facebook',
    industry: '',
    target_audience: '',
    ...initialValues
  });

  useEffect(() => {
    setValues(prev => ({
      ...prev,
      ...initialValues
    }));
  }, [initialValues]);

  const handleChange = (field) => (event) => {
    const newValues = {
      ...values,
      [field]: event.target.value
    };
    setValues(newValues);
    
    // Debounced update to parent
    if (onUpdate) {
      onUpdate(newValues);
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Platform and Industry Row */}
        {(showPlatform || showIndustry) && (
          <>
            {showPlatform && (
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel sx={{ fontWeight: 500 }}>Platform *</InputLabel>
                  <Select 
                    value={values.platform || 'facebook'}
                    onChange={handleChange('platform')}
                    label="Platform *"
                  >
                    <MenuItem value="facebook">Facebook Ads</MenuItem>
                    <MenuItem value="google">Google Ads</MenuItem>
                    <MenuItem value="linkedin">LinkedIn Ads</MenuItem>
                    <MenuItem value="tiktok">TikTok Ads</MenuItem>
                    <MenuItem value="instagram">Instagram Ads</MenuItem>
                    <MenuItem value="twitter">Twitter Ads</MenuItem>
                    <MenuItem value="youtube">YouTube Ads</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            
            {showIndustry && (
              <Grid item xs={12} sm={6}>
                <TextField
                  value={values.industry || ''}
                  onChange={handleChange('industry')}
                  label="Industry (Optional)"
                  fullWidth
                  placeholder="e.g., SaaS, E-commerce, Fitness, Finance"
                  InputLabelProps={{ sx: { fontWeight: 500 } }}
                />
              </Grid>
            )}
          </>
        )}

        {/* Headline */}
        <Grid item xs={12}>
          <TextField
            value={values.headline || ''}
            onChange={handleChange('headline')}
            label="Headline"
            fullWidth
            required
            placeholder="Enter your compelling ad headline..."
            InputLabelProps={{ sx: { fontWeight: 500 } }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.7)'
              }
            }}
          />
        </Grid>

        {/* Body Text */}
        <Grid item xs={12}>
          <TextField
            value={values.body_text || ''}
            onChange={handleChange('body_text')}
            label="Body Text"
            fullWidth
            required
            multiline
            rows={4}
            placeholder="Enter your ad body text..."
            InputLabelProps={{ sx: { fontWeight: 500 } }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.7)'
              }
            }}
          />
        </Grid>

        {/* CTA and Target Audience Row */}
        <Grid item xs={12} sm={showTargetAudience ? 6 : 12}>
          <TextField
            value={values.cta || ''}
            onChange={handleChange('cta')}
            label="Call-to-Action"
            fullWidth
            required
            placeholder="e.g., Get Started Free, Learn More, Shop Now"
            InputLabelProps={{ sx: { fontWeight: 500 } }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.7)'
              }
            }}
          />
        </Grid>
        
        {showTargetAudience && (
          <Grid item xs={12} sm={6}>
            <TextField
              value={values.target_audience || ''}
              onChange={handleChange('target_audience')}
              label="Target Audience (Optional)"
              fullWidth
              placeholder="e.g., SMB owners, Marketing agencies"
              helperText="Help us provide more targeted insights"
              InputLabelProps={{ sx: { fontWeight: 500 } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.7)'
                }
              }}
            />
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default EditableAdForm;
