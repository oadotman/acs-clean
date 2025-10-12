import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  LinearProgress,
  Button,
  Alert,
  Divider
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Info,
  TrendingUp,
  Psychology,
  Gavel,
  RecordVoiceOver,
  Policy,
  AttachMoney,
  Science,
  Business,
  SearchOff,
  ArrowBack
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';

// Helper function to calculate overall score from tool results
const calculateOverallScore = (toolResults) => {
  if (!toolResults || toolResults.length === 0) return 0;
  
  const completedResults = toolResults.filter(result => 
    result.status === 'completed' && result.overall_score !== null && result.overall_score !== undefined
  );
  
  if (completedResults.length === 0) return 0;
  
  const totalScore = completedResults.reduce((sum, result) => sum + (result.overall_score || 0), 0);
  return Math.round(totalScore / completedResults.length);
};

// Helper function to convert backend tool results to display format
const convertToolResults = (backendResults) => {
  const toolIconMap = {
    compliance: Policy,
    legal: Gavel,
    psychology: Psychology,
    brand_voice: RecordVoiceOver,
    roi_generator: AttachMoney,
    ab_test_generator: Science,
    industry_optimizer: Business,
    performance_forensics: SearchOff
  };
  
  return backendResults.map(result => {
    const score = result.overall_score || 0;
    const getStatusAndColor = (score) => {
      if (score >= 80) return { status: 'excellent', color: 'success' };
      if (score >= 60) return { status: 'good', color: 'warning' };
      if (score >= 40) return { status: 'fair', color: 'info' };
      return { status: 'needs improvement', color: 'error' };
    };
    
    const { status, color } = getStatusAndColor(score);
    
    return {
      tool_name: result.tool_name,
      icon: toolIconMap[result.tool_name] || Policy,
      score: Math.round(score),
      status,
      color,
      summary: result.result_data?.summary || `${result.tool_name.replace('_', ' ')} analysis completed`,
      details: result.result_data?.details || result.result_data?.recommendations || [
        'Analysis completed successfully',
        'Results processed and scored',
        'See full report for detailed insights'
      ]
    };
  });
};


const SimplifiedResults = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResults = async () => {
      try {
        console.log('🔄 Loading REAL analysis results for project:', projectId);
        
        // Try to get real project data from the shared workflow service
        try {
          const sharedWorkflowService = await import('../services/sharedWorkflowService').then(module => 
            module.default
          );
          
          const realProject = await sharedWorkflowService.getProject(projectId, true);
          
          if (realProject && realProject.tool_results) {
            console.log('✅ Real backend project data found! Converting to display format...');
            
            const realResults = {
              project_id: projectId,
              project_name: realProject.project_name,
              real_backend_data: true,
              created_at: realProject.created_at || new Date().toISOString(),
              analysis_summary: {
                overall_score: calculateOverallScore(realProject.tool_results),
                total_tools: realProject.tool_results.length,
                tools_completed: realProject.tool_results.filter(r => r.status === 'completed').length,
                status: 'completed'
              },
              ad_copy: {
                headline: realProject.headline,
                body_text: realProject.body_text,
                cta: realProject.cta,
                platform: realProject.platform,
                industry: realProject.industry,
                target_audience: realProject.target_audience
              },
              tool_results: convertToolResults(realProject.tool_results)
            };
            
            setResults(realResults);
            setLoading(false);
            return;
          }
        } catch (apiError) {
          console.error('❌ Failed to fetch real data from backend:', apiError.message);
        }
        
        // If we get here, the backend call failed
        console.log('❌ No real backend data found for project:', projectId);
        setResults(null);
        setLoading(false);
        
      } catch (error) {
        console.error('❌ Error loading analysis results:', error);
        setResults(null);
        setLoading(false);
      }
    };
    
    loadResults();
  }, [projectId]);

  const getScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 80) return 'warning';
    if (score >= 70) return 'info';
    return 'error';
  };

  const getScoreIcon = (score) => {
    if (score >= 85) return <CheckCircle color="success" />;
    if (score >= 70) return <Warning color="warning" />;
    return <Info color="info" />;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box textAlign="center">
          <Typography variant="h5" gutterBottom>
            🎯 Analyzing Your Ad Copy...
          </Typography>
          <LinearProgress sx={{ my: 3 }} />
          <Typography variant="body1" color="text.secondary">
            Running comprehensive analysis through 8 AI-powered tools
          </Typography>
        </Box>
      </Container>
    );
  }

  if (!results) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Analysis results not found. Please try running the analysis again.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/analysis/new')}
          sx={{ mb: 2 }}
        >
          Back to Analysis
        </Button>
        
        <Paper sx={{ p: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <Typography variant="h3" fontWeight={800} gutterBottom>
            📊 Analysis Complete!
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
            {results.project_name}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label={`Overall Score: ${results.analysis_summary.overall_score}%`}
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                fontWeight: 'bold',
                fontSize: '1rem'
              }}
            />
            <Chip 
              label={`${results.analysis_summary.tools_completed} Tools Analyzed`}
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white'
              }}
            />
          </Box>
        </Paper>
      </Box>

      {/* Ad Copy Review */}
      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              📝 Your Ad Copy
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="primary" fontWeight={600}>
                Headline:
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {results.ad_copy.headline}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="primary" fontWeight={600}>
                Body Text:
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {results.ad_copy.body_text}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="primary" fontWeight={600}>
                Call-to-Action:
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {results.ad_copy.cta}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip label={results.ad_copy.platform} size="small" variant="outlined" />
              {results.ad_copy.industry && (
                <Chip label={results.ad_copy.industry} size="small" variant="outlined" />
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Tool Results */}
        <Grid item xs={12} md={8}>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            🔧 Analysis Results
          </Typography>
          
          <Grid container spacing={2}>
            {results.tool_results.map((tool, index) => (
              <Grid item xs={12} sm={6} key={tool.tool_name}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <tool.icon color={tool.color} />
                        <Typography variant="h6" fontWeight={600} sx={{ textTransform: 'capitalize' }}>
                          {tool.tool_name.replace('_', ' ')}
                        </Typography>
                      </Box>
                      {getScoreIcon(tool.score)}
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h4" fontWeight={700} color={`${tool.color}.main`}>
                          {tool.score}%
                        </Typography>
                        <Chip 
                          label={tool.status} 
                          color={tool.color} 
                          size="small"
                          sx={{ textTransform: 'capitalize' }}
                        />
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={tool.score} 
                        color={tool.color}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                    
                    <Typography variant="body2" fontWeight={500} gutterBottom>
                      {tool.summary}
                    </Typography>
                    
                    <Box sx={{ mt: 2 }}>
                      {tool.details.map((detail, idx) => (
                        <Typography key={idx} variant="caption" display="block" sx={{ opacity: 0.8 }}>
                          • {detail}
                        </Typography>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>

      {/* Success Message */}
      <Box sx={{ mt: 4 }}>
        <Alert severity="success" sx={{ mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            🎉 Analysis Complete!
          </Typography>
          <Typography variant="body2">
            Your ad copy scored <strong>{results.analysis_summary.overall_score}%</strong> overall. 
            This is a strong foundation for your advertising campaign. Consider implementing the suggestions above to optimize performance further.
          </Typography>
        </Alert>
        
        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => navigate('/analysis/new')}
            sx={{ mr: 2 }}
          >
            Analyze Another Ad
          </Button>
          <Button 
            variant="outlined" 
            size="large"
            onClick={() => window.print()}
          >
            Export Results
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default SimplifiedResults;