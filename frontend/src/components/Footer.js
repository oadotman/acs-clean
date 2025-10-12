import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  Button,
  TextField,
  IconButton,
  Divider,
  Stack,
  Chip,
  Paper,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import {
  Facebook,
  Twitter,
  LinkedIn,
  Instagram,
  YouTube,
  Email,
  Phone,
  LocationOn,
  Send,
  CheckCircle,
  Security,
  Star,
  TrendingUp
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import BrandLogo from './BrandLogo';

const Footer = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleNewsletterSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      console.error('Invalid email format');
      return;
    }
    
    setLoading(true);
    try {
      // TODO: Replace with actual newsletter service integration
      // Example: const response = await fetch('/api/newsletter/subscribe', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email: email.trim() })
      // });
      
      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Store email locally for development (remove in production)
      console.log('Newsletter signup:', email.trim());
      
      setSubscribed(true);
      setEmail('');
      setTimeout(() => setSubscribed(false), 5000); // Reset after 5 seconds
    } catch (error) {
      console.error('Newsletter subscription failed:', error);
      // TODO: Add error state handling
    } finally {
      setLoading(false);
    }
  };

  const currentYear = new Date().getFullYear();

  const productLinks = [
    { label: 'Ad Copy Analyzer', to: '/analyze' },
    { label: 'Compliance Checker', to: '/compliance-checker' },
    { label: 'ROI Generator', to: '/roi-generator' },
    { label: 'Strategic A/B/C Testing', to: '/strategic-abc-testing' },
    { label: 'Industry Optimizer', to: '/industry-optimizer' },
    { label: 'Performance Forensics', to: '/performance-forensics' },
    { label: 'Psychology Scorer', to: '/psychology-scorer' },
    { label: 'Brand Voice Engine', to: '/brand-voice-engine' },
    { label: 'Legal Risk Scanner', to: '/legal-risk-scanner' }
  ];

  const resourceLinks = [
    { label: 'Getting Started', to: '/resources/getting-started' },
    { label: 'Tutorials & Guides', to: '/resources/tutorials' },
    { label: 'Case Studies', to: '/resources/case-studies' },
    { label: 'Blog', to: '/blog' }
  ];

  const companyLinks = [
    { label: 'About Us', to: '/about' },
    { label: 'Careers', to: '/careers' },
    { label: 'Press & Media', to: '/press' },
    { label: 'Partner Program', to: '/partners' },
    { label: 'Affiliate Program', to: '/affiliates' },
    { label: 'Brand Assets', to: '/brand-assets' }
  ];

  const supportLinks = [
    { label: 'Help Center', to: '/help' },
    { label: 'Contact Us', to: '/contact' },
    { label: 'Feature Requests', to: '/feature-requests' },
    { label: 'Community Forum', to: '/community' }
  ];

  const legalLinks = [
    { label: 'Privacy Policy', to: '/privacy' },
    { label: 'Terms of Service', to: '/terms' },
    { label: 'Cookie Policy', to: '/cookies' },
    { label: 'GDPR Compliance', to: '/gdpr' },
    { label: 'Data Security', to: '/security' }
  ];

  const socialLinks = [
    { icon: <Twitter />, url: 'https://twitter.com/adcopysurge', label: 'Twitter' },
    { icon: <LinkedIn />, url: 'https://linkedin.com/company/adcopysurge', label: 'LinkedIn' },
    { icon: <Facebook />, url: 'https://facebook.com/adcopysurge', label: 'Facebook' },
    { icon: <Instagram />, url: 'https://instagram.com/adcopysurge', label: 'Instagram' },
    { icon: <YouTube />, url: 'https://youtube.com/@adcopysurge', label: 'YouTube' }
  ];

  const trustBadges = [
    { icon: <Security />, text: 'SOC 2 Compliant' },
    { icon: <CheckCircle />, text: 'GDPR Ready' },
    { icon: <Star />, text: '500+ Happy Customers' },
    { icon: <TrendingUp />, text: '300% Avg ROAS Increase' }
  ];

  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: 'grey.900',
        color: 'white',
        mt: 8,
        pt: 6,
        pb: 3,
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: 'linear-gradient(90deg, #2563eb 0%, #f59e0b 50%, #7c3aed 100%)'
        }
      }}
    >
      <Container maxWidth="lg">
        {/* Main Footer Content */}
        <Grid container spacing={6}>
          {/* Company Info & Newsletter */}
          <Grid item xs={12} md={4}>
            <Box sx={{ mb: 3 }}>
              <BrandLogo variant="full" size="medium" darkMode />
              <Typography variant="body1" sx={{ mt: 2, mb: 3, color: 'grey.300' }}>
                The complete marketing intelligence suite. 9 specialized tools to analyze, optimize, 
                and supercharge your ad campaigns with data-driven insights.
              </Typography>
            </Box>

            {/* Newsletter Signup */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Stay Updated
              </Typography>
              {subscribed ? (
                <Paper
                  sx={{
                    p: 2,
                    backgroundColor: 'success.main',
                    color: 'success.contrastText',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}
                >
                  <CheckCircle />
                  <Typography variant="body2">
                    Thanks for subscribing! Check your email.
                  </Typography>
                </Paper>
              ) : (
                <Box component="form" onSubmit={handleNewsletterSubmit}>
                  <TextField
                    fullWidth
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    variant="outlined"
                    size="small"
                    sx={{
                      mb: 2,
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        color: 'white',
                        '& fieldset': {
                          borderColor: 'rgba(255,255,255,0.3)'
                        },
                        '&:hover fieldset': {
                          borderColor: 'rgba(255,255,255,0.5)'
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: 'primary.main'
                        }
                      },
                      '& input::placeholder': {
                        color: 'rgba(255,255,255,0.7)'
                      }
                    }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            type="submit"
                            disabled={loading || !email.trim()}
                            sx={{ 
                              color: 'white',
                              '&:disabled': {
                                color: 'rgba(255,255,255,0.3)'
                              }
                            }}
                          >
                            {loading ? (
                              <CircularProgress size={20} sx={{ color: 'white' }} />
                            ) : (
                              <Send />
                            )}
                          </IconButton>
                        </InputAdornment>
                      )
                    }}
                  />
                  <Typography variant="caption" sx={{ color: 'grey.400' }}>
                    Weekly marketing insights & product updates. No spam, unsubscribe anytime.
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Trust Badges */}
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {trustBadges.map((badge, index) => (
                <Chip
                  key={index}
                  icon={badge.icon}
                  label={badge.text}
                  size="small"
                  variant="outlined"
                  sx={{
                    color: 'grey.300',
                    borderColor: 'rgba(255,255,255,0.3)',
                    '& .MuiChip-icon': {
                      color: 'primary.main'
                    }
                  }}
                />
              ))}
            </Stack>
          </Grid>

          {/* Products */}
          <Grid item xs={12} sm={6} md={2}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Products
            </Typography>
            <Stack spacing={1}>
              {productLinks.map((link) => (
                <Link
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  sx={{
                    color: 'grey.300',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    '&:hover': {
                      color: 'primary.main',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          {/* Resources */}
          <Grid item xs={12} sm={6} md={2}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Resources
            </Typography>
            <Stack spacing={1}>
              {resourceLinks.map((link) => (
                <Link
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  sx={{
                    color: 'grey.300',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    '&:hover': {
                      color: 'primary.main',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          {/* Company */}
          <Grid item xs={12} sm={6} md={2}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Company
            </Typography>
            <Stack spacing={1}>
              {companyLinks.map((link) => (
                <Link
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  sx={{
                    color: 'grey.300',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    '&:hover': {
                      color: 'primary.main',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          {/* Support & Contact */}
          <Grid item xs={12} sm={6} md={2}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Support
            </Typography>
            <Stack spacing={1} sx={{ mb: 3 }}>
              {supportLinks.map((link) => (
                <Link
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  sx={{
                    color: 'grey.300',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    '&:hover': {
                      color: 'primary.main',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>

            {/* Contact Info */}
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Contact
              </Typography>
              <Stack spacing={0.5}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Email sx={{ fontSize: '1rem', color: 'grey.400' }} />
                  <Typography variant="caption" color="grey.300">
                    support@adcopysurge.com
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Phone sx={{ fontSize: '1rem', color: 'grey.400' }} />
                  <Typography variant="caption" color="grey.300">
                    +1 (555) 123-4567
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocationOn sx={{ fontSize: '1rem', color: 'grey.400' }} />
                  <Typography variant="caption" color="grey.300">
                    San Francisco, CA
                  </Typography>
                </Box>
              </Stack>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4, borderColor: 'rgba(255,255,255,0.1)' }} />

        {/* Bottom Footer */}
        <Box>
          {/* Social Links */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
              Follow Us
            </Typography>
            <Stack direction="row" spacing={2}>
              {socialLinks.map((social) => (
                <IconButton
                  key={social.label}
                  component="a"
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'grey.400',
                    '&:hover': {
                      color: 'primary.main',
                      transform: 'translateY(-2px)'
                    },
                    transition: 'all 0.2s ease'
                  }}
                  aria-label={social.label}
                >
                  {social.icon}
                </IconButton>
              ))}
            </Stack>
          </Box>

          {/* Legal & Copyright */}
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={8}>
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={3}
                alignItems={{ xs: 'flex-start', sm: 'center' }}
              >
                <Box>
                  <Typography variant="body2" color="grey.400">
                    © {currentYear} AdCopySurge. All rights reserved.
                  </Typography>
                  <Typography variant="caption" color="grey.500" sx={{ mt: 0.5, display: 'block' }}>
                    AdSurge is owned and operated by Nikola Innovations Limited.
                  </Typography>
                </Box>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  {legalLinks.map((link) => (
                    <Link
                      key={link.to}
                      component={RouterLink}
                      to={link.to}
                      sx={{
                        color: 'grey.400',
                        textDecoration: 'none',
                        fontSize: '0.75rem',
                        '&:hover': {
                          color: 'primary.main'
                        }
                      }}
                    >
                      {link.label}
                    </Link>
                  ))}
                </Stack>
              </Stack>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography 
                variant="caption" 
                color="grey.500"
                sx={{ display: 'block', textAlign: { xs: 'left', md: 'right' } }}
              >
                Built with 💙 for marketers worldwide
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
