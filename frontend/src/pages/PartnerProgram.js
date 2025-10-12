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
  Chip
} from '@mui/material';
import {
  Handshake,
  TrendingUp,
  People,
  Support,
  Star,
  BusinessCenter
} from '@mui/icons-material';

const PartnerProgram = () => {
  const partnerBenefits = [
    {
      icon: <TrendingUp />,
      title: "Revenue Sharing",
      description: "Earn up to 30% recurring commissions on successful referrals"
    },
    {
      icon: <People />,
      title: "Co-Marketing",
      description: "Joint marketing opportunities and case study development"
    },
    {
      icon: <Support />,
      title: "Dedicated Support",
      description: "Priority technical support and account management"
    },
    {
      icon: <Star />,
      title: "Early Access",
      description: "Beta access to new features and exclusive partner tools"
    }
  ];

  const additionalContent = (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 4, textAlign: 'center' }}>
        🤝 What Our Partner Program Will Include
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {partnerBenefits.map((benefit, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card elevation={2} sx={{ height: '100%', p: 2 }}>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <Avatar
                    sx={{
                      bgcolor: 'primary.light',
                      color: 'primary.main',
                      width: 48,
                      height: 48
                    }}
                  >
                    {benefit.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {benefit.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {benefit.description}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      <Box sx={{ textAlign: 'center', p: 4, bgcolor: 'background.paper', borderRadius: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          👥 Perfect For:
        </Typography>
        <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" useFlexGap>
          <Chip label="Marketing Agencies" color="primary" />
          <Chip label="Consultants" color="primary" />
          <Chip label="SaaS Companies" color="primary" />
          <Chip label="Tech Integrators" color="primary" />
          <Chip label="Business Coaches" color="primary" />
        </Stack>
      </Box>
    </Box>
  );

  return (
    <ComingSoon
        title="🤝 Partner Program"
        subtitle="Build your business with AdCopySurge"
        description="We're creating an exclusive partner program for agencies, consultants, and technology companies. Get early access to revenue sharing, co-marketing opportunities, and dedicated partner support."
        icon="🤝"
        expectedDate="Q2 2025"
        additionalContent={additionalContent}
      />
  );
};

export default PartnerProgram;
