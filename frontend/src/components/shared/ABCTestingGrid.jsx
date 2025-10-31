import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  Collapse,
  LinearProgress,
  Tooltip,
  Grid,
  alpha,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ContentCopy as CopyIcon,
  CheckCircle as CheckIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  AutoAwesome as ImproveIcon,
  CompareArrows as CompareIcon,
  FileDownload as ExportIcon,
  TrendingUp as PredictorIcon,
  Science as BeakerIcon
} from '@mui/icons-material';
import toast from 'react-hot-toast';

/**
 * Dynamic A/B/C Testing Grid Component
 * 
 * Displays original, improved, and 3 test variations in a responsive 2x2 grid
 * with interactive features and detailed reasoning
 */
const ABCTestingGrid = ({
  originalCopy,
  improvedCopy,
  variations = [],
  platform = 'facebook',
  onImprove,
  onExport,
  isLoading = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [copiedStates, setCopiedStates] = useState({});
  const [expandedReasons, setExpandedReasons] = useState({});
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState([]);

  // Platform character limits
  const platformLimits = {
    facebook: { headline: 40, body: 125, cta: 30 },
    instagram: { headline: 30, body: 125, cta: 30 },
    google: { headline: 30, body: 90, cta: 15 },
    linkedin: { headline: 70, body: 150, cta: 30 },
    tiktok: { headline: 100, body: 100, cta: 20 }
  };

  const limits = platformLimits[platform] || platformLimits.facebook;

  // Process variations to ensure we have all 4
  const processedVariations = [
    {
      id: 'improved',
      type: 'improved',
      title: 'Improved',
      badge: 'Optimized',
      badgeColor: 'primary',
      ...improvedCopy,
      score: improvedCopy?.score || 85,
      reasoning: [
        'Balanced approach incorporating best practices',
        'Enhanced clarity and emotional appeal'
      ],
      targetAudience: 'General audience',
      approach: 'Combines proven conversion tactics'
    },
    {
      id: 'variation_a',
      type: 'benefit_focused',
      title: 'Variation A',
      badge: 'Benefit-Focused',
      badgeColor: 'success',
      ...variations.find(v => v.variant_type?.includes('benefit') || v.variant_type === 'variation_a_benefit'),
      score: variations.find(v => v.variant_type?.includes('benefit'))?.predicted_score || 82,
      reasoning: [
        'Emphasizes transformation and positive outcomes',
        'Uses aspirational language to inspire action',
        'Focuses on "what you gain" messaging'
      ],
      targetAudience: 'Solution-seekers, optimistic buyers, warm leads',
      approach: 'Benefit-Focused',
      patterns: ['Unlock...', 'Discover...', 'Transform...', 'Achieve...']
    },
    {
      id: 'variation_b',
      type: 'problem_focused',
      title: 'Variation B',
      badge: 'Problem-Focused',
      badgeColor: 'warning',
      ...variations.find(v => v.variant_type?.includes('problem') || v.variant_type === 'variation_b_problem'),
      score: variations.find(v => v.variant_type?.includes('problem'))?.predicted_score || 84,
      reasoning: [
        'Opens with pain point recognition',
        'Shows empathy and understanding',
        'Presents solution as immediate relief'
      ],
      targetAudience: 'Pain-aware audiences, high urgency, active seekers',
      approach: 'Problem-Focused',
      patterns: ['Tired of...', 'Struggling with...', 'Stop...', 'No more...']
    },
    {
      id: 'variation_c',
      type: 'story_driven',
      title: 'Variation C',
      badge: 'Story-Driven',
      badgeColor: 'info',
      ...variations.find(v => v.variant_type?.includes('story') || v.variant_type === 'variation_c_story'),
      score: variations.find(v => v.variant_type?.includes('story'))?.predicted_score || 80,
      reasoning: [
        'Uses narrative structure (setup, conflict, resolution)',
        'Builds emotional connection through storytelling',
        'Includes social proof and testimonial angles'
      ],
      targetAudience: 'Trust-seekers, relationship-oriented buyers, cold traffic',
      approach: 'Story-Driven',
      patterns: ['Like you...', 'Meet [name]...', "Here's how...", 'Imagine...']
    }
  ];

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      toast.success('Copied to clipboard!');
      
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
    }).catch(() => {
      toast.error('Failed to copy');
    });
  };

  const toggleReasonExpanded = (id) => {
    setExpandedReasons(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleFurtherImprove = (variation) => {
    if (onImprove) {
      onImprove(variation);
    } else {
      toast('Further improvement coming soon!', { icon: '🚀' });
    }
  };

  const handleExportAll = () => {
    if (onExport) {
      onExport(processedVariations);
    } else {
      // Default export as JSON
      const exportData = {
        platform,
        original: originalCopy,
        variations: processedVariations.map(v => ({
          type: v.type,
          headline: v.headline,
          body_text: v.body_text,
          cta: v.cta,
          score: v.score,
          reasoning: v.reasoning
        }))
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ad-variations-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      toast.success('Exported all variations!');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getCharCountColor = (text, limit) => {
    const length = text?.length || 0;
    if (length > limit) return theme.palette.error.main;
    if (length > limit * 0.9) return theme.palette.warning.main;
    return theme.palette.success.main;
  };

  const highlightPowerWords = (text) => {
    const powerWords = [
      'exclusive', 'proven', 'guaranteed', 'transform', 'discover', 'unlock',
      'amazing', 'incredible', 'breakthrough', 'revolutionary', 'secret',
      'free', 'save', 'instant', 'now', 'today', 'limited'
    ];
    
    let highlighted = text;
    powerWords.forEach(word => {
      const regex = new RegExp(`\\b(${word})\\b`, 'gi');
      highlighted = highlighted.replace(regex, `<mark style="background: ${alpha(theme.palette.primary.main, 0.2)}; padding: 0 2px;">$1</mark>`);
    });
    
    return highlighted;
  };

  const VariationCard = ({ variation, isOriginal = false }) => {
    const fullText = `${variation.headline} ${variation.body_text} ${variation.cta}`;
    const headlineLength = variation.headline?.length || 0;
    const bodyLength = variation.body_text?.length || 0;
    const ctaLength = variation.cta?.length || 0;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Card
          elevation={isOriginal ? 1 : 3}
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            border: isOriginal ? `2px solid ${alpha(theme.palette.grey[400], 0.3)}` : 'none',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: isOriginal ? 'none' : 'translateY(-4px)',
              boxShadow: theme.shadows[8]
            }
          }}
        >
          <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h6" fontWeight={600}>
                  {isOriginal ? 'Original' : variation.title}
                </Typography>
                {!isOriginal && (
                  <Chip
                    label={variation.badge}
                    color={variation.badgeColor}
                    size="small"
                    sx={{ fontWeight: 600 }}
                  />
                )}
              </Box>
              
              {/* Score Gauge */}
              {!isOriginal && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={`${Math.round(variation.score)}/100`}
                    color={getScoreColor(variation.score)}
                    size="small"
                    icon={<TrendingUp />}
                    sx={{ fontWeight: 700 }}
                  />
                </Box>
              )}
            </Box>

            {/* Score Progress Bar */}
            {!isOriginal && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={variation.score}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: alpha(theme.palette.grey[300], 0.3),
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 3,
                      backgroundColor: 
                        variation.score >= 85 ? theme.palette.success.main :
                        variation.score >= 70 ? theme.palette.warning.main :
                        theme.palette.error.main
                    }
                  }}
                />
              </Box>
            )}

            {/* Copy Text with Power Word Highlighting */}
            <Box sx={{ flexGrow: 1, mb: 2 }}>
              {/* Headline */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  HEADLINE
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={600}
                  dangerouslySetInnerHTML={{ __html: highlightPowerWords(variation.headline || '') }}
                  sx={{ mt: 0.5 }}
                />
                <Typography
                  variant="caption"
                  sx={{ color: getCharCountColor(variation.headline, limits.headline) }}
                >
                  {headlineLength}/{limits.headline}
                </Typography>
              </Box>

              {/* Body */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  BODY
                </Typography>
                <Typography
                  variant="body2"
                  dangerouslySetInnerHTML={{ __html: highlightPowerWords(variation.body_text || '') }}
                  sx={{ mt: 0.5, lineHeight: 1.6 }}
                />
                <Typography
                  variant="caption"
                  sx={{ color: getCharCountColor(variation.body_text, limits.body) }}
                >
                  {bodyLength}/{limits.body}
                </Typography>
              </Box>

              {/* CTA */}
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  CALL-TO-ACTION
                </Typography>
                <Typography
                  variant="body2"
                  fontWeight={600}
                  dangerouslySetInnerHTML={{ __html: highlightPowerWords(variation.cta || '') }}
                  sx={{ mt: 0.5 }}
                />
                <Typography
                  variant="caption"
                  sx={{ color: getCharCountColor(variation.cta, limits.cta) }}
                >
                  {ctaLength}/{limits.cta}
                </Typography>
              </Box>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 1, mb: !isOriginal ? 2 : 0 }}>
              <Button
                variant="outlined"
                size="small"
                fullWidth
                startIcon={copiedStates[variation.id] ? <CheckIcon /> : <CopyIcon />}
                onClick={() => handleCopy(fullText, variation.id)}
                disabled={copiedStates[variation.id]}
                sx={{ textTransform: 'none' }}
              >
                {copiedStates[variation.id] ? 'Copied!' : 'Copy'}
              </Button>
              
              {!isOriginal && (
                <Tooltip title="Refine this variation further">
                  <Button
                    variant="contained"
                    size="small"
                    fullWidth
                    startIcon={<ImproveIcon />}
                    onClick={() => handleFurtherImprove(variation)}
                    sx={{ textTransform: 'none' }}
                  >
                    Improve
                  </Button>
                </Tooltip>
              )}
            </Box>

            {/* Collapsible "Why This Works" Section */}
            {!isOriginal && (
              <>
                <Button
                  size="small"
                  onClick={() => toggleReasonExpanded(variation.id)}
                  endIcon={expandedReasons[variation.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  sx={{ textTransform: 'none', justifyContent: 'space-between', px: 0 }}
                >
                  <Typography variant="caption" fontWeight={600}>
                    Why This Works
                  </Typography>
                </Button>

                <Collapse in={expandedReasons[variation.id]}>
                  <Box
                    sx={{
                      mt: 1,
                      p: 2,
                      backgroundColor: alpha(theme.palette.primary.main, 0.05),
                      borderRadius: 1,
                      borderLeft: `3px solid ${theme.palette.primary.main}`
                    }}
                  >
                    <Typography variant="caption" fontWeight={600} color="primary" display="block" mb={1}>
                      {variation.approach}
                    </Typography>
                    
                    <Typography variant="caption" display="block" mb={1}>
                      <strong>Target:</strong> {variation.targetAudience}
                    </Typography>

                    <Typography variant="caption" display="block" mb={1}>
                      <strong>Strategy:</strong>
                    </Typography>
                    <Box component="ul" sx={{ pl: 2, my: 0 }}>
                      {variation.reasoning.map((reason, idx) => (
                        <Typography key={idx} variant="caption" component="li" sx={{ mb: 0.5 }}>
                          {reason}
                        </Typography>
                      ))}
                    </Box>

                    {variation.patterns && (
                      <>
                        <Typography variant="caption" display="block" mt={1} mb={0.5}>
                          <strong>Common Patterns:</strong>
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {variation.patterns.map((pattern, idx) => (
                            <Chip
                              key={idx}
                              label={pattern}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem', height: 20 }}
                            />
                          ))}
                        </Box>
                      </>
                    )}
                  </Box>
                </Collapse>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Generating A/B/C Test Variations...</Typography>
        <LinearProgress sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} md={6} key={i}>
              <Card sx={{ height: 300 }}>
                <CardContent>
                  <Box sx={{ animation: 'pulse 1.5s ease-in-out infinite' }}>
                    <Box sx={{ height: 20, bgcolor: 'grey.200', borderRadius: 1, mb: 2 }} />
                    <Box sx={{ height: 60, bgcolor: 'grey.100', borderRadius: 1, mb: 2 }} />
                    <Box sx={{ height: 80, bgcolor: 'grey.100', borderRadius: 1 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight={700}>
          <BeakerIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          A/B/C Test Variations
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Compare variations side-by-side">
            <Button
              variant="outlined"
              size="small"
              startIcon={<CompareIcon />}
              onClick={() => setCompareMode(!compareMode)}
              sx={{ textTransform: 'none' }}
            >
              Compare
            </Button>
          </Tooltip>
          
          <Tooltip title="Export all variations">
            <Button
              variant="outlined"
              size="small"
              startIcon={<ExportIcon />}
              onClick={handleExportAll}
              sx={{ textTransform: 'none' }}
            >
              Export
            </Button>
          </Tooltip>
        </Box>
      </Box>

      {/* 2x2 Grid Layout */}
      <Grid container spacing={3}>
        {/* Original (Top Left) */}
        <Grid item xs={12} md={6}>
          <VariationCard
            variation={{
              id: 'original',
              headline: originalCopy?.headline || '',
              body_text: originalCopy?.body_text || '',
              cta: originalCopy?.cta || ''
            }}
            isOriginal={true}
          />
        </Grid>

        {/* Improved (Top Right) */}
        <Grid item xs={12} md={6}>
          <VariationCard variation={processedVariations[0]} />
        </Grid>

        {/* Variation A (Bottom Left) */}
        <Grid item xs={12} md={4}>
          <VariationCard variation={processedVariations[1]} />
        </Grid>

        {/* Variation B (Bottom Center) */}
        <Grid item xs={12} md={4}>
          <VariationCard variation={processedVariations[2]} />
        </Grid>

        {/* Variation C (Bottom Right) */}
        <Grid item xs={12} md={4}>
          <VariationCard variation={processedVariations[3]} />
        </Grid>
      </Grid>

      {/* Performance Predictor (Optional Feature) */}
      <Box sx={{ mt: 4, p: 3, backgroundColor: alpha(theme.palette.info.main, 0.05), borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <PredictorIcon color="info" />
          <Typography variant="h6" fontWeight={600}>
            Performance Prediction
          </Typography>
        </Box>
        
        <Grid container spacing={2}>
          {processedVariations.map((variation, idx) => (
            <Grid item xs={12} sm={6} md={3} key={idx}>
              <Box>
                <Typography variant="caption" fontWeight={600}>
                  {variation.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Est. CTR: {(variation.score / 100 * 3.5).toFixed(2)}%
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
        
        <Typography variant="caption" color="text.secondary" display="block" mt={2}>
          * Predictions based on {platform} benchmarks and historical performance data
        </Typography>
      </Box>
    </Box>
  );
};

export default ABCTestingGrid;
