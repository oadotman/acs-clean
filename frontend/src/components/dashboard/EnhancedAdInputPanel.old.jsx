import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Paper,
  Typography,
  Tabs,
  Tab,
  Grid,
  Chip,
  Card,
  CardContent,
  CircularProgress,
  alpha,
  useTheme,
  IconButton,
  Tooltip
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  AutoFixHigh,
  Close,
  ContentPaste,
  Edit,
  Info as InfoIcon,
  Lightbulb
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
  
  const platformExamples = {
    facebook: "Flash Sale! 50% off everything today only! Shop now and save big!",
    instagram: "✨ New Collection Drop ✨ Limited quantities available. Link in bio!",
    google: "Get 50% Off Premium Plans | Free Trial | No Credit Card Required",
    linkedin: "Transform Your Business with AI-Powered Solutions. Book a Free Demo Today.",
    twitter: "🔥 MEGA SALE: 48 hours only! Don't miss out on huge savings. Click here →",
    tiktok: "This changed EVERYTHING for me 😱 Get yours now! #ad #viral"
  };
  
  const handleSubmit = () => {
    const text = activeTab === 0 
      ? `${headline}\n\n${adText}\n\nCTA: ${cta}\nTarget: ${targetAudience}`
      : adText;
    
    if (text.trim() && onAnalyze) {
      onAnalyze(text.trim(), platform);
    }
  };
  
  const handleTryExample = () => {
    const example = platformExamples[platform] || platformExamples.facebook;
    setAdText(example);
  };

  const charCount = activeTab === 0 
    ? headline.length + adText.length + cta.length + targetAudience.length
    : adText.length;

  const isFormValid = activeTab === 0 
    ? headline.trim() && adText.trim() && cta.trim()
    : adText.trim();
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, height: 0 }}
      animate={{ opacity: 1, y: 0, height: 'auto' }}
      exit={{ opacity: 0, y: -20, height: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Paper 
        elevation={0}
        sx={{ 
          borderRadius: 3,
          border: `1px solid ${alpha(theme.palette.divider, 0.8)}`,
          backgroundColor: 'background.paper',
          overflow: 'hidden'
        }}
      >
        {/* Header Section */}
        <Box 
          sx={{ 
            px: 3,
            pt: 3,
            pb: 2,
            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.03)} 0%, ${alpha(theme.palette.primary.main, 0.01)} 100%)`,
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.6)}`,
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
                top: 16,
                right: 16,
                color: 'text.secondary'
              }}
            >
              <Close fontSize="small" />
            </IconButton>
          )}

          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1 }}>
            <AutoFixHigh sx={{ color: 'primary.main', fontSize: 28 }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" fontWeight={700} gutterBottom>
                Analyze Your {platform ? platform.charAt(0).toUpperCase() + platform.slice(1) : ''} Ad
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Get AI-powered insights to improve compliance, psychology triggers, and performance
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Tab Navigation */}
        <Box sx={{ px: 3, pt: 2, pb: 0 }}>
          <Paper
            elevation={0}
            sx={{
              p: 0.5,
              backgroundColor: alpha(theme.palette.action.hover, 0.05),
              borderRadius: 2,
              display: 'inline-flex',
              border: `1px solid ${alpha(theme.palette.divider, 0.5)}`
            }}
          >
            <Button
              onClick={() => setActiveTab(0)}
              startIcon={<Edit />}
              sx={{
                px: 2.5,
                py: 1,
                borderRadius: 1.5,
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '0.875rem',
                minWidth: 140,
                backgroundColor: activeTab === 0 ? 'primary.main' : 'transparent',
                color: activeTab === 0 ? 'white' : 'text.secondary',
                '&:hover': {
                  backgroundColor: activeTab === 0 
                    ? 'primary.dark' 
                    : alpha(theme.palette.action.hover, 0.08)
                }
              }}
            >
              Manual Input
            </Button>
            <Button
              onClick={() => setActiveTab(1)}
              startIcon={<ContentPaste />}
              sx={{
                px: 2.5,
                py: 1,
                borderRadius: 1.5,
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '0.875rem',
                minWidth: 140,
                backgroundColor: activeTab === 1 ? 'primary.main' : 'transparent',
                color: activeTab === 1 ? 'white' : 'text.secondary',
                '&:hover': {
                  backgroundColor: activeTab === 1 
                    ? 'primary.dark' 
                    : alpha(theme.palette.action.hover, 0.08)
                }
              }}
            >
              Paste Ad Copy
            </Button>
          </Paper>
        </Box>

        {/* Form Content */}
        <Box sx={{ p: 3 }}>
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
                {/* Card 1: Ad Content */}
                <Card 
                  variant="outlined" 
                  sx={{ 
                    mb: 3,
                    borderColor: alpha(theme.palette.divider, 0.6),
                    borderRadius: 2
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <Typography variant="h6" fontWeight={600}>
                        Ad Content
                      </Typography>
                      <Chip label="Required" size="small" color="primary" variant="outlined" />
                    </Box>

                    {/* Headline */}
                    <Box sx={{ mb: 2.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          Headline
                        </Typography>
                        <Tooltip title="The main attention-grabbing text" arrow>
                          <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                        </Tooltip>
                      </Box>
                      <TextField
                        fullWidth
                        placeholder="Enter your headline..."
                        value={headline}
                        onChange={(e) => setHeadline(e.target.value)}
                        disabled={disabled || isAnalyzing}
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: alpha(theme.palette.background.default, 0.4),
                            '&:hover': {
                              backgroundColor: alpha(theme.palette.background.default, 0.6),
                            },
                            '&.Mui-focused': {
                              backgroundColor: 'background.paper',
                            }
                          }
                        }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                        {headline.length}/120 characters
                      </Typography>
                    </Box>

                    {/* Body Text */}
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          Body Copy
                        </Typography>
                        <Tooltip title="The main message of your ad" arrow>
                          <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                        </Tooltip>
                      </Box>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        placeholder="Enter your ad body copy..."
                        value={adText}
                        onChange={(e) => setAdText(e.target.value)}
                        disabled={disabled || isAnalyzing}
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: alpha(theme.palette.background.default, 0.4),
                            '&:hover': {
                              backgroundColor: alpha(theme.palette.background.default, 0.6),
                            },
                            '&.Mui-focused': {
                              backgroundColor: 'background.paper',
                            }
                          }
                        }}
                      />
                    </Box>
                  </CardContent>
                </Card>

                {/* Card 2: Call-to-Action & Audience */}
                <Card 
                  variant="outlined"
                  sx={{ 
                    mb: 3,
                    borderColor: alpha(theme.palette.divider, 0.6),
                    borderRadius: 2
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                      Context & Targeting
                    </Typography>

                    <Grid container spacing={2}>
                      {/* CTA */}
                      <Grid item xs={12} md={6}>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                            <Typography variant="subtitle2" fontWeight={600}>
                              Call-to-Action
                            </Typography>
                            <Tooltip title="The action you want users to take" arrow>
                              <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                            </Tooltip>
                          </Box>
                          <TextField
                            fullWidth
                            placeholder="e.g., Shop Now, Learn More..."
                            value={cta}
                            onChange={(e) => setCta(e.target.value)}
                            disabled={disabled || isAnalyzing}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                backgroundColor: alpha(theme.palette.background.default, 0.4),
                                '&:hover': {
                                  backgroundColor: alpha(theme.palette.background.default, 0.6),
                                },
                                '&.Mui-focused': {
                                  backgroundColor: 'background.paper',
                                }
                              }
                            }}
                          />
                        </Box>
                      </Grid>

                      {/* Target Audience */}
                      <Grid item xs={12} md={6}>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                            <Typography variant="subtitle2" fontWeight={600}>
                              Target Audience
                            </Typography>
                            <Tooltip title="Who is this ad for?" arrow>
                              <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                            </Tooltip>
                          </Box>
                          <TextField
                            fullWidth
                            placeholder="e.g., Small business owners..."
                            value={targetAudience}
                            onChange={(e) => setTargetAudience(e.target.value)}
                            disabled={disabled || isAnalyzing}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                backgroundColor: alpha(theme.palette.background.default, 0.4),
                                '&:hover': {
                                  backgroundColor: alpha(theme.palette.background.default, 0.6),
                                },
                                '&.Mui-focused': {
                                  backgroundColor: 'background.paper',
                                }
                              }
                            }}
                          />
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
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
                    mb: 3,
                    borderColor: alpha(theme.palette.divider, 0.6),
                    borderRadius: 2
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                      Paste Your Ad Copy
                    </Typography>

                    <TextField
                      fullWidth
                      multiline
                      rows={10}
                      placeholder={`Paste your complete ${platform || ''} ad copy here...`}
                      value={adText}
                      onChange={(e) => setAdText(e.target.value)}
                      disabled={disabled || isAnalyzing}
                      sx={{
                        mb: 2,
                        '& .MuiOutlinedInput-root': {
                          fontSize: '1rem',
                          fontFamily: 'inherit',
                          backgroundColor: alpha(theme.palette.background.default, 0.4),
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.background.default, 0.6),
                          },
                          '&.Mui-focused': {
                            backgroundColor: 'background.paper',
                          }
                        }
                      }}
                    />

                    {/* Character Count */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        {adText.length} characters
                      </Typography>
                      
                      {adText.length === 0 && (
                        <Button
                          size="small"
                          startIcon={<Lightbulb />}
                          onClick={handleTryExample}
                          sx={{ textTransform: 'none', fontWeight: 600 }}
                        >
                          Try Example
                        </Button>
                      )}

                      {adText.length > 0 && (
                        <Button
                          size="small"
                          onClick={() => setAdText('')}
                          sx={{ textTransform: 'none' }}
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

        {/* Sticky CTA Footer */}
        <Box 
          sx={{ 
            px: 3,
            py: 2.5,
            borderTop: `1px solid ${alpha(theme.palette.divider, 0.6)}`,
            backgroundColor: alpha(theme.palette.background.paper, 0.9),
            backdropFilter: 'blur(8px)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                ⚡ Analysis takes ~15 seconds
              </Typography>
            </Box>

            <Button
              variant="contained"
              size="large"
              onClick={handleSubmit}
              disabled={!isFormValid || disabled || isAnalyzing}
              startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <Send />}
              sx={{
                px: 4,
                py: 1.5,
                fontWeight: 700,
                fontSize: '1rem',
                textTransform: 'none',
                borderRadius: 2,
                boxShadow: isFormValid ? 4 : 0,
                background: isFormValid 
                  ? `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`
                  : 'default',
                '&:hover': {
                  boxShadow: 6,
                  transform: 'translateY(-1px)',
                  background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                },
                '&:active': {
                  transform: 'translateY(0)'
                },
                '&:disabled': {
                  background: 'action.disabledBackground'
                }
              }}
            >
              {isAnalyzing ? 'Analyzing Ad...' : 'Analyze My Ad Copy'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </motion.div>
  );
};

export default EnhancedAdInputPanel;