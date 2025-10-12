import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  Collapse,
  IconButton,
  Tooltip,
  Stack,
  Divider
} from '@mui/material';
import {
  ShoppingBag as EcommerceIcon,
  Business as B2BIcon,
  StoreMallDirectory as LocalIcon,
  Diamond as LuxuryIcon,
  Share as SocialIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as CustomIcon,
  AutoAwesome as PresetIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Preset configurations based on Phase 6 specifications
const PRESETS = {
  'ecommerce-burst': {
    name: 'E-commerce Burst',
    icon: EcommerceIcon,
    description: 'High-energy sales copy that converts browsers to buyers',
    color: '#ff4081',
    settings: {
      creativity: 7,
      urgency: 8,
      emotion: 'excitement',
      filterCliches: true,
      variants: 3,
      tone: 'exciting',
      emojis: 'moderate',
      ctaStyle: 'hard',
      formality: 4
    },
    features: ['High urgency', 'Strong CTA', 'Moderate emojis', 'Exciting tone']
  },
  'b2b-professional': {
    name: 'B2B SaaS Professional',
    icon: B2BIcon,
    description: 'Trust-building copy for business decision-makers',
    color: '#2196f3',
    settings: {
      creativity: 5,
      urgency: 4,
      emotion: 'trust',
      filterCliches: true,
      variants: 4,
      tone: 'professional',
      emojis: 'disabled',
      ctaStyle: 'soft',
      formality: 7,
      compliance: 'standard'
    },
    features: ['Professional tone', 'No emojis', 'Soft CTA', 'High formality']
  },
  'local-friendly': {
    name: 'Local Business Friendly',
    icon: LocalIcon,
    description: 'Community-focused copy that feels personal and approachable',
    color: '#4caf50',
    settings: {
      creativity: 6,
      urgency: 5,
      emotion: 'warmth',
      filterCliches: true,
      variants: 3,
      tone: 'casual',
      emojis: 'moderate',
      ctaStyle: 'medium',
      formality: 3,
      target: 'local'
    },
    features: ['Casual tone', 'Community focus', 'Medium CTA', 'Low formality']
  },
  'luxury-elegant': {
    name: 'Luxury Brand Elegant',
    icon: LuxuryIcon,
    description: 'Sophisticated copy that conveys premium quality and exclusivity',
    color: '#9c27b0',
    settings: {
      creativity: 8,
      urgency: 3,
      emotion: 'aspiration',
      filterCliches: true,
      variants: 4,
      tone: 'luxury',
      emojis: 'disabled',
      ctaStyle: 'soft',
      formality: 9
    },
    features: ['Luxury tone', 'High creativity', 'No emojis', 'Very formal']
  },
  'social-viral': {
    name: 'Social Media Viral',
    icon: SocialIcon,
    description: 'Engaging, shareable content optimized for social platforms',
    color: '#ff9800',
    settings: {
      creativity: 9,
      urgency: 6,
      emotion: 'joy',
      filterCliches: false,
      variants: 5,
      tone: 'playful',
      emojis: 'expressive',
      ctaStyle: 'medium',
      formality: 2,
      platform: 'instagram'
    },
    features: ['Playful tone', 'High creativity', 'Expressive emojis', 'Very casual']
  }
};

const PresetSelector = ({ 
  onPresetSelect, 
  currentPreset, 
  disabled = false,
  showCustomOption = true 
}) => {
  const [expandedPreset, setExpandedPreset] = useState(null);
  const [showAllPresets, setShowAllPresets] = useState(false);

  const handlePresetClick = (presetKey, preset) => {
    if (disabled) return;
    
    onPresetSelect?.(presetKey, preset.settings);
    setExpandedPreset(null);
  };

  const togglePresetDetails = (presetKey) => {
    setExpandedPreset(expandedPreset === presetKey ? null : presetKey);
  };

  const presetKeys = Object.keys(PRESETS);
  const visiblePresets = showAllPresets ? presetKeys : presetKeys.slice(0, 3);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent sx={{ pb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <PresetIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 600, flex: 1 }}>
            Quick Start Presets
          </Typography>
          <Tooltip title="Choose a preset to auto-configure all creative settings">
            <IconButton size="small">
              <ExpandMoreIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Get professional results instantly with industry-optimized configurations
        </Typography>

        <Grid container spacing={2}>
          {visiblePresets.map((presetKey) => {
            const preset = PRESETS[presetKey];
            const IconComponent = preset.icon;
            const isSelected = currentPreset === presetKey;
            const isExpanded = expandedPreset === presetKey;

            return (
              <Grid item xs={12} sm={6} md={4} key={presetKey}>
                <motion.div
                  whileHover={{ scale: disabled ? 1 : 1.02 }}
                  whileTap={{ scale: disabled ? 1 : 0.98 }}
                >
                  <Card
                    sx={{
                      cursor: disabled ? 'default' : 'pointer',
                      border: isSelected ? `2px solid ${preset.color}` : '1px solid',
                      borderColor: isSelected ? preset.color : 'divider',
                      bgcolor: isSelected ? `${preset.color}08` : 'background.paper',
                      transition: 'all 0.2s ease',
                      opacity: disabled ? 0.6 : 1,
                      '&:hover': disabled ? {} : {
                        borderColor: preset.color,
                        boxShadow: `0 4px 20px ${preset.color}20`
                      }
                    }}
                    onClick={() => handlePresetClick(presetKey, preset)}
                  >
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        <IconComponent 
                          sx={{ 
                            mr: 1, 
                            color: preset.color,
                            fontSize: '1.2rem'
                          }} 
                        />
                        <Typography 
                          variant="subtitle2" 
                          sx={{ 
                            fontWeight: 600,
                            color: isSelected ? preset.color : 'text.primary'
                          }}
                        >
                          {preset.name}
                        </Typography>
                      </Box>

                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ mb: 1.5, minHeight: '2.5em' }}
                      >
                        {preset.description}
                      </Typography>

                      <Stack direction="row" spacing={0.5} sx={{ mb: 1.5, flexWrap: 'wrap', gap: 0.5 }}>
                        {preset.features.slice(0, 2).map((feature, index) => (
                          <Chip
                            key={index}
                            label={feature}
                            size="small"
                            variant="outlined"
                            sx={{
                              fontSize: '0.7rem',
                              height: '20px',
                              borderColor: preset.color,
                              color: preset.color
                            }}
                          />
                        ))}
                        {preset.features.length > 2 && (
                          <Chip
                            label={`+${preset.features.length - 2}`}
                            size="small"
                            variant="outlined"
                            sx={{
                              fontSize: '0.7rem',
                              height: '20px',
                              borderColor: 'text.secondary',
                              color: 'text.secondary'
                            }}
                          />
                        )}
                      </Stack>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Button
                          size="small"
                          variant="text"
                          onClick={(e) => {
                            e.stopPropagation();
                            togglePresetDetails(presetKey);
                          }}
                          sx={{ 
                            color: preset.color,
                            minWidth: 'auto',
                            p: 0.5,
                            fontSize: '0.75rem'
                          }}
                        >
                          {isExpanded ? 'Hide' : 'Details'}
                        </Button>
                        
                        {isSelected && (
                          <Chip
                            label="Active"
                            size="small"
                            sx={{
                              bgcolor: preset.color,
                              color: 'white',
                              fontSize: '0.7rem',
                              height: '20px'
                            }}
                          />
                        )}
                      </Box>

                      <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
                          Configuration:
                        </Typography>
                        <Stack spacing={0.5}>
                          {Object.entries(preset.settings).map(([key, value]) => (
                            <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="caption" color="text.secondary">
                                {key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}:
                              </Typography>
                              <Typography variant="caption" sx={{ fontWeight: 500 }}>
                                {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}
                              </Typography>
                            </Box>
                          ))}
                        </Stack>
                      </Collapse>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            );
          })}

          {showCustomOption && (
            <Grid item xs={12} sm={6} md={4}>
              <motion.div
                whileHover={{ scale: disabled ? 1 : 1.02 }}
                whileTap={{ scale: disabled ? 1 : 0.98 }}
              >
                <Card
                  sx={{
                    cursor: disabled ? 'default' : 'pointer',
                    border: currentPreset === 'custom' ? '2px solid' : '1px dashed',
                    borderColor: currentPreset === 'custom' ? 'primary.main' : 'divider',
                    bgcolor: currentPreset === 'custom' ? 'primary.light' : 'transparent',
                    transition: 'all 0.2s ease',
                    opacity: disabled ? 0.6 : 1,
                    '&:hover': disabled ? {} : {
                      borderColor: 'primary.main',
                      bgcolor: 'primary.light'
                    }
                  }}
                  onClick={() => !disabled && onPresetSelect?.('custom', {})}
                >
                  <CardContent sx={{ 
                    p: 2, 
                    '&:last-child': { pb: 2 },
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '140px'
                  }}>
                    <CustomIcon sx={{ fontSize: '2rem', color: 'primary.main', mb: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, textAlign: 'center' }}>
                      Custom Configuration
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                      Configure all settings manually for maximum control
                    </Typography>
                    {currentPreset === 'custom' && (
                      <Chip
                        label="Active"
                        size="small"
                        sx={{
                          bgcolor: 'primary.main',
                          color: 'white',
                          fontSize: '0.7rem',
                          height: '20px',
                          mt: 1
                        }}
                      />
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          )}
        </Grid>

        {!showAllPresets && presetKeys.length > 3 && (
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Button
              variant="text"
              size="small"
              onClick={() => setShowAllPresets(true)}
              disabled={disabled}
              sx={{ textTransform: 'none' }}
            >
              Show All Presets ({presetKeys.length - 3} more)
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default PresetSelector;