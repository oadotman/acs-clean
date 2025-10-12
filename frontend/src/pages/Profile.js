import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Divider,
  Avatar,
  LinearProgress
} from '@mui/material';
import {
  Person,
  Settings,
  Security,
  Notifications,
  CreditCard,
  Logout,
  Edit,
  Upgrade
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../services/authContext';

const Profile = () => {
  const { user, subscription, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getPlanColor = (tier) => {
    switch (tier) {
      case 'growth': return 'primary';
      case 'agency_standard': return 'secondary';
      case 'agency_premium': return 'success';
      case 'agency_unlimited': return 'info';
      // Legacy support
      case 'basic': return 'primary';
      case 'pro': return 'info';
      default: return 'default';
    }
  };

  const getUsagePercentage = () => {
    const limits = {
      free: 5,
      growth: 100,
      agency_standard: 500,
      agency_premium: 1000,
      agency_unlimited: -1, // -1 indicates unlimited
      // Legacy support
      basic: 100,
      pro: -1
    };
    const currentTier = subscription?.subscription_tier || 'free';
    const limit = limits[currentTier];
    const used = subscription?.monthly_analyses || 0;
    
    // Handle unlimited plans
    if (limit === -1) return 0; // Show 0% for unlimited plans
    
    return Math.min((used / limit) * 100, 100);
  };

  // Handle loading state or null subscription
  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h6">Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Person color="primary" sx={{ fontSize: 40 }} />
          Profile & Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your account settings and subscription
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Profile Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Avatar 
              sx={{ 
                width: 80, 
                height: 80, 
                mx: 'auto', 
                mb: 2, 
                bgcolor: 'primary.main', 
                fontSize: '2rem' 
              }}
            >
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
            
            <Typography variant="h6" fontWeight={600} gutterBottom>
              {subscription?.full_name || user?.email?.split('@')[0] || 'User'}
            </Typography>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {user?.email}
            </Typography>
            
            <Box sx={{ mt: 3, mb: 2 }}>
              <Chip 
                label={`${subscription?.subscription_tier?.toUpperCase() || 'FREE'} PLAN`}
                color={getPlanColor(subscription?.subscription_tier)}
                variant="outlined"
                size="medium"
              />
            </Box>
            
            <Typography variant="body2" color="text.secondary">
              Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'recently'}
            </Typography>
          </Paper>
        </Grid>

        {/* Account Details */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {/* Account Information */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Settings color="primary" />
                  Account Information
                </Typography>
                
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Email Address
                    </Typography>
                    <Typography variant="body1" fontWeight={500}>
                      {user?.email}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Full Name
                    </Typography>
                    <Typography variant="body1" fontWeight={500}>
                      {subscription?.full_name || user?.email?.split('@')[0] || 'Not specified'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Company
                    </Typography>
                    <Typography variant="body1" fontWeight={500}>
                      {subscription?.company || 'Not specified'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Account Status
                    </Typography>
                    <Chip 
                      label="Active" 
                      color="success" 
                      size="small"
                    />
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="outlined"
                    startIcon={<Edit />}
                    disabled
                    sx={{ mr: 2 }}
                  >
                    Edit Profile (Coming Soon)
                  </Button>
                </Box>
              </Paper>
            </Grid>

            {/* Subscription & Usage */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CreditCard color="primary" />
                  Subscription & Usage
                </Typography>
                
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Current Plan
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        label={subscription?.subscription_tier?.toUpperCase() || 'FREE'}
                        color={getPlanColor(subscription?.subscription_tier)}
                        size="medium"
                      />
                      {(subscription?.subscription_tier || 'free') === 'free' && (
                        <Button
                          size="small"
                          variant="outlined"
                          color="primary"
                          component={RouterLink}
                          to="/pricing"
                          startIcon={<Upgrade />}
                          sx={{ ml: 1 }}
                        >
                          Upgrade
                        </Button>
                      )}
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Monthly Usage
                    </Typography>
                    <Typography variant="body1" fontWeight={500}>
                      {subscription?.monthly_analyses || 0} / {
                        (() => {
                          const tier = subscription?.subscription_tier || 'free';
                          const limits = {
                            free: 5,
                            growth: 100,
                            agency_standard: 500,
                            agency_premium: 1000,
                            agency_unlimited: 'Unlimited',
                            // Legacy support
                            basic: 100,
                            pro: 'Unlimited'
                          };
                          return limits[tier] || 5;
                        })()
                      } analyses
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={getUsagePercentage()} 
                      sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      color={getUsagePercentage() > 80 ? 'warning' : 'primary'}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                      {(subscription?.subscription_tier || 'free') === 'free' ? (
                        <>
                          You're using the free plan with basic features. 
                          <Button component={RouterLink} to="/pricing" color="primary" sx={{ ml: 1 }}>
                            Upgrade for more analyses and advanced features
                          </Button>
                        </>
                      ) : (
                        `You're subscribed to the ${subscription?.subscription_tier || 'free'} plan. Thank you for supporting AdCopySurge!`
                      )}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Quick Actions */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Quick Actions
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<Security />}
                      disabled
                    >
                      Security Settings (Soon)
                    </Button>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<Notifications />}
                      disabled
                    >
                      Notifications (Soon)
                    </Button>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="outlined"
                      fullWidth
                      component={RouterLink}
                      to="/pricing"
                      startIcon={<CreditCard />}
                    >
                      View Plans
                    </Button>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="outlined"
                      fullWidth
                      color="error"
                      startIcon={<Logout />}
                      onClick={handleLogout}
                    >
                      Sign Out
                    </Button>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile;
