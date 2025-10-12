import React, { useState } from 'react';
import {
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link as MuiLink,
  InputAdornment,
  Grow
} from '@mui/material';
import {
  Email,
  ArrowBack,
  CheckCircle
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { supabase } from '../lib/supabaseClient';
import AuthCard from '../components/AuthCard';
import '../styles/authFixes.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) {
        console.error('❌ Password reset error:', error);
        setError(error.message || 'Failed to send reset email. Please try again.');
      } else {
        console.log('✅ Password reset email sent to:', email);
        setSuccess(true);
      }
    } catch (err) {
      console.error('💥 Unexpected error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard maxWidth={440}>
      {/* Header */}
      <Box textAlign="center" mb={4}>
        <Grow in timeout={1200}>
          <Box 
            sx={{
              mb: 3,
              display: 'inline-flex',
              p: 3,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.05) rotate(5deg)',
                boxShadow: '0 12px 48px rgba(102, 126, 234, 0.6)',
              },
            }}
          >
            <Email sx={{ fontSize: '2.5rem' }} />
          </Box>
        </Grow>
        <Typography 
          component="h1" 
          variant="h4" 
          fontWeight="bold" 
          gutterBottom
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            mb: 1,
          }}
        >
          Reset Password
        </Typography>
        <Typography variant="body1" sx={{ mb: 1, color: '#4a5568' }}>
          Enter your email to receive reset instructions
        </Typography>
        <Typography variant="body2" sx={{ color: '#718096' }}>
          We'll send you a link to create a new password
        </Typography>
      </Box>

      {/* Success Message */}
      {success && (
        <Alert 
          severity="success" 
          icon={<CheckCircle />}
          sx={{ mb: 3 }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
            Check your email! 📧
          </Typography>
          <Typography variant="body2">
            We've sent password reset instructions to <strong>{email}</strong>
          </Typography>
          <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem', color: '#4a5568' }}>
            Didn't receive it? Check your spam folder or try again.
          </Typography>
        </Alert>
      )}

      {/* Error Message */}
      {error && !success && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {!success && (
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email sx={{ color: 'primary.main', opacity: 0.8 }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiInputLabel-root': {
                color: 'rgba(26, 26, 26, 0.7) !important',
                '&.Mui-focused': {
                  color: '#667eea !important',
                },
              },
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                backgroundColor: '#ffffff',
                color: '#1a1a1a !important',
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 4px 20px rgba(102, 126, 234, 0.15)',
                },
                '&:hover fieldset': {
                  borderColor: 'primary.main',
                  borderWidth: '2px',
                },
                '&.Mui-focused': {
                  backgroundColor: 'rgba(255, 255, 255, 1)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 8px 25px rgba(102, 126, 234, 0.2)',
                },
                '& fieldset': {
                  borderWidth: '1px',
                },
              },
            }}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            sx={{ 
              mt: 3,
              mb: 3,
              py: 2,
              borderRadius: 3,
              fontWeight: 600,
              textTransform: 'none',
              fontSize: '1.1rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
              transition: 'all 0.3s ease',
              '&:hover': {
                background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 12px 48px rgba(102, 126, 234, 0.4)',
              },
              '&:active': {
                transform: 'translateY(0)',
              },
              '&:disabled': {
                background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                transform: 'none',
                boxShadow: 'none',
              },
            }}
          >
            {loading ? (
              <Box display="flex" alignItems="center" gap={1}>
                <CircularProgress size={22} color="inherit" />
                Sending...
              </Box>
            ) : (
              'Send Reset Link'
            )}
          </Button>
        </Box>
      )}

      {/* Back to Login */}
      <Box textAlign="center" mt={success ? 3 : 0}>
        <MuiLink 
          component={Link} 
          to="/login" 
          sx={{ 
            color: '#667eea',
            fontWeight: 600,
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 0.5,
            '&:hover': { 
              textDecoration: 'underline' 
            }
          }}
        >
          <ArrowBack sx={{ fontSize: '1rem' }} />
          Back to Login
        </MuiLink>
      </Box>
    </AuthCard>
  );
};

export default ForgotPassword;