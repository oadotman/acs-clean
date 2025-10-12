import React, { useState, useMemo, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import CreativeControls from '../shared/CreativeControls';
import ABCTestVariants from '../shared/ABCTestVariants';
import creativeControlsService from '../../services/creativeControlsService';
import {
  Box,
  Button,
  TextField,
  Paper,
  Typography,
  Grid,
  Chip,
  Card,
  CardContent,
  CircularProgress,
  alpha,
  useTheme,
  IconButton,
  Tooltip,
  LinearProgress,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Close,
  ContentPaste,
  Edit,
  Info as InfoIcon,
  Lightbulb,
  Title as TitleIcon,
  Description as DescriptionIcon,
  TouchApp as TouchAppIcon,
  People as PeopleIcon,
  CheckCircle,
  Error as ErrorIcon,
  EmojiEmotions,
  Psychology,
  Tune,
  Palette,
  GpsFixed as Target,
  Campaign,
  VolumeUp,
  ToggleOn,
  Science
} from '@mui/icons-material';

const EnhancedAdInputPanel = ({ 
  platform,
  onAnalyze, 
  onClose,
  isAnalyzing = false,
  disabled = false 
}) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [adText, setAdText] = useState('');
  const [headline, setHeadline] = useState('');
  const [cta, setCta] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [emojiLevel, setEmojiLevel] = useState('moderate');
  const [humanTone, setHumanTone] = useState('conversational');
  // Phase 2: Brand consistency and quality
  const [brandTone, setBrandTone] = useState('casual');
  const [formalityLevel, setFormalityLevel] = useState(5);
  const [targetAudienceDescription, setTargetAudienceDescription] = useState('');
  const [brandVoiceDescription, setBrandVoiceDescription] = useState('');
  const [includeCTA, setIncludeCTA] = useState(true);
  const [ctaStyle, setCtaStyle] = useState('medium');
  
  // Phase 4 & 5: Creative Controls
  const [creativityLevel, setCreativityLevel] = useState(5);
  const [urgencyLevel, setUrgencyLevel] = useState(5);
  const [emotionType, setEmotionType] = useState('inspiring');
  const [filterCliches, setFilterCliches] = useState(true);
  const [numVariants, setNumVariants] = useState(1);
  const [showCreativeControls, setShowCreativeControls] = useState(false);
  
  // A/B/C Testing state
  const [enableABCTesting, setEnableABCTesting] = useState(true);
  const [abcVariants, setAbcVariants] = useState([]);
  const [isGeneratingABC, setIsGeneratingABC] = useState(false);
  const [showABCResults, setShowABCResults] = useState(false);
  
  // Initialize react-hook-form for CreativeControls
  const { control, watch, setValue } = useForm({
    defaultValues: {
      creativity_level: 5,
      urgency_level: 5,
      emotion_type: 'inspiring',
      filter_cliches: true,
      num_variants: 1
    }
  });
  
  // Platform-specific character limits
  const platformLimits = {
    facebook: 125,
    instagram: 2200,
    linkedin: 3000,
    twitter: 280,
    tiktok: 100,
    google: 90
  };
  
  const currentPlatformLimit = platformLimits[platform] || 125;
  
  // Set platform-specific defaults
  useEffect(() => {
    if (platform === 'tiktok') {
      setEmojiLevel('expressive');
      setHumanTone('deeply_emotional');
      setBrandTone('playful');
      setFormalityLevel(2);
    } else if (platform === 'linkedin') {
      setEmojiLevel('minimal');
      setHumanTone('balanced');
      setBrandTone('professional');
      setFormalityLevel(7);
    } else if (platform === 'instagram') {
      setEmojiLevel('expressive');
      setHumanTone('conversational');
      setBrandTone('casual');
      setFormalityLevel(3);
    } else if (platform === 'google') {
      setEmojiLevel('minimal');
      setHumanTone('balanced');
      setBrandTone('professional');
      setFormalityLevel(6);
    } else {
      // Facebook, Twitter defaults
      setEmojiLevel('moderate');
      setHumanTone('conversational');
      setBrandTone('casual');
      setFormalityLevel(5);
    }
  }, [platform]);
  
  // Field character limits - updated to be platform-aware
  const LIMITS = {
    headline: 120,
    body: Math.min(1000, currentPlatformLimit * 0.8), // 80% of platform limit for safety
    cta: 50,
    audience: 100,
    paste: currentPlatformLimit // Full platform limit for paste mode
  };
  
  const platformExamples = {
    facebook: "Flash Sale! 50% off everything today only! Shop now and save big!",
    instagram: "✨ New Collection Drop ✨ Limited quantities available. Link in bio!",
    google: "Get 50% Off Premium Plans | Free Trial | No Credit Card Required",
    linkedin: "Transform Your Business with AI-Powered Solutions. Book a Free Demo Today.",
    twitter: "🔥 MEGA SALE: 48 hours only! Don't miss out on huge savings. Click here →",
    tiktok: "This changed EVERYTHING for me 😱 Get yours now! #ad #viral"
  };
  
  const handleSubmit = () => {
    console.log('🔄 EnhancedAdInputPanel: handleSubmit called');
    console.log('📝 EnhancedAdInputPanel: activeTab:', activeTab);
    console.log('📝 EnhancedAdInputPanel: headline:', headline);
    console.log('📝 EnhancedAdInputPanel: adText:', adText);
    console.log('📝 EnhancedAdInputPanel: cta:', cta);
    console.log('📝 EnhancedAdInputPanel: targetAudience:', targetAudience);
    console.log('📝 EnhancedAdInputPanel: platform:', platform);
    console.log('📝 EnhancedAdInputPanel: onAnalyze function:', typeof onAnalyze);
    
    const text = activeTab === 0 
      ? `${headline}\n\n${adText}\n\nCTA: ${cta}\nTarget: ${targetAudience}`
      : adText;
    
    console.log('📝 EnhancedAdInputPanel: final text to analyze:', text);
    console.log('📝 EnhancedAdInputPanel: text.trim().length:', text.trim().length);
    console.log('📝 EnhancedAdInputPanel: onAnalyze exists:', !!onAnalyze);
    
    if (text.trim() && onAnalyze) {
      const analysisData = {
        text: text.trim(), 
        platform,
        emoji_level: emojiLevel,
        human_tone: humanTone,
        brand_tone: brandTone,
        formality_level: formalityLevel,
        target_audience_description: targetAudienceDescription,
        brand_voice_description: brandVoiceDescription,
        include_cta: includeCTA,
        cta_style: ctaStyle
      };
      console.log('✅ EnhancedAdInputPanel: Calling onAnalyze with:', analysisData);
      onAnalyze(text.trim(), platform, {
        emoji_level: emojiLevel,
        human_tone: humanTone,
        brand_tone: brandTone,
        formality_level: formalityLevel,
        target_audience_description: targetAudienceDescription,
        brand_voice_description: brandVoiceDescription,
        include_cta: includeCTA,
        cta_style: ctaStyle,
        // Phase 4 & 5: Creative Controls
        creativity_level: watch('creativity_level'),
        urgency_level: watch('urgency_level'),
        emotion_type: watch('emotion_type'),
        filter_cliches: watch('filter_cliches'),
        num_variants: watch('num_variants')
      });
    } else {
      console.log('❌ EnhancedAdInputPanel: NOT calling onAnalyze - conditions not met');
      console.log('❌   text.trim():', text.trim());
      console.log('❌   onAnalyze:', onAnalyze);
    }
  };
  
  const handleTryExample = () => {
    const example = platformExamples[platform] || platformExamples.facebook;
    setAdText(example);
  };

  // A/B/C Testing handlers
  const handleGenerateABCVariants = async () => {
    console.log('🧪 Generating A/B/C test variants...');
    
    const adData = {
      headline: activeTab === 0 ? headline : adText.split('\n')[0] || '',
      body_text: activeTab === 0 ? adText : adText,
      cta: activeTab === 0 ? cta : '',
      platform: platform,
      industry: 'general',
      target_audience: targetAudience
    };
    
    const options = {
      creativity_level: watch('creativity_level'),
      urgency_level: watch('urgency_level'),
      emotion_type: watch('emotion_type'),
      filter_cliches: watch('filter_cliches'),
      brand_voice_description: brandVoiceDescription,
      emoji_level: emojiLevel,
      human_tone: humanTone,
      brand_tone: brandTone,
      formality_level: formalityLevel
    };
    
    setIsGeneratingABC(true);
    
    try {
      const result = await creativeControlsService.generateABCVariants(adData, options);
      if (result.success) {
        setAbcVariants(result.variants || []);
        setShowABCResults(true);
      }
    } catch (error) {
      console.error('Failed to generate A/B/C variants:', error);
    } finally {
      setIsGeneratingABC(false);
    }
  };

  const handleRegenerateABCVariant = async (variantType) => {
    console.log(`🔄 Regenerating variant ${variantType}...`);
    
    const adData = {
      headline: activeTab === 0 ? headline : adText.split('\n')[0] || '',
      body_text: activeTab === 0 ? adText : adText,
      cta: activeTab === 0 ? cta : '',
      platform: platform,
      industry: 'general',
      target_audience: targetAudience
    };
    
    const options = {
      creativity_level: watch('creativity_level'),
      urgency_level: watch('urgency_level'),
      emotion_type: watch('emotion_type'),
      filter_cliches: watch('filter_cliches'),
      brand_voice_description: brandVoiceDescription
    };
    
    try {
      const result = await creativeControlsService.regenerateABCVariant(adData, variantType, options);
      if (result.success) {
        // Update the specific variant in the array
        setAbcVariants(prev => prev.map(v => 
          v.version === variantType ? result.data.variant : v
        ));
      }
    } catch (error) {
      console.error(`Failed to regenerate variant ${variantType}:`, error);
    }
  };

  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      await creativeControlsService.submitFeedback(feedbackData);
      console.log('Feedback submitted:', feedbackData);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  // Validation and Progress Calculation
  const validation = useMemo(() => {
    if (activeTab === 0) {
      return {
        headline: {
          valid: headline.trim().length > 0 && headline.length <= LIMITS.headline,
          message: headline.length > LIMITS.headline ? 'Too long' : headline.length === 0 ? 'Required' : 'Good'
        },
        body: {
          valid: adText.trim().length > 0 && adText.length <= LIMITS.body,
          message: adText.length > LIMITS.body ? 'Too long' : adText.length === 0 ? 'Required' : 'Good'
        },
        cta: {
          valid: cta.trim().length > 0 && cta.length <= LIMITS.cta,
          message: cta.length > LIMITS.cta ? 'Too long' : cta.length === 0 ? 'Required' : 'Good'
        },
        audience: {
          valid: targetAudience.length <= LIMITS.audience,
          message: targetAudience.length > LIMITS.audience ? 'Too long' : 'Optional'
        }
      };
    } else {
      return {
        paste: {
          valid: adText.trim().length > 0 && adText.length <= LIMITS.paste,
          message: adText.length > LIMITS.paste ? 'Too long' : adText.length === 0 ? 'Required' : 'Good'
        }
      };
    }
  }, [activeTab, headline, adText, cta, targetAudience]);

  const progress = useMemo(() => {
    if (activeTab === 0) {
      const fields = [
        { filled: headline.trim().length > 0, required: true },
        { filled: adText.trim().length > 0, required: true },
        { filled: cta.trim().length > 0, required: true },
        { filled: targetAudience.trim().length > 0, required: false }
      ];
      const requiredFields = fields.filter(f => f.required);
      const filledRequired = requiredFields.filter(f => f.filled).length;
      return (filledRequired / requiredFields.length) * 100;
    } else {
      return adText.trim().length > 0 ? 100 : 0;
    }
  }, [activeTab, headline, adText, cta, targetAudience]);

  const isFormValid = activeTab === 0 
    ? validation.headline.valid && validation.body.valid && validation.cta.valid && validation.audience.valid
    : validation.paste.valid;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <Paper 
        elevation={2}
        sx={{ 
          borderRadius: 3,
          border: `1px solid ${theme.palette.divider}`,
          backgroundColor: 'background.paper',
          overflow: 'hidden',
          boxShadow: theme.palette.mode === 'light'
            ? '0 4px 20px rgba(0, 0, 0, 0.08)'
            : '0 10px 40px rgba(124, 58, 237, 0.2)'
        }}
      >
        {/* Compact Header Section */}
        <Box 
          sx={{ 
            px: 3,
            py: 2,
            background: theme.palette.mode === 'light'
              ? `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.primary.main, 0.02)} 100%)`
              : `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.03)} 0%, ${alpha(theme.palette.primary.main, 0.01)} 100%)`,
            borderBottom: `1px solid ${theme.palette.divider}`,
            position: 'relative'
          }}
        >
          {/* Close Button */}
          {onClose && (
            <IconButton
              onClick={onClose}
              size="small"
              sx={{ 
                position: 'absolute',
                top: 12,
                right: 12,
                color: 'text.secondary'
              }}
            >
              <Close fontSize="small" />
            </IconButton>
          )}

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: 'text.primary' }}>
              {platform ? `${platform.charAt(0).toUpperCase() + platform.slice(1)} Ad` : 'Ad'} Analysis
            </Typography>
            <Chip 
              label="AI-Powered" 
              size="small" 
              color="primary" 
              sx={{ height: 20, fontSize: '0.6875rem', fontWeight: 700 }}
            />
          </Box>
        </Box>

        {/* Progress Indicator */}
        {progress > 0 && progress < 100 && (
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 3,
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              '& .MuiLinearProgress-bar': {
                backgroundColor: theme.palette.primary.main
              }
            }}
          />
        )}

        {/* Tab Navigation - Pill Style with High Contrast */}
        <Box sx={{ px: 3, pt: 2.5, pb: 0 }}>
          <Box
            sx={{
              p: 0.5,
              backgroundColor: theme.palette.mode === 'light'
                ? alpha(theme.palette.grey[200], 0.6)
                : alpha(theme.palette.action.hover, 0.08),
              borderRadius: 2,
              display: 'inline-flex',
              border: `1px solid ${theme.palette.divider}`,
              boxShadow: theme.palette.mode === 'light' ? '0 2px 8px rgba(0,0,0,0.04)' : 'none'
            }}
          >
            <Button
              onClick={() => setActiveTab(0)}
              startIcon={<Edit />}
              sx={{
                px: 3,
                py: 1,
                borderRadius: 1.5,
                textTransform: 'none',
                fontWeight: 700,
                fontSize: '0.875rem',
                minWidth: 160,
                backgroundColor: activeTab === 0 ? 'primary.main' : 'transparent',
                color: activeTab === 0 ? '#FFFFFF' : 'text.secondary',
                boxShadow: activeTab === 0 ? 2 : 0,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  backgroundColor: activeTab === 0 
                    ? 'primary.dark' 
                    : alpha(theme.palette.action.hover, 0.12),
                  boxShadow: activeTab === 0 ? 3 : 0
                }
              }}
            >
              Manual Input
            </Button>
            <Button
              onClick={() => setActiveTab(1)}
              startIcon={<ContentPaste />}
              sx={{
                px: 3,
                py: 1,
                borderRadius: 1.5,
                textTransform: 'none',
                fontWeight: 700,
                fontSize: '0.875rem',
                minWidth: 160,
                backgroundColor: activeTab === 1 ? 'primary.main' : 'transparent',
                color: activeTab === 1 ? '#FFFFFF' : 'text.secondary',
                boxShadow: activeTab === 1 ? 2 : 0,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  backgroundColor: activeTab === 1 
                    ? 'primary.dark' 
                    : alpha(theme.palette.action.hover, 0.12),
                  boxShadow: activeTab === 1 ? 3 : 0
                }
              }}
            >
              Paste Ad Copy
            </Button>
          </Box>
        </Box>

        {/* Form Content */}
        <Box sx={{ p: 3, pt: 2.5 }}>
          <AnimatePresence mode="wait">
            {activeTab === 0 ? (
              // Manual Input Form
              <motion.div
                key="manual"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2 }}
              >
                <Grid container spacing={3}>
                  {/* Card 1: Ad Content */}
                  <Grid item xs={12}>
                    <Card 
                      variant="outlined" 
                      sx={{ 
                        borderColor: theme.palette.divider,
                        borderRadius: 2.5,
                        backgroundColor: theme.palette.mode === 'light'
                          ? alpha(theme.palette.grey[50], 0.5)
                          : alpha(theme.palette.background.paper, 0.4),
                        boxShadow: 'none'
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                          <DescriptionIcon color="primary" sx={{ fontSize: 22 }} />
                          <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>
                            Ad Content
                          </Typography>
                          <Chip label="Required" size="small" color="error" variant="outlined" sx={{ height: 20, fontSize: '0.6875rem' }} />
                        </Box>

                        {/* Headline */}
                        <Box sx={{ mb: 3 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                            <TitleIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                            <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                              Headline
                            </Typography>
                            <Tooltip title="The main attention-grabbing text that appears first" arrow placement="top">
                              <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                            </Tooltip>
                          </Box>
                          <TextField
                            fullWidth
                            placeholder="Enter your compelling headline..."
                            value={headline}
                            onChange={(e) => setHeadline(e.target.value)}
                            disabled={disabled || isAnalyzing}
                            error={headline.length > 0 && !validation.headline.valid}
                            InputProps={{
                              endAdornment: (
                                <InputAdornment position="end">
                                  {headline.length > 0 && (
                                    validation.headline.valid ? (
                                      <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                                    ) : (
                                      <ErrorIcon sx={{ color: 'error.main', fontSize: 20 }} />
                                    )
                                  )}
                                </InputAdornment>
                              )
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                fontSize: '1rem',
                                transition: 'all 0.2s ease-in-out',
                                '&:hover': {
                                  backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                },
                                '&.Mui-focused': {
                                  backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                  boxShadow: theme.palette.mode === 'light'
                                    ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
                                    : `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`
                                }
                              }
                            }}
                          />
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.75 }}>
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                color: headline.length > LIMITS.headline ? 'error.main' : 'text.secondary',
                                fontWeight: 500
                              }}
                            >
                              {headline.length}/{LIMITS.headline} characters
                            </Typography>
                            <Typography variant="caption" sx={{ color: validation.headline.valid ? 'success.main' : 'error.main', fontWeight: 600 }}>
                              {validation.headline.message}
                            </Typography>
                          </Box>
                        </Box>

                        {/* Body Text */}
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                            <DescriptionIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                            <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                              Body Copy
                            </Typography>
                            <Tooltip title="The main message that explains your offer or value proposition" arrow placement="top">
                              <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                            </Tooltip>
                          </Box>
                          <TextField
                            fullWidth
                            multiline
                            rows={5}
                            placeholder="Write your ad body copy here... Explain your value proposition clearly."
                            value={adText}
                            onChange={(e) => setAdText(e.target.value)}
                            disabled={disabled || isAnalyzing}
                            error={adText.length > 0 && !validation.body.valid}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                fontSize: '1rem',
                                lineHeight: 1.6,
                                transition: 'all 0.2s ease-in-out',
                                '&:hover': {
                                  backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                },
                                '&.Mui-focused': {
                                  backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                  boxShadow: theme.palette.mode === 'light'
                                    ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
                                    : `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`
                                }
                              }
                            }}
                          />
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.75 }}>
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                color: adText.length > LIMITS.body ? 'error.main' : 'text.secondary',
                                fontWeight: 500
                              }}
                            >
                              {adText.length}/{LIMITS.body} characters
                            </Typography>
                            <Typography variant="caption" sx={{ color: validation.body.valid ? 'success.main' : 'error.main', fontWeight: 600 }}>
                              {validation.body.message}
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Card 2: Call-to-Action & Audience */}
                  <Grid item xs={12}>
                    <Card 
                      variant="outlined"
                      sx={{ 
                        borderColor: theme.palette.divider,
                        borderRadius: 2.5,
                        backgroundColor: theme.palette.mode === 'light'
                          ? alpha(theme.palette.grey[50], 0.5)
                          : alpha(theme.palette.background.paper, 0.4),
                        boxShadow: 'none'
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                          <TouchAppIcon color="primary" sx={{ fontSize: 22 }} />
                          <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>
                            Context & Targeting
                          </Typography>
                        </Box>

                        <Grid container spacing={3}>
                          {/* CTA */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <TouchAppIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Call-to-Action
                                </Typography>
                                <Tooltip title="The action you want users to take (e.g., Shop Now, Learn More)" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <TextField
                                fullWidth
                                placeholder="e.g., Shop Now, Learn More, Get Started..."
                                value={cta}
                                onChange={(e) => setCta(e.target.value)}
                                disabled={disabled || isAnalyzing}
                                error={cta.length > 0 && !validation.cta.valid}
                                InputProps={{
                                  endAdornment: (
                                    <InputAdornment position="end">
                                      {cta.length > 0 && (
                                        validation.cta.valid ? (
                                          <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                                        ) : (
                                          <ErrorIcon sx={{ color: 'error.main', fontSize: 20 }} />
                                        )
                                      )}
                                    </InputAdornment>
                                  )
                                }}
                                sx={{
                                  '& .MuiOutlinedInput-root': {
                                    backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                    },
                                    '&.Mui-focused': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                      boxShadow: theme.palette.mode === 'light'
                                        ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
                                        : `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`
                                    }
                                  }
                                }}
                              />
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.75 }}>
                                <Typography 
                                  variant="caption" 
                                  sx={{ 
                                    color: cta.length > LIMITS.cta ? 'error.main' : 'text.secondary',
                                    fontWeight: 500
                                  }}
                                >
                                  {cta.length}/{LIMITS.cta}
                                </Typography>
                                <Typography variant="caption" sx={{ color: validation.cta.valid ? 'success.main' : 'error.main', fontWeight: 600 }}>
                                  {validation.cta.message}
                                </Typography>
                              </Box>
                            </Box>
                          </Grid>

                          {/* Target Audience */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <PeopleIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Target Audience
                                </Typography>
                                <Chip label="Optional" size="small" variant="outlined" sx={{ height: 18, fontSize: '0.625rem', ml: 0.5 }} />
                                <Tooltip title="Who is this ad targeting? (e.g., Small business owners, Tech professionals)" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <TextField
                                fullWidth
                                placeholder="e.g., Small business owners, age 25-45..."
                                value={targetAudience}
                                onChange={(e) => setTargetAudience(e.target.value)}
                                disabled={disabled || isAnalyzing}
                                error={!validation.audience.valid}
                                sx={{
                                  '& .MuiOutlinedInput-root': {
                                    backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                    },
                                    '&.Mui-focused': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                      boxShadow: theme.palette.mode === 'light'
                                        ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
                                        : `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`
                                    }
                                  }
                                }}
                              />
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.75 }}>
                                <Typography 
                                  variant="caption" 
                                  sx={{ 
                                    color: targetAudience.length > LIMITS.audience ? 'error.main' : 'text.secondary',
                                    fontWeight: 500
                                  }}
                                >
                                  {targetAudience.length}/{LIMITS.audience}
                                </Typography>
                                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                                  {validation.audience.message}
                                </Typography>
                              </Box>
                            </Box>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  {/* Card 3: Generation Controls */}
                  <Grid item xs={12}>
                    <Card 
                      variant="outlined"
                      sx={{ 
                        borderColor: theme.palette.divider,
                        borderRadius: 2.5,
                        backgroundColor: theme.palette.mode === 'light'
                          ? alpha(theme.palette.grey[50], 0.5)
                          : alpha(theme.palette.background.paper, 0.4),
                        boxShadow: 'none'
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                          <Tune color="primary" sx={{ fontSize: 22 }} />
                          <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>
                            Generation Settings
                          </Typography>
                          <Chip label="AI Powered" size="small" color="primary" variant="outlined" sx={{ height: 20, fontSize: '0.6875rem' }} />
                        </Box>

                        <Grid container spacing={3}>
                          {/* Emoji Level Control */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <EmojiEmotions sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Emoji Level
                                </Typography>
                                <Tooltip title="Control how many emojis are used in the generated content" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <Box
                                sx={{
                                  p: 0.5,
                                  backgroundColor: theme.palette.mode === 'light'
                                    ? alpha(theme.palette.grey[200], 0.6)
                                    : alpha(theme.palette.action.hover, 0.08),
                                  borderRadius: 2,
                                  display: 'inline-flex',
                                  border: `1px solid ${theme.palette.divider}`,
                                  width: '100%'
                                }}
                              >
                                <Button
                                  onClick={() => setEmojiLevel('minimal')}
                                  size="small"
                                  sx={{
                                    flex: 1,
                                    py: 1,
                                    borderRadius: 1.5,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    backgroundColor: emojiLevel === 'minimal' ? 'primary.main' : 'transparent',
                                    color: emojiLevel === 'minimal' ? '#FFFFFF' : 'text.secondary',
                                    '&:hover': {
                                      backgroundColor: emojiLevel === 'minimal' 
                                        ? 'primary.dark' 
                                        : alpha(theme.palette.action.hover, 0.12),
                                    }
                                  }}
                                >
                                  Minimal (1-2)
                                </Button>
                                <Button
                                  onClick={() => setEmojiLevel('moderate')}
                                  size="small"
                                  sx={{
                                    flex: 1,
                                    py: 1,
                                    borderRadius: 1.5,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    backgroundColor: emojiLevel === 'moderate' ? 'primary.main' : 'transparent',
                                    color: emojiLevel === 'moderate' ? '#FFFFFF' : 'text.secondary',
                                    '&:hover': {
                                      backgroundColor: emojiLevel === 'moderate' 
                                        ? 'primary.dark' 
                                        : alpha(theme.palette.action.hover, 0.12),
                                    }
                                  }}
                                >
                                  Moderate (3-5)
                                </Button>
                                <Button
                                  onClick={() => setEmojiLevel('expressive')}
                                  size="small"
                                  sx={{
                                    flex: 1,
                                    py: 1,
                                    borderRadius: 1.5,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    backgroundColor: emojiLevel === 'expressive' ? 'primary.main' : 'transparent',
                                    color: emojiLevel === 'expressive' ? '#FFFFFF' : 'text.secondary',
                                    '&:hover': {
                                      backgroundColor: emojiLevel === 'expressive' 
                                        ? 'primary.dark' 
                                        : alpha(theme.palette.action.hover, 0.12),
                                    }
                                  }}
                                >
                                  Expressive
                                </Button>
                              </Box>
                            </Box>
                          </Grid>

                          {/* Human Tone Control */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <Psychology sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Human Feel
                                </Typography>
                                <Tooltip title="Control how natural and conversational the generated content sounds" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <Box
                                sx={{
                                  p: 0.5,
                                  backgroundColor: theme.palette.mode === 'light'
                                    ? alpha(theme.palette.grey[200], 0.6)
                                    : alpha(theme.palette.action.hover, 0.08),
                                  borderRadius: 2,
                                  display: 'inline-flex',
                                  border: `1px solid ${theme.palette.divider}`,
                                  width: '100%'
                                }}
                              >
                                <Button
                                  onClick={() => setHumanTone('balanced')}
                                  size="small"
                                  sx={{
                                    flex: 1,
                                    py: 1,
                                    borderRadius: 1.5,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    backgroundColor: humanTone === 'balanced' ? 'primary.main' : 'transparent',
                                    color: humanTone === 'balanced' ? '#FFFFFF' : 'text.secondary',
                                    '&:hover': {
                                      backgroundColor: humanTone === 'balanced' 
                                        ? 'primary.dark' 
                                        : alpha(theme.palette.action.hover, 0.12),
                                    }
                                  }}
                                >
                                  Balanced
                                </Button>
                                <Button
                                  onClick={() => setHumanTone('conversational')}
                                  size="small"
                                  sx={{
                                    flex: 1,
                                    py: 1,
                                    borderRadius: 1.5,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    backgroundColor: humanTone === 'conversational' ? 'primary.main' : 'transparent',
                                    color: humanTone === 'conversational' ? '#FFFFFF' : 'text.secondary',
                                    '&:hover': {
                                      backgroundColor: humanTone === 'conversational' 
                                        ? 'primary.dark' 
                                        : alpha(theme.palette.action.hover, 0.12),
                                    }
                                  }}
                                >
                                  Friendly
                                </Button>
                                <Button
                                  onClick={() => setHumanTone('deeply_emotional')}
                                  size="small"
                                  sx={{
                                    flex: 1,
                                    py: 1,
                                    borderRadius: 1.5,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    backgroundColor: humanTone === 'deeply_emotional' ? 'primary.main' : 'transparent',
                                    color: humanTone === 'deeply_emotional' ? '#FFFFFF' : 'text.secondary',
                                    '&:hover': {
                                      backgroundColor: humanTone === 'deeply_emotional' 
                                        ? 'primary.dark' 
                                        : alpha(theme.palette.action.hover, 0.12),
                                    }
                                  }}
                                >
                                  Emotional
                                </Button>
                              </Box>
                            </Box>
                          </Grid>
                        </Grid>
                        
                        {/* Platform-specific hints */}
                        {platform === 'tiktok' && (
                          <Box sx={{ mt: 2, p: 2, borderRadius: 2, backgroundColor: alpha(theme.palette.warning.main, 0.1), border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}` }}>
                            <Typography variant="body2" sx={{ color: 'warning.dark', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 1 }}>
                              🎵 TikTok Optimization: Using casual tone with expressive emojis for maximum engagement
                            </Typography>
                          </Box>
                        )}
                        
                        {currentPlatformLimit <= 125 && (
                          <Box sx={{ mt: 2, p: 2, borderRadius: 2, backgroundColor: alpha(theme.palette.info.main, 0.1), border: `1px solid ${alpha(theme.palette.info.main, 0.3)}` }}>
                            <Typography variant="body2" sx={{ color: 'info.dark', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 1 }}>
                              ⚡ {platform?.toUpperCase()} Limit: {currentPlatformLimit} characters max - Keep it concise!
                            </Typography>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  {/* Card 4: Brand & Audience */}
                  <Grid item xs={12}>
                    <Card 
                      variant="outlined"
                      sx={{ 
                        borderColor: theme.palette.divider,
                        borderRadius: 2.5,
                        backgroundColor: theme.palette.mode === 'light'
                          ? alpha(theme.palette.grey[50], 0.5)
                          : alpha(theme.palette.background.paper, 0.4),
                        boxShadow: 'none'
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                          <Palette color="primary" sx={{ fontSize: 22 }} />
                          <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>
                            Brand & Audience
                          </Typography>
                          <Chip label="Phase 2" size="small" color="secondary" variant="outlined" sx={{ height: 20, fontSize: '0.6875rem' }} />
                        </Box>

                        <Grid container spacing={3}>
                          {/* Brand Tone Dropdown */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <VolumeUp sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Brand Tone
                                </Typography>
                                <Tooltip title="Choose the overall personality and approach for your brand" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <FormControl fullWidth size="small">
                                <Select
                                  value={brandTone}
                                  onChange={(e) => setBrandTone(e.target.value)}
                                  disabled={disabled || isAnalyzing}
                                  sx={{
                                    backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                    '&:hover': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                    },
                                    '&.Mui-focused': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                    }
                                  }}
                                >
                                  <MenuItem value="professional">🏢 Professional - B2B, Corporate</MenuItem>
                                  <MenuItem value="casual">😊 Casual - Friendly, Lifestyle</MenuItem>
                                  <MenuItem value="playful">🎉 Playful - Youth, Entertainment</MenuItem>
                                  <MenuItem value="urgent">⚡ Urgent - Sales, Limited Offers</MenuItem>
                                  <MenuItem value="luxury">✨ Luxury - High-end, Aspirational</MenuItem>
                                </Select>
                              </FormControl>
                            </Box>
                          </Grid>

                          {/* Formality Slider */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <Tune sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Formality Level ({formalityLevel}/10)
                                </Typography>
                                <Tooltip title="Control how formal or casual the language should be" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <Box sx={{ px: 1 }}>
                                <Slider
                                  value={formalityLevel}
                                  onChange={(e, value) => setFormalityLevel(value)}
                                  disabled={disabled || isAnalyzing}
                                  min={0}
                                  max={10}
                                  step={1}
                                  marks={
                                    [
                                      { value: 0, label: 'Very Casual' },
                                      { value: 5, label: 'Balanced' },
                                      { value: 10, label: 'Very Formal' }
                                    ]
                                  }
                                  sx={{
                                    '& .MuiSlider-markLabel': {
                                      fontSize: '0.75rem',
                                      color: 'text.secondary'
                                    }
                                  }}
                                />
                              </Box>
                              <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 1 }}>
                                {formalityLevel <= 3 ? 'Like texting a friend' : 
                                 formalityLevel <= 6 ? 'Conversational and approachable' : 
                                 formalityLevel <= 8 ? 'Professional but warm' : 
                                 'Highly formal and corporate'}
                              </Typography>
                            </Box>
                          </Grid>
                          
                          {/* Target Audience Description */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <Target sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Target Audience
                                </Typography>
                                <Tooltip title="Describe your ideal customer in detail" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <TextField
                                fullWidth
                                multiline
                                rows={3}
                                placeholder="e.g., Busy professionals aged 25-40 who value efficiency and quality..."
                                value={targetAudienceDescription}
                                onChange={(e) => setTargetAudienceDescription(e.target.value)}
                                disabled={disabled || isAnalyzing}
                                sx={{
                                  '& .MuiOutlinedInput-root': {
                                    backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                    fontSize: '0.875rem',
                                    '&:hover': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                    },
                                    '&.Mui-focused': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                    }
                                  }
                                }}
                              />
                            </Box>
                          </Grid>

                          {/* Brand Voice Description */}
                          <Grid item xs={12} md={6}>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                                <Campaign sx={{ fontSize: 18, color: 'text.secondary' }} />
                                <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: '0.875rem' }}>
                                  Brand Voice
                                </Typography>
                                <Tooltip title="Describe your brand's personality and how it should sound" arrow placement="top">
                                  <InfoIcon sx={{ fontSize: 16, color: 'action.active', cursor: 'help' }} />
                                </Tooltip>
                              </Box>
                              <TextField
                                fullWidth
                                multiline
                                rows={3}
                                placeholder="e.g., Witty and irreverent, warm and supportive, bold and confident..."
                                value={brandVoiceDescription}
                                onChange={(e) => setBrandVoiceDescription(e.target.value)}
                                disabled={disabled || isAnalyzing}
                                sx={{
                                  '& .MuiOutlinedInput-root': {
                                    backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                    fontSize: '0.875rem',
                                    '&:hover': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                                    },
                                    '&.Mui-focused': {
                                      backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                                    }
                                  }
                                }}
                              />
                            </Box>
                          </Grid>
                          
                          {/* CTA Controls */}
                          <Grid item xs={12}>
                            <Divider sx={{ my: 1 }} />
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={includeCTA}
                                    onChange={(e) => setIncludeCTA(e.target.checked)}
                                    disabled={disabled || isAnalyzing}
                                    color="primary"
                                  />
                                }
                                label="Include Call-to-Action"
                                sx={{ '& .MuiFormControlLabel-label': { fontWeight: 600, fontSize: '0.875rem' } }}
                              />
                              
                              {includeCTA && (
                                <Box sx={{ minWidth: 200 }}>
                                  <FormControl size="small" fullWidth>
                                    <InputLabel>CTA Style</InputLabel>
                                    <Select
                                      value={ctaStyle}
                                      onChange={(e) => setCtaStyle(e.target.value)}
                                      disabled={disabled || isAnalyzing}
                                      label="CTA Style"
                                      sx={{
                                        backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                                      }}
                                    >
                                      <MenuItem value="soft">💬 Soft - Learn More, Discover</MenuItem>
                                      <MenuItem value="medium">🚀 Medium - Get Started, Try Now</MenuItem>
                                      <MenuItem value="hard">⚡ Hard - Buy Now, Don't Miss Out</MenuItem>
                                    </Select>
                                  </FormControl>
                                </Box>
                              )}
                            </Box>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  {/* Card 5: Phase 4 & 5 Creative Controls */}
                  <Grid item xs={12}>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.4 }}
                    >
                      <CreativeControls 
                        control={control}
                        setValue={setValue}
                        platform={platform}
                        onSettingsChange={(name, value) => {
                          setValue(name, value);
                          console.log(`Creative control ${name} changed to:`, value);
                        }}
                        showPreview={false}
                        compact={false}
                      />
                    </motion.div>
                  </Grid>
                </Grid>
              </motion.div>
            ) : (
              // Paste Ad Copy
              <motion.div
                key="paste"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                <Card 
                  variant="outlined"
                  sx={{ 
                    borderColor: theme.palette.divider,
                    borderRadius: 2.5,
                    backgroundColor: theme.palette.mode === 'light'
                      ? alpha(theme.palette.grey[50], 0.5)
                      : alpha(theme.palette.background.paper, 0.4),
                    boxShadow: 'none'
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                      <ContentPaste color="primary" sx={{ fontSize: 22 }} />
                      <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>
                        Paste Your Complete Ad Copy
                      </Typography>
                    </Box>

                    <TextField
                      fullWidth
                      multiline
                      rows={12}
                      placeholder={`Paste your complete ${platform || ''} ad copy here...\n\nInclude headline, body text, and call-to-action.`}
                      value={adText}
                      onChange={(e) => setAdText(e.target.value)}
                      disabled={disabled || isAnalyzing}
                      error={adText.length > 0 && !validation.paste.valid}
                      sx={{
                        mb: 2,
                        '& .MuiOutlinedInput-root': {
                          fontSize: '1rem',
                          fontFamily: 'inherit',
                          lineHeight: 1.6,
                          backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.3),
                          transition: 'all 0.2s ease-in-out',
                          '&:hover': {
                            backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : alpha(theme.palette.background.default, 0.4),
                          },
                          '&.Mui-focused': {
                            backgroundColor: theme.palette.mode === 'light' ? '#FFFFFF' : 'background.paper',
                            boxShadow: theme.palette.mode === 'light'
                              ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
                              : `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`
                          }
                        }
                      }}
                    />

                    {/* Character Count & Actions */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: adText.length > LIMITS.paste ? 'error.main' : 'text.secondary',
                            fontWeight: 500,
                            display: 'block',
                            mb: 0.5
                          }}
                        >
                          {adText.length}/{LIMITS.paste} characters ({platform?.toUpperCase()} limit)
                        </Typography>
                        <Typography variant="caption" sx={{ color: validation.paste?.valid ? 'success.main' : 'error.main', fontWeight: 600 }}>
                          {validation.paste?.message}
                        </Typography>
                      </Box>
                      
                      {adText.length === 0 ? (
                        <Button
                          size="small"
                          startIcon={<Lightbulb />}
                          onClick={handleTryExample}
                          variant="outlined"
                          sx={{ 
                            textTransform: 'none', 
                            fontWeight: 600,
                            borderRadius: 1.5
                          }}
                        >
                          Try Example
                        </Button>
                      ) : (
                        <Button
                          size="small"
                          onClick={() => setAdText('')}
                          variant="outlined"
                          color="error"
                          sx={{ textTransform: 'none', fontWeight: 600, borderRadius: 1.5 }}
                        >
                          Clear
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </Box>

        {/* Sticky CTA Footer with Glassmorphism */}
        <Box 
          sx={{ 
            px: 3,
            py: 2.5,
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.mode === 'light'
              ? alpha(theme.palette.background.paper, 0.95)
              : alpha(theme.palette.background.paper, 0.9),
            backdropFilter: 'blur(12px)',
            boxShadow: theme.palette.mode === 'light'
              ? '0 -4px 20px rgba(0, 0, 0, 0.05)'
              : '0 -4px 20px rgba(0, 0, 0, 0.3)'
          }}
        >
          {/* A/B/C Testing Toggle */}
          <Box sx={{ mb: 2, pb: 2, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.5)}` }}>
            <FormControlLabel
              control={
                <Switch
                  checked={enableABCTesting}
                  onChange={(e) => setEnableABCTesting(e.target.checked)}
                  color="primary"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Science color="primary" sx={{ fontSize: '1.2rem' }} />
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Generate A/B/C Test Variants
                  </Typography>
                  <Tooltip title="Automatically generate 3 strategic variants to test different psychological approaches">
                    <InfoIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
                  </Tooltip>
                </Box>
              }
              sx={{ m: 0 }}
            />
            {enableABCTesting && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, ml: 4 }}>
                Creates 3 variants: Benefit-focused, Problem-focused, and Story-driven approaches
              </Typography>
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2, flexWrap: 'wrap' }}>
            <Box sx={{ flex: 1, minWidth: 200 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 500 }}>
                ⚡ Analysis takes ~15 seconds{enableABCTesting ? ' • A/B/C generation ~30 seconds' : ''}
              </Typography>
              {progress > 0 && progress < 100 && (
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 0.5, fontWeight: 600 }}>
                  {Math.round(progress)}% Complete
                </Typography>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              {enableABCTesting && (
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleGenerateABCVariants}
                  disabled={!isFormValid || disabled || isGeneratingABC}
                  startIcon={isGeneratingABC ? <CircularProgress size={20} color="inherit" /> : <Science />}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontWeight: 600,
                    fontSize: '0.95rem',
                    textTransform: 'none',
                    borderRadius: 2,
                    minWidth: 180,
                    borderColor: 'primary.main',
                    color: 'primary.main',
                    '&:hover': {
                      borderColor: 'primary.dark',
                      backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    }
                  }}
                >
                  {isGeneratingABC ? 'Generating...' : 'Generate A/B/C Tests'}
                </Button>
              )}

              <Button
                variant="contained"
                size="large"
                onClick={enableABCTesting ? handleGenerateABCVariants : handleSubmit}
                disabled={!isFormValid || disabled || isAnalyzing || isGeneratingABC}
                startIcon={isAnalyzing || isGeneratingABC ? <CircularProgress size={20} color="inherit" /> : enableABCTesting ? <Science /> : <Send />}
                sx={{
                  px: 5,
                  py: 1.5,
                  fontWeight: 700,
                  fontSize: '1rem',
                  textTransform: 'none',
                  borderRadius: 2,
                  minWidth: 200,
                  boxShadow: isFormValid ? 4 : 0,
                  background: isFormValid 
                    ? `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`
                    : undefined,
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    boxShadow: isFormValid ? 6 : 0,
                    transform: isFormValid ? 'translateY(-2px)' : 'none',
                    background: isFormValid 
                      ? `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`
                      : undefined,
                  },
                  '&:active': {
                    transform: 'translateY(0)'
                  },
                  '&:disabled': {
                    background: theme.palette.action.disabledBackground,
                    color: theme.palette.action.disabled
                  }
                }}
              >
                {isAnalyzing ? 'Analyzing...' : 
                 isGeneratingABC ? 'Generating Tests...' :
                 enableABCTesting ? 'Generate A/B/C Test Variants' : 'Analyze My Ad Copy'}
              </Button>
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* A/B/C Test Results */}
      <AnimatePresence>
        {showABCResults && abcVariants.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
          >
            <Box sx={{ mt: 3 }}>
              <ABCTestVariants
                variants={abcVariants}
                onGenerate={handleGenerateABCVariants}
                onRegenerateVariant={handleRegenerateABCVariant}
                onSaveVariant={(variant) => console.log('Save variant:', variant)}
                onFeedbackSubmit={handleFeedbackSubmit}
                isGenerating={isGeneratingABC}
                platform={platform}
              />
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default EnhancedAdInputPanel;
