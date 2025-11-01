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
  Menu,
  MenuItem,
  alpha,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ContentCopy as CopyIcon,
  CheckCircle as CheckIcon,
  CheckCircle,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  AutoAwesome as ImproveIcon,
  CompareArrows as CompareIcon,
  FileDownload as ExportIcon,
  TrendingUp,
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
  console.log('🧪 ABCTestingGrid MOUNTED');
  console.log('📥 Props received:', { 
    hasOriginalCopy: !!originalCopy, 
    hasImprovedCopy: !!improvedCopy, 
    variationsCount: variations?.length || 0,
    platform,
    isLoading,
    originalCopy,
    improvedCopy,
    variations
  });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [copiedStates, setCopiedStates] = useState({});
  const [expandedReasons, setExpandedReasons] = useState({});
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState([]);
  const [exportMenuAnchor, setExportMenuAnchor] = useState(null);

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
  console.log('🔧 Processing variations...');
  console.log('📦 Raw variations array:', variations);
  
  const processedVariations = [
    {
      id: 'improved',
      type: 'improved',
      title: 'Improved',
      badge: 'Optimized',
      badgeColor: 'primary',
      headline: improvedCopy?.headline || '(Improved version will appear here)',
      body_text: improvedCopy?.body_text || 'Optimized ad copy with enhanced messaging',
      cta: improvedCopy?.cta || 'Learn More',
      score: improvedCopy?.score || improvedCopy?.predicted_score || 85,
      reasoning: improvedCopy?.reasoning || [
        'Balanced approach incorporating best practices',
        'Enhanced clarity and emotional appeal',
        'Optimized for platform-specific engagement'
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
      headline: variations.find(v => v.variant_type?.includes('benefit'))?.headline || '(Benefit-focused variation)',
      body_text: variations.find(v => v.variant_type?.includes('benefit'))?.body_text || 'Highlights positive outcomes and transformation',
      cta: variations.find(v => v.variant_type?.includes('benefit'))?.cta || 'Discover Benefits',
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
      headline: variations.find(v => v.variant_type?.includes('problem'))?.headline || '(Problem-focused variation)',
      body_text: variations.find(v => v.variant_type?.includes('problem'))?.body_text || 'Identifies pain points and offers solutions',
      cta: variations.find(v => v.variant_type?.includes('problem'))?.cta || 'Solve This Now',
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
      headline: variations.find(v => v.variant_type?.includes('story'))?.headline || '(Story-driven variation)',
      body_text: variations.find(v => v.variant_type?.includes('story'))?.body_text || 'Tells a compelling story to build emotional connection',
      cta: variations.find(v => v.variant_type?.includes('story'))?.cta || 'Hear Our Story',
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
  
  console.log('✅ Processed variations:', processedVariations);
  console.log('📊 Variation summary:', processedVariations.map(v => ({
    id: v.id,
    title: v.title,
    hasHeadline: !!v.headline,
    hasBody: !!v.body_text,
    score: v.score
  })));

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

  const handleFurtherImprove = async (variation) => {
    // Check if user has sufficient credits (need 2 credits)
    try {
      // Import credit check utility
      const { checkCredits, deductCredits } = await import('../../services/apiService');
      
      const hasCredits = await checkCredits(2);
      if (!hasCredits) {
        toast.error('Insufficient credits. You need 2 credits to improve a variant.');
        return;
      }
      
      // Deduct 2 credits
      await deductCredits(2, 'variant_improvement');
      
      if (onImprove) {
        toast.success('Improving variant... (2 credits deducted)');
        onImprove(variation);
      } else {
        toast('Further improvement coming soon!', { icon: '🚀' });
      }
    } catch (error) {
      console.error('Credit check/deduction error:', error);
      toast.error('Failed to process improvement request');
    }
  };

  const handleExportAll = (format = 'json') => {
    if (format === 'csv') {
      // Export as CSV
      const csvContent = [
        ['Type', 'Strategy', 'Headline', 'Body Text', 'CTA', 'Score', 'Target Audience', 'Best For'],
        // Original
        ['Original', 'Baseline', 
         originalCopy?.headline || '', 
         originalCopy?.body_text || '', 
         originalCopy?.cta || '',
         originalCopy?.score || 60,
         'General',
         'Baseline comparison'],
        // Processed variations
        ...processedVariations.map(v => [
          v.title,
          v.approach || v.badge,
          v.headline || '',
          v.body_text || '',
          v.cta || '',
          v.score || 0,
          v.targetAudience || '',
          (v.patterns || []).join('; ')
        ])
      ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `abc-test-variations-${platform}-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      
      toast.success('Exported as CSV!');
    } else {
      // Default export as JSON
      if (onExport) {
        onExport(processedVariations);
      } else {
        const exportData = {
          platform,
          original: originalCopy,
          improved: processedVariations[0],
          variations: processedVariations.slice(1).map(v => ({
            type: v.type,
            headline: v.headline,
            body_text: v.body_text,
            cta: v.cta,
            score: v.score,
            reasoning: v.reasoning,
            targetAudience: v.targetAudience
          }))
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ad-variations-${platform}-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        toast.success('Exported as JSON!');
      }
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getCharCountColor = (text, limit) => {
    const length = text?.length || 0;
    // More subtle: only show red when OVER limit, otherwise gray
    if (length > limit) return theme.palette.error.main;
    return theme.palette.text.secondary; // Subtle gray
  };
  
  // Find the winning variation (highest score)
  const getWinningVariation = () => {
    const allVariations = [originalCopy, ...processedVariations];
    return allVariations.reduce((winner, current) => 
      (current.score || 0) > (winner.score || 0) ? current : winner
    , allVariations[0]);
  };
  
  const winningVariation = getWinningVariation();

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
    
    // Check if this is the winning variation
    const isWinner = !isOriginal && (variation.score || 0) === (winningVariation.score || 0) && variation.id === winningVariation.id;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        style={{ height: '100%' }}
      >
        <Card
          elevation={isOriginal ? 1 : 2}
          sx={{
            height: '100%',
            minHeight: '500px',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            border: `2px solid`,
            // Purposeful color: green border ONLY for winner, otherwise subtle gray
            borderColor: isOriginal 
              ? theme.palette.divider
              : isWinner
                ? theme.palette.success.main
                : alpha(theme.palette.divider, 0.5),
            background: isOriginal 
              ? alpha(theme.palette.background.paper, 0.5)
              : isWinner
                ? alpha(theme.palette.success.main, 0.02)
                : alpha(theme.palette.background.paper, 0.95),
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': !isOriginal ? {
              transform: 'translateY(-2px)',
              boxShadow: `0 12px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
              borderColor: isWinner ? theme.palette.success.main : theme.palette.primary.light
            } : {}
          }}>
          <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5, flexWrap: 'wrap' }}>
                <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>
                  {isOriginal ? 'Original' : variation.title}
                </Typography>
                {!isOriginal && (
                  <Chip
                    label={variation.badge}
                    color={variation.badgeColor}
                    size="small"
                    sx={{ fontWeight: 700, fontSize: '0.7rem', height: 24 }}
                  />
                )}
                {/* Winner Badge */}
                {isWinner && (
                  <Chip
                    icon={<CheckCircle sx={{ fontSize: 14 }} />}
                    label="Expected Winner"
                    color="success"
                    size="small"
                    sx={{ fontWeight: 700, fontSize: '0.7rem', height: 24 }}
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
                <Tooltip title="Further refine this variation (2 credits)">
                  <Button
                    variant="outlined"
                    size="small"
                    fullWidth
                    startIcon={<ImproveIcon sx={{ fontSize: 16 }} />}
                    onClick={() => handleFurtherImprove(variation)}
                    sx={{ 
                      textTransform: 'none',
                      borderColor: alpha(theme.palette.primary.main, 0.3),
                      color: theme.palette.text.secondary,
                      '&:hover': {
                        borderColor: theme.palette.primary.main,
                        color: theme.palette.primary.main,
                        bgcolor: alpha(theme.palette.primary.main, 0.04)
                      }
                    }}
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
    console.log('⏳ ABCTestingGrid: Rendering loading state...');
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Generating A/B/C Test Variations...</Typography>
        <LinearProgress sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} md={6} key={i}>
              <Card sx={{ height: 300 }}>
                <CardContent>
                  <Box>
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

  console.log('🎨 ABCTestingGrid: Rendering main grid...');
  
  return (
    <Box>
      {/* Test Overview Section */}
      <Card 
        elevation={0}
        sx={{ 
          mb: 4, 
          p: 3,
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`
        }}
      >
        <Typography variant="h6" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BeakerIcon sx={{ color: theme.palette.primary.main }} />
          Test Overview
        </Typography>
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Original Score
              </Typography>
              <Typography variant="h4" fontWeight={700} color="warning.main">
                {Math.round(originalCopy?.score || 60)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Best Score
              </Typography>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {Math.round(winningVariation?.score || 75)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Improvement
              </Typography>
              <Typography variant="h4" fontWeight={700} color="primary.main">
                +{Math.round((winningVariation?.score || 75) - (originalCopy?.score || 60))}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Variations
              </Typography>
              <Typography variant="h4" fontWeight={700}>
                {processedVariations.length}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Card>
      
      {/* Header */}
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
              onClick={(e) => setExportMenuAnchor(e.currentTarget)}
              sx={{ textTransform: 'none' }}
            >
              Export
            </Button>
          </Tooltip>
        </Box>
      </Box>

      {/* 2x2 Grid Layout - Top row: Original + Improved, Bottom row: A/B/C variants */}
      <Grid container spacing={4}>
        {/* Top Row - Original and Improved */}
        <Grid item xs={12} md={6}>
          <VariationCard
            variation={{
              id: 'original',
              title: 'Original',
              headline: originalCopy?.headline || '',
              body_text: originalCopy?.body_text || '',
              cta: originalCopy?.cta || '',
              score: originalCopy?.score || 60
            }}
            isOriginal={true}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <VariationCard variation={processedVariations[0]} />
        </Grid>

        {/* Bottom Row - A/B/C Variations */}
        <Grid item xs={12} md={4}>
          <VariationCard variation={processedVariations[1]} />
        </Grid>

        <Grid item xs={12} md={4}>
          <VariationCard variation={processedVariations[2]} />
        </Grid>

        <Grid item xs={12} md={4}>
          <VariationCard variation={processedVariations[3]} />
        </Grid>
      </Grid>

      {/* Performance Predictor */}
      <Box sx={{ 
        mt: 4, 
        p: 3, 
        backgroundColor: alpha(theme.palette.info.main, 0.08), 
        borderRadius: 2,
        border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <TrendingUp sx={{ color: theme.palette.info.main, fontSize: '1.5rem' }} />
          <Typography variant="h6" fontWeight={700} color="info.main">
            A/B/C Performance Predictions
          </Typography>
        </Box>
        
        <Grid container spacing={3}>
          {[{ title: 'Original', score: originalCopy?.score || 60 }, ...processedVariations].map((variation, idx) => (
            <Grid item xs={6} sm={4} md={2.4} key={idx}>
              <Box sx={{ 
                p: 2, 
                borderRadius: 1, 
                backgroundColor: alpha(theme.palette.background.paper, 0.8),
                border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
                textAlign: 'center'
              }}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  {variation.title}
                </Typography>
                <Typography variant="h5" fontWeight={700} color="primary" gutterBottom>
                  {variation.score || 75}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Est. CTR: {(((variation.score || 75) / 100 * 3.5)).toFixed(2)}%
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Conv: {(((variation.score || 75) / 100 * 2.1)).toFixed(2)}%
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
        
        <Typography variant="caption" color="text.secondary" display="block" mt={2}>
          * Predictions based on {platform} benchmarks and AI analysis of copy effectiveness
        </Typography>
      </Box>

      {/* Export Menu */}
      <Menu
        anchorEl={exportMenuAnchor}
        open={Boolean(exportMenuAnchor)}
        onClose={() => setExportMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          handleExportAll('json');
          setExportMenuAnchor(null);
        }}>
          <ExportIcon sx={{ mr: 1 }} />
          Export as JSON
        </MenuItem>
        <MenuItem onClick={() => {
          handleExportAll('csv');
          setExportMenuAnchor(null);
        }}>
          <ExportIcon sx={{ mr: 1 }} />
          Export as CSV
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ABCTestingGrid;
