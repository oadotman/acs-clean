import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Checkbox,
  FormControlLabel,
  Chip,
  Button,
  Divider,
  IconButton,
  Collapse,
  Tooltip,
  Switch,
  Alert,
  CircularProgress,
  Badge
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle,
  Science,
  ContentCopy,
  Refresh,
  AutoAwesome,
  TrendingUp,
  Psychology,
  Speed
} from '@mui/icons-material';

/**
 * Component for displaying generated ad copy variations with selection and analysis features
 */
const VariationPreview = ({ 
  variations = [], 
  originalDraft,
  onVariationSelect,
  onAnalyzeSelected,
  showAnalysisOptions = true,
  compact = false
}) => {
  const [selectedVariations, setSelectedVariations] = useState(new Set());
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [expanded, setExpanded] = useState(!compact);
  const [analyzing, setAnalyzing] = useState(false);

  const handleSelectAll = () => {
    if (selectedVariations.size === variations.length) {
      setSelectedVariations(new Set());
    } else {
      setSelectedVariations(new Set(variations.map(v => v.id)));
    }
  };

  const handleSelectBest = () => {
    // Select top 3 variations based on ROI score or other metrics
    const bestVariations = [...variations]
      .sort((a, b) => (b.metadata?.roi_score || 0) - (a.metadata?.roi_score || 0))
      .slice(0, 3)
      .map(v => v.id);
    setSelectedVariations(new Set(bestVariations));
  };

  const handleVariationToggle = (variationId) => {
    const newSelected = new Set(selectedVariations);
    if (newSelected.has(variationId)) {
      newSelected.delete(variationId);
    } else {
      newSelected.add(variationId);
    }
    setSelectedVariations(newSelected);
    
    if (onVariationSelect) {
      onVariationSelect(Array.from(newSelected));
    }
  };

  const handleAnalyzeSelected = async () => {
    if (selectedVariations.size === 0) return;
    
    setAnalyzing(true);
    try {
      const selectedVars = variations.filter(v => selectedVariations.has(v.id));
      await onAnalyzeSelected?.(selectedVars, autoAnalyze);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  if (!variations.length) {
    return null;
  }

  return (
    <Paper sx={{ p: compact ? 2 : 3, mt: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AutoAwesome sx={{ color: 'primary.main' }} />
          <Typography variant={compact ? "subtitle1" : "h6"} sx={{ fontWeight: 700 }}>
            💎 Generated Variations
          </Typography>
          <Badge badgeContent={variations.length} color="primary">
            <Chip size="small" label="Ready" color="success" variant="outlined" />
          </Badge>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {compact && (
            <IconButton onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          )}
        </Box>
      </Box>

      <Collapse in={expanded}>
        {/* Selection Controls */}
        <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(37, 99, 235, 0.05)', borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Select variations to analyze ({selectedVariations.size} selected)
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button 
                size="small" 
                onClick={handleSelectAll}
                startIcon={<CheckCircle />}
              >
                {selectedVariations.size === variations.length ? 'Deselect All' : 'Select All'}
              </Button>
              <Button 
                size="small" 
                onClick={handleSelectBest}
                startIcon={<TrendingUp />}
                color="warning"
              >
                Select Best
              </Button>
            </Box>
          </Box>
          
          {showAnalysisOptions && (
            <FormControlLabel
              control={
                <Switch 
                  checked={autoAnalyze}
                  onChange={(e) => setAutoAnalyze(e.target.checked)}
                  color="primary"
                />
              }
              label="🚀 Run through all 8 analysis tools automatically"
              sx={{ mb: 1 }}
            />
          )}
        </Box>

        {/* Variations Grid */}
        <Grid container spacing={2}>
          {variations.map((variation, index) => (
            <Grid item xs={12} md={6} key={variation.id || index}>
              <Card 
                sx={{ 
                  border: selectedVariations.has(variation.id || index) ? 2 : 1,
                  borderColor: selectedVariations.has(variation.id || index) ? 'primary.main' : 'divider',
                  position: 'relative',
                  '&:hover': {
                    boxShadow: 2
                  }
                }}
              >
                <CardContent sx={{ p: 2 }}>
                  {/* Variation Header */}
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Checkbox
                        checked={selectedVariations.has(variation.id || index)}
                        onChange={() => handleVariationToggle(variation.id || index)}
                        color="primary"
                      />
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        Variation {String.fromCharCode(65 + index)}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {variation.metadata?.roi_score && (
                        <Chip 
                          label={`ROI: ${variation.metadata.roi_score}/100`}
                          size="small"
                          color="warning"
                          variant="filled"
                          icon={<Speed />}
                        />
                      )}
                      {variation.variation_strategy && (
                        <Chip 
                          label={variation.variation_strategy.replace('_', ' ')}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>

                  {/* Variation Content */}
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ mb: 1.5 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block' }}>
                        HEADLINE
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
                        {variation.headline}
                      </Typography>
                      <IconButton 
                        size="small" 
                        onClick={() => copyToClipboard(variation.headline)}
                        sx={{ ml: 1 }}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Box>
                    
                    <Box sx={{ mb: 1.5 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block' }}>
                        BODY TEXT
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {variation.body_text}
                      </Typography>
                      <IconButton 
                        size="small" 
                        onClick={() => copyToClipboard(variation.body_text)}
                        sx={{ ml: 1 }}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block' }}>
                          CTA
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                          {variation.cta}
                        </Typography>
                      </Box>
                      <IconButton 
                        size="small" 
                        onClick={() => copyToClipboard(variation.cta)}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>

                  {/* ROI Explanation */}
                  {variation.metadata?.roi_explanation && (
                    <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(245, 158, 11, 0.1)', borderRadius: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                        WHY THIS WORKS:
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {variation.metadata.roi_explanation}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Action Buttons */}
        {showAnalysisOptions && (
          <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleAnalyzeSelected}
              disabled={selectedVariations.size === 0 || analyzing}
              startIcon={analyzing ? <CircularProgress size={20} /> : <Science />}
              sx={{ 
                minWidth: 280,
                py: 1.5,
                px: 4,
                fontSize: '1.1rem',
                fontWeight: 700,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  transform: 'translateY(-2px)',
                },
                '&:disabled': {
                  background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                  transform: 'none'
                }
              }}
            >
              {analyzing 
                ? `🔬 Analyzing ${selectedVariations.size} variations...`
                : `🔬 Analyze Selected Variations (${selectedVariations.size})`
              }
            </Button>
          </Box>
        )}

        {/* Info Alert */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>💡 Tip:</strong> Select your best variations and we'll run them through all 8 analysis tools 
            (Compliance, Legal Risk, Brand Voice, Psychology, etc.) to give you comprehensive insights 
            for campaign optimization.
          </Typography>
        </Alert>
      </Collapse>
    </Paper>
  );
};

export default VariationPreview;
