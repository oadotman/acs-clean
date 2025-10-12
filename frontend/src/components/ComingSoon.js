import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  TextField,
  Stack,
  Avatar,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Schedule,
  Email,
  Rocket,
  CheckCircle,
  NotificationsActive
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

const ComingSoon = ({
  title = "Coming Soon",
  subtitle = "We're working hard to bring you something amazing",
  description = "This feature is currently under development. Enter your email to be notified when it's ready!",
  icon = "🚀",
  expectedDate = "Q2 2025",
  showEmailCapture = true,
  showBackButton = true,
  additionalContent = null
}) => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      return;
    }

    setLoading(true);
    
    try {
      // TODO: Replace with actual email capture service
      // Example API call:
      // await apiService.post('/api/v1/email-capture', { 
      //   email: email.trim(),
      //   source: 'coming_soon_' + title.toLowerCase().replace(/\s+/g, '_')
      // });
      
      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Store email locally for development
      console.log('Email captured for coming soon page:', email.trim(), 'Page:', title);
      
      setSubmitted(true);
      setEmail('');
    } catch (error) {
      console.error('Email capture failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          mb: 4,
          textAlign: 'center'
        }}
      >
        <Container maxWidth="md">
          <Avatar
            sx={{
              width: 120,
              height: 120,
              fontSize: '4rem',
              bgcolor: 'rgba(255,255,255,0.1)',
              mx: 'auto',
              mb: 3
            }}
          >
            {icon}
          </Avatar>
          
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              mb: 2,
              fontSize: { xs: '2.5rem', md: '3rem' }
            }}
          >
            {title}
          </Typography>
          
          <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
            {subtitle}
          </Typography>
          
          <Typography 
            variant="body1" 
            sx={{ 
              mb: 4, 
              color: 'rgba(255,255,255,0.8)', 
              maxWidth: 500, 
              mx: 'auto',
              lineHeight: 1.6
            }}
          >
            {description}
          </Typography>
          
          {expectedDate && (
            <Chip
              icon={<Schedule />}
              label={`Expected Release: ${expectedDate}`}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.15)',
                color: 'white',
                fontWeight: 600,
                fontSize: '0.875rem'
              }}
            />
          )}
        </Container>
      </Box>

      <Container maxWidth="md">
        {/* Email Capture */}
        {showEmailCapture && (
          <Box sx={{ mb: 8 }}>
            <Paper
              elevation={8}
              sx={{
                p: 4,
                textAlign: 'center',
                background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
              }}
            >
              {submitted ? (
                <Box>
                  <Avatar
                    sx={{
                      width: 64,
                      height: 64,
                      bgcolor: 'success.light',
                      mx: 'auto',
                      mb: 2
                    }}
                  >
                    <CheckCircle sx={{ fontSize: '2rem' }} color="success" />
                  </Avatar>
                  <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                    🎉 You're on the list!
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    We'll notify you as soon as this feature is ready. 
                    Thanks for your patience!
                  </Typography>
                  <Button
                    variant="outlined"
                    onClick={() => setSubmitted(false)}
                    sx={{ mt: 2 }}
                  >
                    Add Another Email
                  </Button>
                </Box>
              ) : (
                <Box>
                  <Avatar
                    sx={{
                      width: 64,
                      height: 64,
                      bgcolor: 'primary.light',
                      mx: 'auto',
                      mb: 2
                    }}
                  >
                    <NotificationsActive sx={{ fontSize: '2rem' }} />
                  </Avatar>
                  <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                    📧 Get Notified When We Launch
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    Be the first to know when this feature goes live. 
                    Join our exclusive early access list.
                  </Typography>
                  
                  <Box 
                    component="form" 
                    onSubmit={handleEmailSubmit}
                    sx={{ maxWidth: 400, mx: 'auto' }}
                  >
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="stretch">
                      <TextField
                        fullWidth
                        type="email"
                        placeholder="Enter your email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        disabled={loading}
                        InputProps={{
                          startAdornment: <Email sx={{ mr: 1, color: 'text.secondary' }} />
                        }}
                      />
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        disabled={loading || !email.trim()}
                        sx={{
                          minWidth: { sm: 140 },
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {loading ? (
                          <CircularProgress size={20} color="inherit" />
                        ) : (
                          'Notify Me'
                        )}
                      </Button>
                    </Stack>
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                    💌 We'll only email you when this feature launches. No spam, ever.
                  </Typography>
                </Box>
              )}
            </Paper>
          </Box>
        )}

        {/* Additional Content */}
        {additionalContent && (
          <Box sx={{ mb: 8 }}>
            {additionalContent}
          </Box>
        )}

        {/* Help Section */}
        <Box sx={{ mb: 6 }}>
          <Alert 
            severity="info" 
            sx={{ 
              borderRadius: 3,
              '& .MuiAlert-message': {
                width: '100%'
              }
            }}
          >
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Have Questions or Feedback?
                </Typography>
                <Typography variant="body2">
                  We'd love to hear your thoughts on what features you'd like to see.
                </Typography>
              </Box>
              <Button
                component={Link}
                to="/contact"
                variant="outlined"
                size="small"
              >
                Contact Us
              </Button>
            </Stack>
          </Alert>
        </Box>

        {/* Back to Previous Page */}
        {showBackButton && (
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                component={Link}
                to="/"
                variant="contained"
                startIcon={<Rocket />}
              >
                Explore Available Features
              </Button>
              <Button
                onClick={() => window.history.back()}
                variant="outlined"
              >
                Go Back
              </Button>
            </Stack>
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default ComingSoon;
