import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';

const BrandLogo = ({ 
  variant = 'full', // 'full', 'compact', 'icon'
  size = 'medium', // 'small', 'medium', 'large'
  color = 'primary' // 'primary', 'white', 'dark'
}) => {
  const theme = useTheme();
  
  const getSizes = () => {
    switch (size) {
      case 'small':
        return {
          logoSize: 24,
          fontSize: '1rem',
          spacing: 1
        };
      case 'large':
        return {
          logoSize: 40,
          fontSize: '1.5rem',
          spacing: 2
        };
      default:
        return {
          logoSize: 32,
          fontSize: '1.25rem',
          spacing: 1.5
        };
    }
  };

  const getColors = () => {
    switch (color) {
      case 'white':
        return {
          primary: '#ffffff',
          secondary: 'rgba(255,255,255,0.9)',
          accent: '#f59e0b'
        };
      case 'dark':
        return {
          primary: theme.palette.text.primary,
          secondary: theme.palette.text.secondary,
          accent: theme.palette.warning.main
        };
      default:
        return {
          primary: theme.palette.primary.main,
          secondary: theme.palette.primary.main,
          accent: theme.palette.warning.main
        };
    }
  };

  const { logoSize, fontSize, spacing } = getSizes();
  const colors = getColors();

  const LogoIcon = ({ size }) => (
    <Box
      sx={{
        width: size,
        height: size,
        borderRadius: '12px',
        background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.accent} 100%)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%)',
          borderRadius: '12px',
        }
      }}
    >
      <TrendingUp 
        sx={{ 
          color: 'white', 
          fontSize: size * 0.6,
          zIndex: 1
        }} 
      />
    </Box>
  );

  if (variant === 'icon') {
    return <LogoIcon size={logoSize} />;
  }

  if (variant === 'compact') {
    return (
      <Box display="flex" alignItems="center" gap={spacing}>
        <LogoIcon size={logoSize} />
        <Typography
          variant="h6"
          sx={{
            fontWeight: 800,
            fontSize: fontSize,
            color: colors.primary,
            background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.accent} 100%)`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.01em'
          }}
        >
          ACS
        </Typography>
      </Box>
    );
  }

  return (
    <Box display="flex" alignItems="center" gap={spacing}>
      <LogoIcon size={logoSize} />
      <Box>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 800,
            fontSize: fontSize,
            color: colors.primary,
            lineHeight: 1,
            letterSpacing: '-0.01em',
            background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.accent} 100%)`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          AdCopySurge
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: colors.secondary,
            fontSize: '0.65rem',
            fontWeight: 500,
            letterSpacing: '0.05em',
            textTransform: 'uppercase'
          }}
        >
          Ad Optimizer
        </Typography>
      </Box>
    </Box>
  );
};

export default BrandLogo;
