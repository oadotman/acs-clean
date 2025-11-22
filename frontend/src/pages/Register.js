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
  IconButton,
  Grow,
  LinearProgress
} from '@mui/material';
import {
  Person,
  Business,
  Email,
  Lock,
  PersonAdd,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import AuthCard from '../components/AuthCard';
import '../styles/authFixes.css';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    company: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [isExistingUser, setIsExistingUser] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [submitAttempted, setSubmitAttempted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Calculate password strength
    if (name === 'password') {
      calculatePasswordStrength(value);
    }
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 6) strength += 25;
    if (password.length >= 10) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password) || /[^A-Za-z0-9]/.test(password)) strength += 25;
    setPasswordStrength(strength);
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 25) return 'error';
    if (passwordStrength <= 50) return 'warning';
    if (passwordStrength <= 75) return 'info';
    return 'success';
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength <= 25) return 'Weak';
    if (passwordStrength <= 50) return 'Fair';
    if (passwordStrength <= 75) return 'Good';
    return 'Strong';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setIsExistingUser(false);
    setSubmitAttempted(true);

    // Basic validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    if (passwordStrength < 50) {
      setError('Please choose a stronger password (at least 50% strength)');
      return;
    }

    setLoading(true);

    try {
      const result = await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        company: formData.company
      });

      if (result.success) {
        setSuccess(true);

        // Check if there's a pending team invitation
        const pendingInviteCode = localStorage.getItem('pendingInviteCode');

        if (pendingInviteCode) {
          // If there's a pending invitation, redirect to join-team page
          setTimeout(() => {
            navigate('/join-team');
          }, 1500);
        } else {
          // Navigate to new analysis after a brief success message
          setTimeout(() => {
            navigate('/analysis/new');
          }, 2000);
        }
      } else {
        const errorMessage = result.error || 'Registration failed';
        
        // Check for specific error patterns
        if (errorMessage.toLowerCase().includes('already registered') || 
            errorMessage.toLowerCase().includes('already exists') ||
            errorMessage.toLowerCase().includes('user already registered')) {
          setIsExistingUser(true);
          setError('An account with this email already exists.');
        } else if (errorMessage.toLowerCase().includes('email') && 
                   errorMessage.toLowerCase().includes('invalid')) {
          setError('Please enter a valid email address.');
        } else if (errorMessage.toLowerCase().includes('password') && 
                   (errorMessage.toLowerCase().includes('weak') || 
                    errorMessage.toLowerCase().includes('short'))) {
          setError('Password must be at least 6 characters long.');
        } else {
          setError(errorMessage);
        }
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard maxWidth={460}>
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
            <PersonAdd sx={{ fontSize: '2.5rem' }} />
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
          Get Started
        </Typography>
        <Typography variant="body1" sx={{ mb: 1, color: '#4a5568' }}>
          Create your AdCopySurge account
        </Typography>
        <Typography variant="body2" sx={{ color: '#718096' }}>
          Join thousands of marketers optimizing their ad copy
        </Typography>
      </Box>

      {/* Success Message */}
      {success && (
        <Alert 
          severity="success" 
          sx={{ mb: 2, animation: 'fadeIn 0.3s ease-in' }}
          icon={<PersonAdd />}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
            Account created successfully! 🎉
          </Typography>
          <Typography variant="body2">
            Redirecting you to start your first analysis...
          </Typography>
        </Alert>
      )}
      
      {/* Error Message with Contextual Help */}
      {error && !success && (
        <Alert 
          severity={isExistingUser ? 'info' : 'error'} 
          sx={{ mb: 2 }}
          action={
            isExistingUser ? (
              <Button 
                component={Link} 
                to="/login" 
                size="small" 
                variant="contained"
                color="primary"
                sx={{ textTransform: 'none' }}
              >
                Sign In
              </Button>
            ) : null
          }
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: isExistingUser ? 1 : 0 }}>
            {error}
          </Typography>
          {isExistingUser && (
            <Typography variant="body2" color="text.secondary">
              Click "Sign In" to access your existing account instead.
            </Typography>
          )}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="full_name"
          label="Full Name"
          name="full_name"
          autoComplete="name"
          autoFocus
          value={formData.full_name}
          onChange={handleChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Person sx={{ color: 'primary.main', opacity: 0.8 }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
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
          fullWidth
          id="company"
          label="Company (Optional)"
          name="company"
          autoComplete="organization"
          value={formData.company}
          onChange={handleChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Business sx={{ color: 'primary.main', opacity: 0.8 }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
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
          id="email"
          label="Email Address"
          name="email"
          autoComplete="email"
          type="email"
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
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
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
          autoComplete="new-password"
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
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
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
        
        {/* Password Strength Indicator */}
        {formData.password && (
          <Box sx={{ mt: 1, mb: 1 }}>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="caption" color="text.secondary">
                Password strength:
              </Typography>
              <Typography 
                variant="caption" 
                color={getPasswordStrengthColor() + '.main'}
                sx={{ fontWeight: 600 }}
              >
                {getPasswordStrengthText()}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={passwordStrength}
              color={getPasswordStrengthColor()}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
              }}
            />
          </Box>
        )}

        <TextField
          margin="normal"
          required
          fullWidth
          name="confirmPassword"
          label="Confirm Password"
          type={showConfirmPassword ? 'text' : 'password'}
          id="confirmPassword"
          autoComplete="new-password"
          value={formData.confirmPassword}
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
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  edge="end"
                  size="small"
                  sx={{
                    color: 'primary.main',
                    '&:hover': {
                      backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    },
                  }}
                >
                  {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
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
              Creating account...
            </Box>
          ) : (
            'Create Account'
          )}
        </Button>
        
        <Box textAlign="center">
          <Typography variant="body2" color="text.secondary">
            Already have an account?{' '}
            <MuiLink 
              component={Link} 
              to="/login" 
              variant="body2"
              sx={{ 
                color: 'primary.main',
                fontWeight: 600,
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' }
              }}
            >
              Sign in here
            </MuiLink>
          </Typography>
        </Box>
      </Box>
    </AuthCard>
  );
};

export default Register;
