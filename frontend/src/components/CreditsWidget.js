import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  Button,
  LinearProgress,
  Tooltip,
  alpha,
  useTheme
} from '@mui/material';
import {
  Upgrade as UpgradeIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import paddleService from '../services/paddleService';
import creditsService from '../services/creditsService';
import { getUserCredits } from '../utils/creditSystem';
import { SUBSCRIPTION_TIERS } from '../constants/plans';
import toast from 'react-hot-toast';

const CreditsWidget = ({ collapsed = false }) => {
  const theme = useTheme();
  const { user, subscription } = useAuth();
  const [credits, setCredits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);

  // Fetch credits from service
  useEffect(() => {
    const fetchCredits = async () => {
      try {
        setLoading(true);
        
        // Get credits from new credit system
        const userCreditsData = await getUserCredits(user?.id);
        console.log('CreditsWidget: Fetched credits data:', userCreditsData);
        
        const currentTier = subscription?.tier || userCreditsData.tier || 'free';
        
        // Check if user has unlimited credits
        const planLimits = PLAN_LIMITS[currentTier.toUpperCase()] || PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE];
        const isUnlimited = planLimits.monthlyCredits === -1 || planLimits.adAnalyses === -1 || 
                           userCreditsData.credits === Infinity || 
                           userCreditsData.credits >= 999999;
        
        const formattedCredits = {
          current: isUnlimited ? Infinity : userCreditsData.credits,
          total: isUnlimited ? Infinity : (planLimits.monthlyCredits || planLimits.adAnalyses || 5),
          resetDate: userCreditsData.resetDate ? new Date(userCreditsData.resetDate) : null,
          tier: currentTier,
          isUnlimited
        };
        
        console.log('CreditsWidget: Formatted credits:', formattedCredits);
        setCredits(formattedCredits);
      } catch (error) {
        console.error('Failed to fetch credits:', error);
        // Don't show toast error in development to avoid spam
        if (process.env.NODE_ENV === 'production') {
          toast.error('Failed to load credits');
        }
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchCredits();
      // Refresh credits every minute to show updates
      const interval = setInterval(fetchCredits, 60000);
      return () => clearInterval(interval);
    }
  }, [user, subscription?.tier]);

  const handleUpgrade = async () => {
    if (!user) {
      toast.error('Please log in to upgrade your plan');
      return;
    }

    try {
      setUpgrading(true);
      
      const productMapping = paddleService.getPaddleProductMapping();
      const targetPlan = credits?.tier === 'basic' ? 'pro' : 'pro';
      
      await paddleService.openCheckout({
        productId: productMapping[targetPlan].productId,
        email: user.email,
        userId: user.id,
        planName: targetPlan,
        successCallback: () => {
          toast.success('Upgrade successful! Your account will be updated shortly.');
          // Refresh credits after successful upgrade
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        },
        closeCallback: () => {
          console.log('Upgrade cancelled');
        }
      });
    } catch (error) {
      console.error('Upgrade failed:', error);
      toast.error('Failed to start upgrade process. Please try again.');
    } finally {
      setUpgrading(false);
    }
  };

  const getCreditsColor = () => {
    if (!credits) return 'default';
    if (credits.isUnlimited || credits.current === Infinity) return 'success';
    const percentage = (credits.current / credits.total) * 100;
    if (percentage <= 10) return 'error';
    if (percentage <= 25) return 'warning';
    return 'success';
  };

  const getCreditsIcon = () => {
    if (!credits) return <InfoIcon />;
    if (credits.isUnlimited || credits.current === Infinity) return <InfoIcon />;
    const percentage = (credits.current / credits.total) * 100;
    if (percentage <= 25) return <WarningIcon />;
    return <InfoIcon />;
  };

  const formatResetDate = (credits) => {
    if (credits?.isUnlimited || credits?.current === Infinity) {
      return 'Unlimited Plan';
    }
    
    if (credits?.daysUntilReset !== undefined) {
      const days = credits.daysUntilReset;
      if (days === 0) return 'Today';
      if (days === 1) return '1 day';
      return `${days} days`;
    }
    
    if (!credits?.resetDate) return 'Unknown';
    const now = new Date();
    const diffTime = Math.abs(credits.resetDate - now);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day';
    return `${diffDays} days`;
  };

  if (loading) {
    return (
      <Box sx={{ p: collapsed ? 1 : 2, width: '100%' }}>
        <LinearProgress size="small" />
      </Box>
    );
  }

  if (!credits) {
    return null;
  }

  const creditsPercentage = credits.isUnlimited ? 100 : (credits.current / credits.total) * 100;
  const isLowCredits = !credits.isUnlimited && creditsPercentage <= 25;

  if (collapsed) {
    return (
        <Tooltip 
        title={credits.isUnlimited ? `Unlimited credits • ${formatResetDate(credits)}` : `${credits.current}/${credits.total} credits • Resets in ${formatResetDate(credits)}`}
        placement="right"
      >
        <Box 
          sx={{ 
            p: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            gap: 0.5
          }}
        >
          <Chip
            icon={getCreditsIcon()}
            label={credits.isUnlimited ? "∞" : credits.current}
            color={getCreditsColor()}
            size="small"
            variant="outlined"
          />
          {isLowCredits && (
            <Button
              size="small"
              variant="contained"
              color="primary"
              onClick={handleUpgrade}
              disabled={upgrading}
              sx={{ 
                minWidth: 'auto',
                px: 1,
                fontSize: '0.7rem'
              }}
            >
              <UpgradeIcon sx={{ fontSize: '0.9rem' }} />
            </Button>
          )}
        </Box>
      </Tooltip>
    );
  }

  return (
    <Box
      sx={{
        px: 2,
        py: 1.5,
        borderTop: `1px solid ${alpha(theme.palette.divider, 0.6)}`,
        backgroundColor: 'background.paper',
      }}
    >
      {/* Credits Display - Minimal */}
      <Box sx={{ mb: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography 
            variant="caption" 
            sx={{
              fontSize: '0.6875rem',
              fontWeight: 700,
              color: alpha(theme.palette.text.secondary, 0.7),
              letterSpacing: '0.08em',
              textTransform: 'uppercase'
            }}
          >
            Credits
          </Typography>
          <Typography 
            variant="body2" 
            sx={{
              fontSize: '0.8125rem',
              fontWeight: 600,
              color: credits.isUnlimited ? 'success.main' : (creditsPercentage <= 25 ? 'error.main' : 'text.primary')
            }}
          >
            {credits.isUnlimited ? "∞" : `${credits.current}/${credits.total}`}
          </Typography>
        </Box>
        
        <LinearProgress
          variant={credits.isUnlimited ? "indeterminate" : "determinate"}
          value={credits.isUnlimited ? undefined : creditsPercentage}
          color={getCreditsColor()}
          sx={{
            height: 4,
            borderRadius: 2,
            mb: 0.75,
            backgroundColor: alpha(theme.palette.grey[300], 0.2),
            ...(credits.isUnlimited && {
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(90deg, #10b981, #059669, #047857, #065f46)',
                backgroundSize: '200% 100%',
                animation: 'gradient 2s ease infinite'
              },
              '@keyframes gradient': {
                '0%': { backgroundPosition: '0% 50%' },
                '50%': { backgroundPosition: '100% 50%' },
                '100%': { backgroundPosition: '0% 50%' }
              }
            })
          }}
        />
        
        <Typography 
          variant="caption" 
          sx={{
            fontSize: '0.6875rem',
            color: alpha(theme.palette.text.secondary, 0.8)
          }}
        >
          Resets in {formatResetDate(credits)}
        </Typography>
      </Box>

      {/* Upgrade Button - Minimal */}
      {!credits.isUnlimited && (isLowCredits || ['free', 'basic', 'growth'].includes(credits.tier?.toLowerCase())) && (
        <Button
          variant="contained"
          color="primary"
          fullWidth
          size="small"
          onClick={handleUpgrade}
          disabled={upgrading}
          sx={{
            py: 0.75,
            fontSize: '0.75rem',
            fontWeight: 600,
            textTransform: 'none',
            borderRadius: 1.5,
            boxShadow: 'none',
            '&:hover': {
              boxShadow: 1,
            }
          }}
        >
          {upgrading ? 'Processing...' : '⚡ Upgrade'}
        </Button>
      )}
    </Box>
  );
};

export default CreditsWidget;