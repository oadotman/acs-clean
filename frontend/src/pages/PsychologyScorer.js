import React, { useState } from 'react';
import { Container, Paper, Typography, Button, Box, CircularProgress, Grid, Chip } from '@mui/material';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const PsychologyScorer = () => {
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
      const response = await apiService.scorePsychology(data);
      setResults(response);
      toast.success('Psychology analysis complete! 🧠');
    } catch (error) {
      setError(new Error(error.response?.data?.detail || 'Analysis failed'));
      toast.error('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={0} sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', color: 'white', textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800, mb: 2 }}>🧠 Psychology Scorer</Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
          Score your copy on 15+ psychological triggers including urgency, social proof, authority, and more.
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                title="📝 Copy to Score"
                subtitle="Analyze your ad copy for psychological triggers and persuasion techniques"
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
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                    '&:hover': { background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)', transform: 'translateY(-2px)' }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      🧠 Analyzing Psychology...
                    </>
                  ) : (
                    '🚀 Score Psychology Triggers'
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
            🧠 Psychology Scoring Results
          </Typography>
          
          {/* Overall Psychology Score */}
          {results.overall_score && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                📊 Overall Psychology Score
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(139, 92, 246, 0.05)' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    {results.overall_score}%
                  </Typography>
                  <Box>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {results.overall_score >= 80 ? '✅ Highly Persuasive' : 
                       results.overall_score >= 60 ? '⚠️ Moderately Persuasive' : '❌ Needs More Psychology'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Psychological persuasion effectiveness
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Box>
          )}

          {/* Psychology Scores Breakdown */}
          {results.psychology_scores && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                🧙 Psychology Triggers Analysis
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(results.psychology_scores).map(([trigger, score]) => (
                  <Grid item xs={12} sm={6} md={4} key={trigger}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                        {trigger.replace('_', ' ')}
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

          {/* Emotional Triggers */}
          {results.emotional_triggers && results.emotional_triggers.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                ❤️ Detected Emotional Triggers
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(236, 72, 153, 0.05)' }}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {results.emotional_triggers.map((trigger, index) => (
                    <Chip key={index} label={trigger} color="primary" variant="outlined" />
                  ))}
                </Box>
              </Paper>
            </Box>
          )}

          {/* Persuasion Techniques */}
          {results.persuasion_techniques && results.persuasion_techniques.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                🎯 Persuasion Techniques Used
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(34, 197, 94, 0.05)' }}>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                  {results.persuasion_techniques.map((technique, index) => (
                    <li key={index}>
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        <strong>{technique.name}:</strong> {technique.description}
                      </Typography>
                    </li>
                  ))}
                </ul>
              </Paper>
            </Box>
          )}

          {/* Recommendations */}
          {results.recommendations && results.recommendations.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                💡 Psychology Enhancement Recommendations
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(59, 130, 246, 0.05)' }}>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                  {results.recommendations.map((rec, index) => (
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
          <ErrorMessage variant="inline" title="Psychology Analysis Failed" message={error.message} error={error} onRetry={() => setError(null)} showActions={false} />
        </Box>
      )}
    </Container>
  );
};

export default PsychologyScorer;
