import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Avatar,
  Stack
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Group as GroupIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import teamService from '../services/teamService';

const InviteAccept = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, loading: authLoading } = useAuth();

  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [error, setError] = useState(null);
  const [accepted, setAccepted] = useState(false);

  // Fetch invitation details on mount
  useEffect(() => {
    if (token) {
      fetchInvitationDetails();
    } else {
      setError('Invalid invitation link');
      setLoading(false);
    }
  }, [token]);

  const fetchInvitationDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      const details = await teamService.getInvitationDetails(token);
      setInvitation(details);

      // If invitation is not valid, show error
      if (!details.is_valid) {
        setError(details.validation_message);
      }
    } catch (err) {
      console.error('Error fetching invitation:', err);
      setError(err.message || 'Failed to load invitation details');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptInvitation = async () => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      const returnUrl = encodeURIComponent(location.pathname);
      navigate(`/login?return=${returnUrl}`);
      return;
    }

    try {
      setAccepting(true);
      setError(null);

      // Accept the invitation
      const result = await teamService.acceptInvitation(token, user.id);

      if (result.success) {
        setAccepted(true);
        
        // Redirect to team dashboard after 2 seconds
        setTimeout(() => {
          navigate('/agency/team');
        }, 2000);
      }
    } catch (err) {
      console.error('Error accepting invitation:', err);
      setError(err.message || 'Failed to accept invitation');
    } finally {
      setAccepting(false);
    }
  };

  // Loading state
  if (authLoading || loading) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
          <CircularProgress size={60} />
          <Typography variant="h6" color="text.secondary">
            Loading invitation...
          </Typography>
        </Box>
      </Container>
    );
  }

  // Error state
  if (error && !invitation) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              Invalid Invitation
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              {error}
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => navigate('/')}
              sx={{ mt: 3 }}
            >
              Go to Home
            </Button>
          </CardContent>
        </Card>
      </Container>
    );
  }

  // Success state (after acceptance)
  if (accepted) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              Welcome to the Team!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              You've successfully joined {invitation?.agency_name}
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

  // Main invitation display
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
              <GroupIcon sx={{ fontSize: 48 }} />
            </Avatar>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              Team Invitation
            </Typography>
            <Typography variant="body1" color="text.secondary">
              You've been invited to join a team on AdCopySurge
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Invitation Details */}
          <Stack spacing={3}>
            {/* Agency Name */}
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                AGENCY
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <GroupIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {invitation?.agency_name}
                </Typography>
              </Box>
            </Box>

            {/* Role */}
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                YOUR ROLE
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {invitation?.role_name}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, ml: 4 }}>
                {invitation?.role_description}
              </Typography>
            </Box>

            {/* Invited By */}
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                INVITED BY
              </Typography>
              <Typography variant="body1" sx={{ ml: 4 }}>
                {invitation?.invited_by_name || invitation?.invited_by_email}
              </Typography>
            </Box>

            {/* Personal Message */}
            {invitation?.message && (
              <Box>
                <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                  MESSAGE
                </Typography>
                <Alert severity="info" icon={<InfoIcon />} sx={{ ml: 0 }}>
                  <Typography variant="body2">
                    "{invitation.message}"
                  </Typography>
                </Alert>
              </Box>
            )}

            {/* Expiration */}
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                EXPIRATION
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 4 }}>
                <ScheduleIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  Expires on {new Date(invitation?.expires_at).toLocaleDateString()} at {new Date(invitation?.expires_at).toLocaleTimeString()}
                </Typography>
              </Box>
            </Box>

            {/* Status Badge */}
            {invitation?.status && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Chip
                  label={invitation.status.toUpperCase()}
                  color={invitation.is_valid ? 'success' : 'default'}
                  size="small"
                />
              </Box>
            )}
          </Stack>

          <Divider sx={{ my: 4 }} />

          {/* Error Message */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {invitation?.is_valid ? (
              <>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={handleAcceptInvitation}
                  disabled={accepting}
                  startIcon={accepting ? <CircularProgress size={20} /> : <CheckCircleIcon />}
                >
                  {accepting ? 'Accepting...' : isAuthenticated ? 'Accept Invitation' : 'Sign In to Accept'}
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
                  disabled={accepting}
                >
                  Decline
                </Button>
              </>
            ) : (
              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={() => navigate('/')}
              >
                Go to Home
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Additional Info */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography variant="body2" color="text.secondary">
          By accepting this invitation, you agree to join {invitation?.agency_name} and
          comply with AdCopySurge's Terms of Service
        </Typography>
      </Box>
    </Container>
  );
};

export default InviteAccept;
