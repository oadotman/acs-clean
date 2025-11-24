import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link as MuiLink,
  InputAdornment,
  IconButton,
  Fade,
  Checkbox,
  FormControlLabel,
  Grow,
  Slide
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Login as LoginIcon
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import AuthCard from '../components/AuthCard';
import '../styles/authFixes.css';

const Login = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true); // Default to true for better UX

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      console.log('ℹ️ User already authenticated, redirecting to new analysis...');
      navigate('/analysis/new', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Load saved email if user was remembered
  useEffect(() => {
    const savedEmail = localStorage.getItem('adcopysurge-saved-email');
    const wasRemembered = localStorage.getItem('adcopysurge-remember-user') === 'true';
    
    if (savedEmail && wasRemembered) {
      setFormData(prev => ({ ...prev, email: savedEmail }));
      setRememberMe(true);
      console.log('💾 Loaded saved email for user');
    }
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('🚀 Submitting login form with rememberMe:', rememberMe);
      
      const result = await login(formData.email.trim(), formData.password, rememberMe);
      
      if (result.success) {
        // Save email for future logins if remember me is checked
        if (rememberMe) {
          localStorage.setItem('adcopysurge-saved-email', formData.email.trim());
          console.log('💾 Email saved for future logins');
        } else {
          localStorage.removeItem('adcopysurge-saved-email');
        }

        // Check if there's a pending team invitation
        const pendingInviteCode = localStorage.getItem('pendingInviteCode');

        if (pendingInviteCode) {
          console.log('🎫 Found pending invitation code, redirecting to join-team page...');
          navigate('/join-team', { replace: true });
        } else {
          console.log('✅ Login successful, navigating to new analysis...');
          navigate('/analysis/new', { replace: true });
        }
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      console.error('💥 Login error:', err);
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard>
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
                  <LoginIcon sx={{ fontSize: '2.5rem' }} />
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
                Welcome Back
              </Typography>
              <Typography variant="body1" sx={{ mb: 1, color: '#4a5568' }}>
                Sign in to your AdCopySurge account
              </Typography>
              <Typography variant="body2" sx={{ color: '#718096' }}>
                Enter your credentials to access your dashboard
              </Typography>
            </Box>

          {/* Demo credentials removed for cleaner UI - still available for testing */}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
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
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock sx={{ color: 'primary.main', opacity: 0.8 }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      size="small"
                      sx={{
                        color: 'primary.main',
                        '&:hover': {
                          backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        },
                      }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
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

            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mt: 2, mb: 3 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    size="small"
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body2" sx={{ color: '#4a5568' }}>
                    Remember me
                  </Typography>
                }
              />
              <MuiLink
                component={Link}
                to="/forgot-password"
                variant="body2"
                color="primary"
                sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
              >
                Forgot password?
              </MuiLink>
            </Box>

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
                  Signing in...
                </Box>
              ) : (
                'Sign In'
              )}
            </Button>
            
            <Box textAlign="center">
              <Typography variant="body2" sx={{ color: '#4a5568' }}>
                Don't have an account?{' '}
                <MuiLink 
                  component={Link} 
                  to="/register" 
                  variant="body2"
                  sx={{ 
                    color: '#667eea',
                    fontWeight: 600,
                    textDecoration: 'none',
                    '&:hover': { textDecoration: 'underline' }
                  }}
                >
                  Sign up here
                </MuiLink>
              </Typography>
            </Box>
          </Box>
    </AuthCard>
  );
};

export default Login;
