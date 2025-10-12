import React, { useState } from 'react';
import { Container, Paper, Typography, Button, Box, CircularProgress, Grid, TextField } from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const BrandVoiceEngine = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: '',
      target_audience: '',
      brand_samples: ''
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.alignBrandVoice(data);
      setResults(response);
      toast.success('Brand voice analysis complete! 🎯');
    } catch (error) {
      setError(new Error(error.response?.data?.detail || 'Analysis failed'));
      toast.error('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={0} sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)', color: 'white', textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800, mb: 2 }}>🎯 Brand Voice Engine</Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
          Ensure all generated copy matches your brand voice by analyzing your existing content and style.
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 3, backgroundColor: 'rgba(6, 182, 212, 0.05)' }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'cyan.600', mb: 2 }}>
                  🎨 Brand Voice Samples
                </Typography>
                <Controller
                  name="brand_samples"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Brand Content Samples"
                      fullWidth
                      multiline
                      rows={6}
                      placeholder="Paste 3-5 examples of your existing content (emails, website copy, social posts, etc.)"
                      helperText="The more samples you provide, the better we can match your brand voice"
                    />
                  )}
                />
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                title="📝 Copy to Align"
                subtitle="Ad copy that will be adjusted to match your brand voice"
              />
            </Grid>

            <Grid item xs={12}>
              <Box display="flex" justifyContent="center" mt={2}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ 
                    minWidth: 280, py: 2, px: 4, fontSize: '1.1rem', fontWeight: 700, borderRadius: 3,
                    background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
                    '&:hover': { background: 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)', transform: 'translateY(-2px)' }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🎯 Aligning Brand Voice...
                    </>
                  ) : (
                    '🚀 Align Brand Voice'
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {results && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
            🎯 Brand Voice Alignment Results
          </Typography>
          
          {/* Overall Alignment Score */}
          {results.alignment_score && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                📊 Brand Voice Alignment Score
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(6, 182, 212, 0.05)' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    {results.alignment_score}%
                  </Typography>
                  <Box>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {results.alignment_score >= 80 ? '✅ Excellent Match' : 
                       results.alignment_score >= 60 ? '⚠️ Good Match' : '❌ Needs Improvement'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Brand voice consistency rating
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Box>
          )}

          {/* Tone Analysis */}
          {results.tone_analysis && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                🎨 Detected Tone Characteristics
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(results.tone_analysis).map(([trait, score]) => (
                  <Grid item xs={12} sm={6} md={4} key={trait}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                        {trait.replace('_', ' ')}
                      </Typography>
                      <Typography variant="h6" color="primary.main">
                        {score}%
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Brand-Aligned Copy Suggestion */}
          {results.suggested_copy && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                ✨ Brand-Aligned Copy Suggestions
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(34, 197, 94, 0.05)' }}>
                {results.suggested_copy.headline && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Headline:</Typography>
                    <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                      "{results.suggested_copy.headline}"
                    </Typography>
                  </Box>
                )}
                {results.suggested_copy.body_text && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Body Text:</Typography>
                    <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                      "{results.suggested_copy.body_text}"
                    </Typography>
                  </Box>
                )}
                {results.suggested_copy.cta && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>CTA:</Typography>
                    <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                      "{results.suggested_copy.cta}"
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Box>
          )}

          {/* Brand Consistency Analysis */}
          {results.brand_consistency && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                🔍 Brand Consistency Analysis
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(59, 130, 246, 0.05)' }}>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                  {results.brand_consistency.map((insight, index) => (
                    <li key={index}>
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        {insight}
                      </Typography>
                    </li>
                  ))}
                </ul>
              </Paper>
            </Box>
          )}
        </Paper>
      )}
      
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage variant="inline" title="Brand Voice Analysis Failed" message={error.message} error={error} onRetry={() => setError(null)} showActions={false} />
        </Box>
      )}
    </Container>
  );
};

export default BrandVoiceEngine;
