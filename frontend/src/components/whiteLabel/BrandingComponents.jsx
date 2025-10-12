import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { useWhiteLabel } from '../../contexts/WhiteLabelContext';

// White-label aware logo component
export const BrandLogo = ({ 
  size = 'medium', 
  variant = 'full', 
  sx = {},
  fallbackText = 'AdCopySurge',
  ...props 
}) => {
  const { effectiveBranding } = useWhiteLabel();
  const branding = effectiveBranding;
  const theme = useTheme();

  const sizes = {
    small: { width: 32, height: 32, fontSize: '0.875rem' },
    medium: { width: 40, height: 40, fontSize: '1rem' },
    large: { width: 48, height: 48, fontSize: '1.25rem' },
    xlarge: { width: 64, height: 64, fontSize: '1.5rem' }
  };

  const sizeConfig = sizes[size];

  // If we have a custom logo, show it
  if (branding.logo) {
    return (
      <Box
        component="img"
        src={branding.logo}
        alt={`${branding.companyName} logo`}
        sx={{
          ...sizeConfig,
          objectFit: 'contain',
          ...sx
        }}
        {...props}
      />
    );
  }

  // Fallback to company initial or text
  const initial = branding.companyName?.charAt(0) || 'A';
  
  if (variant === 'icon') {
    return (
      <Box
        sx={{
          ...sizeConfig,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 2,
          bgcolor: branding.primaryColor,
          color: theme.palette.getContrastText(branding.primaryColor),
          fontWeight: 700,
          fontSize: sizeConfig.fontSize,
          ...sx
        }}
        {...props}
      >
        {initial}
      </Box>
    );
  }

  // Full text logo
  return (
    <Typography
      variant="h6"
      sx={{
        fontWeight: 800,
        color: branding.primaryColor,
        fontSize: sizeConfig.fontSize,
        lineHeight: 1,
        ...sx
      }}
      {...props}
    >
      {branding.companyName || fallbackText}
    </Typography>
  );
};

// White-label aware company name component
export const CompanyName = ({ 
  variant = 'body1', 
  fallback = 'AdCopySurge', 
  sx = {},
  ...props 
}) => {
  const { effectiveBranding } = useWhiteLabel();
  const branding = effectiveBranding;

  return (
    <Typography
      variant={variant}
      sx={sx}
      {...props}
    >
      {branding.companyName || fallback}
    </Typography>
  );
};

// White-label aware powered-by footer
export const PoweredByFooter = ({ sx = {}, ...props }) => {
  const { effectiveBranding } = useWhiteLabel();
  const branding = effectiveBranding;
  const theme = useTheme();

  // Don't show if white-label is enabled and "powered by" is removed
  if (!branding.showPoweredBy) {
    return null;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 1,
        borderTop: `1px solid ${theme.palette.divider}`,
        ...sx
      }}
      {...props}
    >
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{
          fontSize: '0.75rem',
          opacity: 0.7
        }}
      >
        Powered by{' '}
        <Typography
          component="span"
          variant="caption"
          sx={{
            color: theme.palette.primary.main,
            fontWeight: 600,
            textDecoration: 'none'
          }}
        >
          AdCopySurge
        </Typography>
      </Typography>
    </Box>
  );
};

// White-label aware color swatch
export const BrandColorSwatch = ({ 
  color, 
  size = 24, 
  variant = 'primary', 
  sx = {},
  ...props 
}) => {
  const { effectiveBranding } = useWhiteLabel();
  const branding = effectiveBranding;

  const colorValue = color || (variant === 'secondary' ? branding.secondaryColor : branding.primaryColor);

  return (
    <Box
      sx={{
        width: size,
        height: size,
        borderRadius: 1,
        bgcolor: colorValue,
        border: 1,
        borderColor: 'divider',
        flexShrink: 0,
        ...sx
      }}
      {...props}
    />
  );
};

// White-label aware support link
export const SupportContact = ({ 
  variant = 'body2', 
  fallbackEmail = 'support@adcopysurge.com',
  sx = {},
  ...props 
}) => {
  const { settings } = useWhiteLabel();
  const supportEmail = settings.customSupportEmail || fallbackEmail;

  return (
    <Typography
      variant={variant}
      component="a"
      href={`mailto:${supportEmail}`}
      sx={{
        color: 'primary.main',
        textDecoration: 'none',
        '&:hover': {
          textDecoration: 'underline'
        },
        ...sx
      }}
      {...props}
    >
      {supportEmail}
    </Typography>
  );
};

// Preview mode indicator
export const PreviewModeIndicator = () => {
  const { settings } = useWhiteLabel();
  const theme = useTheme();

  if (!settings.previewMode) {
    return null;
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        bgcolor: 'warning.main',
        color: 'warning.contrastText',
        py: 0.5,
        textAlign: 'center',
        fontSize: '0.875rem',
        fontWeight: 600,
        boxShadow: theme.shadows[4]
      }}
    >
      🎨 Preview Mode: White-label changes are being previewed
    </Box>
  );
};

// White-label branding card for previews
export const BrandingPreviewCard = ({ sx = {}, ...props }) => {
  const { effectiveBranding } = useWhiteLabel();
  const branding = effectiveBranding;
  const theme = useTheme();

  return (
    <Box
      sx={{
        p: 3,
        border: 1,
        borderColor: 'divider',
        borderRadius: 2,
        bgcolor: 'background.paper',
        ...sx
      }}
      {...props}
    >
      {/* Header with logo and company name */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          mb: 2,
          p: 2,
          borderRadius: 1,
          bgcolor: branding.primaryColor,
          color: theme.palette.getContrastText(branding.primaryColor)
        }}
      >
        <BrandLogo size="medium" variant="icon" />
        <Typography variant="h6" fontWeight={600} color="inherit">
          {branding.companyName}
        </Typography>
      </Box>

      {/* Color palette */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
          Brand Colors
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <BrandColorSwatch variant="primary" size={32} />
          <BrandColorSwatch variant="secondary" size={32} />
        </Box>
      </Box>

      {/* Sample content */}
      <Box>
        <Typography variant="body2" color="text.secondary">
          This is how your white-label branding will appear throughout the platform.
        </Typography>
      </Box>

      {/* Footer */}
      <PoweredByFooter sx={{ mt: 2 }} />
    </Box>
  );
};