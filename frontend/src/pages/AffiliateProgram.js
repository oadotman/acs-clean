import React from 'react';
import ComingSoon from '../components/ComingSoon';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  Avatar,
  Chip,
  Paper
} from '@mui/material';
import {
  AttachMoney,
  TrendingUp,
  Share,
  Analytics,
  School,
  Timer
} from '@mui/icons-material';

const AffiliateProgram = () => {
  const affiliateBenefits = [
    {
      icon: <AttachMoney />,
      title: "High Commissions",
      description: "Earn 40% commission on all referrals - one of the highest in SaaS"
    },
    {
      icon: <Timer />,
      title: "Recurring Revenue",
      description: "Get paid monthly for the lifetime of each customer you refer"
    },
    {
      icon: <Analytics />,
      title: "Real-time Tracking",
      description: "Advanced dashboard with conversion tracking and analytics"
    },
    {
      icon: <Share />,
      title: "Marketing Materials",
      description: "Professional banners, email templates, and social media content"
    },
    {
      icon: <School />,
      title: "Training & Support",
      description: "Complete training program and dedicated affiliate manager"
    },
    {
      icon: <TrendingUp />,
      title: "Performance Bonuses",
      description: "Extra bonuses for top performers and volume achievements"
    }
  ];

  const commissionStructure = [
    { tier: "Starter", referrals: "1-10", commission: "40%", color: "primary" },
    { tier: "Pro", referrals: "11-25", commission: "45%", color: "secondary" },
    { tier: "Elite", referrals: "26+", commission: "50%", color: "success" }
  ];

  const additionalContent = (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 4, textAlign: 'center' }}>
        💰 What Our Affiliate Program Will Include
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 6 }}>
        {affiliateBenefits.map((benefit, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card elevation={2} sx={{ height: '100%', p: 2 }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar
                  sx={{
                    bgcolor: 'warning.light',
                    color: 'warning.main',
                    width: 56,
                    height: 56,
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  {benefit.icon}
                </Avatar>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  {benefit.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {benefit.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* Commission Structure */}
      <Paper 
        sx={{ 
          p: 4, 
          mb: 4,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}>
          📊 Tiered Commission Structure
        </Typography>
        <Grid container spacing={3}>
          {commissionStructure.map((tier, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Paper 
                elevation={3}
                sx={{ 
                  p: 3, 
                  textAlign: 'center',
                  border: '2px solid',
                  borderColor: `${tier.color}.main`,
                  position: 'relative'
                }}
              >
                <Chip 
                  label={tier.tier}
                  color={tier.color}
                  sx={{ 
                    position: 'absolute',
                    top: -12,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontWeight: 600
                  }}
                />
                <Typography variant="h4" color={`${tier.color}.main`} fontWeight={800} sx={{ mt: 1 }}>
                  {tier.commission}
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Commission Rate
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {tier.referrals} successful referrals
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Paper>
      
      <Box sx={{ textAlign: 'center', p: 4, bgcolor: 'background.paper', borderRadius: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          🎯 Perfect For:
        </Typography>
        <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" useFlexGap>
          <Chip label="Content Creators" color="warning" />
          <Chip label="Marketing Influencers" color="warning" />
          <Chip label="Business Bloggers" color="warning" />
          <Chip label="Course Creators" color="warning" />
          <Chip label="Newsletter Writers" color="warning" />
          <Chip label="Social Media Managers" color="warning" />
        </Stack>
        
        <Typography variant="body2" color="text.secondary" sx={{ mt: 3, maxWidth: 500, mx: 'auto' }}>
          Join thousands of affiliates already earning passive income by promoting the best ad copy optimization platform in the market.
        </Typography>
      </Box>
    </Box>
  );

  return (
    <ComingSoon
        title="💰 Affiliate Program"
        subtitle="Earn up to 50% recurring commissions"
        description="Join our exclusive affiliate program and earn industry-leading commissions by promoting AdCopySurge to your audience. Complete with marketing materials, real-time tracking, and dedicated support."
        icon="💰"
        expectedDate="Q2 2025"
        additionalContent={additionalContent}
      />
  );
};

export default AffiliateProgram;
