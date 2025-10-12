import React from 'react';
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Typography,
} from '@mui/material';
import { Controller } from 'react-hook-form';

const CopyInputForm = ({ 
  control, 
  errors, 
  showPlatform = true, 
  showIndustry = true,
  showTargetAudience = true,
  title = "📝 Ad Content",
  subtitle = "Enter your ad copy details for analysis"
}) => {
  return (
    <Paper 
      variant="outlined" 
      sx={{ 
        p: 3, 
        backgroundColor: 'rgba(124, 58, 237, 0.02)',
        border: '1px solid rgba(124, 58, 237, 0.1)'
      }}
    >
      <Typography 
        variant="h6" 
        gutterBottom 
        sx={{ 
          fontWeight: 600,
          color: 'secondary.main',
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        {title}
      </Typography>
      
      {subtitle && (
        <Typography 
          variant="body2" 
          color="textSecondary" 
          sx={{ mb: 3 }}
        >
          {subtitle}
        </Typography>
      )}
      
      <Grid container spacing={3}>
        {/* Platform and Industry Row */}
        {(showPlatform || showIndustry) && (
          <>
            {showPlatform && (
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel sx={{ fontWeight: 500 }}>Platform *</InputLabel>
                  <Controller
                    name="platform"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Platform *">
                        <MenuItem value="facebook">Facebook Ads</MenuItem>
                        <MenuItem value="google">Google Ads</MenuItem>
                        <MenuItem value="linkedin">LinkedIn Ads</MenuItem>
                        <MenuItem value="tiktok">TikTok Ads</MenuItem>
                        <MenuItem value="instagram">Instagram Ads</MenuItem>
                        <MenuItem value="twitter">Twitter Ads</MenuItem>
                        <MenuItem value="youtube">YouTube Ads</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
            )}
            
            {showIndustry && (
              <Grid item xs={12} sm={6}>
                <Controller
                  name="industry"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Industry (Optional)"
                      fullWidth
                      placeholder="e.g., SaaS, E-commerce, Fitness, Finance"
                      InputLabelProps={{ sx: { fontWeight: 500 } }}
                    />
                  )}
                />
              </Grid>
            )}
          </>
        )}

        {/* Headline */}
        <Grid item xs={12}>
          <Controller
            name="headline"
            control={control}
            rules={{ required: 'Headline is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Headline"
                fullWidth
                required
                error={!!errors.headline}
                helperText={errors.headline?.message || "The main attention-grabbing text of your ad"}
                placeholder="Enter your compelling ad headline..."
                InputLabelProps={{ sx: { fontWeight: 500 } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.7)'
                  }
                }}
              />
            )}
          />
        </Grid>

        {/* Body Text */}
        <Grid item xs={12}>
          <Controller
            name="body_text"
            control={control}
            rules={{ required: 'Body text is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Body Text"
                fullWidth
                required
                multiline
                rows={4}
                error={!!errors.body_text}
                helperText={errors.body_text?.message || "The main content that explains your value proposition"}
                placeholder="Enter your ad body text..."
                InputLabelProps={{ sx: { fontWeight: 500 } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.7)'
                  }
                }}
              />
            )}
          />
        </Grid>

        {/* CTA and Target Audience Row */}
        <Grid item xs={12} sm={showTargetAudience ? 6 : 12}>
          <Controller
            name="cta"
            control={control}
            rules={{ required: 'Call-to-action is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Call-to-Action"
                fullWidth
                required
                error={!!errors.cta}
                helperText={errors.cta?.message || "The action you want users to take"}
                placeholder="e.g., Get Started Free, Learn More, Shop Now"
                InputLabelProps={{ sx: { fontWeight: 500 } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.7)'
                  }
                }}
              />
            )}
          />
        </Grid>
        
        {showTargetAudience && (
          <Grid item xs={12} sm={6}>
            <Controller
              name="target_audience"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
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
              )}
            />
          </Grid>
        )}
      </Grid>
    </Paper>
  );
};

export default CopyInputForm;
