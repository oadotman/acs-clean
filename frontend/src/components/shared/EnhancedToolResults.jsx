import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Chip,
  Alert,
  LinearProgress,
  Divider
} from '@mui/material';

const EnhancedToolResults = ({ results, toolType, title }) => {
  if (!results) return null;

  const renderOverallScore = () => {
    if (!results.overall_score) return null;
    
    const getScoreColor = (score) => {
      if (score >= 80) return 'success.main';
      if (score >= 60) return 'warning.main';
      return 'error.main';
    };

    const getScoreLabel = (score) => {
      if (score >= 80) return '✅ Excellent';
      if (score >= 60) return '⚠️ Good';
      return '❌ Needs Improvement';
    };

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          📊 Overall Score
        </Typography>
        <Paper sx={{ p: 3, bgcolor: 'rgba(37, 99, 235, 0.05)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 2 }}>
            <Typography variant="h3" sx={{ fontWeight: 700, color: getScoreColor(results.overall_score) }}>
              {results.overall_score}%
            </Typography>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
                {getScoreLabel(results.overall_score)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={results.overall_score}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(results.overall_score),
                    borderRadius: 4
                  }
                }}
              />
            </Box>
          </Box>
        </Paper>
      </Box>
    );
  };

  const renderViolations = () => {
    if (!results.violations || results.violations.length === 0) {
      return (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6">
            🎉 No violations found! Your ad copy looks compliant.
          </Typography>
        </Alert>
      );
    }

    const getRiskColor = (level) => {
      switch (level?.toLowerCase()) {
        case 'high': return 'error';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'default';
      }
    };

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          🚨 Issues Found ({results.violations.length})
        </Typography>
        {results.violations.map((violation, index) => (
          <Paper key={index} sx={{ p: 3, mb: 2, bgcolor: 'rgba(244, 67, 54, 0.05)' }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
              <Chip 
                label={violation.risk_level || violation.severity || 'Medium'} 
                color={getRiskColor(violation.risk_level || violation.severity)}
                size="small"
              />
              <Typography variant="h6" sx={{ fontWeight: 600, flex: 1 }}>
                {violation.issue_type || violation.type || violation.title}
              </Typography>
            </Box>
            <Typography variant="body1" sx={{ mb: 2 }}>
              <strong>Issue:</strong> {violation.description || violation.message}
            </Typography>
            {violation.flagged_text && (
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2, fontStyle: 'italic' }}>
                <strong>Flagged Text:</strong> "{violation.flagged_text}"
              </Typography>
            )}
            <Typography variant="body1" sx={{ color: 'success.main' }}>
              <strong>Suggestion:</strong> {violation.suggestion || violation.fix || 'Review and revise this section'}
            </Typography>
          </Paper>
        ))}
      </Box>
    );
  };

  const renderScoreBreakdown = () => {
    const scores = results.psychology_scores || results.breakdown_scores || results.scores;
    if (!scores) return null;

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          📈 Detailed Breakdown
        </Typography>
        <Grid container spacing={2}>
          {Object.entries(scores).map(([category, score]) => (
            <Grid item xs={12} sm={6} md={4} key={category}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, textTransform: 'capitalize', mb: 1 }}>
                  {category.replace(/_/g, ' ')}
                </Typography>
                <Typography variant="h5" color="primary.main" sx={{ fontWeight: 700 }}>
                  {score}%
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  const renderTags = (items, title, color = 'primary') => {
    if (!items || items.length === 0) return null;

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <Paper sx={{ p: 3, bgcolor: `rgba(37, 99, 235, 0.05)` }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {items.map((item, index) => (
              <Chip 
                key={index} 
                label={typeof item === 'string' ? item : item.name || item.title}
                color={color}
                variant="outlined"
              />
            ))}
          </Box>
        </Paper>
      </Box>
    );
  };

  const renderRecommendations = () => {
    const recommendations = results.recommendations || results.suggestions || results.tips;
    if (!recommendations || recommendations.length === 0) return null;

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          💡 Recommendations
        </Typography>
        <Paper sx={{ p: 3, bgcolor: 'rgba(34, 197, 94, 0.05)' }}>
          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
            {recommendations.map((rec, index) => (
              <li key={index}>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  {typeof rec === 'string' ? rec : rec.text || rec.message}
                </Typography>
              </li>
            ))}
          </ul>
        </Paper>
      </Box>
    );
  };

  const renderGeneratedContent = () => {
    if (!results.generated_copy && !results.variations && !results.alternatives) return null;

    const content = results.generated_copy || results.variations || results.alternatives;
    if (!content) return null;

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          ✨ Generated Content
        </Typography>
        <Paper sx={{ p: 3, bgcolor: 'rgba(139, 92, 246, 0.05)' }}>
          {Array.isArray(content) ? (
            content.map((item, index) => (
              <Box key={index} sx={{ mb: index < content.length - 1 ? 3 : 0 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Variation {index + 1}
                </Typography>
                {item.headline && (
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    <strong>Headline:</strong> {item.headline}
                  </Typography>
                )}
                {item.body_text && (
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    <strong>Body:</strong> {item.body_text}
                  </Typography>
                )}
                {item.cta && (
                  <Typography variant="body1">
                    <strong>CTA:</strong> {item.cta}
                  </Typography>
                )}
                {index < content.length - 1 && <Divider sx={{ mt: 2 }} />}
              </Box>
            ))
          ) : (
            <Box>
              {content.headline && (
                <Typography variant="body1" sx={{ mb: 1 }}>
                  <strong>Headline:</strong> {content.headline}
                </Typography>
              )}
              {content.body_text && (
                <Typography variant="body1" sx={{ mb: 1 }}>
                  <strong>Body:</strong> {content.body_text}
                </Typography>
              )}
              {content.cta && (
                <Typography variant="body1">
                  <strong>CTA:</strong> {content.cta}
                </Typography>
              )}
            </Box>
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
        {title}
      </Typography>
      
      {renderOverallScore()}
      {renderViolations()}
      {renderScoreBreakdown()}
      {renderTags(results.emotional_triggers, '❤️ Emotional Triggers')}
      {renderTags(results.persuasion_techniques, '🎯 Persuasion Techniques')}
      {renderTags(results.detected_features, '🔍 Detected Features')}
      {renderGeneratedContent()}
      {renderRecommendations()}
    </Paper>
  );
};

export default EnhancedToolResults;
