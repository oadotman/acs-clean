import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Divider,
  Stack,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Compare as CompareIcon,
  ContentCopy as ContentCopyIcon,
  Star as StarIcon,
  Warning as WarningIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Favorite as FavoriteIcon,
  FilterList as FilterListIcon,
  TrendingUp as TrendingUpIcon,
  SwapHoriz as SwapHorizIcon,
  Visibility as VisibilityIcon,
  Save as SaveIcon,
  Share as ShareIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import UserFeedback from './UserFeedback';
import creativeControlsService from '../../services/creativeControlsService';

const VariantComparison = ({ variants = [], onSaveVariant, onMixAndMatch, showMetrics = true, platform = 'facebook' }) => {
  const [selectedVariants, setSelectedVariants] = useState([]);
  const [showMixDialog, setShowMixDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [mixedVariant, setMixedVariant] = useState(null);

  // Handle feedback submission
  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      await creativeControlsService.submitFeedback(feedbackData);
      console.log('Feedback submitted successfully:', feedbackData);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  // Calculate comparison metrics
  const comparisonMetrics = useMemo(() => {
    if (variants.length === 0) return null;

    const creativityScores = variants.map(v => v.variant_config?.creativity_level || 5);
    const urgencyScores = variants.map(v => v.variant_config?.urgency_level || 5);
    const lengths = variants.map(v => (v.headline?.length || 0) + (v.body_text?.length || 0) + (v.cta?.length || 0));
    const clicheCounts = variants.map(v => v.cliche_count || 0);

    return {
      creativity: {
        min: Math.min(...creativityScores),
        max: Math.max(...creativityScores),
        avg: creativityScores.reduce((a, b) => a + b, 0) / creativityScores.length
      },
      urgency: {
        min: Math.min(...urgencyScores),
        max: Math.max(...urgencyScores),
        avg: urgencyScores.reduce((a, b) => a + b, 0) / urgencyScores.length
      },
      length: {
        min: Math.min(...lengths),
        max: Math.max(...lengths),
        avg: lengths.reduce((a, b) => a + b, 0) / lengths.length
      },
      originality: {
        bestScore: Math.min(...clicheCounts),
        worstScore: Math.max(...clicheCounts),
        avg: clicheCounts.reduce((a, b) => a + b, 0) / clicheCounts.length
      }
    };
  }, [variants]);

  const VariantCard = ({ variant, index, isSelected, onSelect }) => {
    const config = variant.variant_config || {};
    const riskLevel = variant.risk_level || 'Medium';
    const riskColor = riskLevel === 'Low' ? '#4caf50' : riskLevel === 'Medium' ? '#ff9800' : '#f44336';

    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
      >
        <Card 
          variant="outlined"
          sx={{ 
            height: '100%',
            cursor: 'pointer',
            border: isSelected ? '2px solid #1976d2' : '1px solid rgba(0, 0, 0, 0.12)',
            backgroundColor: isSelected ? 'rgba(25, 118, 210, 0.05)' : 'inherit',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              boxShadow: 2,
              transform: 'translateY(-2px)'
            }
          }}
          onClick={() => onSelect && onSelect(variant, index)}
        >
          <CardContent sx={{ p: 2 }}>
            {/* Variant Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {variant.variant_name || `Variant ${index + 1}`}
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Chip
                  size="small"
                  label={riskLevel}
                  sx={{
                    backgroundColor: riskColor + '20',
                    color: riskColor,
                    fontWeight: 600
                  }}
                />
                {variant.predicted_performance_score && (
                  <Chip
                    size="small"
                    label={`${variant.predicted_performance_score}%`}
                    color="primary"
                    variant="outlined"
                  />
                )}
              </Box>
            </Box>

            {/* Creative Settings */}
            <Grid container spacing={1} sx={{ mb: 2 }}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <PsychologyIcon fontSize="small" color="primary" />
                  <Typography variant="caption" display="block">Creativity</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {config.creativity_level || 5}/10
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <SpeedIcon fontSize="small" color="secondary" />
                  <Typography variant="caption" display="block">Urgency</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {config.urgency_level || 5}/10
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <FavoriteIcon fontSize="small" color="error" />
                  <Typography variant="caption" display="block">Emotion</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>
                    {config.emotion_type?.charAt(0).toUpperCase() + config.emotion_type?.slice(1) || 'N/A'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            {/* Ad Copy Content */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                HEADLINE
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                {variant.headline || 'No headline'}
              </Typography>

              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                BODY TEXT
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, lineHeight: 1.4 }}>
                {variant.body_text || 'No body text'}
              </Typography>

              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                CALL-TO-ACTION
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                {variant.cta || 'No CTA'}
              </Typography>
            </Box>

            {/* Metrics */}
            {showMetrics && (
              <Box>
                <Divider sx={{ my: 1 }} />
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">Length</Typography>
                    <Typography variant="body2">
                      {(variant.headline?.length || 0) + (variant.body_text?.length || 0) + (variant.cta?.length || 0)} chars
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">Originality</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="body2">
                        {variant.cliche_count === 0 ? 'Perfect' : variant.cliche_count === 1 ? 'Good' : 'Fair'}
                      </Typography>
                      {variant.cliche_count === 0 && <StarIcon fontSize="small" color="warning" />}
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {/* User Feedback */}
            <Box sx={{ mt: 2 }}>
              <UserFeedback
                generatedCopy={{
                  headline: variant.headline,
                  body: variant.body_text,
                  cta: variant.cta
                }}
                analysisId={variant.analysis_id || `variant_${index}`}
                onFeedbackSubmit={handleFeedbackSubmit}
                platform={platform}
                compact={true}
              />
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const ComparisonTable = () => (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell><strong>Aspect</strong></TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                <strong>Variant {index + 1}</strong>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Creativity Level</TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                {variant.variant_config?.creativity_level || 5}/10
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Urgency Level</TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                {variant.variant_config?.urgency_level || 5}/10
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Emotion Type</TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                {variant.variant_config?.emotion_type || 'N/A'}
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Character Count</TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                {(variant.headline?.length || 0) + (variant.body_text?.length || 0) + (variant.cta?.length || 0)}
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Cliché Count</TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                {variant.cliche_count || 0}
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Risk Level</TableCell>
            {variants.map((variant, index) => (
              <TableCell key={index} align="center">
                <Chip
                  size="small"
                  label={variant.risk_level || 'Medium'}
                  color={
                    variant.risk_level === 'Low' ? 'success' :
                    variant.risk_level === 'Medium' ? 'warning' : 'error'
                  }
                />
              </TableCell>
            ))}
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );

  const MixAndMatchDialog = () => (
    <Dialog open={showMixDialog} onClose={() => setShowMixDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SwapHorizIcon />
          Mix & Match Elements
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          Combine the best elements from different variants to create the perfect ad copy.
        </Typography>

        <Grid container spacing={3}>
          {/* Headlines */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              Headlines
            </Typography>
            <Stack spacing={1}>
              {variants.map((variant, index) => (
                <Card 
                  key={`headline-${index}`} 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.05)' }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">{variant.headline}</Typography>
                    <Chip size="small" label={`Variant ${index + 1}`} />
                  </Box>
                </Card>
              ))}
            </Stack>
          </Grid>

          {/* Body Text */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              Body Text
            </Typography>
            <Stack spacing={1}>
              {variants.map((variant, index) => (
                <Card 
                  key={`body-${index}`} 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.05)' }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="body2" sx={{ flex: 1 }}>
                      {variant.body_text?.substring(0, 120)}
                      {variant.body_text?.length > 120 && '...'}
                    </Typography>
                    <Chip size="small" label={`Variant ${index + 1}`} />
                  </Box>
                </Card>
              ))}
            </Stack>
          </Grid>

          {/* CTAs */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              Call-to-Actions
            </Typography>
            <Stack spacing={1}>
              {variants.map((variant, index) => (
                <Card 
                  key={`cta-${index}`} 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.05)' }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                      {variant.cta}
                    </Typography>
                    <Chip size="small" label={`Variant ${index + 1}`} />
                  </Box>
                </Card>
              ))}
            </Stack>
          </Grid>
        </Grid>

        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            Click on elements above to mix and match them. The combined variant will appear below.
          </Typography>
        </Alert>

        {mixedVariant && (
          <Box sx={{ mt: 3, p: 2, border: '2px dashed #1976d2', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              Mixed Variant Preview
            </Typography>
            {/* Mixed variant preview would go here */}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowMixDialog(false)}>Cancel</Button>
        <Button variant="contained" disabled={!mixedVariant}>
          Save Mixed Variant
        </Button>
      </DialogActions>
    </Dialog>
  );

  const MetricsSummary = () => (
    <Card variant="outlined" sx={{ mb: 3, backgroundColor: 'rgba(25, 118, 210, 0.02)' }}>
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingUpIcon />
          Comparison Overview
        </Typography>
        
        {comparisonMetrics && (
          <Grid container spacing={2}>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" color="textSecondary">Creativity Range</Typography>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {comparisonMetrics.creativity.min}-{comparisonMetrics.creativity.max}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(comparisonMetrics.creativity.avg / 10) * 100} 
                  sx={{ mt: 1 }}
                />
              </Box>
            </Grid>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" color="textSecondary">Urgency Range</Typography>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {comparisonMetrics.urgency.min}-{comparisonMetrics.urgency.max}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(comparisonMetrics.urgency.avg / 10) * 100} 
                  sx={{ mt: 1 }}
                  color="secondary"
                />
              </Box>
            </Grid>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" color="textSecondary">Length Range</Typography>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {comparisonMetrics.length.min}-{comparisonMetrics.length.max}
                </Typography>
                <Typography variant="caption" color="textSecondary">characters</Typography>
              </Box>
            </Grid>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" color="textSecondary">Best Originality</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {comparisonMetrics.originality.bestScore === 0 ? 'Perfect' : 'Good'}
                  </Typography>
                  {comparisonMetrics.originality.bestScore === 0 && <StarIcon color="warning" />}
                </Box>
              </Box>
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  if (variants.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="textSecondary">
          No variants to compare
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Generate multiple variants to see the comparison here.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          <CompareIcon />
          Variant Comparison
          <Chip label={`${variants.length} variants`} color="primary" size="small" />
        </Typography>
        
        <Stack direction="row" spacing={1}>
          <Button
            startIcon={<SwapHorizIcon />}
            variant="outlined"
            onClick={() => setShowMixDialog(true)}
            disabled={variants.length < 2}
          >
            Mix & Match
          </Button>
          <Button
            startIcon={<SaveIcon />}
            variant="contained"
            onClick={() => onSaveVariant && onSaveVariant(selectedVariants)}
            disabled={selectedVariants.length === 0}
          >
            Save Selected
          </Button>
        </Stack>
      </Box>

      <MetricsSummary />

      <Box sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Card View" />
          <Tab label="Table View" />
        </Tabs>
      </Box>

      <AnimatePresence mode="wait">
        {activeTab === 0 ? (
          <motion.div
            key="cards"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={3}>
              {variants.map((variant, index) => (
                <Grid item xs={12} md={6} lg={4} key={index}>
                  <VariantCard
                    variant={variant}
                    index={index}
                    isSelected={selectedVariants.includes(variant)}
                    onSelect={(variant) => {
                      setSelectedVariants(prev => 
                        prev.includes(variant) 
                          ? prev.filter(v => v !== variant)
                          : [...prev, variant]
                      );
                    }}
                  />
                </Grid>
              ))}
            </Grid>
          </motion.div>
        ) : (
          <motion.div
            key="table"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ComparisonTable />
          </motion.div>
        )}
      </AnimatePresence>

      <MixAndMatchDialog />
    </Box>
  );
};

export default VariantComparison;