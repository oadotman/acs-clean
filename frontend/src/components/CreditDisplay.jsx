import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  alpha,
  useTheme
} from '@mui/material';
import {
  Info as InfoIcon,
  Upgrade as UpgradeIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import { getUserCredits } from '../utils/creditSystem';
import { SUBSCRIPTION_TIERS, PLAN_LIMITS, isUnlimited } from '../constants/plans';

const CreditDisplay = ({ 
  showDetails = true, 
  compact = false, 
  onUpgrade = null,
  refreshTrigger = 0 
}) => {
  const theme = useTheme();
  const { user } = useAuth();
  const [credits, setCredits] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCredits = async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const creditData = await getUserCredits(user.id);
      console.log('🎯 CreditDisplay: Fetched credits:', creditData);
      setCredits(creditData);
    } catch (error) {
      console.error('❌ CreditDisplay: Error fetching credits:', error);
      // Set default free tier credits on error
      setCredits({
        credits: PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE].adAnalyses,
        monthlyAllowance: PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE].adAnalyses,
        subscriptionTier: SUBSCRIPTION_TIERS.FREE
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCredits();
  }, [user?.id, refreshTrigger]);

  if (loading || !credits) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <LinearProgress sx={{ width: 60, height: 4, borderRadius: 2 }} />
        <Typography variant="caption" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  const isUnlimitedPlan = credits.subscriptionTier === SUBSCRIPTION_TIERS.AGENCY_UNLIMITED ||
                         isUnlimited(credits.monthlyAllowance) ||
                         credits.credits >= 999999;

  const getCreditColor = () => {
    if (isUnlimitedPlan) return 'success';
    if (credits.credits === 0) return 'error';
    
    const percentage = (credits.credits / (credits.monthlyAllowance || 1)) * 100;
    if (percentage > 50) return 'success';
    if (percentage > 20) return 'warning';
    return 'error';
  };

  const formatCredits = (amount) => {
    if (isUnlimitedPlan) return '∞';
    return amount?.toLocaleString() || '0';
  };

  const creditColor = getCreditColor();
  const percentage = isUnlimitedPlan ? 100 : Math.min((credits.credits / (credits.monthlyAllowance || 1)) * 100, 100);

  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          size="small"
          label={`${formatCredits(credits.credits)} credits`}
          color={creditColor}
          variant={isUnlimitedPlan ? 'filled' : 'outlined'}
          sx={{
            fontWeight: 600,
            '& .MuiChip-label': {
              fontSize: isUnlimitedPlan ? '1.1em' : '0.875rem'
            }
          }}
        />
        {!isUnlimitedPlan && credits.credits <= 2 && (
          <Tooltip title="Low credits - consider upgrading">
            <IconButton size="small" onClick={onUpgrade} color="warning">
              <UpgradeIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    );
  }

  return (
    <Card 
      variant="outlined" 
      sx={{ 
        borderRadius: 2,
        border: `1px solid ${alpha(theme.palette[creditColor].main, 0.3)}`,
        backgroundColor: alpha(theme.palette[creditColor].main, 0.02)
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle2" fontWeight={600} color="text.primary">
            Analysis Credits
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Tooltip title="Refresh credit balance">
              <IconButton size="small" onClick={fetchCredits}>
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            {showDetails && (
              <Tooltip 
                title={
                  isUnlimitedPlan 
                    ? "You have unlimited analyses with your Agency Unlimited plan"
                    : `You have ${credits.credits} of ${credits.monthlyAllowance} monthly credits remaining`
                }
              >
                <IconButton size="small">
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography 
            variant="h4" 
            fontWeight={700} 
            color={`${creditColor}.main`}
            sx={{
              fontSize: isUnlimitedPlan ? '2.5rem' : '2rem',
              lineHeight: 1
            }}
          >
            {formatCredits(credits.credits)}
          </Typography>
          {!isUnlimitedPlan && (
            <Typography variant="body2" color="text.secondary">
              / {formatCredits(credits.monthlyAllowance)} this month
            </Typography>
          )}
        </Box>

        {!isUnlimitedPlan && (
          <Box sx={{ mb: showDetails ? 2 : 0 }}>
            <LinearProgress
              variant="determinate"
              value={percentage}
              color={creditColor}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: alpha(theme.palette[creditColor].main, 0.1),
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4
                }
              }}
            />
          </Box>
        )}

        {showDetails && (
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              {isUnlimitedPlan 
                ? 'Unlimited analyses • Agency Unlimited Plan'
                : `${Math.round(percentage)}% of monthly credits used`
              }
            </Typography>
            
            {!isUnlimitedPlan && credits.credits <= 2 && (
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Chip
                  size="small"
                  label="Low Credits"
                  color="warning"
                  variant="outlined"
                />
                {onUpgrade && (
                  <Typography 
                    variant="caption" 
                    color="primary" 
                    sx={{ cursor: 'pointer', textDecoration: 'underline' }}
                    onClick={onUpgrade}
                  >
                    Upgrade Plan
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CreditDisplay;