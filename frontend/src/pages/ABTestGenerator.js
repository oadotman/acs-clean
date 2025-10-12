import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Tab,
  Tabs,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const ABTestGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [selectedTab, setSelectedTab] = useState(0);
  
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: '',
      target_audience: '',
      test_variables: ['headline', 'emotion', 'cta']
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await apiService.generateABTests(data);
      setResults(response);
      toast.success(`Generated ${response.variations?.length || 0} A/B test variations! 🧪`);
    } catch (error) {
      console.error('A/B test generation failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Generation failed';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          mb: 3,
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800, mb: 2, letterSpacing: '-0.02em' }}>
          🧪 A/B Test Generator
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
          Generate multiple ad variations testing different psychological angles, headlines, CTAs, and emotions.
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 3, backgroundColor: 'rgba(16, 185, 129, 0.05)' }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'success.main', mb: 2 }}>
                  🎯 Test Variables
                </Typography>
                <Grid container spacing={2}>
                  {['headline', 'emotion', 'cta', 'urgency', 'social_proof', 'authority'].map((variable) => (
                    <Grid item xs={12} sm={6} key={variable}>
                      <Controller
                        name="test_variables"
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={field.value.includes(variable)}
                                onChange={(e) => {
                                  const newValue = e.target.checked 
                                    ? [...field.value, variable]
                                    : field.value.filter(v => v !== variable);
                                  field.onChange(newValue);
                                }}
                              />
                            }
                            label={variable.replace('_', ' ').toUpperCase()}
                          />
                        )}
                      />
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                title="📝 Base Ad Copy"
                subtitle="Your original ad copy that will be used as the control variation"
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
                    minWidth: 280,
                    py: 2,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                      transform: 'translateY(-2px)',
                    }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🧪 Generating Variations...
                    </>
                  ) : (
                    <>
                      🚀 Generate A/B Tests
                    </>
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
            🧪 A/B Test Variations
          </Typography>
          
          <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
            <Tab label="All Variations" />
            <Tab label="Testing Framework" />
          </Tabs>

          {selectedTab === 0 && results.variations && results.variations.map((variation, index) => (
            <Card key={index} sx={{ mb: 3, border: '2px solid', borderColor: 'success.light' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Variation {String.fromCharCode(65 + index)} - {variation.test_focus}
                  </Typography>
                  <Chip 
                    label={variation.psychological_trigger} 
                    color="success"
                    variant="outlined"
                  />
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, mb: 1 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        HEADLINE
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {variation.headline}
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, mb: 1 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        BODY TEXT
                      </Typography>
                      <Typography variant="body1">
                        {variation.body_text}
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        CALL-TO-ACTION
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {variation.cta}
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ p: 2, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        HYPOTHESIS
                      </Typography>
                      <Typography variant="body2">
                        {variation.test_hypothesis}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}

          {selectedTab === 1 && results.testing_framework && (
            <Box>
              <Paper sx={{ p: 3, mb: 3, bgcolor: 'rgba(16, 185, 129, 0.05)' }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  📊 Testing Recommendations
                </Typography>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                  {results.testing_framework.recommendations?.map((rec, index) => (
                    <li key={index}>
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        {rec}
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
          <ErrorMessage
            variant="inline"
            title="A/B Test Generation Failed"
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

export default ABTestGenerator;
