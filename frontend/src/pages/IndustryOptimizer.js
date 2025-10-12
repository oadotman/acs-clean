import React, { useState } from 'react';
import { Container, Grid, Paper, Typography, Button, Box, CircularProgress, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const IndustryOptimizer = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: 'saas',
      target_audience: '',
      optimization_level: 'moderate'
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.optimizeForIndustry(data);
      setResults(response);
      toast.success('Industry-optimized copy generated! 🏢');
    } catch (error) {
      setError(new Error(error.response?.data?.detail || 'Optimization failed'));
      toast.error('Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={0} sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)', color: 'white', textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800, mb: 2, letterSpacing: '-0.02em' }}>
          🏢 Industry Optimizer
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
          Adapt your copy to industry-specific language, pain points, and frameworks for maximum relevance.
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 3, backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'primary.main', mb: 2 }}>
                  🎯 Industry Settings
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Target Industry *</InputLabel>
                      <Controller
                        name="industry"
                        control={control}
                        render={({ field }) => (
                          <Select {...field} label="Target Industry *">
                            <MenuItem value="saas">SaaS & Software</MenuItem>
                            <MenuItem value="ecommerce">E-commerce & Retail</MenuItem>
                            <MenuItem value="finance">Finance & Banking</MenuItem>
                            <MenuItem value="healthcare">Healthcare & Wellness</MenuItem>
                            <MenuItem value="education">Education & Training</MenuItem>
                            <MenuItem value="realestate">Real Estate</MenuItem>
                            <MenuItem value="fitness">Fitness & Nutrition</MenuItem>
                            <MenuItem value="consulting">Consulting & Services</MenuItem>
                            <MenuItem value="automotive">Automotive</MenuItem>
                            <MenuItem value="travel">Travel & Hospitality</MenuItem>
                          </Select>
                        )}
                      />
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Optimization Level</InputLabel>
                      <Controller
                        name="optimization_level"
                        control={control}
                        render={({ field }) => (
                          <Select {...field} label="Optimization Level">
                            <MenuItem value="light">Light (Subtle adjustments)</MenuItem>
                            <MenuItem value="moderate">Moderate (Clear industry focus)</MenuItem>
                            <MenuItem value="heavy">Heavy (Industry-native language)</MenuItem>
                          </Select>
                        )}
                      />
                    </FormControl>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                showIndustry={false}
                title="📝 Copy to Optimize"
                subtitle="Your ad copy that will be adapted for the selected industry"
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
                    background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)',
                    '&:hover': { background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)', transform: 'translateY(-2px)' }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🏢 Optimizing for Industry...
                    </>
                  ) : (
                    '🚀 Optimize for Industry'
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
            🏢 Industry-Optimized Results
          </Typography>
          {/* Results display would go here */}
        </Paper>
      )}
      
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage variant="inline" title="Industry Optimization Failed" message={error.message} error={error} onRetry={() => setError(null)} showActions={false} />
        </Box>
      )}
    </Container>
  );
};

export default IndustryOptimizer;
