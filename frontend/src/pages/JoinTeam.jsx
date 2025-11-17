import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Avatar,
  Stack,
  Divider,
  InputAdornment
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  GroupAdd as GroupAddIcon,
  Lock as LockIcon,
  ContentPaste as PasteIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import teamService from '../services/teamService';
import toast from 'react-hot-toast';

const JoinTeam = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [inviteCode, setInviteCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [joinedTeam, setJoinedTeam] = useState(null);

  const handleCodeInput = (e) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (value.length <= 6) {
      setInviteCode(value);
      setError(null);
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      const cleanedCode = text.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
      setInviteCode(cleanedCode);
      setError(null);
    } catch (err) {
      toast.error('Unable to paste from clipboard');
    }
  };

  const handleJoinTeam = async () => {
    if (!isAuthenticated) {
      // Save the code to localStorage and redirect to login
      localStorage.setItem('pendingInviteCode', inviteCode);
      const returnUrl = encodeURIComponent('/join-team');
      navigate(`/login?return=${returnUrl}`);
      return;
    }

    if (inviteCode.length !== 6) {
      setError('Please enter a valid 6-character code');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Call backend API to accept invitation by code
      const response = await teamService.acceptInvitationByCode(inviteCode, user.id);

      if (response.success) {
        setSuccess(true);
        setJoinedTeam(response);
        toast.success('Successfully joined the team!');

        // Redirect to team dashboard after 2 seconds
        setTimeout(() => {
          navigate('/agency/team');
        }, 2000);
      }
    } catch (err) {
      console.error('Error joining team:', err);
      setError(err.message || 'Invalid or expired invitation code');
    } finally {
      setLoading(false);
    }
  };

  // Check for pending invite code on mount (after login redirect)
  React.useEffect(() => {
    if (isAuthenticated) {
      const pendingCode = localStorage.getItem('pendingInviteCode');
      if (pendingCode) {
        setInviteCode(pendingCode);
        localStorage.removeItem('pendingInviteCode');
        // Auto-submit if we have a pending code
        setTimeout(() => {
          if (pendingCode.length === 6) {
            handleJoinTeam();
          }
        }, 500);
      }
    }
  }, [isAuthenticated]);

  // Success state
  if (success) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Card elevation={3}>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              Welcome to the Team!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              You've successfully joined {joinedTeam?.agency_name || 'the team'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Redirecting you to the team dashboard...
            </Typography>
            <CircularProgress size={24} sx={{ mt: 3 }} />
          </CardContent>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Card elevation={3}>
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                margin: '0 auto',
                mb: 2
              }}
            >
              <GroupAddIcon sx={{ fontSize: 48 }} />
            </Avatar>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              Join a Team
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Enter your invitation code to join a team
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Code Input Section */}
          <Stack spacing={3}>
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Enter the 6-character invitation code you received:
              </Typography>

              <TextField
                fullWidth
                placeholder="ABC123"
                value={inviteCode}
                onChange={handleCodeInput}
                variant="outlined"
                inputProps={{
                  style: {
                    textAlign: 'center',
                    fontSize: '2rem',
                    fontWeight: 700,
                    letterSpacing: '0.5rem',
                    fontFamily: 'monospace'
                  },
                  maxLength: 6,
                  autoComplete: 'off',
                  autoCorrect: 'off',
                  autoCapitalize: 'off',
                  spellCheck: false
                }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockIcon color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button
                        size="small"
                        onClick={handlePaste}
                        startIcon={<PasteIcon />}
                        sx={{ minWidth: 'auto' }}
                      >
                        Paste
                      </Button>
                    </InputAdornment>
                  )
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'grey.50',
                    '&:hover': {
                      bgcolor: 'grey.100'
                    },
                    '&.Mui-focused': {
                      bgcolor: 'background.paper'
                    }
                  }
                }}
                error={!!error}
                helperText={error}
              />

              {/* Visual indicator of code length */}
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Box sx={{ display: 'inline-flex', gap: 1 }}>
                  {[...Array(6)].map((_, i) => (
                    <Box
                      key={i}
                      sx={{
                        width: 10,
                        height: 10,
                        borderRadius: '50%',
                        bgcolor: inviteCode.length > i ? 'primary.main' : 'grey.300',
                        transition: 'background-color 0.2s'
                      }}
                    />
                  ))}
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {inviteCode.length}/6 characters
                </Typography>
              </Box>
            </Box>

            {/* Info Box */}
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Don't have a code? Ask your team administrator to send you an invitation.
              </Typography>
            </Alert>
          </Stack>

          <Divider sx={{ my: 4 }} />

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handleJoinTeam}
              disabled={loading || inviteCode.length !== 6}
              startIcon={loading ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            >
              {loading ? 'Joining...' : isAuthenticated ? 'Join Team' : 'Sign In to Join'}
            </Button>

            {!isAuthenticated && (
              <Typography variant="body2" color="text.secondary" textAlign="center">
                You'll be redirected to sign in or create an account
              </Typography>
            )}

            <Button
              variant="outlined"
              size="large"
              fullWidth
              onClick={() => navigate('/')}
              disabled={loading}
            >
              Cancel
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Additional Info */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography variant="body2" color="text.secondary">
          By joining a team, you agree to comply with AdCopySurge's Terms of Service
        </Typography>
      </Box>
    </Container>
  );
};

export default JoinTeam;