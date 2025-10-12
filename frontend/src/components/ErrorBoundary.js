import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Alert,
  Stack
} from '@mui/material';
import {
  ErrorOutline as ErrorIcon,
  Refresh as RefreshIcon,
  Home as HomeIcon
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to your error reporting service
    console.error('Dashboard Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            minHeight: '50vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3
          }}
        >
          <Card sx={{ maxWidth: 600, textAlign: 'center' }}>
            <CardContent sx={{ p: 4 }}>
              <ErrorIcon
                sx={{
                  fontSize: 64,
                  color: 'error.main',
                  mb: 2
                }}
              />
              
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                Something went wrong
              </Typography>
              
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                {this.props.fallbackMessage || 
                 'We encountered an error while loading this part of the dashboard. This is usually temporary.'}
              </Typography>

              {process.env.NODE_ENV === 'development' && this.state.error && (
                <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Error Details (Development Mode):
                  </Typography>
                  <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', overflowX: 'auto' }}>
                    {this.state.error.toString()}
                  </Typography>
                </Alert>
              )}

              <Stack direction="row" spacing={2} justifyContent="center">
                <Button
                  variant="contained"
                  startIcon={<RefreshIcon />}
                  onClick={this.handleRetry}
                >
                  Try Again
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<HomeIcon />}
                  component={RouterLink}
                  to="/dashboard"
                  onClick={() => window.location.reload()}
                >
                  Reload Page
                </Button>
              </Stack>

              <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                If this problem persists, please contact support or try refreshing the page.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for easy wrapping
export const withErrorBoundary = (Component, fallbackMessage) => {
  return function WrappedComponent(props) {
    return (
      <ErrorBoundary fallbackMessage={fallbackMessage}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
};

export default ErrorBoundary;
