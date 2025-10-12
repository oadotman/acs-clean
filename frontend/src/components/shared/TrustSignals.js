import React from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Paper,
  Chip
} from '@mui/material';
import { 
  Security, 
  Verified, 
  Speed,
  BusinessCenter,
  StarRate,
  Shield
} from '@mui/icons-material';

const TrustSignals = () => {
  const securityBadges = [
    {
      icon: <Security sx={{ color: '#10b981', fontSize: 32 }} />,
      label: 'SOC 2 Type II Certified',
      description: 'Enterprise security standards'
    },
    {
      icon: <Shield sx={{ color: '#3b82f6', fontSize: 32 }} />,
      label: 'GDPR Compliant',
      description: 'Data protection certified'
    },
    {
      icon: <Verified sx={{ color: '#8b5cf6', fontSize: 32 }} />,
      label: 'Enterprise Ready',
      description: '99.9% uptime SLA'
    }
  ];

  const clientTypes = [
    'Fortune 500 Companies',
    'Leading Ad Agencies',
    'E-commerce Brands',
    'SaaS Startups',
    'Marketing Teams',
    'Solo Entrepreneurs'
  ];

  const awards = [
    {
      title: 'Best Ad Optimization Tool',
      year: '2024',
      organization: 'Marketing Tech Awards'
    },
    {
      title: 'Top AI Marketing Solution',
      year: '2024', 
      organization: 'AdTech Innovation Summit'
    },
    {
      title: 'Editor\'s Choice',
      year: '2024',
      organization: 'Digital Marketing Weekly'
    }
  ];

  return (
    <Box sx={{ py: { xs: 6, md: 8 } }}>
      <Container maxWidth="lg">
        {/* Security & Compliance Badges */}
        <Typography variant="h6" sx={{ 
          textAlign: 'center', 
          color: '#E5E7EB', 
          mb: 4,
          fontWeight: 600
        }}>
          Trusted by 500+ agencies with enterprise-grade security
        </Typography>
        
        <Grid container spacing={4} sx={{ mb: 8 }} justifyContent="center">
          {securityBadges.map((badge, index) => (
            <Grid item xs={12} sm={4} key={index}>
              <Paper sx={{
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                p: 3,
                textAlign: 'center',
                height: '100%',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(255, 255, 255, 0.1)'
                }
              }}>
                <Box sx={{ mb: 2 }}>
                  {badge.icon}
                </Box>
                <Typography variant="body1" sx={{ 
                  color: '#F9FAFB', 
                  fontWeight: 600,
                  mb: 1
                }}>
                  {badge.label}
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: '#E5E7EB',
                  opacity: 0.8
                }}>
                  {badge.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Client Types */}
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography variant="h6" sx={{ 
            color: '#E5E7EB', 
            mb: 3,
            fontWeight: 600
          }}>
            Used by leading companies worldwide
          </Typography>
          
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: 2, 
            justifyContent: 'center',
            maxWidth: '600px',
            mx: 'auto'
          }}>
            {clientTypes.map((type, index) => (
              <Chip
                key={index}
                label={type}
                sx={{
                  background: 'rgba(168, 85, 247, 0.1)',
                  border: '1px solid rgba(168, 85, 247, 0.2)',
                  color: '#C084FC',
                  fontWeight: 500,
                  '&:hover': {
                    background: 'rgba(168, 85, 247, 0.15)',
                    borderColor: 'rgba(168, 85, 247, 0.3)'
                  }
                }}
              />
            ))}
          </Box>
        </Box>

        {/* Awards & Recognition */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ 
            color: '#E5E7EB', 
            mb: 4,
            fontWeight: 600
          }}>
            Industry Recognition
          </Typography>
          
          <Grid container spacing={3} justifyContent="center">
            {awards.map((award, index) => (
              <Grid item xs={12} sm={4} key={index}>
                <Box sx={{
                  background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%)',
                  border: '1px solid rgba(251, 191, 36, 0.2)',
                  borderRadius: 3,
                  p: 3,
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    borderColor: 'rgba(251, 191, 36, 0.3)'
                  }
                }}>
                  <StarRate sx={{ color: '#fbbf24', fontSize: 32, mb: 2 }} />
                  <Typography variant="body1" sx={{ 
                    color: '#F9FAFB', 
                    fontWeight: 600,
                    mb: 1
                  }}>
                    {award.title}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: '#fbbf24',
                    fontWeight: 500,
                    mb: 1
                  }}>
                    {award.year}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: '#E5E7EB',
                    opacity: 0.8,
                    fontSize: '0.85rem'
                  }}>
                    {award.organization}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default TrustSignals;