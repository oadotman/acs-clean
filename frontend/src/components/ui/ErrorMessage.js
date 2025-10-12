import React from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  AlertTitle,
  useTheme,
  Container
} from '@mui/material';
import {
  ErrorOutline as ErrorIcon,
  Refresh as RefreshIcon,
  Home as HomeIcon,
  ContactSupport as SupportIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const ErrorMessage = ({
  variant = 'default', // 'default', 'page', 'inline', 'compact'
  title = 'Something went wrong',
  message = 'Please try again or contact support if the problem persists.',
  error = null, // Error object for development details
  onRetry = null,
  onHome = null,
  onSupport = null,
  showActions = true,
  showDetails = false,
  maxWidth = 'sm',
  sx = {}
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    }
  };

  const handleGoHome = () => {
    if (onHome) {
      onHome();
    } else {
      navigate('/analysis/new');
    }
  };

  const handleContactSupport = () => {
    if (onSupport) {
      onSupport();
    } else {
      // In production, this would open a support modal or redirect to support
      window.open('mailto:support@adcopysurge.com?subject=Error Report', '_blank');
    }
  };

  const getErrorDetails = () => {
    if (!error || !showDetails) return null;
    
    return (
      <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <Typography variant="caption" component="pre" sx={{ fontSize: '0.75rem', overflow: 'auto' }}>
          {error.message || error.toString()}
          {error.stack && process.env.NODE_ENV === 'development' && (
            <>
              {'\n\n'}
              {error.stack}
            </>
          )}
        </Typography>
      </Box>
    );
  };

  const renderInlineError = () => (
    <Alert 
      severity="error" 
      sx={{ 
        borderRadius: 2,
        ...sx 
      }}
      action={showActions && onRetry ? (
        <Button color="inherit" size="small" onClick={handleRetry} startIcon={<RefreshIcon />}>
          Retry
        </Button>
      ) : null}
    >
      <AlertTitle>{title}</AlertTitle>
      {message}
      {getErrorDetails()}
    </Alert>
  );

  const renderCompactError = () => (
    <Box 
      display="flex" 
      alignItems="center" 
      gap={1} 
      sx={{ 
        color: 'error.main',
        p: 1,
        borderRadius: 1,
        bgcolor: 'error.light',
        border: '1px solid',
        borderColor: 'error.main',
        ...sx 
      }}
    >
      <ErrorIcon fontSize="small" />
      <Typography variant="body2" sx={{ flexGrow: 1 }}>
        {message}
      </Typography>
      {showActions && onRetry && (
        <Button
          size="small"
          color="error"
          onClick={handleRetry}
          startIcon={<RefreshIcon />}
          sx={{ minWidth: 'auto', px: 1 }}
        >
          Retry
        </Button>
      )}
    </Box>
  );

  const renderPageError = () => (
    <Container maxWidth={maxWidth} sx={{ py: 8, ...sx }}>
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        textAlign="center"
        sx={{ minHeight: '50vh' }}
      >
        {/* Error Icon */}
        <Box
          sx={{
            width: 120,
            height: 120,
            borderRadius: '50%',
            backgroundColor: 'error.light',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 3,
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              border: `2px dashed ${theme.palette.error.main}40`,
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
          <ErrorIcon sx={{ fontSize: 60, color: 'error.main', opacity: 0.8 }} />
        </Box>

        {/* Error Content */}
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
          {title}
        </Typography>

        <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: 500, lineHeight: 1.6 }}>
          {message}
        </Typography>

        {/* Action Buttons */}
        {showActions && (
          <Box display="flex" gap={2} flexWrap="wrap" justifyContent="center">
            {onRetry && (
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={handleRetry}
                sx={{ minWidth: 140 }}
              >
                Try Again
              </Button>
            )}
            
            <Button
              variant="outlined"
              startIcon={<HomeIcon />}
              onClick={handleGoHome}
              sx={{ minWidth: 140 }}
            >
              Go Home
            </Button>

            <Button
              variant="text"
              startIcon={<SupportIcon />}
              onClick={handleContactSupport}
              sx={{ minWidth: 140 }}
            >
              Contact Support
            </Button>
          </Box>
        )}

        {getErrorDetails()}
      </Box>
    </Container>
  );

  const renderDefaultError = () => (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      textAlign="center"
      sx={{ p: 4, ...sx }}
    >
      <ErrorIcon sx={{ fontSize: 48, color: 'error.main', mb: 2, opacity: 0.8 }} />
      
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'text.primary' }}>
        {title}
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
        {message}
      </Typography>

      {showActions && (
        <Box display="flex" gap={1} flexWrap="wrap" justifyContent="center">
          {onRetry && (
            <Button
              variant="contained"
              size="small"
              startIcon={<RefreshIcon />}
              onClick={handleRetry}
            >
              Retry
            </Button>
          )}
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<HomeIcon />}
            onClick={handleGoHome}
          >
            Go Home
          </Button>
        </Box>
      )}

      {getErrorDetails()}
    </Box>
  );

  switch (variant) {
    case 'page':
      return renderPageError();
    case 'inline':
      return renderInlineError();
    case 'compact':
      return renderCompactError();
    default:
      return renderDefaultError();
  }
};

export default ErrorMessage;
