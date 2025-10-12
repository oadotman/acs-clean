import React from 'react';
import {
  Box,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Paper,
  alpha,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';

// Platform Icons - Using emoji for now, can be replaced with custom SVGs
const PlatformIcon = ({ platform, size = 28 }) => {
  const icons = {
    facebook: '👥',
    instagram: '📷',
    google: '🔍',
    linkedin: '💼',
    twitter: '🐦',
    tiktok: '🎵'
  };
  
  return (
    <Box sx={{ fontSize: size, lineHeight: 1 }}>
      {icons[platform] || '📱'}
    </Box>
  );
};

const PlatformButton = ({ platform, selected, onClick, disabled }) => {
  const theme = useTheme();
  
  const platformData = {
    facebook: { name: 'Facebook', color: '#1877f2' },
    instagram: { name: 'Instagram', color: '#e4405f' },
    google: { name: 'Google Ads', color: '#4285f4' },
    linkedin: { name: 'LinkedIn', color: '#0077b5' },
    twitter: { name: 'Twitter', color: '#1da1f2' },
    tiktok: { name: 'TikTok', color: '#000000' }
  };
  
  const data = platformData[platform];
  
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <ToggleButton
        value={platform}
        selected={selected}
        onClick={onClick}
        disabled={disabled}
        sx={{
          border: 'none',
          borderRadius: 3,
          p: 2,
          minWidth: 120,
          height: 80,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          backgroundColor: selected 
            ? alpha(data.color, 0.1) 
            : 'background.paper',
          border: selected 
            ? `2px solid ${data.color}` 
            : `2px solid ${theme.palette.divider}`,
          color: selected ? data.color : 'text.primary',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: alpha(data.color, 0.08),
            borderColor: alpha(data.color, 0.5),
            boxShadow: `0 4px 12px ${alpha(data.color, 0.2)}`,
          },
          '&.Mui-selected': {
            backgroundColor: alpha(data.color, 0.12),
            borderColor: data.color,
            '&:hover': {
              backgroundColor: alpha(data.color, 0.16),
            }
          },
          '&.Mui-disabled': {
            opacity: 0.5,
            '&:hover': {
              transform: 'none'
            }
          }
        }}
      >
        <PlatformIcon platform={platform} size={32} />
        <Typography 
          variant="body2" 
          fontWeight={selected ? 600 : 500}
          sx={{ 
            lineHeight: 1.2,
            textAlign: 'center',
            color: 'inherit'
          }}
        >
          {data.name}
        </Typography>
      </ToggleButton>
    </motion.div>
  );
};

const PlatformSelector = ({ 
  selectedPlatform, 
  onPlatformChange, 
  disabled = false,
  className 
}) => {
  const theme = useTheme();
  
  const platforms = ['facebook', 'instagram', 'google', 'linkedin', 'twitter', 'tiktok'];
  
  const handlePlatformChange = (event, newPlatform) => {
    if (newPlatform && !disabled) {
      onPlatformChange(newPlatform);
    }
  };

  return (
    <Paper 
      elevation={1}
      className={className}
      sx={{ 
        p: 3,
        borderRadius: 3,
        border: `1px solid ${theme.palette.divider}`,
        backgroundColor: 'background.paper'
      }}
    >
      <Box sx={{ mb: 3 }}>
        <Typography 
          variant="h6" 
          fontWeight={700}
          color="text.primary"
          gutterBottom
        >
          Select Platform
        </Typography>
        <Typography 
          variant="body2" 
          color="text.secondary"
        >
          Choose which platform you're creating ads for
        </Typography>
      </Box>
      
      <ToggleButtonGroup
        value={selectedPlatform}
        exclusive
        onChange={handlePlatformChange}
        aria-label="Select advertising platform"
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: 'repeat(2, 1fr)',
            sm: 'repeat(3, 1fr)',
            md: 'repeat(6, 1fr)'
          },
          gap: 2,
          width: '100%',
          '& .MuiToggleButtonGroup-grouped': {
            margin: 0,
            border: 'none',
            '&:not(:first-of-type)': {
              borderRadius: 3,
            },
            '&:first-of-type': {
              borderRadius: 3,
            },
          },
        }}
      >
        {platforms.map((platform, index) => (
          <PlatformButton
            key={platform}
            platform={platform}
            selected={selectedPlatform === platform}
            onClick={(e) => handlePlatformChange(e, platform)}
            disabled={disabled}
          />
        ))}
      </ToggleButtonGroup>
      
      {selectedPlatform && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <Box 
            sx={{ 
              mt: 3, 
              p: 2, 
              borderRadius: 2,
              backgroundColor: alpha(theme.palette.success.main, 0.05),
              border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`
            }}
          >
            <Typography 
              variant="body2" 
              color="success.dark"
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                fontWeight: 500
              }}
            >
              ✓ Platform selected: {selectedPlatform.charAt(0).toUpperCase() + selectedPlatform.slice(1)}
            </Typography>
          </Box>
        </motion.div>
      )}
    </Paper>
  );
};

export default PlatformSelector;