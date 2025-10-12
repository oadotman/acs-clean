import React from 'react';
import { Box, Chip, Tooltip } from '@mui/material';
import { AutoAwesome } from '@mui/icons-material';

const IntelligentContentAssistant = ({ 
  text, 
  field, 
  platform = 'facebook',
  industry,
  onSuggestionApply,
  disabled = false 
}) => {
  if (disabled || !text || text.length < 5) {
    return null;
  }

  // Simple quality scoring placeholder
  const qualityScore = Math.max(60, Math.min(100, text.length * 2 + Math.random() * 20));

  return (
    <Box sx={{ position: 'absolute', right: -50, top: 8, zIndex: 1 }}>
      <Tooltip title={`Content quality: ${Math.round(qualityScore)}/100`}>
        <Chip
          icon={<AutoAwesome />}
          label={Math.round(qualityScore)}
          size="small"
          color={qualityScore >= 80 ? 'success' : qualityScore >= 60 ? 'warning' : 'error'}
          variant="filled"
          sx={{ fontWeight: 600 }}
        />
      </Tooltip>
    </Box>
  );
};

export default IntelligentContentAssistant;
