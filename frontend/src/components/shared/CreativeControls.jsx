import React, { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Typography,
  Grid,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
  Chip,
  Tooltip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Stack,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Favorite as FavoriteIcon,
  FilterList as FilterListIcon,
  ContentCopy as ContentCopyIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Controller, useWatch } from 'react-hook-form';
import PresetSelector from './PresetSelector';

const CreativeControls = ({ 
  control, 
  platform = 'facebook',
  onSettingsChange,
  showPreview = true,
  compact = false,
  setValue // Add setValue prop from react-hook-form
}) => {
  const [previewData, setPreviewData] = useState(null);
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [currentPreset, setCurrentPreset] = useState('custom');

  // Creative level descriptions
  const creativityLevels = {
    0: { label: 'Ultra Safe', desc: 'Extremely conservative, proven only', color: '#4caf50' },
    1: { label: 'Very Safe', desc: 'Minimal creative risk', color: '#66bb6a' },
    2: { label: 'Safe', desc: 'Conventional approaches', color: '#81c784' },
    3: { label: 'Mostly Safe', desc: 'Slight variations on proven methods', color: '#aed581' },
    4: { label: 'Balanced Conservative', desc: 'Leaning safe with some creativity', color: '#ffeb3b' },
    5: { label: 'Balanced', desc: 'Perfect balance of safe and creative', color: '#ffc107' },
    6: { label: 'Balanced Creative', desc: 'Leaning creative with some safety', color: '#ff9800' },
    7: { label: 'Creative', desc: 'Bold angles and fresh approaches', color: '#ff5722' },
    8: { label: 'Very Creative', desc: 'Unconventional and attention-grabbing', color: '#f44336' },
    9: { label: 'Bold', desc: 'Risky, standout messaging', color: '#e91e63' },
    10: { label: 'Experimental', desc: 'Maximum creativity, highest risk', color: '#9c27b0' }
  };

  // Urgency level descriptions
  const urgencyLevels = {
    0: { label: 'No Pressure', desc: 'Completely relaxed approach', color: '#4caf50' },
    1: { label: 'Minimal', desc: 'Gentle suggestions only', color: '#66bb6a' },
    2: { label: 'Subtle', desc: 'Light encouragement', color: '#81c784' },
    3: { label: 'Gentle', desc: 'Soft nudging toward action', color: '#aed581' },
    4: { label: 'Moderate Low', desc: 'Some encouragement', color: '#ffeb3b' },
    5: { label: 'Balanced', desc: 'Reasonable time sensitivity', color: '#ffc107' },
    6: { label: 'Moderate High', desc: 'Clear action encouragement', color: '#ff9800' },
    7: { label: 'Urgent', desc: 'Definite time pressure', color: '#ff5722' },
    8: { label: 'High Urgency', desc: 'Strong scarcity messaging', color: '#f44336' },
    9: { label: 'Critical', desc: 'Fear of missing out focus', color: '#e91e63' },
    10: { label: 'Maximum', desc: 'Immediate action required', color: '#9c27b0' }
  };

  // Emotion types
  const emotionTypes = {
    inspiring: { label: 'Inspiring', desc: 'Motivational and uplifting content', icon: '✨' },
    urgent: { label: 'Urgent', desc: 'Time-sensitive, scarcity-driven', icon: '⏰' },
    trust_building: { label: 'Trust Building', desc: 'Credible, reliable, professional', icon: '🤝' },
    aspirational: { label: 'Aspirational', desc: 'Luxury, lifestyle, status', icon: '🌟' },
    problem_solving: { label: 'Problem Solving', desc: 'Pain point focused, solution-oriented', icon: '🔧' },
    excitement: { label: 'Excitement', desc: 'Energetic, enthusiastic, fun', icon: '🎉' },
    fomo: { label: 'FOMO', desc: 'Social proof, popularity', icon: '📈' },
    curiosity: { label: 'Curiosity', desc: 'Intriguing, mysterious, discovery', icon: '🔍' },
    confidence: { label: 'Confidence', desc: 'Empowering, self-assured, bold', icon: '💪' },
    comfort: { label: 'Comfort', desc: 'Safe, familiar, reassuring', icon: '🛡️' }
  };

  // Platform recommendations
  const platformRecommendations = {
    facebook: { creativity: 6, urgency: 5, preferredEmotions: ['trust_building', 'problem_solving', 'excitement'] },
    instagram: { creativity: 7, urgency: 4, preferredEmotions: ['aspirational', 'excitement', 'inspiring'] },
    linkedin: { creativity: 4, urgency: 3, preferredEmotions: ['trust_building', 'confidence', 'problem_solving'] },
    twitter: { creativity: 7, urgency: 6, preferredEmotions: ['excitement', 'curiosity', 'fomo'] },
    tiktok: { creativity: 9, urgency: 3, preferredEmotions: ['excitement', 'inspiring', 'curiosity'] },
    google: { creativity: 5, urgency: 7, preferredEmotions: ['problem_solving', 'trust_building', 'urgent'] }
  };

  // Calculate risk analysis when settings change
  const calculateRiskAnalysis = useCallback((creativity, urgency, emotion) => {
    const platformRec = platformRecommendations[platform];
    
    const creativityRisk = Math.max(0, creativity - platformRec.creativity);
    const urgencyRisk = Math.max(0, urgency - 7); // 7+ is risky urgency
    const emotionRisk = platformRec.preferredEmotions.includes(emotion) ? 0 : 1;
    
    const totalRisk = creativityRisk + urgencyRisk + emotionRisk;
    
    let riskLevel, riskColor, riskMessage;
    if (totalRisk === 0) {
      riskLevel = 'Low';
      riskColor = '#4caf50';
      riskMessage = 'Safe settings for reliable performance';
    } else if (totalRisk <= 2) {
      riskLevel = 'Medium';
      riskColor = '#ff9800';
      riskMessage = 'Moderate risk with potential for higher engagement';
    } else {
      riskLevel = 'High';
      riskColor = '#f44336';
      riskMessage = 'High risk - may not be suitable for all audiences';
    }
    
    return {
      level: riskLevel,
      color: riskColor,
      message: riskMessage,
      score: totalRisk,
      recommendations: getRiskRecommendations(totalRisk, platform)
    };
  }, [platform]);

  const getRiskRecommendations = (riskScore, platform) => {
    const recommendations = [];
    
    if (riskScore === 0) {
      recommendations.push('Consider slightly increasing creativity for better engagement');
      recommendations.push('Test higher creativity levels to find your audience\'s preference');
    } else if (riskScore <= 2) {
      recommendations.push('Good balance of safety and creativity');
      recommendations.push('Monitor performance and adjust based on results');
    } else {
      recommendations.push('High risk settings - test with smaller audiences first');
      recommendations.push('Consider reducing creativity or urgency levels');
      recommendations.push(`These settings may not align well with ${platform} audience expectations`);
    }
    
    return recommendations;
  };

  // Handle settings change and notify parent
  const handleSettingsChange = useCallback((name, value) => {
    if (onSettingsChange) {
      onSettingsChange(name, value);
    }
  }, [onSettingsChange]);

  // Handle preset selection
  const handlePresetSelect = useCallback((presetKey, presetSettings) => {
    setCurrentPreset(presetKey);
    
    if (presetKey !== 'custom' && setValue && presetSettings) {
      // Apply preset settings to form controls
      Object.entries(presetSettings).forEach(([key, value]) => {
        // Map preset settings to form field names
        const fieldMap = {
          creativity: 'creativity_level',
          urgency: 'urgency_level',
          emotion: 'emotion_type',
          filterCliches: 'filter_cliches',
          variants: 'num_variants'
        };
        
        const fieldName = fieldMap[key] || key;
        setValue(fieldName, value);
        
        // Notify parent of each change
        handleSettingsChange(fieldName, value);
      });
    }
  }, [setValue, handleSettingsChange]);

  const CreativeSlider = ({ name, label, icon, levels, control }) => {
    const value = useWatch({ control, name, defaultValue: 5 });
    const levelInfo = levels[value];
    
    useEffect(() => {
      handleSettingsChange(name, value);
    }, [name, value, handleSettingsChange]);
    
    return (
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          {icon}
          <Typography variant="subtitle2" sx={{ ml: 1, fontWeight: 600 }}>
            {label}
          </Typography>
          <Tooltip title={levelInfo.desc}>
            <IconButton size="small" sx={{ ml: 1 }}>
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Controller
          name={name}
          control={control}
          defaultValue={5}
          render={({ field }) => (
            <Slider
              {...field}
              min={0}
              max={10}
              marks
              step={1}
              valueLabelDisplay="auto"
              sx={{
                color: levelInfo.color,
                '& .MuiSlider-thumb': {
                  backgroundColor: levelInfo.color,
                },
                '& .MuiSlider-track': {
                  backgroundColor: levelInfo.color,
                },
                '& .MuiSlider-rail': {
                  opacity: 0.3,
                }
              }}
            />
          )}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
          <Chip 
            label={`${levelInfo.label} (${value}/10)`}
            size="small"
            sx={{ 
              backgroundColor: levelInfo.color + '20',
              color: levelInfo.color,
              fontWeight: 600
            }}
          />
          <Typography variant="caption" color="textSecondary">
            {levelInfo.desc}
          </Typography>
        </Box>
      </Box>
    );
  };

  const RiskAnalysisDisplay = ({ risk }) => (
    <AnimatePresence>
      {risk && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Alert 
            severity={risk.level === 'Low' ? 'success' : risk.level === 'Medium' ? 'warning' : 'error'}
            sx={{ mb: 2 }}
            icon={<WarningIcon />}
          >
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {risk.level} Risk Level - {risk.message}
            </Typography>
            {risk.recommendations.length > 0 && (
              <Box sx={{ mt: 1 }}>
                {risk.recommendations.map((rec, index) => (
                  <Typography key={index} variant="caption" display="block" sx={{ mt: 0.5 }}>
                    • {rec}
                  </Typography>
                ))}
              </Box>
            )}
          </Alert>
        </motion.div>
      )}
    </AnimatePresence>
  );

  const PlatformOptimization = ({ platform }) => {
    const rec = platformRecommendations[platform];
    
    return (
      <Card variant="outlined" sx={{ mb: 2, backgroundColor: 'rgba(25, 118, 210, 0.05)' }}>
        <CardContent sx={{ py: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            📊 {platform.charAt(0).toUpperCase() + platform.slice(1)} Platform Optimization
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Typography variant="caption" color="textSecondary">Recommended Creativity</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>{rec.creativity}/10</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="caption" color="textSecondary">Recommended Urgency</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>{rec.urgency}/10</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="caption" color="textSecondary">Best Emotions</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {rec.preferredEmotions.map(emotion => (
                  <Chip 
                    key={emotion}
                    label={emotionTypes[emotion]?.icon}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  if (compact) {
    return (
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center' }}>
          🎨 Creative Controls
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <CreativeSlider
              name="creativity_level"
              label="Creativity"
              icon={<PsychologyIcon color="primary" />}
              levels={creativityLevels}
              control={control}
            />
          </Grid>
          <Grid item xs={6}>
            <CreativeSlider
              name="urgency_level"
              label="Urgency"
              icon={<SpeedIcon color="secondary" />}
              levels={urgencyLevels}
              control={control}
            />
          </Grid>
        </Grid>
      </Paper>
    );
  }

  return (
    <Paper 
      variant="outlined" 
      sx={{ 
        p: 3, 
        backgroundColor: 'rgba(156, 39, 176, 0.02)',
        border: '1px solid rgba(156, 39, 176, 0.1)'
      }}
    >
      <Typography 
        variant="h6" 
        gutterBottom 
        sx={{ 
          fontWeight: 600,
          color: 'primary.main',
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        🎨 Creative Controls
        <Chip 
          label="Phase 4 & 5"
          size="small"
          color="primary"
          variant="outlined"
          sx={{ ml: 1 }}
        />
      </Typography>
      
      <Typography 
        variant="body2" 
        color="textSecondary" 
        sx={{ mb: 3 }}
      >
        Fine-tune your ad copy's creativity, urgency, and emotional impact for optimal performance.
      </Typography>

      <PresetSelector
        onPresetSelect={handlePresetSelect}
        currentPreset={currentPreset}
        disabled={false}
        showCustomOption={true}
      />

      <PlatformOptimization platform={platform} />
      
      <Grid container spacing={3}>
        {/* Creativity Level */}
        <Grid item xs={12} md={6}>
          <CreativeSlider
            name="creativity_level"
            label="Creativity Level"
            icon={<PsychologyIcon color="primary" />}
            levels={creativityLevels}
            control={control}
          />
        </Grid>

        {/* Urgency Level */}
        <Grid item xs={12} md={6}>
          <CreativeSlider
            name="urgency_level"
            label="Urgency Level"
            icon={<SpeedIcon color="secondary" />}
            levels={urgencyLevels}
            control={control}
          />
        </Grid>

        {/* Emotion Type */}
        <Grid item xs={12} md={6}>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <FavoriteIcon color="error" />
              <Typography variant="subtitle2" sx={{ ml: 1, fontWeight: 600 }}>
                Emotion Type
              </Typography>
            </Box>
            
            <FormControl fullWidth>
              <Controller
                name="emotion_type"
                control={control}
                defaultValue="inspiring"
                render={({ field }) => (
                  <Select {...field} displayEmpty>
                    {Object.entries(emotionTypes).map(([key, emotion]) => (
                      <MenuItem key={key} value={key}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <span>{emotion.icon}</span>
                          <Box>
                            <Typography variant="body2">{emotion.label}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {emotion.desc}
                            </Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                )}
              />
            </FormControl>
          </Box>
        </Grid>

        {/* Additional Controls */}
        <Grid item xs={12} md={6}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
              Additional Controls
            </Typography>
            
            <Stack spacing={2}>
              {/* Cliché Filter Toggle */}
              <Controller
                name="filter_cliches"
                control={control}
                defaultValue={true}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Switch 
                        {...field} 
                        checked={field.value}
                        color="primary"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <FilterListIcon fontSize="small" />
                        <span>Filter Marketing Clichés</span>
                        <Tooltip title="Remove overused marketing phrases like 'game-changer', 'revolutionary', etc.">
                          <InfoIcon fontSize="small" />
                        </Tooltip>
                      </Box>
                    }
                  />
                )}
              />

              {/* Number of Variants */}
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Number of Variants</InputLabel>
                <Controller
                  name="num_variants"
                  control={control}
                  defaultValue={1}
                  render={({ field }) => (
                    <Select {...field} label="Number of Variants">
                      {[1, 2, 3, 4, 5].map(num => (
                        <MenuItem key={num} value={num}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <ContentCopyIcon fontSize="small" />
                            {num} {num === 1 ? 'Variant' : 'Variants'}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  )}
                />
              </FormControl>
            </Stack>
          </Box>
        </Grid>
      </Grid>

      {/* Risk Analysis */}
      {riskAnalysis && <RiskAnalysisDisplay risk={riskAnalysis} />}

      {/* Advanced Settings */}
      <Accordion 
        expanded={showAdvanced} 
        onChange={() => setShowAdvanced(!showAdvanced)}
        sx={{ mt: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            🔧 Advanced Creative Settings
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="body2" color="textSecondary">
                Advanced settings will be available in future updates, including:
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" display="block">• Custom emotion blending</Typography>
                <Typography variant="caption" display="block">• Industry-specific optimizations</Typography>
                <Typography variant="caption" display="block">• A/B testing automation</Typography>
                <Typography variant="caption" display="block">• Performance-based auto-optimization</Typography>
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Real-time Preview */}
      {showPreview && previewData && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Divider sx={{ my: 3 }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
            📋 Real-time Preview
          </Typography>
          <Card variant="outlined" sx={{ p: 2, backgroundColor: 'rgba(0, 0, 0, 0.02)' }}>
            <Typography variant="body2">
              Preview functionality will show how your settings affect the generated copy in real-time.
            </Typography>
          </Card>
        </motion.div>
      )}
    </Paper>
  );
};

export default CreativeControls;