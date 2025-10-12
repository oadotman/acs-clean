import React, { useState } from 'react';
import { Container, Paper, Typography, Button, Box, CircularProgress, TextField, Grid } from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const PerformanceForensics = () => {
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
      performance_metrics: ''
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.analyzePerformance(data);
      setResults(response);
      toast.success('Performance analysis complete! 🔍');
    } catch (error) {
      setError(new Error(error.response?.data?.detail || 'Analysis failed'));
      toast.error('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={0} sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: 'white', textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800, mb: 2 }}>🔍 Performance Forensics</Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
          Analyze existing ad copy to understand why it's performing well or poorly with actionable insights.
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Controller
                name="performance_metrics"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Performance Data (Optional)"
                    fullWidth
                    multiline
                    rows={3}
                    placeholder="CTR: 2.5%, CPC: $1.20, Conversions: 45, etc."
                    helperText="Include any performance metrics you have"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                title="📝 Ad Copy to Analyze"
                subtitle="Paste your existing ad copy for detailed performance analysis"
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
                    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    '&:hover': { background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)', transform: 'translateY(-2px)' }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🔍 Analyzing Performance...
                    </>
                  ) : (
                    '🚀 Analyze Performance'
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
            🔍 Performance Analysis Results
          </Typography>
        </Paper>
      )}
      
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage variant="inline" title="Performance Analysis Failed" message={error.message} error={error} onRetry={() => setError(null)} showActions={false} />
        </Box>
      )}
    </Container>
  );
};

export default PerformanceForensics;
