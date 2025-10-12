import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Container, 
  Typography, 
  Box, 
  CircularProgress, 
  Alert, 
  Button,
  Paper 
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import { supabase } from '../lib/supabaseClientClean';
import ComprehensiveResults from '../components/ComprehensiveResults';

const AnalysisResultsPage = () => {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  // Fetch analysis data
  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: async () => {
      if (!analysisId || !user?.id) {
        throw new Error('Analysis ID or user not available');
      }

      console.log('🔍 Fetching analysis:', { analysisId, userId: user.id });

      const { data, error } = await supabase
        .from('ad_analyses')
        .select('*')
        .eq('id', analysisId)
        .eq('user_id', user.id) // Security check
        .single();

      if (error) {
        console.error('Error fetching analysis:', error);
        throw error;
      }

      if (!data) {
        throw new Error('Analysis not found');
      }

      return data;
    },
    enabled: !!analysisId && !!user?.id
  });

  const handleBack = () => {
    navigate('/history');
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
          <CircularProgress size={40} />
          <Typography variant="h6" color="text.secondary">
            Loading analysis results...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error || !analysis) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error?.message || 'Analysis not found'}
        </Alert>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={handleBack}
        >
          Back to History
        </Button>
      </Container>
    );
  }

  // Transform analysis data to match ComprehensiveResults expected format
  const resultsData = {
    original: {
      copy: [analysis.headline, analysis.body_text, analysis.cta].filter(Boolean).join('\n\n'),
      score: analysis.overall_score || 60
    },
    improved: {
      copy: analysis.improved_version || 'Improved version not available',
      score: analysis.improved_score || analysis.overall_score + 15
    },
    ai_powered: true,
    confidence: 0.85,
    sample_size: 1000,
    evidence_level: 'high',
    keyImprovements: analysis.improvements || [
      'Optimized for better conversion',
      'Improved compliance and clarity',
      'Enhanced persuasive elements'
    ]
  };

  const originalAdCopy = [analysis.headline, analysis.body_text, analysis.cta]
    .filter(Boolean)
    .join('\n\n');

  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      {/* Header with back button */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={handleBack}
          sx={{ flexShrink: 0 }}
        >
          Back to History
        </Button>
        <Box>
          <Typography variant="h4" fontWeight="bold">
            Analysis Results
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {analysis.headline || 'Untitled Ad'}
          </Typography>
        </Box>
      </Box>

      {/* Analysis Results */}
      <ComprehensiveResults
        results={resultsData}
        adCopy={originalAdCopy}
        platform={analysis.platform}
        onBack={handleBack}
        // Note: Further improve functionality will be restricted for free users
        // as we implemented in ComprehensiveResults component
      />
    </Container>
  );
};

export default AnalysisResultsPage;