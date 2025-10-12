import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  CircularProgress,
  Typography,
  Paper,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  Slider,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { AutoAwesome, Refresh, CheckCircle } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../../services/apiService';

const GenerateAdInput = ({ onAdCopiesGenerated, onClear, defaultPlatform = 'facebook' }) => {
  const [generating, setGenerating] = useState(false);
  const [generationResults, setGenerationResults] = useState(null);
  
  const { control, handleSubmit, watch, reset, formState: { errors } } = useForm({
    defaultValues: {
      platform: defaultPlatform,
      productService: '',
      valueProposition: '',
      targetAudience: '',
      tone: 'professional',
      industry: '',
      keyBenefits: '',
      numVariations: 3,
      includeEmojis: false,
      includeUrgency: true,
      includeStats: false
    }
  });

  const numVariations = watch('numVariations');

  const toneOptions = [
    { value: 'professional', label: 'Professional' },
    { value: 'casual', label: 'Casual & Friendly' },
    { value: 'urgent', label: 'Urgent & Direct' },
    { value: 'luxury', label: 'Premium & Luxury' },
    { value: 'playful', label: 'Fun & Playful' },
    { value: 'authoritative', label: 'Expert & Authoritative' }
  ];

  const onSubmit = async (data) => {
    setGenerating(true);
    
    try {
      const generationRequest = {
        ...data,
        prompt_context: `Create ${data.numVariations} compelling ad variations for ${data.platform} targeting ${data.targetAudience || 'general audience'}`,
        generation_options: {
          include_emojis: data.includeEmojis,
          include_urgency: data.includeUrgency,
          include_stats: data.includeStats,
          tone: data.tone
        }
      };

      const results = await apiService.generateAdCopy(generationRequest);
      
      if (results.ads && results.ads.length > 0) {
        setGenerationResults(results);
        onAdCopiesGenerated(results.ads);
        toast.success(`🤖 Generated ${results.ads.length} ad variation${results.ads.length > 1 ? 's' : ''}!`);
      } else {
        toast.error('Failed to generate ad variations');
      }
    } catch (error) {
      console.error('Generation failed:', error);
      toast.error(error.message || 'Failed to generate ad copy');
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerateWithChanges = () => {
    setGenerationResults(null);
    if (onClear) onClear();
  };

  const examplePrompts = [
    {
      productService: "Email Marketing Software",
      valueProposition: "Increase open rates by 40% with AI-powered subject lines",
      targetAudience: "Small business owners and marketers",
      keyBenefits: "Easy setup, automated campaigns, detailed analytics"
    },
    {
      productService: "Online Fitness Course",
      valueProposition: "Get fit from home with 15-minute daily workouts",
      targetAudience: "Busy professionals aged 25-45",
      keyBenefits: "No equipment needed, flexible schedule, proven results"
    },
    {
      productService: "Financial Planning App",
      valueProposition: "Take control of your finances and build wealth faster",
      targetAudience: "Young professionals starting their careers",
      keyBenefits: "Budget tracking, investment advice, goal setting"
    }
  ];

  const loadExample = (example) => {
    reset({
      ...watch(),
      ...example
    });
  };

  return (
    <Box>
      {!generationResults ? (
        <Box>
          {/* Instructions */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>How it works:</strong> Describe your product/service and target audience. 
              Our AI will generate compelling ad variations optimized for your selected platform.
            </Typography>
          </Alert>

          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              {/* Platform and Basic Info */}
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Target Platform</InputLabel>
                  <Controller
                    name="platform"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Target Platform">
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

              <Grid item xs={12} sm={6}>
                <Controller
                  name="industry"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Industry (Optional)"
                      fullWidth
                      placeholder="e.g., SaaS, E-commerce, Health & Fitness"
                    />
                  )}
                />
              </Grid>

              {/* Product/Service */}
              <Grid item xs={12}>
                <Controller
                  name="productService"
                  control={control}
                  rules={{ required: 'Product/Service description is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Product/Service"
                      fullWidth
                      required
                      error={!!errors.productService}
                      helperText={errors.productService?.message || "What are you advertising?"}
                      placeholder="e.g., AI-powered email marketing software"
                    />
                  )}
                />
              </Grid>

              {/* Value Proposition */}
              <Grid item xs={12}>
                <Controller
                  name="valueProposition"
                  control={control}
                  rules={{ required: 'Value proposition is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Main Value Proposition"
                      fullWidth
                      required
                      multiline
                      rows={2}
                      error={!!errors.valueProposition}
                      helperText={errors.valueProposition?.message || "What's the main benefit or unique selling point?"}
                      placeholder="e.g., Increase email open rates by 40% with AI-powered optimization"
                    />
                  )}
                />
              </Grid>

              {/* Target Audience */}
              <Grid item xs={12} sm={6}>
                <Controller
                  name="targetAudience"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Target Audience"
                      fullWidth
                      placeholder="e.g., Small business owners, Marketing managers"
                      helperText="Who is your ideal customer?"
                    />
                  )}
                />
              </Grid>

              {/* Tone */}
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Tone of Voice</InputLabel>
                  <Controller
                    name="tone"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Tone of Voice">
                        {toneOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>

              {/* Key Benefits */}
              <Grid item xs={12}>
                <Controller
                  name="keyBenefits"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Key Benefits (Optional)"
                      fullWidth
                      multiline
                      rows={2}
                      placeholder="e.g., Easy setup, 24/7 support, money-back guarantee"
                      helperText="List the main benefits or features to highlight"
                    />
                  )}
                />
              </Grid>

              {/* Generation Options */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    ⚙️ Generation Options
                  </Typography>
                  
                  <Grid container spacing={3}>
                    {/* Number of Variations */}
                    <Grid item xs={12} sm={6}>
                      <Typography gutterBottom>
                        Number of Variations: {numVariations}
                      </Typography>
                      <Controller
                        name="numVariations"
                        control={control}
                        render={({ field }) => (
                          <Slider
                            {...field}
                            min={1}
                            max={8}
                            step={1}
                            marks
                            valueLabelDisplay="auto"
                          />
                        )}
                      />
                    </Grid>

                    {/* Switches */}
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Controller
                          name="includeEmojis"
                          control={control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch {...field} checked={field.value} />}
                              label="Include Emojis"
                            />
                          )}
                        />
                        <Controller
                          name="includeUrgency"
                          control={control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch {...field} checked={field.value} />}
                              label="Add Urgency Elements"
                            />
                          )}
                        />
                        <Controller
                          name="includeStats"
                          control={control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch {...field} checked={field.value} />}
                              label="Include Statistics/Numbers"
                            />
                          )}
                        />
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Quick Examples */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom color="text.secondary">
                  Quick Start Examples (click to use):
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {examplePrompts.map((example, index) => (
                    <Chip
                      key={index}
                      label={example.productService}
                      variant="outlined"
                      clickable
                      size="small"
                      onClick={() => loadExample(example)}
                      sx={{ fontSize: '0.75rem' }}
                    />
                  ))}
                </Box>
              </Grid>

              {/* Actions */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    onClick={() => reset()}
                    disabled={generating}
                  >
                    Clear Form
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={generating ? <CircularProgress size={20} /> : <AutoAwesome />}
                    disabled={generating}
                    sx={{ minWidth: 180 }}
                  >
                    {generating ? 'Generating...' : `Generate ${numVariations} Ads`}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Box>
      ) : (
        <Box>
          {/* Generation Success */}
          <Alert severity="success" sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle fontSize="small" />
              <Typography variant="body2">
                Successfully generated <strong>{generationResults.ads.length}</strong> ad variation{generationResults.ads.length > 1 ? 's' : ''} 
                optimized for {generationResults.platform || 'your target platform'}.
              </Typography>
            </Box>
          </Alert>

          {/* Generated Ads Preview */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              🤖 Generated Ad Variations
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {generationResults.ads.map((ad, index) => (
                <Chip
                  key={index}
                  label={`Variation ${index + 1}: ${ad.headline?.substring(0, 25) || 'Generated Ad'}${ad.headline?.length > 25 ? '...' : ''}`}
                  color="secondary"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
            {generationResults.generation_info && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                Generated with: {generationResults.generation_info}
              </Typography>
            )}
          </Paper>

          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRegenerateWithChanges}
            >
              Generate More Variations
            </Button>
            <Typography variant="body2" color="success.main" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle fontSize="small" />
              Ready to review and analyze
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default GenerateAdInput;
