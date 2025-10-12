import React, { useCallback, useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Grid,
  Box,
  LinearProgress,
  Card,
  CardContent,
  Chip,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import {
  ExpandMore,
  ContentCopy,
  SwapHoriz,
  TrendingUp,
  Psychology,
  Science,
  AccessTime
} from '@mui/icons-material';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import apiService from '../services/apiService';
import useFetch from '../hooks/useFetch';
import { SkeletonLoader, ErrorMessage, EmptyState } from '../components/ui';

const AnalysisResults = () => {
  const { analysisId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Check if we have comprehensive results passed via navigation state
  const comprehensiveResults = location.state?.results;
  const fromAnalysis = location.state?.fromAnalysis;
  const analysisData = location.state?.analysisData;
  
  // State for improvement functionality
  const [improvements, setImprovements] = useState([]);
  const [isImproving, setIsImproving] = useState(false);
  const [improvementError, setImprovementError] = useState(null);

  // Fetch analysis data with our standardized hook
  const fetchAnalysisData = useCallback(async () => {
    console.log('🚀 AnalysisResults: Starting fetch with params:', {
      analysisId,
      hasUser: !!user,
      userId: user?.id,
      hasComprehensiveResults: !!comprehensiveResults,
      fromAnalysis
    });
    
    try {
      // If we have comprehensive results from navigation, use them immediately
      if (comprehensiveResults && fromAnalysis) {
        console.log('🎉 Using comprehensive results from navigation:', comprehensiveResults);
        console.log('⏰ Returning results immediately without API call');
        
        // Transform comprehensive results to match expected analysis format
        const transformedResults = {
          id: comprehensiveResults.analysis_id,
          headline: analysisData?.adCopy?.split('\n')[0] || comprehensiveResults.original?.copy?.split('\n')[0] || 'Ad Analysis',
          body_text: analysisData?.adCopy || comprehensiveResults.original?.copy || 'No content available',
          cta: 'View Results',
          platform: analysisData?.platform || comprehensiveResults.platform || 'facebook',
          overall_score: Math.round(comprehensiveResults.original?.score || 75),
          clarity_score: 75,
          persuasion_score: 75,
          emotion_score: 75,
          cta_strength_score: 75,
          platform_fit_score: 75,
          analysis_data: {
            feedback: comprehensiveResults.improved?.improvements?.map(imp => imp.description).join(' ') || 'Analysis completed successfully',
            comprehensive_results: comprehensiveResults
          },
          created_at: new Date().toISOString()
        };
        
        console.log('✅ Transformed results ready:', transformedResults);
        return transformedResults;
      }
      
      // Fallback to API fetch only if no comprehensive results
      console.log('🔄 No comprehensive results, fetching from API...', {
        hasUser: !!user,
        hasAnalysisId: !!analysisId
      });
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      if (!analysisId) {
        throw new Error('Analysis ID not provided');
      }
      
      console.log('📡 Making API call to getAnalysisDetail...');
      const startTime = Date.now();
      
      const result = await apiService.getAnalysisDetail(analysisId);
      
      const endTime = Date.now();
      console.log(`✅ API call completed in ${endTime - startTime}ms:`, result);
      
      return result;
    } catch (error) {
      console.error('❌ Error in fetchAnalysisData:', error);
      throw error;
    }
  }, [user?.id, analysisId, comprehensiveResults, fromAnalysis, analysisData]);

  const {
    data: analysis,
    isLoading,
    error,
    refetch,
    shouldShowEmpty,
    shouldShowError,
    shouldShowLoading
  } = useFetch(
    fetchAnalysisData,
    null,
    { 
      dependencies: [user?.id, analysisId], // Simplified dependencies to prevent infinite loops
      retryCount: 0, // Disable retries to prevent hanging
      retryDelay: 1000,
      timeoutMs: 5000 // Increased timeout but still reasonable
    }
  );

  // Loading state
  if (shouldShowLoading) {
    return <SkeletonLoader variant="analysis" maxWidth="lg" />;
  }

  // Error state
  if (shouldShowError) {
    return (
      <ErrorMessage
        variant="page"
        title="Failed to load analysis"
        message={error?.message || 'We couldn\'t load the analysis results. This might be because the analysis doesn\'t exist or you don\'t have permission to view it.'}
        error={error}
        onRetry={refetch}
        onHome={() => navigate('/analysis/new')}
        maxWidth="lg"
      />
    );
  }

  // Empty state - this shouldn't normally happen, but just in case
  if (shouldShowEmpty) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <EmptyState
          variant="analysis"
          title="No analysis data found"
          description="The analysis you're looking for doesn't exist or has no data available."
          actionText="Run New Analysis"
          onAction={() => navigate('/analyze')}
        />
      </Container>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const formatScore = (score) => Math.round(score);
  
  // Handle improve ad functionality
  const handleImproveAd = async () => {
    if (!analysis) return;
    
    setIsImproving(true);
    setImprovementError(null);
    
    try {
      const response = await apiService.post('/ads/improve', {
        headline: analysis.headline,
        body_text: analysis.body_text,
        cta: analysis.cta,
        platform: analysis.platform,
        current_overall_score: analysis.overall_score,
        analysis_id: analysisId
      });
      
      if (response.success && response.improvements) {
        setImprovements(response.improvements);
      } else {
        setImprovementError('Failed to generate improvements. Please try again.');
      }
    } catch (error) {
      console.error('Error improving ad:', error);
      setImprovementError('Unable to generate improvements right now. Please try again later.');
    } finally {
      setIsImproving(false);
    }
  };
  
  // Copy text to clipboard
  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };
  
  // Get strategy icon
  const getStrategyIcon = (strategy) => {
    switch (strategy) {
      case 'emotional': return <Psychology color="secondary" />;
      case 'logical': return <Science color="primary" />;
      case 'urgency': return <AccessTime color="warning" />;
      default: return <TrendingUp />;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Analysis Results
      </Typography>

      <Grid container spacing={3}>
        {/* Original Ad */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Original Ad
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Chip label={analysis.platform.toUpperCase()} color="primary" size="small" />
            </Box>
            <Typography variant="h6" gutterBottom>
              {analysis.headline}
            </Typography>
            <Typography variant="body1" paragraph>
              {analysis.body_text}
            </Typography>
            <Typography variant="h6" color="primary">
              {analysis.cta}
            </Typography>
          </Paper>
        </Grid>

        {/* Scores */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance Scores
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Overall Score</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatScore(analysis.overall_score ?? 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.overall_score ?? 0}
                    color={getScoreColor(analysis.overall_score ?? 0)}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Clarity</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatScore(analysis.clarity_score ?? 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.clarity_score ?? 0}
                    color={getScoreColor(analysis.clarity_score ?? 0)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Persuasion</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatScore(analysis.persuasion_score ?? 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.persuasion_score ?? 0}
                    color={getScoreColor(analysis.persuasion_score ?? 0)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Emotion</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatScore(analysis.emotion_score ?? 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.emotion_score ?? 0}
                    color={getScoreColor(analysis.emotion_score ?? 0)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">CTA Strength</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatScore(analysis.cta_strength_score ?? 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.cta_strength_score ?? 0}
                    color={getScoreColor(analysis.cta_strength_score ?? 0)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Platform Fit</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatScore(analysis.platform_fit_score ?? 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.platform_fit_score ?? 0}
                    color={getScoreColor(analysis.platform_fit_score ?? 0)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* AI Feedback */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              AI Feedback
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              {analysis.analysis_data?.feedback || analysis.feedback || 'AI analysis completed successfully.'}
            </Typography>
            
            {/* Improve Ad Button */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleImproveAd}
                disabled={isImproving}
                startIcon={isImproving ? <LinearProgress /> : <TrendingUp />}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1e40af 0%, #6d28d9 100%)',
                  }
                }}
              >
                {isImproving ? 'Generating Improvements...' : '🚀 Improve This Ad'}
              </Button>
            </Box>
            
            {/* Error Message */}
            {improvementError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {improvementError}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Improved Alternatives */}
        {improvements.length > 0 && (
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom sx={{ 
              fontWeight: 700, 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              mt: 2 
            }}>
              🎯 Strategic Ad Improvements
            </Typography>
            
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Here are 3 strategically enhanced versions of your ad, each optimized for different psychology approaches:
            </Typography>
            
            {improvements.map((improvement, index) => (
              <Accordion key={index} sx={{ mb: 2 }}>
                <AccordionSummary 
                  expandIcon={<ExpandMore />}
                  sx={{
                    bgcolor: 'background.paper',
                    '&:hover': {
                      bgcolor: 'grey.50'
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    {getStrategyIcon(improvement.variant_type)}
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" fontWeight={600}>
                        {improvement.strategy_focus || `${improvement.variant_type} Strategy`}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Chip 
                          label={`Score: ${improvement.predicted_score?.toFixed(1) || 'N/A'}%`}
                          color="success"
                          size="small"
                        />
                        <Chip 
                          label={`+${improvement.score_improvement?.toFixed(1) || '0'}% improvement`}
                          color="primary" 
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </Box>
                </AccordionSummary>
                
                <AccordionDetails>
                  <Grid container spacing={3}>
                    {/* Improved Ad Content */}
                    <Grid item xs={12} md={8}>
                      <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            HEADLINE
                          </Typography>
                          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                            {improvement.headline}
                          </Typography>
                          <Tooltip title="Copy headline">
                            <IconButton 
                              size="small" 
                              onClick={() => copyToClipboard(improvement.headline, 'headline')}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            BODY TEXT
                          </Typography>
                          <Typography variant="body1" paragraph>
                            {improvement.body_text}
                          </Typography>
                          <Tooltip title="Copy body text">
                            <IconButton 
                              size="small" 
                              onClick={() => copyToClipboard(improvement.body_text, 'body')}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            CALL TO ACTION
                          </Typography>
                          <Typography variant="h6" color="primary" gutterBottom sx={{ fontWeight: 600 }}>
                            {improvement.cta}
                          </Typography>
                          <Tooltip title="Copy CTA">
                            <IconButton 
                              size="small" 
                              onClick={() => copyToClipboard(improvement.cta, 'cta')}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        
                        {/* Action Buttons */}
                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                          <Button 
                            variant="outlined" 
                            size="small"
                            startIcon={<ContentCopy />}
                            onClick={() => copyToClipboard(
                              `${improvement.headline}\n\n${improvement.body_text}\n\n${improvement.cta}`, 
                              'full ad'
                            )}
                          >
                            Copy All
                          </Button>
                          <Button 
                            variant="contained" 
                            size="small"
                            startIcon={<SwapHoriz />}
                            color="secondary"
                          >
                            Use This Version
                          </Button>
                        </Box>
                      </Paper>
                    </Grid>
                    
                    {/* Improvement Analysis */}
                    <Grid item xs={12} md={4}>
                      <Box>
                        <Typography variant="h6" gutterBottom fontWeight={600}>
                          Why This Works
                        </Typography>
                        <Typography variant="body2" paragraph>
                          {improvement.improvement_reason}
                        </Typography>
                        
                        {/* Score Improvement Visual */}
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Performance Prediction
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={improvement.predicted_score || 0}
                            sx={{ 
                              height: 8, 
                              borderRadius: 4,
                              bgcolor: 'grey.200'
                            }}
                            color="success"
                          />
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Predicted score: {improvement.predicted_score?.toFixed(1) || 'N/A'}%
                          </Typography>
                        </Box>
                        
                        <Alert severity="info" sx={{ mt: 2 }}>
                          <Typography variant="body2">
                            <strong>Strategy:</strong> {improvement.variant_type?.charAt(0).toUpperCase() + improvement.variant_type?.slice(1)}
                          </Typography>
                        </Alert>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Grid>
        )}
        
        {/* Original Alternatives (fallback) */}
        {improvements.length === 0 && analysis.ad_generations && analysis.ad_generations.length > 0 && (
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              AI-Generated Alternatives
            </Typography>
            <Grid container spacing={2}>
              {analysis.ad_generations.map((alternative, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card>
                    <CardContent>
                      <Box sx={{ mb: 2 }}>
                        <Chip 
                          label={alternative.variant_type?.replace('_', ' ')?.toUpperCase() || 'ALTERNATIVE'} 
                          color="secondary" 
                          size="small" 
                        />
                      </Box>
                      <Typography variant="h6" gutterBottom>
                        {alternative.generated_headline || 'No headline provided'}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {alternative.generated_body_text || 'No body text provided'}
                      </Typography>
                      <Typography variant="subtitle2" color="primary" gutterBottom>
                        {alternative.generated_cta || 'No CTA provided'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {alternative.improvement_reason || 'No improvement reason provided'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default AnalysisResults;
