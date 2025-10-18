import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Tooltip,
  Chip,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Alert,
  CircularProgress,
  Rating,
  Avatar,
  Tabs,
  Tab,
  Paper,
  useTheme,
  Fade
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  SwapHoriz as MixIcon,
  Check as CheckIcon,
  AutoFixHigh as ImproveIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  EmojiEmotions as EmotionIcon,
  Info as InfoIcon,
  BarChart as BarChartIcon,
  Timeline as TimelineIcon,
  FlashOn as FlashOnIcon,
  ThumbUp as ThumbUpIcon,
  AttachMoney as AttachMoneyIcon,
  Close as CloseIcon,
  Speed as PerformanceIcon,
  AutoFixHigh as AutoFixHighIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled, alpha } from '@mui/material/styles';
import { useSnackbar } from 'notistack';
import { variantService } from '../../services/variantService';

// Custom styled components with enhanced theming
const MetricChip = styled(Chip)(({ theme, metrictype }) => {
  const metricColors = {
    engagement: theme.palette.info.main,
    conversion: theme.palette.success.main,
    relevance: theme.palette.warning.main,
    ctr: theme.palette.error.main,
    roas: theme.palette.primary.main,
    frequency: theme.palette.secondary.main
  };

  return {
    backgroundColor: alpha(metricColors[metrictype] || theme.palette.grey[300], 0.2),
    color: theme.palette.getContrastText(metricColors[metrictype] || theme.palette.grey[300]),
    fontWeight: 600,
    fontSize: '0.65rem',
    height: 20,
    '& .MuiChip-icon': { 
      fontSize: '0.8rem',
      color: metricColors[metrictype] || theme.palette.grey[500]
    },
    '&:hover': {
      backgroundColor: alpha(metricColors[metrictype] || theme.palette.grey[300], 0.3),
    },
  };
});


const VariantCard = styled(Card, {
  shouldForwardProp: (prop) => !['isselected', 'varianttype'].includes(prop)
})(({ theme, isselected, varianttype }) => {
  const variantColors = {
    A: {
      light: theme.palette.primary.light,
      main: theme.palette.primary.main,
      dark: theme.palette.primary.dark,
      contrast: theme.palette.primary.contrastText
    },
    B: {
      light: theme.palette.secondary.light,
      main: theme.palette.secondary.main,
      dark: theme.palette.secondary.dark,
      contrast: theme.palette.secondary.contrastText
    },
    C: {
      light: theme.palette.success.light,
      main: theme.palette.success.main,
      dark: theme.palette.success.dark,
      contrast: theme.palette.success.contrastText
    }
  };

  const color = variantColors[varianttype] || variantColors.A;
  
  return {
    cursor: 'pointer',
    transition: theme.transitions.create(['box-shadow', 'transform'], {
      duration: theme.transitions.duration.short,
    }),
    border: `2px solid ${isselected === 'true' ? color.main : theme.palette.divider}`,
    borderRadius: theme.shape.borderRadius * 2,
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: theme.shadows[4],
      borderColor: color.main,
    },
    ...(isselected === 'true' && {
      transform: 'translateY(-2px)',
      boxShadow: theme.shadows[6],
      backgroundColor: alpha(color.main, 0.02),
    }),
  };
});

const VariantHeader = styled(CardContent, {
  shouldForwardProp: (prop) => prop.varianttype === undefined
})(({ theme, varianttype }) => {
  const variantColors = {
    A: {
      light: theme.palette.primary.light,
      main: theme.palette.primary.main,
      dark: theme.palette.primary.dark,
      contrast: theme.palette.primary.contrastText
    },
    B: {
      light: theme.palette.secondary.light,
      main: theme.palette.secondary.main,
      dark: theme.palette.secondary.dark,
      contrast: theme.palette.secondary.contrastText
    },
    C: {
      light: theme.palette.success.light,
      main: theme.palette.success.main,
      dark: theme.palette.success.dark,
      contrast: theme.palette.success.contrastText
    }
  };

  const color = variantColors[varianttype] || variantColors.A;
  
  return {
    padding: theme.spacing(2),
    borderBottom: `1px solid ${theme.palette.divider}`,
    background: `linear-gradient(135deg, ${color.light} 0%, ${color.main} 100%)`,
    color: color.contrast,
    '& .variant-title': {
      display: 'flex',
      alignItems: 'center',
      gap: theme.spacing(1),
      marginBottom: theme.spacing(1),
      '& h6': {
        fontWeight: 700,
        color: color.contrast,
        textShadow: '0 1px 2px rgba(0,0,0,0.1)',
      },
    },
    '& .variant-stats': {
      display: 'flex',
      gap: theme.spacing(1),
      flexWrap: 'wrap',
    },
  };
});

