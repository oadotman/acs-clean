import React, { useState } from 'react';
import { Container, Paper, Typography, Button, Box, CircularProgress, Grid, Alert } from '@mui/material';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const LegalRiskScanner = () => {
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
      target_audience: ''
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.scanLegalRisks(data);
      setResults(response);
      if (response.risk_level === 'high') {
        toast.error('High legal risks detected! ⚠️');
      } else if (response.risk_level === 'medium') {
        toast.warning('Some legal risks found');
      } else {
        toast.success('Legal scan complete - low risk! ✅');
      }
    } catch (error) {
      setError(new Error(error.response?.data?.detail || 'Scan failed'));
      toast.error('Legal scan failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={0} sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', color: 'white', textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800, mb: 2 }}>⚖️ Legal Risk Scanner</Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
          Identify problematic legal claims in your ad copy and get safer alternatives while maintaining impact.
        </Typography>
      </Paper>

      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Disclaimer:</strong> This tool provides general guidance only and is not a substitute for professional legal advice. 
          Always consult with a qualified attorney for legal compliance in your specific situation.
        </Typography>
      </Alert>

      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                title="📝 Copy to Scan"
                subtitle="Review your ad copy for potential legal risks and problematic claims"
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
                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    '&:hover': { background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)', transform: 'translateY(-2px)' }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      ⚖️ Scanning for Risks...
                    </>
                  ) : (
                    '🚀 Scan Legal Risks'
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
            ⚖️ Legal Risk Assessment
          </Typography>
        </Paper>
      )}
      
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage variant="inline" title="Legal Risk Scan Failed" message={error.message} error={error} onRetry={() => setError(null)} showActions={false} />
        </Box>
      )}
    </Container>
  );
};

export default LegalRiskScanner;
