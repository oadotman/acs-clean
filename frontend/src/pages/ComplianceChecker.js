import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';
import EnhancedToolResults from '../components/shared/EnhancedToolResults';

const ComplianceChecker = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  const { control, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: '',
      target_audience: '',
      strict_mode: false
    }
  });

  const selectedPlatform = watch('platform');

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await apiService.checkCompliance(data);
      setResults(response);
      
      if (response.violations && response.violations.length > 0) {
        toast.error(`Found ${response.violations.length} compliance issues`);
      } else {
        toast.success('Your ad copy is compliant! 🎉');
      }
    } catch (error) {
      console.error('Compliance check failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Compliance check failed';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
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
          🛡️ Platform Compliance Checker
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            opacity: 0.9,
            fontWeight: 400,
            maxWidth: 600,
            mx: 'auto'
          }}
        >
          Scan your ad copy for policy violations across Facebook, Google, TikTok, and other platforms. 
          Get instant feedback and compliant alternatives.
        </Typography>
      </Paper>

      {/* Form Section */}
      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            {/* Platform-specific settings */}
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
                  ⚙️ Compliance Settings
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel sx={{ fontWeight: 500 }}>Primary Platform *</InputLabel>
                      <Controller
                        name="platform"
                        control={control}
                        render={({ field }) => (
                          <Select {...field} label="Primary Platform *">
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
                    <FormControl fullWidth>
                      <InputLabel sx={{ fontWeight: 500 }}>Strictness Level</InputLabel>
                      <Controller
                        name="strict_mode"
                        control={control}
                        render={({ field }) => (
                          <Select {...field} label="Strictness Level">
                            <MenuItem value={false}>Standard Check</MenuItem>
                            <MenuItem value={true}>Strict Mode (Extra Safe)</MenuItem>
                          </Select>
                        )}
                      />
                    </FormControl>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Ad Content Input */}
            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                showPlatform={false}
                title="📝 Ad Copy to Check"
                subtitle={`Checking compliance for ${selectedPlatform} platform policies`}
              />
            </Grid>

            {/* Submit Button */}
            <Grid item xs={12}>
              <Box display="flex" justifyContent="center" mt={2}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ 
                    minWidth: 280,
                    py: 2,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                      transform: 'translateY(-2px)',
                    }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🔍 Checking Compliance...
                    </>
                  ) : (
                    <>
                      🛡️ Check Compliance
                    </>
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {/* Results Section */}
      {results && (
        <EnhancedToolResults 
          results={{
            ...results,
            recommendations: results.platform_tips
          }} 
          toolType="compliance" 
          title="🛡️ Compliance Report"
        />
      )}
      
      {/* Error Display */}
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage
            variant="inline"
            title="Compliance Check Failed"
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

export default ComplianceChecker;
