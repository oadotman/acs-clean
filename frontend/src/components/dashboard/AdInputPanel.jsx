import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Paper,
  Typography,
  Collapse,
  CircularProgress,
  alpha,
  useTheme
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  AutoFixHigh,
  Close
} from '@mui/icons-material';

const AdInputPanel = ({ 
  platform,
  onAnalyze, 
  onClose,
  isAnalyzing = false,
  disabled = false 
}) => {
  const theme = useTheme();
  const [adText, setAdText] = useState('');
  const [showExamples, setShowExamples] = useState(true);
  
  const platformExamples = {
    facebook: "Flash Sale! 50% off everything today only! Shop now and save big!",
    instagram: "✨ New Collection Drop ✨ Limited quantities available. Link in bio!",
    google: "Get 50% Off Premium Plans | Free Trial | No Credit Card Required",
    linkedin: "Transform Your Business with AI-Powered Solutions. Book a Free Demo Today.",
    twitter: "🔥 MEGA SALE: 48 hours only! Don't miss out on huge savings. Click here →",
    tiktok: "This changed EVERYTHING for me 😱 Get yours now! #ad #viral"
  };
  
  const handleSubmit = () => {
    if (adText.trim() && onAnalyze) {
      onAnalyze(adText.trim(), platform);
    }
  };
  
  const handleTryExample = () => {
    const example = platformExamples[platform] || platformExamples.facebook;
    setAdText(example);
    setShowExamples(false);
  };
  
  const currentExample = platformExamples[platform] || platformExamples.facebook;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, height: 0 }}
      animate={{ opacity: 1, y: 0, height: 'auto' }}
      exit={{ opacity: 0, y: -20, height: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Paper 
        elevation={2}
        sx={{ 
          p: 3,
          borderRadius: 3,
          border: `2px solid ${theme.palette.primary.main}`,
          backgroundColor: 'background.paper',
          position: 'relative'
        }}
      >
        {/* Close Button */}
        {onClose && (
          <Box sx={{ position: 'absolute', top: 12, right: 12 }}>
            <Button
              size="small"
              onClick={onClose}
              startIcon={<Close />}
              sx={{ 
                textTransform: 'none',
                minWidth: 'auto',
                color: 'text.secondary'
              }}
            >
              Close
            </Button>
          </Box>
        )}
        
        {/* Header */}
        <Box sx={{ mb: 3, pr: 8 }}>
          <Typography 
            variant="h6" 
            fontWeight={700}
            color="primary.main"
            gutterBottom
            sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
          >
            <AutoFixHigh />
            Analyze Your {platform ? platform.charAt(0).toUpperCase() + platform.slice(1) : ''} Ad
          </Typography>
          <Typography 
            variant="body2" 
            color="text.secondary"
          >
            Paste your ad copy below and we'll analyze it for compliance, psychology triggers, and optimization opportunities
          </Typography>
        </Box>
        
        {/* Text Input */}
        <TextField
          fullWidth
          multiline
          rows={6}
          placeholder={`Paste your ${platform || ''} ad copy here...`}
          value={adText}
          onChange={(e) => setAdText(e.target.value)}
          disabled={disabled || isAnalyzing}
          sx={{
            mb: 2,
            '& .MuiOutlinedInput-root': {
              fontSize: '1rem',
              fontFamily: 'inherit',
              backgroundColor: alpha(theme.palette.background.default, 0.5),
              '&:hover': {
                backgroundColor: alpha(theme.palette.background.default, 0.7),
              },
              '&.Mui-focused': {
                backgroundColor: 'background.paper',
              }
            }
          }}
        />
        
        {/* Character Count */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            {adText.length} characters
          </Typography>
          
          {adText.length > 0 && (
            <Button
              size="small"
              onClick={() => setAdText('')}
              sx={{ textTransform: 'none', minWidth: 'auto' }}
            >
              Clear
            </Button>
          )}
        </Box>
        
        {/* Example Section */}
        <AnimatePresence>
          {showExamples && adText.length === 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Box 
                sx={{ 
                  mb: 3, 
                  p: 2, 
                  borderRadius: 2,
                  backgroundColor: alpha(theme.palette.info.main, 0.05),
                  border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`
                }}
              >
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>Example for {platform}:</strong>
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    fontStyle: 'italic',
                    color: 'text.secondary',
                    mb: 1
                  }}
                >
                  "{currentExample}"
                </Typography>
                <Button
                  size="small"
                  variant="text"
                  onClick={handleTryExample}
                  sx={{ textTransform: 'none', fontWeight: 600 }}
                >
                  Try this example
                </Button>
              </Box>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handleSubmit}
            disabled={!adText.trim() || disabled || isAnalyzing}
            startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <Send />}
            sx={{
              py: 1.5,
              fontWeight: 700,
              fontSize: '1rem',
              textTransform: 'none',
              boxShadow: 3,
              '&:hover': {
                boxShadow: 6,
                transform: 'translateY(-1px)'
              },
              '&:active': {
                transform: 'translateY(0)'
              }
            }}
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze Now'}
          </Button>
        </Box>
        
        {/* Info Footer */}
        <Box 
          sx={{ 
            mt: 3, 
            pt: 2, 
            borderTop: 1, 
            borderColor: 'divider'
          }}
        >
          <Typography variant="caption" color="text.secondary">
            ⚡ Analysis typically takes 15-20 seconds • Results will appear below
          </Typography>
        </Box>
      </Paper>
    </motion.div>
  );
};

export default AdInputPanel;