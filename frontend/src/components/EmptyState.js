import React from 'react';
import { Box, Typography, Button, useTheme } from '@mui/material';
import { 
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Add as AddIcon,
  History as HistoryIcon,
  LibraryBooks as LibraryBooksIcon
} from '@mui/icons-material';

const EmptyState = ({ 
  variant = 'analysis', // 'analysis', 'history', 'reports', 'templates', 'generic'
  title,
  description,
  actionText,
  onAction,
  size = 'medium' // 'small', 'medium', 'large'
}) => {
  const theme = useTheme();

  const getVariantConfig = () => {
    switch (variant) {
      case 'analysis':
        return {
          icon: AnalyticsIcon,
          defaultTitle: 'No analysis yet',
          defaultDescription: 'Start by analyzing your first ad to get AI-powered insights and optimization suggestions.',
          defaultActionText: 'Analyze New Ad',
          color: theme.palette.primary.main,
          bgColor: theme.palette.primary.light + '10'
        };
      case 'history':
        return {
          icon: HistoryIcon,
          defaultTitle: 'No analysis history',
          defaultDescription: 'Your completed analyses will appear here. Create your first analysis to start building your history.',
          defaultActionText: 'Create Analysis',
          color: theme.palette.secondary.main,
          bgColor: theme.palette.secondary.light + '10'
        };
      case 'reports':
        return {
          icon: AssessmentIcon,
          defaultTitle: 'No reports available',
          defaultDescription: 'Generate reports and insights once you have completed some ad analyses.',
          defaultActionText: 'View Analytics',
          color: theme.palette.success.main,
          bgColor: theme.palette.success.light + '10'
        };
      case 'templates':
        return {
          icon: LibraryBooksIcon,
          defaultTitle: 'No templates found',
          defaultDescription: 'Browse our template library to find proven ad copy templates for your industry.',
          defaultActionText: 'Browse Templates',
          color: theme.palette.warning.main,
          bgColor: theme.palette.warning.light + '10'
        };
      default:
        return {
          icon: TrendingUpIcon,
          defaultTitle: 'Nothing to see here',
          defaultDescription: 'This area will populate with content once you start using the platform.',
          defaultActionText: 'Get Started',
          color: theme.palette.text.secondary,
          bgColor: theme.palette.grey[100]
        };
    }
  };

  const getSizes = () => {
    switch (size) {
      case 'small':
        return {
          iconSize: 48,
          titleVariant: 'h6',
          descriptionVariant: 'body2',
          spacing: 2,
          maxWidth: 280
        };
      case 'large':
        return {
          iconSize: 96,
          titleVariant: 'h4',
          descriptionVariant: 'body1',
          spacing: 4,
          maxWidth: 480
        };
      default:
        return {
          iconSize: 64,
          titleVariant: 'h5',
          descriptionVariant: 'body1',
          spacing: 3,
          maxWidth: 360
        };
    }
  };

  const config = getVariantConfig();
  const sizes = getSizes();
  const IconComponent = config.icon;

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      textAlign="center"
      sx={{
        py: sizes.spacing * 2,
        px: sizes.spacing,
        maxWidth: sizes.maxWidth,
        mx: 'auto'
      }}
    >
      {/* Illustration Container */}
      <Box
        sx={{
          width: sizes.iconSize + 32,
          height: sizes.iconSize + 32,
          borderRadius: '50%',
          backgroundColor: config.bgColor,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: sizes.spacing,
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            border: `2px dashed ${config.color}40`,
            transform: 'translate(-50%, -50%)',
            animation: 'pulse 2s infinite'
          },
          '@keyframes pulse': {
            '0%': {
              transform: 'translate(-50%, -50%) scale(1)',
              opacity: 1
            },
            '70%': {
              transform: 'translate(-50%, -50%) scale(1.05)',
              opacity: 0.7
            },
            '100%': {
              transform: 'translate(-50%, -50%) scale(1)',
              opacity: 1
            }
          }
        }}
      >
        <IconComponent 
          sx={{ 
            fontSize: sizes.iconSize,
            color: config.color,
            opacity: 0.8
          }} 
        />
      </Box>

      {/* Content */}
      <Typography 
        variant={sizes.titleVariant}
        gutterBottom
        sx={{
          fontWeight: 600,
          color: theme.palette.text.primary,
          mb: 1
        }}
      >
        {title || config.defaultTitle}
      </Typography>

      <Typography 
        variant={sizes.descriptionVariant}
        color="text.secondary"
        sx={{
          mb: sizes.spacing,
          lineHeight: 1.6,
          maxWidth: '100%'
        }}
      >
        {description || config.defaultDescription}
      </Typography>

      {/* Action Button */}
      {onAction && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAction}
          size={size === 'large' ? 'large' : 'medium'}
          sx={{
            mt: 1,
            minWidth: 140,
            background: `linear-gradient(135deg, ${config.color} 0%, ${theme.palette.primary.main} 100%)`,
            '&:hover': {
              background: `linear-gradient(135deg, ${config.color}DD 0%, ${theme.palette.primary.dark} 100%)`,
            }
          }}
        >
          {actionText || config.defaultActionText}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;
