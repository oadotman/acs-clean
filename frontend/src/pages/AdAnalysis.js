import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  CircularProgress,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import { ContentCopy, Edit } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import PasteInput from '../components/input/PasteInput';
import FileUploadInput from '../components/input/FileUploadInput';
import GenerateAdInput from '../components/input/GenerateAdInput';
import AdCopyReview from '../components/input/AdCopyReview';
import IntelligentContentAssistant from '../components/shared/IntelligentContentAssistant';
import sharedWorkflowService from '../services/sharedWorkflowService';

const AdAnalysis = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inputMethod, setInputMethod] = useState('manual');
  const [adCopies, setAdCopies] = useState([]);
  
  
  const { control, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    defaultValues: {
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      target_audience: '',
      industry: ''
    }
  });
  
  // Handle pre-filled data from onboarding
  useEffect(() => {
    const prefillData = location.state?.prefillData;
    if (prefillData) {
      setValue('headline', prefillData.headline || '');
      setValue('body_text', prefillData.body_text || '');
      setValue('cta', prefillData.cta || '');
      setValue('platform', prefillData.platform || 'facebook');
      setValue('industry', prefillData.industry || '');
      setValue('target_audience', prefillData.target_audience || '');
      
      // Show variation options if coming from onboarding
      if (location.state?.isFromOnboarding) {
        setShowVariationOptions(true);
      }
    }
  }, [location.state, setValue]);


  // Ad copies management functions
  const addAdCopy = () => {
    const newAdCopy = {
      id: Date.now().toString(),
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: '',
      target_audience: ''
    };
    setAdCopies(prev => [...prev, newAdCopy]);
  };

  const updateAdCopy = (id, updatedData) => {
    setAdCopies(prev => prev.map(ad => 
      (ad.id === id || prev.indexOf(ad) === id) ? { ...ad, ...updatedData, id: ad.id } : ad
    ));
  };

  const removeAdCopy = (id) => {
    if (adCopies.length > 1) {
      setAdCopies(prev => prev.filter((ad, index) => ad.id !== id && index !== id));
    }
  };

  const handleAdCopiesParsed = (newAdCopies) => {
    const adsWithIds = newAdCopies.map(ad => ({
      ...ad,
      id: Date.now().toString() + Math.random().toString(36).substring(2)
    }));
    setAdCopies(adsWithIds);
  };

  const handleClearAdCopies = () => {
    setAdCopies([]);
  };

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simplified workflow - just run analysis with auto-generated project name
      const analysisData = {
        headline: data.headline,
        body_text: data.body_text,
        cta: data.cta,
        platform: data.platform,
        target_audience: data.target_audience || null,
        industry: data.industry || null
      };

      const response = await sharedWorkflowService.startAdhocAnalysis(analysisData);
      
      toast.success(`Analysis started! Project: "${response.project_name}"`);
      navigate(`/project/${response.project_id}/results`);
      
    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Analysis failed';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  

  const handleAnalyzeAll = async () => {
    setLoading(true);
    setError(null);

    try {
      const validAds = adCopies.filter(ad => ad.headline && ad.body_text && ad.cta);
      
      if (validAds.length === 0) {
        toast.error('Please ensure all ads have headline, body text, and CTA filled');
        return;
      }

      if (validAds.length === 1) {
        // Single ad - use simplified analysis workflow
        const analysisData = {
          headline: validAds[0].headline,
          body_text: validAds[0].body_text,
          cta: validAds[0].cta,
          platform: validAds[0].platform,
          industry: validAds[0].industry,
          target_audience: validAds[0].target_audience
        };
        
        const response = await sharedWorkflowService.startAdhocAnalysis(analysisData);
        
        toast.success(`Analysis started! Project: "${response.project_name}"`);
        navigate(`/project/${response.project_id}/results`);
      } else {
        // Multiple ads - analyze each one separately
        const results = [];
        
        for (const ad of validAds) {
          const analysisData = {
            headline: ad.headline,
            body_text: ad.body_text,
            cta: ad.cta,
            platform: ad.platform,
            industry: ad.industry,
            target_audience: ad.target_audience
          };
          
          const response = await sharedWorkflowService.startAdhocAnalysis(analysisData);
          results.push(response);
        }
        
        toast.success(`Analysis started for ${validAds.length} ads with auto-generated project names!`);
        
        // Navigate to the first project's results
        if (results.length > 0) {
          navigate(`/project/${results[0].project_id}/results`);
        }
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Analysis failed';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      {/* Header Section */}
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          mb: 3,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography 
          variant="h3" 
          gutterBottom 
          sx={{ 
            fontWeight: 800,
            mb: 2,
            letterSpacing: '-0.02em'
          }}
        >
          📊 Analyze Your Ad Copy
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            opacity: 0.9,
            fontWeight: 400,
            maxWidth: 500,
            mx: 'auto'
          }}
        >
          Get AI-powered insights to optimize your ad performance and boost conversions across all platforms
        </Typography>
      </Paper>

      {/* Input Method Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={inputMethod}
          onChange={(_, newValue) => setInputMethod(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderBottom: '1px solid',
            borderColor: 'divider',
            '& .MuiTabs-scrollButtons': {
              color: 'primary.main'
            }
          }}
        >
          <Tab 
            value="manual" 
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Edit fontSize="small" />
                Manual Input
              </Box>
            }
          />
          <Tab 
            value="paste" 
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ContentCopy fontSize="small" />
                <Badge badgeContent={adCopies.length > 0 ? adCopies.length : null} color="primary">
                  Paste Ad Copy
                </Badge>
              </Box>
            }
          />
        </Tabs>
        
        {/* Tab Tooltips/Help Text */}
        <Box sx={{ px: 3, py: 2, bgcolor: 'grey.50', borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
            {inputMethod === 'manual' && '📝 Enter your ad copy manually using the clean form below'}
            {inputMethod === 'paste' && '📋 Paste ad copy from any source - our AI will parse it automatically'}
          </Typography>
        </Box>
      </Paper>

      {/* Form Section */}
      <Paper sx={{ p: 4 }}>
        {inputMethod === 'manual' && (
          <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            {/* Configuration Section */}
            <Grid item xs={12}>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 3, 
                  backgroundColor: 'rgba(37, 99, 235, 0.02)',
                  border: '1px solid rgba(37, 99, 235, 0.1)'
                }}
              >
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 600,
                    color: 'primary.main',
                    mb: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}
                >
                  ⚙️ Platform & Context
                </Typography>
                <Grid container spacing={3}>
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
                          placeholder="e.g., SaaS, E-commerce, Fitness"
                          InputLabelProps={{ sx: { fontWeight: 500 } }}
                        />
                      )}
                    />
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Ad Content Section */}
            <Grid item xs={12}>
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
                  📝 Your Ad Content
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Box sx={{ position: 'relative' }}>
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
                                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                                pr: 6 // Make room for assistant
                              }
                            }}
                          />
                        )}
                      />
                      <IntelligentContentAssistant
                        text={watch('headline')}
                        field="headline"
                        platform={watch('platform')}
                        industry={watch('industry')}
                        onSuggestionApply={(suggestion) => {
                          setValue('headline', suggestion);
                        }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ position: 'relative' }}>
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
                                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                                pr: 6 // Make room for assistant
                              }
                            }}
                          />
                        )}
                      />
                      <IntelligentContentAssistant
                        text={watch('body_text')}
                        field="body_text"
                        platform={watch('platform')}
                        industry={watch('industry')}
                        onSuggestionApply={(suggestion) => {
                          setValue('body_text', suggestion);
                        }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ position: 'relative' }}>
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
                                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                                pr: 6 // Make room for assistant
                              }
                            }}
                          />
                        )}
                      />
                      <IntelligentContentAssistant
                        text={watch('cta')}
                        field="cta"
                        platform={watch('platform')}
                        industry={watch('industry')}
                        onSuggestionApply={(suggestion) => {
                          setValue('cta', suggestion);
                        }}
                      />
                    </Box>
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
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              backgroundColor: 'rgba(255, 255, 255, 0.7)'
                            }
                          }}
                        />
                      )}
                    />
                  </Grid>
                </Grid>
              </Paper>
            </Grid>



            {/* Submit Button */}
            <Grid item xs={12}>
              <Box display="flex" justifyContent="center" mt={4}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  onClick={() => onSubmit(watch())}
                  sx={{ 
                    minWidth: 300,
                    py: 2,
                    px: 4,
                    fontSize: '1.2rem',
                    fontWeight: 700,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                    boxShadow: '0 8px 32px rgba(37, 99, 235, 0.3)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1e40af 0%, #2563eb 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 12px 40px rgba(37, 99, 235, 0.4)',
                    },
                    '&:disabled': {
                      background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                      transform: 'none',
                      boxShadow: 'none'
                    }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🎯 Analyzing Your Ad...
                    </>
                  ) : (
                    <>
                      🚀 Analyze My Ad Copy
                    </>
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
        )}
        
        
        {/* Paste Input Method */}
        {inputMethod === 'paste' && (
          <PasteInput
            onAdCopiesParsed={handleAdCopiesParsed}
            onClear={handleClearAdCopies}
            defaultPlatform="facebook"
          />
        )}
        
      </Paper>
      
      {/* Review and Edit Parsed Ads */}
      {inputMethod !== 'manual' && adCopies.length > 0 && (
        <Paper sx={{ p: 4, mt: 3 }}>
          <AdCopyReview
            adCopies={adCopies}
            onUpdateAdCopy={updateAdCopy}
            onRemoveAdCopy={removeAdCopy}
            onAddAdCopy={addAdCopy}
            onAnalyzeAll={handleAnalyzeAll}
            loading={loading}
          />
        </Paper>
      )}
      
      {/* Error Display */}
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage
            variant="inline"
            title="Analysis Failed"
            message={error.message}
            error={error}
            onRetry={() => setError(null)}
            showActions={false}
          />
        </Box>
      )}
      
    </Container>
  );
};

export default AdAnalysis;
