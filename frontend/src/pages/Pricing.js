import React, { useState } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  CircularProgress,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAuth } from '../services/authContext';
import { useNavigate } from 'react-router-dom';
import paddleService from '../services/paddleService';
import toast from 'react-hot-toast';
import PRICING_PLANS from '../constants/plans';
import PricingTable from '../components/pricing/PricingTable';

const Pricing = () => {
  const { isAuthenticated, subscription, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState({});
  const [isYearly, setIsYearly] = useState(false);
  
  // Safe initialization of paddleProducts with fallback
  const [paddleProducts] = useState(() => {
    try {
      return paddleService.getPaddleProductMapping();
    } catch (error) {
      console.error('Failed to load Paddle products:', error);
      return {
        basic: { productId: 'basic_monthly', name: 'Basic Plan', price: 49 },
        pro: { productId: 'pro_monthly', name: 'Pro Plan', price: 99 }
      };
    }
  });

  // Use updated pricing plans directly
  const plans = PRICING_PLANS;

  const handlePlanSelect = async (plan) => {
    if (!isAuthenticated) {
      navigate('/register');
      return;
    }

    if (plan.name === 'Free') {
      navigate('/analysis/new');
      return;
    }

    // Handle paid plan upgrade with Paddle
    const planKey = plan.tier || plan.name.toLowerCase();
    const billingPeriod = isYearly ? 'yearly' : 'monthly';
    setLoading(prev => ({ ...prev, [planKey]: true }));
    
    try {
      const paddleProduct = paddleProducts[planKey];
      
      // Handle new nested structure (monthly/yearly) vs legacy structure
      let selectedProduct;
      if (paddleProduct && typeof paddleProduct === 'object' && paddleProduct.monthly) {
        // New nested structure
        selectedProduct = paddleProduct[billingPeriod];
      } else {
        // Legacy structure (for basic/pro fallback)
        selectedProduct = paddleProduct;
      }
      
      if (!selectedProduct) {
        throw new Error('Invalid plan selected');
      }

      // Check if Paddle is configured
      const paddleVendorId = process.env.REACT_APP_PADDLE_VENDOR_ID;
      
      if (!paddleVendorId) {
        // Development mode - show info message
        toast.error(
          `Paddle billing not configured. Would upgrade to ${plan.name} plan ($${plan.price}/${plan.period})`,
          { duration: 4000 }
        );
        console.log('🛍️ Development mode: Would upgrade to:', {
          plan: plan.name,
          price: plan.price,
          period: plan.period,
          productId: selectedProduct.productId
        });
        return;
      }

      // Open Paddle checkout overlay
      await paddleService.openCheckout({
        productId: selectedProduct.productId,
        email: user?.email || '',
        userId: user?.id || '',
        planName: `${plan.name} (${billingPeriod})`,
        successCallback: (data) => {
          toast.success(`Successfully upgraded to ${plan.name} plan!`);
          setTimeout(() => {
            navigate('/analysis/new?success=true');
          }, 2000);
        },
        closeCallback: () => {
          console.log('Paddle checkout closed');
        }
      });
      
    } catch (error) {
      console.error('Upgrade failed:', error);
      toast.error(`Failed to upgrade: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, [planKey]: false }));
    }
  };

  const isCurrentPlan = (planName) => {
    if (!subscription) return planName === 'Free';
    // Check if subscription has the expected property
    const currentTier = subscription.subscription_tier || subscription.tier;
    return currentTier === planName.toLowerCase();
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      py: 8,
      background: 'linear-gradient(135deg, #0f0b1d 0%, #1a1333 50%, #2d1b5e 100%)'
    }}>
      <Container maxWidth="lg">
        <Box textAlign="center" sx={{ mb: 6 }}>
          <Typography 
            variant="h2" 
            component="h1" 
            sx={{
              color: '#F9FAFB',
              fontWeight: 800,
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              mb: 3
            }}
          >
            Choose Your Plan
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: '#E5E7EB',
              maxWidth: 600, 
              mx: 'auto', 
              mb: 4,
              fontSize: { xs: '1.1rem', md: '1.3rem' },
              lineHeight: 1.6
            }}
          >
            Unlock the power of AI-driven ad analysis and optimization. 
            Start free and upgrade as your business grows.
          </Typography>
        </Box>

        {/* Pricing Table */}
        <PricingTable 
          plans={plans}
          onPlanSelect={handlePlanSelect}
          isYearly={isYearly}
          setIsYearly={setIsYearly}
        />

        <Box textAlign="center" sx={{ mt: 8 }}>
          <Typography 
            variant="body1" 
            sx={{
              color: '#E5E7EB',
              fontSize: '1.1rem',
              fontWeight: 500
            }}
          >
            💳 No credit card required for Free plan • 🔒 SOC 2 + GDPR Compliant • 💯 30-day money-back guarantee
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Pricing;