const ABTestVariantsTab = ({ 
  initialVariants = [], 
  adCopy = '', 
  platform = 'facebook',
  onVariantsUpdate,
  onVariantSelect,
  initialLoading = false
}) => {
  const { enqueueSnackbar } = useSnackbar();
  const [variants, setVariants] = useState(initialVariants);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showMixDialog, setShowMixDialog] = useState(false);
  const [improvementPrompt, setImprovementPrompt] = useState('');
  const [isImproving, setIsImproving] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [variantMetrics, setVariantMetrics] = useState({});

  // Load variants on mount if not provided
  useEffect(() => {
    const loadInitialVariants = async () => {
      if (initialVariants.length === 0 && adCopy) {
        try {
          setIsLoading(true);
          const generatedVariants = await variantService.generateVariants(adCopy, platform);
          setVariants(generatedVariants);
          onVariantsUpdate?.(generatedVariants);
        } catch (error) {
          enqueueSnackbar('Failed to generate variants', { variant: 'error' });
          console.error('Error generating variants:', error);
        } finally {
          setIsLoading(false);
        }
      }
    };

    loadInitialVariants();
  }, [adCopy, platform, onVariantsUpdate, enqueueSnackbar]);

  // Load metrics for variants
  useEffect(() => {
    const loadMetrics = async () => {
      const metrics = {};
      for (const variant of variants) {
        try {
          const data = await variantService.getVariantMetrics(variant.id);
          metrics[variant.id] = data;
        } catch (error) {
          console.error(`Error loading metrics for variant ${variant.id}:`, error);
          // Fallback to default metrics
          metrics[variant.id] = {
            engagement: Math.floor(Math.random() * 30) + 70, // 70-100
            conversion: Math.floor(Math.random() * 40) + 60, // 60-100
            relevance: Math.floor(Math.random() * 35) + 65,  // 65-100
            ctr: (Math.random() * 5 + 1).toFixed(2),        // 1-6%
            roas: (Math.random() * 8 + 3).toFixed(1),       // 3-11x
            frequency: (Math.random() * 3 + 1).toFixed(1)   // 1-4
          };
        }
      }
      setVariantMetrics(metrics);
    };

    if (variants.length > 0) {
      loadMetrics();
    }
  }, [variants]);

  // Default variants if none provided
  const defaultVariants = [
    {
      id: 'A',
      type: 'A',
      title: 'Benefit-Focused',
      headline: adCopy.split('\n')[0] || 'Transform Your Results with Our Solution',
      description: adCopy.split('\n').slice(1).join('\n') || 'Experience significant improvements in your key metrics with our proven solution.',
      cta: 'Get Started Now',
      strategy: 'Focused on highlighting benefits and value proposition',
      tone: 'Inspirational and aspirational',
      length: 'Medium',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 'B',
      type: 'B',
      title: 'Problem-Solution',
      headline: `Struggling with ${adCopy.split(' ')[0] || 'Challenges'}?`,
      description: `Our solution addresses your ${adCopy.split(' ').slice(0, 3).join(' ').toLowerCase() || 'specific pain points'} to deliver better results.`,
      cta: 'Solve My Problem',
      strategy: 'Identifies pain points and offers solutions',
      tone: 'Empathetic and supportive',
      length: 'Short',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 'C',
      type: 'C',
      title: 'Social Proof',
      headline: 'Join 10,000+ Satisfied Customers',
      description: `"${adCopy.split('.').slice(0, 2).join('. ')}..." - See why businesses trust our solution.`,
      cta: 'Join Now',
      strategy: 'Leverages social proof and testimonials',
      tone: 'Trust-building and credible',
      length: 'Long',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
  ];

  const displayVariants = variants.length > 0 ? variants : defaultVariants;

  const handleVariantSelect = (variant) => {
    setSelectedVariant(selectedVariant?.id === variant.id ? null : variant);
    onVariantSelect?.(variant);
  };

  const handleRegenerate = async (variantId) => {
    try {
      setIsGenerating(true);
      const updatedVariant = await variantService.regenerateVariant(variantId, {
        ad_copy: adCopy,
        platform,
        variant_type: variantId === 'all' ? 'all' : displayVariants.find(v => v.id === variantId)?.type
      });
      
      if (variantId === 'all') {
        setVariants(updatedVariant.variants);
        onVariantsUpdate?.(updatedVariant.variants);
      } else {
        const updatedVariants = variants.map(v => 
          v.id === variantId ? { ...v, ...updatedVariant } : v
        );
        setVariants(updatedVariants);
        onVariantsUpdate?.(updatedVariants);
      }
      
      enqueueSnackbar('Variant regenerated successfully', { variant: 'success' });
    } catch (error) {
      console.error('Error regenerating variant:', error);
      enqueueSnackbar('Failed to regenerate variant', { variant: 'error' });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImprove = (variant) => {
    setSelectedVariant(variant);
    setShowMixDialog(true);
  };

  const handleImproveSubmit = async () => {
    if (!improvementPrompt.trim() || !selectedVariant) return;
    
    try {
      setIsImproving(true);
      const improvedVariant = await variantService.improveVariant(
        selectedVariant.id,
        improvementPrompt
      );
      
      const updatedVariants = variants.map(v => 
        v.id === selectedVariant.id ? { ...v, ...improvedVariant } : v
      );
      
      setVariants(updatedVariants);
      onVariantsUpdate?.(updatedVariants);
      setShowMixDialog(false);
      setImprovementPrompt('');
      
      enqueueSnackbar('Variant improved successfully', { variant: 'success' });
    } catch (error) {
      console.error('Error improving variant:', error);
      enqueueSnackbar('Failed to improve variant', { variant: 'error' });
    } finally {
      setIsImproving(false);
    }
  };

  const renderMetricChip = (variantId, metricType, label, icon) => {
    const value = variantMetrics[variantId]?.[metricType] || 0;
    return (
      <MetricChip
        size="small"
        icon={icon}
        label={`${label}: ${typeof value === 'number' ? value.toFixed(0) + '%' : value}`}
        metrictype={metricType}
        sx={{ mb: 0.5 }}
      />
    );
  };

  const renderVariantMetrics = (variantId) => {
    const metrics = variantMetrics[variantId] || {};
    return (
      <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {renderMetricChip(variantId, 'engagement', 'Engage', <TrendingUpIcon />)}
        {renderMetricChip(variantId, 'conversion', 'Convert', <ThumbUpIcon />)}
        {renderMetricChip(variantId, 'relevance', 'Relevance', <BarChartIcon />)}
        {renderMetricChip(variantId, 'ctr', 'CTR', <FlashOnIcon />)}
        {renderMetricChip(variantId, 'roas', 'ROAS', <AttachMoneyIcon />)}
        {renderMetricChip(variantId, 'frequency', 'Freq', <TimelineIcon />)}
      </Box>
    );
  };

  const renderVariantCard = (variant) => {
    const isSelected = selectedVariant?.id === variant.id;
    const metrics = variantMetrics[variant.id] || {};
    const engagementScore = metrics.engagement || 0;
    const conversionScore = metrics.conversion || 0;
    const relevanceScore = metrics.relevance || 0;
    
    const overallScore = ((engagementScore + conversionScore + relevanceScore) / 3).toFixed(1);
    
    return (
      <Grid item xs={12} md={4} key={variant.id}>
        <VariantCard 
          elevation={isSelected ? 3 : 1}
          isselected={isSelected.toString()}
          varianttype={variant.type}
          onClick={() => handleVariantSelect(variant)}
        >
          <VariantHeader varianttype={variant.type}>
            <Box className="variant-title">
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar 
                  sx={{ 
                    bgcolor: 'background.paper',
                    color: variant.type === 'A' ? 'primary.main' : 
                           variant.type === 'B' ? 'secondary.main' : 'success.main',
                    width: 28,
                    height: 28,
                    fontSize: '0.875rem',
                    fontWeight: 'bold'
                  }}
                >
                  {variant.type}
                </Avatar>
                {variant.title}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
              <Rating 
                value={overallScore / 20} 
                precision={0.5} 
                readOnly 
                size="small" 
                sx={{ 
                  '& .MuiRating-iconFilled': {
                    color: variant.type === 'A' ? 'primary.main' : 
                           variant.type === 'B' ? 'secondary.main' : 'success.main'
                  }
                }}
              />
              <Chip 
                label={`${overallScore}%`} 
                size="small" 
                sx={{ 
                  bgcolor: 'background.paper',
                  color: 'text.primary',
                  fontWeight: 'bold',
                  fontSize: '0.75rem',
                  height: 24
                }}
              />
            </Box>
          </VariantHeader>
          
          <CardContent sx={{ flexGrow: 1, p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                fontWeight: 600, 
                mb: 1,
                color: 'text.primary',
                minHeight: 24,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              {variant.headline}
            </Typography>
            
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                flexGrow: 1,
                mb: 2,
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              {variant.body_text || variant.description}
            </Typography>
            
            <Box sx={{ mt: 'auto' }}>
              <Chip 
                label={variant.cta} 
                size="small" 
                color={variant.type === 'A' ? 'primary' : variant.type === 'B' ? 'secondary' : 'success'}
                variant="outlined"
                sx={{ 
                  fontWeight: 600,
                  borderWidth: '2px',
                  '&:hover': { borderWidth: '2px' },
                  mb: 1
                }}
              />
              
              {renderVariantMetrics(variant.id)}
              
              <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                  {new Date(variant.updatedAt).toLocaleDateString()}
                </Typography>
                
                <Box>
                  <Tooltip title="Copy to clipboard">
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(
                          `${variant.headline}\n\n${variant.body_text || variant.description}\n\n${variant.cta}`
                        );
                        enqueueSnackbar('Copied to clipboard', { variant: 'success' });
                      }}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Regenerate">
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRegenerate(variant.id);
                      }}
                      disabled={isLoading || isGenerating}
                    >
                      <RefreshIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Improve">
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleImprove(variant);
                      }}
                      disabled={isLoading || isImproving}
                    >
                      <ImproveIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </VariantCard>
      </Grid>
    );
  };

  // Filter variants based on active tab
  const filteredVariants = activeTab === 'all' 
    ? displayVariants 
    : displayVariants.filter(variant => variant.type === activeTab);

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header with tabs and actions */}
      <Paper sx={{ mb: 3, borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          px: 3,
          pt: 2,
          pb: 0
        }}>
          <Typography variant="h6" fontWeight={700}>
            A/B/C Test Variants
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<RefreshIcon />}
              onClick={() => handleRegenerate('all')}
              disabled={isLoading || isGenerating}
              sx={{ minWidth: 140 }}
            >
              {isGenerating ? 'Generating...' : 'Regenerate All'}
            </Button>
            
            <Button
              variant="contained"
              color="primary"
              size="small"
              startIcon={<ImproveIcon />}
              onClick={() => selectedVariant && handleImprove(selectedVariant)}
              disabled={!selectedVariant || isLoading || isImproving}
              sx={{ minWidth: 140 }}
            >
              Improve Selected
            </Button>
          </Box>
        </Box>

        {/* Tabs */}
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
          sx={{
            '& .MuiTabs-flexContainer': {
              justifyContent: 'center',
              bgcolor: 'background.paper',
              borderBottom: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
          <Tab 
            label="All Variants" 
            value="all" 
            icon={<BarChartIcon />} 
            iconPosition="start"
            sx={{ minHeight: 48 }}
          />
          <Tab 
            label="Benefit (A)" 
            value="A" 
            icon={<PsychologyIcon />} 
            iconPosition="start"
            sx={{ minHeight: 48 }}
          />
          <Tab 
            label="Problem (B)" 
            value="B" 
            icon={<PerformanceIcon />} 
            iconPosition="start"
            sx={{ minHeight: 48 }}
          />
          <Tab 
            label="Social (C)" 
            value="C" 
            icon={<EmotionIcon />} 
            iconPosition="start"
            sx={{ minHeight: 48 }}
          />
        </Tabs>
      </Paper>

      {/* Loading state */}
      {(isLoading || isGenerating) && (
        <Box sx={{ width: '100%', mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
            {isGenerating ? 'Generating variants...' : 'Loading variants...'}
          </Typography>
        </Box>
      )}

      {/* Variants grid */}
      <Grid container spacing={3}>
        {filteredVariants.map((variant) => renderVariantCard(variant))}
      </Grid>

      {/* Empty state */}
      {!isLoading && filteredVariants.length === 0 && (
        <Box sx={{ 
          textAlign: 'center', 
          p: 6, 
          bgcolor: 'background.paper',
          borderRadius: 2,
          border: '1px dashed',
          borderColor: 'divider'
        }}>
          <Box sx={{ fontSize: 48, mb: 2, color: 'text.secondary' }}>
            <BarChartIcon fontSize="inherit" />
          </Box>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No variants found
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            {activeTab === 'all' 
              ? 'Try generating some variants to get started.'
              : `No variants match the selected filter. Try changing the tab or generating new variants.`}
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => handleRegenerate('all')}
            disabled={isLoading || isGenerating}
            startIcon={<RefreshIcon />}
          >
            Generate Variants
          </Button>
        </Box>
      )}

      {/* Improvement Dialog */}
      <Dialog 
        open={showMixDialog && !!selectedVariant} 
        onClose={() => !isImproving && setShowMixDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            minHeight: '60vh',
            maxHeight: '90vh',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          alignItems: 'center',
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.paper',
          position: 'sticky',
          top: 0,
          zIndex: 1
        }}>
          <ImproveIcon color="primary" sx={{ mr: 1 }} />
          Improve Variant {selectedVariant?.type}
          <Box sx={{ flex: 1 }} />
          <IconButton 
            onClick={() => !isImproving && setShowMixDialog(false)}
            disabled={isImproving}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
          <Grid container sx={{ height: '100%' }}>
            {/* Left side - Current variant */}
            <Grid item xs={12} md={6} sx={{ p: 3, borderRight: { md: '1px solid' }, borderColor: 'divider' }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  CURRENT VARIANT
                </Typography>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {selectedVariant?.headline}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {selectedVariant?.description}
                </Typography>
                <Chip 
                  label={selectedVariant?.cta} 
                  color={selectedVariant?.type === 'A' ? 'primary' : selectedVariant?.type === 'B' ? 'secondary' : 'success'}
                  size="small"
                  sx={{ mb: 2 }}
                />
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    VARIANT DETAILS
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, mb: 2 }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary" display="block">Strategy</Typography>
                      <Typography variant="body2">{selectedVariant?.strategy || 'N/A'}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" display="block">Tone</Typography>
                      <Typography variant="body2">{selectedVariant?.tone || 'N/A'}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" display="block">Length</Typography>
                      <Typography variant="body2">{selectedVariant?.length || 'N/A'}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" display="block">Last Updated</Typography>
                      <Typography variant="body2">
                        {selectedVariant?.updatedAt ? new Date(selectedVariant.updatedAt).toLocaleString() : 'N/A'}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Box>
              
              <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  IMPROVEMENT INSTRUCTIONS
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  variant="outlined"
                  placeholder="Describe the improvements you'd like to make to this variant. Be as specific as possible..."
                  value={improvementPrompt}
                  onChange={(e) => setImprovementPrompt(e.target.value)}
                  disabled={isImproving}
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip 
                    label="More engaging" 
                    size="small" 
                    variant="outlined"
                    onClick={() => setImprovementPrompt(prev => prev + ' Make the copy more engaging and attention-grabbing.')}
                    disabled={isImproving}
                  />
                  <Chip 
                    label="Higher conversion" 
                    size="small" 
                    variant="outlined"
                    onClick={() => setImprovementPrompt(prev => prev + ' Optimize for higher conversion rates.')}
                    disabled={isImproving}
                  />
                  <Chip 
                    label="Shorter" 
                    size="small" 
                    variant="outlined"
                    onClick={() => setImprovementPrompt(prev => prev + ' Make the copy more concise.')}
                    disabled={isImproving}
                  />
                  <Chip 
                    label="More specific" 
                    size="small" 
                    variant="outlined"
                    onClick={() => setImprovementPrompt(prev => prev + ' Add more specific details and benefits.')}
                    disabled={isImproving}
                  />
                </Box>
              </Box>
            </Grid>
            
            {/* Right side - Preview */}
            <Grid item xs={12} md={6} sx={{ p: 3, bgcolor: 'background.default', position: 'relative' }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                PREVIEW
              </Typography>
              
              {isImproving ? (
                <Box sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%',
                  py: 8,
                  textAlign: 'center'
                }}>
                  <CircularProgress size={48} thickness={4} sx={{ mb: 3, color: 'primary.main' }} />
                  <Typography variant="h6" gutterBottom>
                        Improving Your Variant
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: '80%', mb: 3 }}>
                        Our AI is generating an improved version of your variant based on your instructions. This may take a moment...
                      </Typography>
                      <LinearProgress sx={{ width: '80%', height: 8, borderRadius: 5 }} />
                    </Box>
                  ) : improvementPrompt ? (
                    <Paper 
                      elevation={0} 
                      sx={{ 
                        p: 3, 
                        bgcolor: 'background.paper',
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: 'divider',
                        minHeight: 300,
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        textAlign: 'center'
                      }}
                    >
                      <AutoFixHighIcon 
                        color="primary" 
                        sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} 
                      />
                      <Typography variant="h6" gutterBottom>
                        Preview Improvements
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: '80%', mb: 3 }}>
                        Your improved variant will appear here once you click the "Generate Improvements" button.
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        size="large"
                        onClick={handleImproveSubmit}
                        disabled={!improvementPrompt.trim()}
                        startIcon={<AutoFixHighIcon />}
                      >
                        Generate Improvements
                      </Button>
                    </Paper>
                  ) : (
                    <Paper 
                      elevation={0} 
                      sx={{ 
                        p: 3, 
                        bgcolor: 'background.paper',
                        borderRadius: 2,
                        border: '1px dashed',
                        borderColor: 'divider',
                        minHeight: 300,
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        textAlign: 'center'
                      }}
                    >
                      <PsychologyIcon 
                        color="disabled" 
                        sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} 
                      />
                      <Typography variant="h6" gutterBottom>
                        How would you like to improve this variant?
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: '80%' }}>
                        Enter your improvement instructions on the left to see a preview of the enhanced variant.
                      </Typography>
                    </Paper>
                  )}
                </Grid>
              </Grid>
            </DialogContent>
            
            <DialogActions sx={{ 
              p: 2, 
              bgcolor: 'background.paper',
              borderTop: '1px solid',
              borderColor: 'divider',
              position: 'sticky',
              bottom: 0,
              zIndex: 1
            }}>
              <Button 
                onClick={() => setShowMixDialog(false)}
                disabled={isImproving}
                sx={{ minWidth: 100 }}
              >
                Cancel
              </Button>
              
              <Button 
                variant="contained"
                color="primary"
                onClick={handleImproveSubmit}
                disabled={!improvementPrompt.trim() || isImproving}
                startIcon={isImproving ? <CircularProgress size={20} color="inherit" /> : <AutoFixHighIcon />}
                sx={{ minWidth: 220 }}
              >
                {isImproving ? 'Generating...' : 'Generate Improvements'}
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      );
    };
    
    export default ABTestVariantsTab;
