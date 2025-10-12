import React, { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
  Chip,
  Switch,
  FormControlLabel
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { Controller } from 'react-hook-form';

const EnhancedCopyInputForm = ({ 
  control, 
  errors, 
  title = "📝 Ad Copy Content", 
  subtitle,
  showPlatform = true,
  toolType = null,
  showAdvancedInputs = true
}) => {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const getAdvancedInputsForTool = () => {
    switch (toolType) {
      case 'brand_voice':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Controller
                name="brand_samples"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Brand Voice Samples"
                    fullWidth
                    multiline
                    rows={4}
                    placeholder="Paste 3-5 examples of your existing content (emails, website copy, social posts, etc.)"
                    helperText="The more samples you provide, the better we can match your brand voice"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="brand_tone"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Desired Brand Tone</InputLabel>
                    <Select {...field} label="Desired Brand Tone">
                      <MenuItem value="professional">Professional</MenuItem>
                      <MenuItem value="casual">Casual</MenuItem>
                      <MenuItem value="friendly">Friendly</MenuItem>
                      <MenuItem value="authoritative">Authoritative</MenuItem>
                      <MenuItem value="playful">Playful</MenuItem>
                      <MenuItem value="sophisticated">Sophisticated</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="voice_characteristics"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Voice Characteristics"
                    fullWidth
                    placeholder="e.g., witty, direct, empathetic"
                    helperText="Describe your brand's personality"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 'compliance':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="strict_mode"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Compliance Level</InputLabel>
                    <Select {...field} label="Compliance Level">
                      <MenuItem value={false}>Standard Check</MenuItem>
                      <MenuItem value={true}>Strict Mode (Extra Safe)</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="regulatory_context"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Regulatory Context"
                    fullWidth
                    placeholder="e.g., Healthcare, Financial, Food & Beverage"
                    helperText="Industry-specific regulations to check"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 'psychology':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Controller
                name="psychology_focus"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Psychology Focus Areas"
                    fullWidth
                    placeholder="e.g., urgency, social proof, authority, scarcity"
                    helperText="Specific psychological triggers to analyze for"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="customer_mindset"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Customer Mindset</InputLabel>
                    <Select {...field} label="Customer Mindset">
                      <MenuItem value="problem_aware">Problem Aware</MenuItem>
                      <MenuItem value="solution_aware">Solution Aware</MenuItem>
                      <MenuItem value="product_aware">Product Aware</MenuItem>
                      <MenuItem value="most_aware">Most Aware</MenuItem>
                      <MenuItem value="unaware">Unaware</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="buying_stage"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Buying Stage</InputLabel>
                    <Select {...field} label="Buying Stage">
                      <MenuItem value="awareness">Awareness</MenuItem>
                      <MenuItem value="consideration">Consideration</MenuItem>
                      <MenuItem value="decision">Decision</MenuItem>
                      <MenuItem value="retention">Retention</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
          </Grid>
        );

      case 'legal':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="risk_tolerance"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Risk Tolerance</InputLabel>
                    <Select {...field} label="Risk Tolerance">
                      <MenuItem value="conservative">Conservative (Lowest Risk)</MenuItem>
                      <MenuItem value="moderate">Moderate Risk</MenuItem>
                      <MenuItem value="aggressive">Aggressive (Higher Risk)</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="legal_jurisdiction"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Legal Jurisdiction"
                    fullWidth
                    placeholder="e.g., US, EU, UK, Global"
                    helperText="Primary jurisdiction for legal compliance"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 'roi_generator':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="roi_target"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Target ROI (%)"
                    fullWidth
                    type="number"
                    placeholder="300"
                    helperText="Desired return on investment percentage"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="customer_ltv"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Customer LTV ($)"
                    fullWidth
                    type="number"
                    placeholder="1000"
                    helperText="Average customer lifetime value"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="value_proposition"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Unique Value Proposition"
                    fullWidth
                    multiline
                    rows={2}
                    placeholder="What makes your product/service uniquely valuable?"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 'performance_forensics':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="current_performance"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Current CTR (%)"
                    fullWidth
                    type="number"
                    step="0.01"
                    placeholder="2.5"
                    helperText="Current click-through rate"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="target_performance"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Target CTR (%)"
                    fullWidth
                    type="number"
                    step="0.01"
                    placeholder="5.0"
                    helperText="Desired click-through rate"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="performance_context"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Performance Context"
                    fullWidth
                    multiline
                    rows={2}
                    placeholder="Any additional context about current performance challenges?"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  return (
    <Paper variant="outlined" sx={{ p: 3, backgroundColor: 'rgba(124, 58, 237, 0.02)', border: '1px solid rgba(124, 58, 237, 0.1)' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'secondary.main', mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        {title}
      </Typography>
      
      {subtitle && (
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          {subtitle}
        </Typography>
      )}
      
      <Grid container spacing={3}>
        {/* Platform Selection */}
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
                  </Select>
                )}
              />
            </FormControl>
          </Grid>
        )}
        
        {/* Industry */}
        <Grid item xs={12} sm={showPlatform ? 6 : 12}>
          <Controller
            name="industry"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Industry (Optional)"
                fullWidth
                placeholder="e.g., SaaS, E-commerce, Fitness"
                InputLabelProps={{ sx: { fontWeight: 500 } }}
              />
            )}
          />
        </Grid>

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
              />
            )}
          />
        </Grid>

        {/* CTA and Target Audience */}
        <Grid item xs={12} sm={6}>
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
              />
            )}
          />
        </Grid>
        
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
              />
            )}
          />
        </Grid>
      </Grid>

      {/* Advanced Tool-Specific Inputs */}
      {showAdvancedInputs && toolType && (
        <Box sx={{ mt: 3 }}>
          <Accordion expanded={advancedOpen} onChange={() => setAdvancedOpen(!advancedOpen)}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                🔧 Advanced {toolType.replace('_', ' ')} Settings
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              {getAdvancedInputsForTool()}
            </AccordionDetails>
          </Accordion>
        </Box>
      )}
    </Paper>
  );
};

export default EnhancedCopyInputForm;
