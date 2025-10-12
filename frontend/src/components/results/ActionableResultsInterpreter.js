import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Alert,
  Grid
} from '@mui/material';
import {
  AutoFixHigh,
  Download,
  Share
} from '@mui/icons-material';
import StartIcon from '../icons/StartIcon';
import toast from 'react-hot-toast';

/**
 * Transforms complex analysis results into actionable insights and recommendations
 * Provides clear next steps, priority rankings, and one-click fixes
 */
const ActionableResultsInterpreter = ({ 
  analysisResults, 
  adCopy, 
  onApplyFix, 
  onGenerateVariations,
  showAdvanced = false 
}) => {
  // Process results for display
  const processResults = () => {
    const scoreBreakdown = {};
    let overallScore = 0;
    let totalTools = 0;

    Object.entries(analysisResults || {}).forEach(([tool, results]) => {
      if (!results) return;
      totalTools++;
      const toolScore = results.overall_score || results.score || 0;
      scoreBreakdown[tool] = toolScore;
      overallScore += toolScore;
    });

    const finalScore = totalTools > 0 ? Math.round(overallScore / totalTools) : 0;

    return {
      overallScore: finalScore,
      scoreBreakdown,
      totalTools
    };
  };

  const processed = processResults();

  return (
    <Box>
      {/* Overall Score & Quick Summary */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Typography variant="h2" sx={{ fontWeight: 800, mb: 1, textAlign: 'center' }}>
          {processed.overallScore}/100
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, textAlign: 'center', mb: 2 }}>
          Overall Score
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
          🎯 Your Ad Analysis Results
        </Typography>
        <Typography variant="body1" sx={{ opacity: 0.9 }}>
          {processed.overallScore >= 80 
            ? "🎉 Excellent! Your ad is optimized and ready to perform well."
            : processed.overallScore >= 60
            ? "⚡ Good foundation! A few optimizations will significantly improve performance."
            : "🚀 Great potential! Let's fix these issues to unlock better results."
          }
        </Typography>
      </Paper>

      {/* Action Buttons */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          🚀 What's Next?
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<AutoFixHigh />}
              onClick={() => onGenerateVariations?.()}
              sx={{ py: 1.5 }}
            >
              Generate Optimized Variations
            </Button>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              startIcon={<Download />}
              sx={{ py: 1.5 }}
            >
              Export Report
            </Button>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              startIcon={<Share />}
              sx={{ py: 1.5 }}
            >
              Share Results
            </Button>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              startIcon={<StartIcon />}
              sx={{ py: 1.5 }}
            >
              Run Another Analysis
            </Button>
          </Grid>
        </Grid>
        
        <Alert severity="success" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>💡 Pro Tip:</strong> Generate variations to test different approaches based on these insights. 
            Each variation can address different optimization opportunities for maximum performance.
          </Typography>
        </Alert>
      </Paper>
    </Box>
  );
};

export default ActionableResultsInterpreter;
