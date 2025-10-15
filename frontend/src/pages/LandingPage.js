import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  Chip,
  Stack,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  useTheme,
  useMediaQuery,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Fade,
  Zoom,
  Grow,
  keyframes,
  Switch,
  FormControlLabel,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import { gradients } from '../utils/gradients';
import {
  Speed,
  CheckCircle,
  Star,
  AutoAwesome,
  Analytics,
  CompareArrows,
  Lightbulb,
  ArrowForward,
  Security,
  Verified,
  PlayArrow,
  TrendingUp,
  RocketLaunch,
  EmojiEvents,
  LocalFireDepartment,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import PRICING_PLANS from '../constants/plans';
import PricingTable from '../components/pricing/PricingTable';
import TrustSignals from '../components/shared/TrustSignals';

const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, loading } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [liveCounter, setLiveCounter] = useState(0);
  const [adText, setAdText] = useState('');
  const [showInstantScore, setShowInstantScore] = useState(false);
  const [instantScore, setInstantScore] = useState(null);
  // Pricing plan toggle state - MUST be declared before any conditional returns
  const [isYearly, setIsYearly] = useState(false);
  
  // Redirect authenticated users to new analysis automatically
  useEffect(() => {
    if (!loading && isAuthenticated) {
      console.log('🔄 Authenticated user on landing page, redirecting to new analysis...');
      navigate('/analysis/new', { replace: true });
    }
  }, [isAuthenticated, loading, navigate]);
  
  // Live counter showing money wasted while reading
  useEffect(() => {
    const timer = setInterval(() => {
      setLiveCounter(prev => prev + 0.23); // $0.23 per second = ~$20/minute
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  // Instant ad scoring simulation
  useEffect(() => {
    if (adText.trim().length > 10) {
      const timer = setTimeout(() => {
        const score = Math.floor(Math.random() * 30) + 15; // Random score 15-45 (poor)
        setInstantScore(score);
        setShowInstantScore(true);
      }, 800);
      
      return () => clearTimeout(timer);
    } else {
      setShowInstantScore(false);
      setInstantScore(null);
    }
  }, [adText]);
  
  // Show loading or redirect immediately if authenticated
  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        sx={{ bgcolor: 'background.default' }}
      >
        <Box textAlign="center">
          <CircularProgress size={48} sx={{ mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Checking authentication...
          </Typography>
        </Box>
      </Box>
    );
  }
  
  // If authenticated, don't render the landing page (redirect is happening)
  if (isAuthenticated) {
    return null;
  }

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/analysis/new');
    } else {
      navigate('/register');
    }
  };
  
  const handleFreeScan = () => {
    if (isAuthenticated) {
      navigate('/analysis/new');
    } else {
      navigate('/register?cta=free-scan');
    }
  };
  
  const handleWatchDemo = () => {
    document.getElementById('demo-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  const socialProofData = [
    {
      name: "Adenike C.",
      company: "TechStart Inc",
      result: "Prevented a compliance suspension and preserved $47K in campaign value.",
      type: "SaaS, $2.4M spend"
    },
    {
      name: "Mike R.",
      company: "E-commerce Pro",
      result: "Improved profit margins by 28% within the first month through optimized copy variants.",
      type: "$180K/month"
    },
    {
      name: "Jules L.",
      company: "Agency",
      result: "Doubled testing throughput and improved client retention from 82% to 94%.",
      type: "40 clients, $4M spend"
    },
    {
      name: "Alex K.",
      company: "FinTech Startup",
      result: "Reduced CPC from $3.80 to $2.10 and lifted CTR by 78%.",
      type: "$500K/Q"
    },
    {
      name: "David M.",
      company: "Health & Wellness Co",
      result: "Scaled from $50K to $180K monthly spend with sustainable ROAS growth.",
      type: "B2C, $3.6M spend"
    },
    {
      name: "Lisa T.",
      company: "Marketing Agency",
      result: "Boosted average client ROAS by 96% and won 6 new retainers in 60 days.",
      type: "B2B,$1.1M spend"
    },
    {
      name: "Robert S.",
      company: "EdTech Platform",
      result: "Cut cost per acquisition by 38% and improved lead-to-signup conversion by 2.1x.",
      type: "B2B SaaS, $1.8M spend"
    },
    {
      name: "Emma W.",
      company: "Fashion Retailer",
      result: "Recovered from iOS14 impact with new compliant ad angles — achieved 1.8x profit growth.",
      type: "E-commerce, $2.5M spend"
    },
    {
      name: "Carlos R.",
      company: "Solar Installation",
      result: "Generated 400 qualified leads in Q3 with a 160% ROI increase.",
      type: "Local Service, $900K spend"
    }
  ];

  // Use the updated pricing plans directly
  const pricingData = PRICING_PLANS.map(plan => ({
    ...plan,
    name: plan.name === 'Free' ? 'Free Test Drive' : plan.name
  }));

  const roleMessages = [
    {
      role: "CMOs",
      message: "Walk into leadership meetings with proof, not excuses."
    },
    {
      role: "Agencies", 
      message: "Deliver data-backed results in minutes, not days."
    },
    {
      role: "Founders",
      message: "Get enterprise-level ad insights without enterprise costs."
    }
  ];

  // Animation keyframes
  const pulseGlow = keyframes`
    0%, 100% {
      box-shadow: 0 0 40px rgba(192, 132, 252, 0.4);
    }
    50% {
      box-shadow: 0 0 60px rgba(168, 85, 247, 0.6);
    }
  `;

  const float = keyframes`
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-20px);
    }
  `;

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: gradients.darkHero,
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: '-50%',
        left: '-50%',
        width: '200%',
        height: '200%',
        background: 'radial-gradient(circle at 30% 20%, rgba(124, 58, 237, 0.2) 0%, transparent 40%), radial-gradient(circle at 70% 60%, rgba(168, 85, 247, 0.15) 0%, transparent 40%), radial-gradient(circle at 50% 80%, rgba(192, 132, 252, 0.1) 0%, transparent 50%)',
        pointerEvents: 'none',
        zIndex: 0,
        animation: `${float} 20s ease-in-out infinite`,
      },
      '&::after': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(180deg, transparent 0%, rgba(15, 11, 29, 0.6) 100%)',
        pointerEvents: 'none',
        zIndex: 1,
      }
    }}>

      {/* Hero Section */}
      <Box sx={{ 
        background: 'transparent',
        color: '#F9FAFB',
        py: { xs: 8, md: 12 },
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          {/* Pre-headline Badge */}
          <Zoom in timeout={800}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Chip
                icon={<Verified sx={{ color: '#10B981' }} />}
                label="Used by performance marketers at leading agencies, SaaS companies, and e-commerce brands"
                sx={{
                  background: gradients.glassCard,
                  backdropFilter: 'blur(20px)',
                  border: '2px solid rgba(16, 185, 129, 0.3)',
                  color: '#F9FAFB',
                  fontWeight: 600,
                  fontSize: { xs: '0.85rem', md: '1rem' },
                  py: 2.5,
                  px: 3,
                  height: 'auto',
                  borderRadius: 100,
                  boxShadow: '0 8px 25px rgba(16, 185, 129, 0.2)',
                  '& .MuiChip-label': {
                    px: 2,
                    py: 1
                  },
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'scale(1.02)',
                    boxShadow: '0 12px 35px rgba(16, 185, 129, 0.3)',
                  }
                }}
              />
            </Box>
          </Zoom>
          
          <Fade in timeout={1200}>
            <Grid container spacing={6} alignItems="center">
              <Grid item xs={12} md={10} sx={{ mx: 'auto', textAlign: 'center' }}>
                {/* Main Headline */}
                <Typography
                  variant="h1"
                  sx={{
                    fontSize: { xs: '2.2rem', sm: '3rem', md: '4rem', lg: '4.8rem' },
                    fontWeight: 900,
                    mb: 4,
                    lineHeight: 1.1,
                    color: '#F9FAFB',
                    textAlign: 'center',
                    letterSpacing: '-0.03em',
                    textShadow: '0 4px 20px rgba(192, 132, 252, 0.3)',
                  }}
                >
                  Generate High-Converting,{' '}
                  <Box component="span" sx={{ 
                    background: gradients.ctaPrimary,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontWeight: 900,
                  }}>
                    Policy-Safe Ad Variants
                  </Box>
                  {' '}in 2 Minutes
                  <Box component="span" sx={{ 
                    display: 'block',
                    mt: 2,
                    fontSize: { xs: '1.8rem', sm: '2.5rem', md: '3.2rem', lg: '3.8rem' },
                    fontWeight: 700,
                    color: '#10B981'
                  }}>
                    — Backed by Behavioral Science
                  </Box>
                </Typography>
                
                {/* Subheadline */}
                <Typography
                  variant="h4"
                  sx={{
                    mb: 3,
                    fontWeight: 600,
                    color: '#F9FAFB',
                    fontSize: { xs: '1.3rem', sm: '1.5rem', md: '1.8rem' },
                    lineHeight: 1.5,
                    maxWidth: '950px',
                    mx: 'auto',
                    textAlign: 'center',
                  }}
                >
                  AdCopySurge analyzes your existing ads, identifies weak points, and delivers psychology-backed, compliant variants that{' '}
                  <Box component="span" sx={{ 
                    color: '#10B981', 
                    fontWeight: 700,
                  }}>
                    outperform competitors
                  </Box>
                  {' '}— without risking ad bans.
                </Typography>
                
                {/* Supporting Text */}
                <Typography
                  variant="h6"
                  sx={{
                    mb: 6,
                    fontWeight: 500,
                    color: '#E5E7EB',
                    fontSize: { xs: '1rem', sm: '1.1rem', md: '1.2rem' },
                    lineHeight: 1.6,
                    maxWidth: '800px',
                    mx: 'auto',
                    textAlign: 'center',
                    opacity: 0.9,
                  }}
                >
                  The only platform combining compliance scanning, behavioral psychology scoring, and ROI-driven variant generation — all in one streamlined workflow.
                </Typography>

                {/* Performance Insights Card */}
                <Grow in timeout={1600}>
                  <Paper sx={{ 
                    background: gradients.cardPurple,
                    backdropFilter: 'blur(30px)',
                    border: '2px solid rgba(192, 132, 252, 0.3)',
                    borderRadius: 6,
                    p: { xs: 4, md: 8 },
                    mb: 6,
                    boxShadow: '0 30px 80px rgba(124, 58, 237, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 40px 100px rgba(168, 85, 247, 0.4)',
                      borderColor: 'rgba(192, 132, 252, 0.6)',
                    }
                  }}>
                    <Typography variant="h4" sx={{ 
                      color: '#F9FAFB', 
                      fontWeight: 800, 
                      mb: 6, 
                      textAlign: 'center',
                      fontSize: { xs: '1.5rem', md: '2rem' },
                      textShadow: '0 2px 10px rgba(192, 132, 252, 0.5)',
                      letterSpacing: '-0.02em',
                    }}>
                      Why Your Competitors Pay Less & Convert More
                    </Typography>
                
                    <TableContainer sx={{ 
                      backgroundColor: 'rgba(15, 11, 29, 0.5)',
                      borderRadius: 4,
                      overflow: 'hidden',
                      border: '1px solid rgba(168, 85, 247, 0.2)',
                      '& .MuiTableCell-root': {
                        borderColor: 'rgba(168, 85, 247, 0.15)',
                        color: '#F9FAFB',
                        fontWeight: 600,
                        py: { xs: 2.5, md: 3.5 },
                        px: { xs: 2, md: 4 },
                        fontSize: { xs: '0.9rem', md: '1.1rem' },
                      }
                    }}>
                      <Table>
                        <TableHead>
                          <TableRow sx={{ 
                            background: 'rgba(124, 58, 237, 0.2)',
                            borderBottom: '2px solid rgba(192, 132, 252, 0.3)',
                          }}>
                            <TableCell sx={{ color: '#FCA5A5', fontWeight: 700, fontSize: { xs: '1rem', md: '1.2rem' } }}>❌ Your Performance</TableCell>
                            <TableCell sx={{ color: '#86EFAC', fontWeight: 700, fontSize: { xs: '1rem', md: '1.2rem' } }}>✅ Your Competitors</TableCell>
                            <TableCell sx={{ color: '#C084FC', fontWeight: 700, fontSize: { xs: '1rem', md: '1.2rem' } }}>💸 The Pain</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          <TableRow sx={{ 
                            '&:hover': { 
                              backgroundColor: 'rgba(168, 85, 247, 0.05)',
                              transition: 'all 0.3s ease',
                            } 
                          }}>
                            <TableCell sx={{ color: '#FCA5A5', fontWeight: 700, fontSize: { xs: '1.1rem', md: '1.3rem' } }}>0.8% CTR</TableCell>
                            <TableCell sx={{ color: '#86EFAC', fontWeight: 700, fontSize: { xs: '1.1rem', md: '1.3rem' } }}>2.4% CTR</TableCell>
                            <TableCell sx={{ color: '#A855F7', fontWeight: 700 }}>You're paying 200% more per click</TableCell>
                          </TableRow>
                          <TableRow sx={{ 
                            '&:hover': { 
                              backgroundColor: 'rgba(168, 85, 247, 0.05)',
                              transition: 'all 0.3s ease',
                            } 
                          }}>
                            <TableCell sx={{ color: '#FCA5A5', fontWeight: 700, fontSize: { xs: '1.1rem', md: '1.3rem' } }}>$2.50 CPC</TableCell>
                            <TableCell sx={{ color: '#86EFAC', fontWeight: 700, fontSize: { xs: '1.1rem', md: '1.3rem' } }}>$0.90 CPC</TableCell>
                            <TableCell sx={{ color: '#A855F7', fontWeight: 700 }}>$16,000 wasted per 10K clicks</TableCell>
                          </TableRow>
                          <TableRow sx={{ 
                            '&:hover': { 
                              backgroundColor: 'rgba(168, 85, 247, 0.05)',
                              transition: 'all 0.3s ease',
                            } 
                          }}>
                            <TableCell sx={{ color: '#FCA5A5', fontWeight: 700, fontSize: { xs: '1.1rem', md: '1.3rem' } }}>2.1x ROAS</TableCell>
                            <TableCell sx={{ color: '#86EFAC', fontWeight: 700, fontSize: { xs: '1.1rem', md: '1.3rem' } }}>6.8x ROAS</TableCell>
                            <TableCell sx={{ color: '#A855F7', fontWeight: 700 }}>They make 3x more profit than you</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                
                    <Typography variant="h5" sx={{ 
                      color: '#86EFAC', 
                      fontWeight: 800, 
                      textAlign: 'center', 
                      mt: 6,
                      fontSize: { xs: '1.2rem', md: '1.5rem' },
                      textShadow: '0 2px 10px rgba(134, 239, 172, 0.3)',
                      mb: 4
                    }}>
                      📈 Right now, your competitors are making significantly more profit than you
                    </Typography>
                    
                    {/* CTA after competitor comparison */}
                    <Box sx={{ textAlign: 'center', mt: 4 }}>
                      <Button
                        variant="contained"
                        size="large"
                        onClick={handleFreeScan}
                        startIcon={<Analytics />}
                        sx={{
                          background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%)',
                          color: '#7c3aed',
                          fontSize: { xs: '1rem', md: '1.2rem' },
                          px: { xs: 4, md: 6 },
                          py: { xs: 2, md: 2.5 },
                          borderRadius: 3,
                          fontWeight: 700,
                          textTransform: 'none',
                          boxShadow: '0 8px 25px rgba(255, 255, 255, 0.2)',
                          border: '2px solid rgba(124, 58, 237, 0.2)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, rgba(250,247,255,0.9) 0%, rgba(243,232,255,0.9) 100%)',
                            transform: 'translateY(-2px)',
                            boxShadow: '0 12px 35px rgba(124, 58, 237, 0.3)',
                            color: '#6d28d9'
                          },
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}
                      >
                        Run My Free Ad Analysis Now
                      </Button>
                    </Box>
                  </Paper>
                </Grow>
                
                <Stack 
                  direction={{ xs: 'column', sm: 'row' }} 
                  spacing={3} 
                  sx={{ mb: 6, mt: 6 }} 
                  justifyContent="center"
                >
                  <Zoom in timeout={2000}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Button
                        variant="contained"
                        size="large"
                        onClick={handleFreeScan}
                        startIcon={<RocketLaunch />}
                        sx={{
                          background: gradients.ctaPrimary,
                          color: '#F9FAFB',
                          fontSize: { xs: '1.1rem', md: '1.3rem' },
                          px: { xs: 5, md: 8 },
                          py: { xs: 2.5, md: 3.5 },
                          borderRadius: 3,
                          fontWeight: 800,
                          textTransform: 'none',
                          boxShadow: '0 15px 50px rgba(192, 132, 252, 0.4)',
                          border: '2px solid rgba(255, 255, 255, 0.2)',
                          '&:hover': {
                            background: gradients.ctaHover,
                            transform: 'translateY(-4px)',
                            boxShadow: '0 20px 60px rgba(192, 132, 252, 0.6)',
                          },
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}
                      >
                        Get Your Free Ad Analysis in 2 Minutes
                      </Button>
                      <Typography variant="body2" sx={{ 
                        color: 'rgba(249, 250, 251, 0.8)', 
                        mt: 1.5, 
                        textAlign: 'center',
                        fontSize: '0.9rem'
                      }}>
                        Takes 2 minutes. No credit card required.
                      </Typography>
                    </Box>
                  </Zoom>
                  <Zoom in timeout={2200}>
                    <Button
                      variant="outlined"
                      size="large"
                      startIcon={<PlayArrow />}
                      sx={{
                        borderColor: 'rgba(192, 132, 252, 0.6)',
                        borderWidth: '2px',
                        color: '#C084FC',
                        fontWeight: 700,
                        textTransform: 'none',
                        px: { xs: 4, md: 6 },
                        py: { xs: 2.5, md: 3.5 },
                        borderRadius: 3,
                        fontSize: { xs: '1rem', md: '1.2rem' },
                        backdropFilter: 'blur(10px)',
                        '&:hover': {
                          borderColor: '#C084FC',
                          backgroundColor: 'rgba(192, 132, 252, 0.15)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 10px 30px rgba(192, 132, 252, 0.3)',
                        },
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                      }}
                      onClick={handleWatchDemo}
                    >
                      ▶️ Watch 90-Second Demo
                    </Button>
                  </Zoom>
                </Stack>

                {/* Trust Line */}
                <Typography variant="body1" sx={{ 
                  color: '#10B981', 
                  mb: 3, 
                  textAlign: 'center',
                  fontSize: { xs: '1rem', md: '1.2rem' },
                  fontWeight: 600,
                }}>
                  ✅ No credit card required • ✅ GDPR-Compliant • ✅ Cancel anytime
                </Typography>
              </Grid>
            </Grid>
          </Fade>
        </Container>
      </Box>
      
      {/* Social Proof Bar */}
      <Box sx={{ 
        background: gradients.darkSection,
        py: { xs: 6, md: 10 }, 
        borderTop: '1px solid rgba(192, 132, 252, 0.2)',
        borderBottom: '1px solid rgba(192, 132, 252, 0.2)',
        position: 'relative',
        zIndex: 2,
        boxShadow: 'inset 0 1px 30px rgba(124, 58, 237, 0.1)',
      }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} justifyContent="center" alignItems="center">
            <Grid item xs={6} sm={3} textAlign="center">
              <Zoom in timeout={400}>
                <Box>
                  <Typography variant="h3" sx={{ 
                    background: gradients.ctaPrimary,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontWeight: 900,
                    fontSize: { xs: '2rem', md: '3rem' },
                    mb: 1.5,
                    textShadow: '0 4px 20px rgba(192, 132, 252, 0.3)',
                  }}>
                    $12M+
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#E5E7EB', 
                    fontWeight: 600,
                    fontSize: { xs: '0.9rem', md: '1rem' },
                  }}>
                    ad spend saved
                  </Typography>
                </Box>
              </Zoom>
            </Grid>
            <Grid item xs={6} sm={3} textAlign="center">
              <Zoom in timeout={600}>
                <Box>
                  <Typography variant="h3" sx={{ 
                    background: gradients.ctaPrimary,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontWeight: 900,
                    fontSize: { xs: '2rem', md: '3rem' },
                    mb: 1.5,
                  }}>
                    300%
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#E5E7EB', 
                    fontWeight: 600,
                    fontSize: { xs: '0.9rem', md: '1rem' },
                  }}>
                    avg ROAS lift (90 days)
                  </Typography>
                </Box>
              </Zoom>
            </Grid>
            <Grid item xs={6} sm={3} textAlign="center">
              <Zoom in timeout={800}>
                <Box>
                  <Typography variant="h3" sx={{ 
                    background: gradients.ctaPrimary,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontWeight: 900,
                    fontSize: { xs: '2rem', md: '3rem' },
                    mb: 1.5,
                  }}>
                    500+
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#E5E7EB', 
                    fontWeight: 600,
                    fontSize: { xs: '0.9rem', md: '1rem' },
                  }}>
                    agencies trust us
                  </Typography>
                </Box>
              </Zoom>
            </Grid>
            <Grid item xs={6} sm={3} textAlign="center">
              <Zoom in timeout={1000}>
                <Box>
                  <Typography variant="h3" sx={{ 
                    background: gradients.ctaPrimary,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontWeight: 900,
                    fontSize: { xs: '2rem', md: '3rem' },
                    mb: 1.5,
                  }}>
                    10,000+
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#E5E7EB', 
                    fontWeight: 600,
                    fontSize: { xs: '0.9rem', md: '1rem' },
                  }}>
                    ads analyzed daily
                  </Typography>
                </Box>
              </Zoom>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* 9 Proprietary Engines Section */}
      <Box sx={{ 
        background: gradients.darkSectionAlt,
        py: { xs: 10, md: 14 }, 
        color: '#F9FAFB',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 3,
            fontSize: { xs: '2.8rem', md: '4rem' },
            color: '#F9FAFB',
            letterSpacing: '-0.02em'
          }}>
              The 9-Tool Workflow
          </Typography>
          <Typography variant="h3" sx={{ 
            textAlign: 'center', 
            fontWeight: 700, 
            mb: 4,
            fontSize: { xs: '1.8rem', md: '2.5rem' },
            color: '#C084FC'
          }}>
            Your Ad, Perfected by 9 Specialized Proprietary Engines
          </Typography>
          <Typography variant="h5" sx={{ 
            textAlign: 'center', 
            color: '#E5E7EB', 
            mb: 8,
            fontSize: { xs: '1.3rem', md: '1.6rem' },
            maxWidth: '900px',
            mx: 'auto',
            opacity: 0.9,
            lineHeight: 1.5
          }}>
            Paste your ad copy — AdCopySurge runs it through nine advanced engines that analyze compliance, psychology, and ROI potential, producing a compliant, conversion-optimized version in under 2 minutes.
          </Typography>
          
          {/* Visual Flow */}
          <Box sx={{ textAlign: 'center', mb: 10 }}>
            <Paper sx={{
              background: gradients.glassCardPurple,
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(192, 132, 252, 0.3)',
              borderRadius: 4,
              p: { xs: 4, md: 6 },
              maxWidth: '800px',
              mx: 'auto',
              boxShadow: '0 15px 40px rgba(124, 58, 237, 0.2)'
            }}>
              <Typography variant="h4" sx={{ 
                color: '#F9FAFB', 
                fontWeight: 700,
                mb: 4,
                fontSize: { xs: '1.5rem', md: '2rem' }
              }}>
                Your Ad Copy → 9 Specialized Engines → (Optimized Copy + A/B/C Variants)
              </Typography>
            </Paper>
          </Box>
          
          {/* The 9 Engines Grid */}
          <Grid container spacing={4}>
            {[
              { name: 'Ad Copy Analyzer', icon: <Analytics />, desc: 'Deep-dive structural analysis' },
              { name: 'Compliance Checker', icon: <Security />, desc: 'Platform policy validation' },
              { name: 'Psychology Scorer', icon: <Lightbulb />, desc: 'Behavioral trigger assessment' },
              { name: 'A/B/C Variant Generator', icon: <CompareArrows />, desc: 'Strategic testing variants' },
              { name: 'ROI Optimizer', icon: <TrendingUp />, desc: 'Revenue impact prediction' },
              { name: 'Industry Optimizer', icon: <AutoAwesome />, desc: 'Sector-specific optimization' },
              { name: 'Legal Risk Scanner', icon: <CheckCircle />, desc: 'Regulatory compliance check' },
              { name: 'Brand Voice Engine', icon: <Star />, desc: 'Tone and messaging alignment' },
              { name: 'Performance Forensics', icon: <Speed />, desc: 'Conversion bottleneck detection' }
            ].map((engine, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Paper sx={{ 
                  background: 'linear-gradient(135deg, #ffffff 0%, #faf7ff 100%)',
                  border: '2px solid rgba(124, 58, 237, 0.1)',
                  borderRadius: 4,
                  p: 4,
                  height: '100%',
                  textAlign: 'center',
                  boxShadow: '0 10px 40px rgba(124, 58, 237, 0.08)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 20px 60px rgba(124, 58, 237, 0.15)',
                    borderColor: 'rgba(124, 58, 237, 0.2)'
                  }
                }}>
                  <Box sx={{ 
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    background: gradients.purplePrimary,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    boxShadow: '0 8px 25px rgba(124, 58, 237, 0.3)'
                  }}>
                    {React.cloneElement(engine.icon, { 
                      sx: { color: 'white', fontSize: '1.8rem' }
                    })}
                  </Box>
                  <Typography variant="h6" sx={{ 
                    color: '#1e1b4b', 
                    fontWeight: 700, 
                    mb: 2,
                    fontSize: '1.1rem'
                  }}>
                    {engine.name}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: '#6b7280',
                    fontSize: '0.95rem'
                  }}>
                    {engine.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
          
          {/* CTA */}
          <Box sx={{ textAlign: 'center', mt: 8 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleFreeScan}
              sx={{
                background: gradients.ctaPrimary,
                color: '#F9FAFB',
                fontSize: { xs: '1.2rem', md: '1.4rem' },
                px: { xs: 6, md: 10 },
                py: { xs: 2.5, md: 3.5 },
                borderRadius: 3,
                fontWeight: 800,
                textTransform: 'none',
                boxShadow: '0 15px 50px rgba(192, 132, 252, 0.4)',
                border: '2px solid rgba(255, 255, 255, 0.2)',
                '&:hover': {
                  background: gradients.ctaHover,
                  transform: 'translateY(-4px)',
                  boxShadow: '0 20px 60px rgba(192, 132, 252, 0.6)',
                },
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              Get Your Free Ad Analysis in 2 Minutes
            </Button>
          </Box>
        </Container>
      </Box>
      
      {/* Transformation Section */}
      <Box sx={{ 
        background: gradients.landingHero,
        py: { xs: 10, md: 14 }, 
        color: 'white',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 3,
            fontSize: { xs: '2.8rem', md: '4rem' },
            letterSpacing: '-0.02em'
          }}>
              See The Transformation
          </Typography>
          <Typography variant="h5" sx={{ 
            textAlign: 'center', 
            color: 'rgba(255,255,255,0.9)', 
            mb: 10,
            fontSize: { xs: '1.4rem', md: '1.8rem' },
            maxWidth: '900px',
            mx: 'auto',
            lineHeight: 1.5
          }}>
            Upload your ad. Get forensic analysis. Deploy optimized alternatives. See results in 2 minutes or less.
          </Typography>
          
          <Grid container spacing={6} alignItems="stretch">
            {/* Before */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ 
                background: 'rgba(75, 85, 99, 0.1)', 
                backdropFilter: 'blur(10px)',
                border: '2px solid rgba(75, 85, 99, 0.3)',
                borderRadius: 4,
                p: 6,
                height: '100%',
                textAlign: 'center'
              }}>
                <Typography variant="h4" sx={{ color: '#9ca3af', fontWeight: 700, mb: 4 }}>
                  BEFORE
                </Typography>
                <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.8)', mb: 4 }}>
                  Uncertain, reactive, inconsistent results.
                </Typography>
                
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>CTR:</Typography>
                    <Typography variant="h6" sx={{ color: '#ef4444' }}>0.8%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>CPC:</Typography>
                    <Typography variant="h6" sx={{ color: '#ef4444' }}>$2.50</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>ROAS:</Typography>
                    <Typography variant="h6" sx={{ color: '#ef4444' }}>2.1x</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>Result:</Typography>
                    <Typography variant="h6" sx={{ color: '#ef4444' }}>❌ Losing $2,340/month</Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            
            {/* After */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ 
                background: gradients.purplePrimary,
                border: '2px solid #a855f7',
                borderRadius: 4,
                p: 6,
                height: '100%',
                textAlign: 'center',
                boxShadow: '0 20px 60px rgba(124, 58, 237, 0.4)',
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: -2,
                  left: -2,
                  right: -2,
                  bottom: -2,
                  background: gradients.primaryLight,
                  borderRadius: 4,
                  zIndex: -1
                }
              }}>
                <Typography variant="h4" sx={{ color: 'white', fontWeight: 800, mb: 4 }}>
                  AFTER
                </Typography>
                <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.95)', mb: 4 }}>
                  Strategic, confident, predictably profitable.
                </Typography>
                
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>CTR:</Typography>
                    <Typography variant="h6" sx={{ color: '#fbbf24' }}>2.4%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>CPC:</Typography>
                    <Typography variant="h6" sx={{ color: '#fbbf24' }}>$1.80</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>ROAS:</Typography>
                    <Typography variant="h6" sx={{ color: '#fbbf24' }}>6.8x</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>Result:</Typography>
                    <Typography variant="h6" sx={{ color: '#F9F6EE' }}>✅ Generating $8,120/month profit</Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
          
          {/* Real Testimonial */}
          <Box sx={{ textAlign: 'center', mt: 6 }}>
            <Paper sx={{
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 4,
              p: 4,
              maxWidth: '600px',
              mx: 'auto'
            }}>
              <Typography variant="body1" sx={{ 
                color: 'rgba(255,255,255,0.9)', 
                fontSize: '1.1rem',
                fontStyle: 'italic',
                mb: 3,
                lineHeight: 1.6
              }}>
                "AdCopySurge helped us reduce CPC from $3.80 to $2.10 and lift CTR by 78%. The compliance scanner alone saved us from two potential account suspensions."
              </Typography>
              <Typography variant="body2" sx={{ 
                color: '#f59e0b', 
                fontWeight: 600
              }}>
                — Alex K., FinTech Startup ($500K/Q spend)
              </Typography>
            </Paper>
          </Box>
          
          <Box sx={{ textAlign: 'center', mt: 6 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleFreeScan}
              sx={{
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                color: '#7c3aed',
                fontSize: '1.3rem',
                px: 8,
                py: 3,
                fontWeight: 800,
                textTransform: 'none',
                borderRadius: 4,
                border: '2px solid rgba(255, 255, 255, 0.3)',
                boxShadow: '0 12px 40px rgba(255, 255, 255, 0.2)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #faf7ff 0%, #f3e8ff 100%)',
                  transform: 'translateY(-3px)',
                  boxShadow: '0 16px 50px rgba(255, 255, 255, 0.3)',
                  color: '#6d28d9'
                },
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              See How Much You're Leaving on the Table — Try It Free
            </Button>
          </Box>
        </Container>
      </Box>
      
      {/* How It Works Section */}
      <Box sx={{ 
        background: gradients.darkSection,
        py: { xs: 10, md: 14 }, 
        color: '#F9FAFB',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 3,
            fontSize: { xs: '2.8rem', md: '4rem' },
            color: '#F9FAFB',
            letterSpacing: '-0.02em'
          }}>
              How It Works: 3 Simple Steps
          </Typography>
          <Typography variant="h5" sx={{ 
            textAlign: 'center', 
            color: '#E5E7EB', 
            mb: 12,
            fontSize: { xs: '1.4rem', md: '1.8rem' },
            maxWidth: '800px',
            mx: 'auto',
            opacity: 0.9,
          }}>
            From struggling ad to optimized winner in under 2 minutes.
          </Typography>
          
          <Grid container spacing={6} justifyContent="center">
            {/* Step 1 */}
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ 
                  width: 100, 
                  height: 100, 
                  borderRadius: '50%', 
                  background: gradients.purplePrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 4,
                  boxShadow: '0 10px 30px rgba(124, 58, 237, 0.3)',
                  border: '3px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 800 }}>1</Typography>
                </Box>
                <Typography variant="h5" sx={{ 
                  fontWeight: 700, 
                  mb: 2,
                  color: '#F9FAFB'
                }}>Paste Your Ad (10s)</Typography>
                <Typography variant="body1" sx={{ 
                  color: '#E5E7EB',
                  fontSize: '1.1rem',
                  lineHeight: 1.6,
                  opacity: 0.9,
                }}>
                  Paste your underperforming ad copy.
                </Typography>
              </Box>
            </Grid>
            
            {/* Step 2 */}
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ 
                  width: 100, 
                  height: 100, 
                  borderRadius: '50%', 
                  background: gradients.purplePrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 4,
                  boxShadow: '0 10px 30px rgba(124, 58, 237, 0.3)',
                  border: '3px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 800 }}>2</Typography>
                </Box>
                <Typography variant="h5" sx={{ 
                  fontWeight: 700, 
                  mb: 2,
                  color: '#F9FAFB'
                }}>Get Your Analysis (50s)</Typography>
                <Typography variant="body1" sx={{ 
                  color: '#E5E7EB',
                  fontSize: '1.1rem',
                  lineHeight: 1.6,
                  opacity: 0.9,
                }}>
                  Adcopysurge scans for 47 optimization factors: compliance, psychology, positioning, competition.
                </Typography>
              </Box>
            </Grid>
            
            {/* Step 3 */}
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ 
                  width: 100, 
                  height: 100, 
                  borderRadius: '50%', 
                  background: gradients.purplePrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 4,
                  boxShadow: '0 10px 30px rgba(124, 58, 237, 0.3)',
                  border: '3px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 800 }}>3</Typography>
                </Box>
                <Typography variant="h5" sx={{ 
                  fontWeight: 700, 
                  mb: 2,
                  color: '#F9FAFB'
                }}>Deploy Optimized Ads (2–3m)</Typography>
                <Typography variant="body1" sx={{ 
                  color: '#E5E7EB',
                  fontSize: '1.1rem',
                  lineHeight: 1.6,
                  opacity: 0.9,
                }}>
                  Get strategic A/B/C test variants: benefit-focused, problem-focused, and story-driven approaches. Copy → paste → test → profit.
                </Typography>
              </Box>
            </Grid>
          </Grid>
          
          {/* Timeline */}
          <Box sx={{ textAlign: 'center', mt: 10 }}>
            <Paper sx={{
              background: gradients.glassCardPurple,
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(124, 58, 237, 0.2)',
              borderRadius: 4,
              p: 4,
              display: 'inline-block',
              boxShadow: '0 10px 30px rgba(124, 58, 237, 0.15)'
            }}>
              <Typography variant="h5" sx={{ 
                color: '#C084FC', 
                fontWeight: 800, 
                fontSize: '1.4rem',
                mb: 1
              }}>
                ⏱ Total Timeline
              </Typography>
              <Typography variant="h6" sx={{ 
                color: '#F9FAFB', 
                fontWeight: 700
              }}>
                Struggling Ad → Profitable Campaign = 2 minutes
              </Typography>
            </Paper>
          </Box>
          
          {/* One-Line Summary CTA */}
          <Box sx={{ textAlign: 'center', mt: 8 }}>
            <Typography variant="h5" sx={{ 
              color: '#C084FC', 
              fontWeight: 700,
              mb: 4,
              fontSize: { xs: '1.3rem', md: '1.5rem' }
            }}>
              In 120 seconds, get 3 psychology-backed, compliant variants and ROI predictions.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleFreeScan}
              sx={{
                background: gradients.ctaPrimary,
                color: '#F9FAFB',
                fontSize: { xs: '1.1rem', md: '1.3rem' },
                px: { xs: 5, md: 8 },
                py: { xs: 2, md: 3 },
                borderRadius: 3,
                fontWeight: 700,
                textTransform: 'none',
                boxShadow: '0 12px 40px rgba(192, 132, 252, 0.4)',
                border: '2px solid rgba(255, 255, 255, 0.2)',
                '&:hover': {
                  background: gradients.ctaHover,
                  transform: 'translateY(-3px)',
                  boxShadow: '0 16px 50px rgba(192, 132, 252, 0.6)',
                },
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              Get Your Free Ad Analysis in 2 Minutes
            </Button>
          </Box>
        </Container>
      </Box>
      
      {/* Strategic A/B/C Testing Section */}
      <Box sx={{ 
        background: gradients.darkSectionAlt,
        py: { xs: 10, md: 14 }, 
        color: '#F9FAFB',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 3,
            fontSize: { xs: '2.8rem', md: '4rem' },
            color: '#F9FAFB',
            letterSpacing: '-0.02em'
          }}>
              Strategic A/B/C Testing: Know What Works Before You Spend
          </Typography>
          <Typography variant="h5" sx={{ 
            textAlign: 'center', 
            color: '#E5E7EB', 
            mb: 10,
            fontSize: { xs: '1.4rem', md: '1.8rem' },
            maxWidth: '900px',
            mx: 'auto',
            opacity: 0.9,
          }}>
            Stop running random ad tests. Generate 3 scientifically-designed variants—each targeting different psychological triggers.
          </Typography>
          
          {/* A/B/C Comparison Table */}
          <Paper sx={{
            background: 'linear-gradient(135deg, #ffffff 0%, #faf7ff 100%)',
            border: '3px solid rgba(124, 58, 237, 0.2)',
            borderRadius: 4,
            p: { xs: 4, md: 6 },
            mb: 10,
            boxShadow: '0 20px 60px rgba(124, 58, 237, 0.15)',
            overflow: 'hidden'
          }}>
            <Grid container spacing={0}>
              {/* Version A */}
              <Grid item xs={12} md={4}>
                <Box sx={{ 
                  textAlign: 'center',
                  p: { xs: 3, md: 4 },
                  height: '100%',
                  borderRight: { md: '2px solid rgba(124, 58, 237, 0.1)' },
                  borderBottom: { xs: '2px solid rgba(124, 58, 237, 0.1)', md: 'none' }
                }}>
                  <Typography variant="h5" sx={{ 
                    color: '#7c3aed', 
                    fontWeight: 800, 
                    mb: 2,
                    fontSize: { xs: '1.3rem', md: '1.5rem' }
                  }}>
                    VERSION A
                  </Typography>
                  <Typography variant="h6" sx={{ 
                    color: '#1e1b4b', 
                    fontWeight: 700, 
                    mb: 3
                  }}>
                    Benefit-Focused
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#4b5563', 
                    mb: 3,
                    lineHeight: 1.6
                  }}>
                    Appeals to aspirations and desired outcomes
                  </Typography>
                  <Box sx={{ 
                    background: 'rgba(124, 58, 237, 0.05)',
                    borderRadius: 3,
                    p: 3,
                    mb: 3
                  }}>
                    <Typography variant="body2" sx={{ 
                      color: '#7c3aed', 
                      fontWeight: 700,
                      mb: 1
                    }}>
                      Best for:
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      color: '#4b5563',
                      fontSize: '0.9rem',
                      lineHeight: 1.5
                    }}>
                      • Solution-seekers<br/>
                      • Warm leads<br/>
                      • Known problems
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              {/* Version B */}
              <Grid item xs={12} md={4}>
                <Box sx={{ 
                  textAlign: 'center',
                  p: { xs: 3, md: 4 },
                  height: '100%',
                  borderRight: { md: '2px solid rgba(124, 58, 237, 0.1)' },
                  borderBottom: { xs: '2px solid rgba(124, 58, 237, 0.1)', md: 'none' }
                }}>
                  <Typography variant="h5" sx={{ 
                    color: '#7c3aed', 
                    fontWeight: 800, 
                    mb: 2,
                    fontSize: { xs: '1.3rem', md: '1.5rem' }
                  }}>
                    VERSION B
                  </Typography>
                  <Typography variant="h6" sx={{ 
                    color: '#1e1b4b', 
                    fontWeight: 700, 
                    mb: 3
                  }}>
                    Problem-Focused
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#4b5563', 
                    mb: 3,
                    lineHeight: 1.6
                  }}>
                    Identifies with pain points and frustrations
                  </Typography>
                  <Box sx={{ 
                    background: 'rgba(124, 58, 237, 0.05)',
                    borderRadius: 3,
                    p: 3,
                    mb: 3
                  }}>
                    <Typography variant="body2" sx={{ 
                      color: '#7c3aed', 
                      fontWeight: 700,
                      mb: 1
                    }}>
                      Best for:
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      color: '#4b5563',
                      fontSize: '0.9rem',
                      lineHeight: 1.5
                    }}>
                      • Pain-aware audiences<br/>
                      • High urgency<br/>
                      • Immediate solutions
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              {/* Version C */}
              <Grid item xs={12} md={4}>
                <Box sx={{ 
                  textAlign: 'center',
                  p: { xs: 3, md: 4 },
                  height: '100%'
                }}>
                  <Typography variant="h5" sx={{ 
                    color: '#7c3aed', 
                    fontWeight: 800, 
                    mb: 2,
                    fontSize: { xs: '1.3rem', md: '1.5rem' }
                  }}>
                    VERSION C
                  </Typography>
                  <Typography variant="h6" sx={{ 
                    color: '#1e1b4b', 
                    fontWeight: 700, 
                    mb: 3
                  }}>
                    Story-Driven
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: '#4b5563', 
                    mb: 3,
                    lineHeight: 1.6
                  }}>
                    Creates emotional connection through narrative
                  </Typography>
                  <Box sx={{ 
                    background: 'rgba(124, 58, 237, 0.05)',
                    borderRadius: 3,
                    p: 3,
                    mb: 3
                  }}>
                    <Typography variant="body2" sx={{ 
                      color: '#7c3aed', 
                      fontWeight: 700,
                      mb: 1
                    }}>
                      Best for:
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      color: '#4b5563',
                      fontSize: '0.9rem',
                      lineHeight: 1.5
                    }}>
                      • Building trust<br/>
                      • Cold traffic<br/>
                      • Brand awareness
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Process Flow */}
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography variant="h4" sx={{ 
              color: '#C084FC', 
              fontWeight: 800,
              mb: 4,
              fontSize: { xs: '1.8rem', md: '2.2rem' }
            }}>
              Generate all 3 variants in 120 seconds → Test on your platform → Use winner → Rinse and repeat
            </Typography>
          </Box>
          
          {/* Testimonial */}
          <Paper sx={{ 
            background: gradients.glassCardPurple,
            backdropFilter: 'blur(10px)',
            border: '2px solid rgba(192, 132, 252, 0.3)',
            borderRadius: 4,
            p: { xs: 4, md: 6 },
            textAlign: 'center',
            mb: 8,
            boxShadow: '0 15px 40px rgba(124, 58, 237, 0.2)'
          }}>
            <Typography variant="h6" sx={{ 
              color: '#F9FAFB', 
              fontWeight: 600,
              mb: 2,
              fontSize: { xs: '1.1rem', md: '1.3rem' },
              fontStyle: 'italic',
              lineHeight: 1.6
            }}>
              "We tested all 3 variants. Version B (problem-focused) outperformed our original by 147%. Now we know our audience responds to pain points."
            </Typography>
            <Typography variant="body1" sx={{ 
              color: '#E5E7EB', 
              fontWeight: 600,
              fontSize: '1rem'
            }}>
              — Marketing Director, SaaS Company
            </Typography>
          </Paper>
          
          {/* CTA */}
          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleFreeScan}
              sx={{
                background: gradients.ctaPrimary,
                color: '#F9FAFB',
                fontSize: { xs: '1.2rem', md: '1.4rem' },
                px: { xs: 6, md: 10 },
                py: { xs: 2.5, md: 3.5 },
                borderRadius: 3,
                fontWeight: 800,
                textTransform: 'none',
                boxShadow: '0 15px 50px rgba(192, 132, 252, 0.4)',
                border: '2px solid rgba(255, 255, 255, 0.2)',
                '&:hover': {
                  background: gradients.ctaHover,
                  transform: 'translateY(-4px)',
                  boxShadow: '0 20px 60px rgba(192, 132, 252, 0.6)',
                },
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              Get Your Free Ad Analysis in 2 Minutes
            </Button>
            <Typography variant="body2" sx={{ 
              color: 'rgba(249, 250, 251, 0.8)', 
              mt: 2, 
              textAlign: 'center',
              fontSize: '0.9rem'
            }}>
              Takes 2 minutes. No credit card required.
            </Typography>
          </Box>
        </Container>
      </Box>
      
      {/* Social Proof Section */}
      <Box sx={{ 
        background: gradients.darkSectionAlt,
        py: { xs: 8, md: 12 }, 
        color: '#F9FAFB',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 3,
            fontSize: { xs: '2.5rem', md: '3.5rem' },
            color: '#F9FAFB',
            letterSpacing: '-0.02em',
          }}>
              Success Stories: Real Results From Real Companies
          </Typography>
          <Typography variant="h6" sx={{ 
            textAlign: 'center', 
            color: '#E5E7EB', 
            mb: 8,
            fontSize: '1.2rem',
            maxWidth: '600px',
            mx: 'auto',
            opacity: 0.9,
          }}>
            See how companies transformed their ad performance with data-driven optimization.
          </Typography>
          
          <Grid container spacing={4} sx={{ mt: 2 }}>
            {socialProofData.map((proof, index) => (
              <React.Fragment key={index}>
                <Grid item xs={12} sm={6} md={4}>
                  <Paper sx={{ 
                    background: 'linear-gradient(135deg, #ffffff 0%, #faf7ff 100%)',
                    border: '2px solid rgba(124, 58, 237, 0.1)',
                    borderRadius: 4,
                    p: 4,
                    height: '100%',
                    boxShadow: '0 10px 40px rgba(124, 58, 237, 0.08)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 20px 60px rgba(124, 58, 237, 0.15)',
                      borderColor: 'rgba(124, 58, 237, 0.2)'
                    }
                  }}>
                    <Typography variant="body2" sx={{ 
                      color: '#7c3aed', 
                      fontWeight: 700, 
                      mb: 2,
                      fontSize: '0.9rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      {proof.type}
                    </Typography>
                    <Typography variant="h6" sx={{ 
                      color: '#1e1b4b', 
                      fontWeight: 700, 
                      mb: 2,
                      fontSize: '1.1rem'
                    }}>
                      {proof.company}
                    </Typography>
                    <Typography variant="body1" sx={{ 
                      color: '#4b5563', 
                      mb: 3,
                      lineHeight: 1.6,
                      fontSize: '1rem'
                    }}>
                      {proof.result}
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      color: '#9ca3af',
                      fontStyle: 'italic'
                    }}>
                      — {proof.name}
                    </Typography>
                  </Paper>
                </Grid>
              </React.Fragment>
            ))}
          </Grid>
        </Container>
      </Box>
      

      {/* Trust Signals Section */}
      <Box sx={{ 
        background: gradients.darkSectionAlt,
        position: 'relative',
        zIndex: 2
      }}>
        <TrustSignals />
      </Box>

      {/* Pricing Section */}
      <Box sx={{ 
        background: gradients.darkSection,
        py: { xs: 10, md: 14 }, 
        color: '#F9FAFB',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 3,
            fontSize: { xs: '2.8rem', md: '4rem' },
            color: '#F9FAFB',
            letterSpacing: '-0.02em'
          }}>
             Choose Your Growth Plan
          </Typography>
          <Typography variant="h5" sx={{ 
            textAlign: 'center', 
            color: '#E5E7EB', 
            mb: 2,
            fontSize: { xs: '1.4rem', md: '1.8rem' },
            maxWidth: '800px',
            mx: 'auto',
            opacity: 0.9,
          }}>
            You've seen the difference it makes,
          </Typography>
          
          <Typography variant="h4" sx={{ 
            textAlign: 'center', 
            color: '#F9FAFB', 
            mb: 8,
            fontSize: { xs: '1.6rem', md: '2rem' },
            maxWidth: '800px',
            mx: 'auto',
            fontWeight: 700,
          }}>
            Choose Your Plan or Start Free — See Results in 2 Minutes
          </Typography>
          
          {/* Pricing Table */}
          <PricingTable 
            plans={pricingData}
            onPlanSelect={(plan) => {
              if (plan.name.includes('Free')) {
                handleFreeScan();
              } else {
                handleFreeScan(); // For now, all plans lead to registration/analysis
              }
            }}
            isYearly={isYearly}
            setIsYearly={setIsYearly}
          />
          
          {/* Guarantee */}
          <Box sx={{ 
            textAlign: 'center', 
            mt: 10,
            p: 6,
            background: gradients.glassCardPurple,
            backdropFilter: 'blur(10px)',
            borderRadius: 4,
            border: '2px solid rgba(168, 85, 247, 0.2)',
            boxShadow: '0 15px 40px rgba(168, 85, 247, 0.1)'
          }}>
            <Typography variant="h5" sx={{ 
              fontWeight: 700, 
              mb: 3, 
              color: '#7c3aed',
              fontSize: '1.3rem'
            }}>
              💯 If AdCopySurge doesn't pay for itself in 30 days, we refund you and personally audit your next campaign free.
            </Typography>
            <Typography variant="body1" sx={{ 
              color: '#6b7280',
              fontWeight: 500
            }}>
              🔒 Secure payment • 💳 Cancel anytime • 🔄 Money-back guarantee
            </Typography>
          </Box>
        </Container>
      </Box>
      
      {/* Built for Every Role Section */}
      <Box sx={{ 
        background: gradients.landingHero,
        py: { xs: 10, md: 12 }, 
        color: 'white',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h2" sx={{ 
            textAlign: 'center', 
            fontWeight: 800, 
            mb: 8,
            color: 'white',
            fontSize: { xs: '2.8rem', md: '4rem' },
            letterSpacing: '-0.02em'
          }}>
                Built For Every Role
          </Typography>
          
          <Grid container spacing={4}>
            {roleMessages.map((role, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper sx={{ 
                  background: gradients.glassCardPurple,
                  backdropFilter: 'blur(20px)',
                  border: '2px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: 4,
                  p: 6,
                  textAlign: 'center',
                  height: '100%',
                  boxShadow: '0 15px 40px rgba(0, 0, 0, 0.2)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
                  }
                }}>
                  <Typography variant="h5" sx={{ 
                    color: 'white', 
                    fontWeight: 700, 
                    mb: 3,
                    fontSize: '1.3rem'
                  }}>
                    For {role.role}:
                  </Typography>
                  <Typography variant="body1" sx={{ 
                    color: 'rgba(255,255,255,0.95)',
                    fontSize: '1.1rem',
                    lineHeight: 1.6
                  }}>
                    {role.message}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
      
      {/* Trust & Security Section */}
      <Box sx={{ 
        background: gradients.darkSection,
        py: { xs: 8, md: 12 }, 
        color: '#F9FAFB',
        position: 'relative',
        zIndex: 2,
        borderTop: '1px solid rgba(192, 132, 252, 0.2)'
      }}>
        <Container maxWidth="lg">
          <Typography variant="h3" sx={{ 
            textAlign: 'center',
            fontWeight: 800, 
            mb: 6,
            fontSize: { xs: '2rem', md: '2.5rem' },
            color: '#F9FAFB',
            letterSpacing: '-0.02em'
          }}>
            🔒 Trusted by 500+ Marketing Teams — Enterprise-Grade Security
          </Typography>
          
          <Grid container spacing={4} justifyContent="center">
            <Grid item xs={12} sm={6} md={3} textAlign="center">
              <Typography variant="body1" sx={{ 
                color: '#10B981', 
                fontWeight: 600,
                fontSize: '1.1rem'
              }}>
                ✅ GDPR-Compliant Data Handling
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3} textAlign="center">
              <Typography variant="body1" sx={{ 
                color: '#10B981', 
                fontWeight: 600,
                fontSize: '1.1rem'
              }}>
                ✅ 99.9% Uptime SLA
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3} textAlign="center">
              <Typography variant="body1" sx={{ 
                color: '#10B981', 
                fontWeight: 600,
                fontSize: '1.1rem'
              }}>
                ✅ Encrypted Data at Rest & in Transit
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3} textAlign="center">
              <Typography variant="body1" sx={{ 
                color: '#10B981', 
                fontWeight: 600,
                fontSize: '1.1rem'
              }}>
                ✅ SOC 2 Certification (Q2 2025)
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Final CTA - Stop Guessing Start Scaling */}
      <Box sx={{ 
        background: gradients.landingHero,
        py: { xs: 12, md: 16 }, 
        textAlign: 'center',
        color: 'white',
        position: 'relative',
        zIndex: 2
      }}>
        <Container maxWidth="lg">
          <Typography variant="h1" sx={{ 
            fontWeight: 900, 
            mb: 4,
            fontSize: { xs: '3rem', md: '5rem' },
            letterSpacing: '-0.03em',
            lineHeight: 1.1
          }}>
            Stop Guessing.{' '}
            <Box component="span" sx={{ 
              background: gradients.ctaPrimary,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Start Scaling.
            </Box>
          </Typography>
          
          <Typography variant="h4" sx={{ 
            mb: 8,
            fontSize: { xs: '1.5rem', md: '2rem' },
            color: 'rgba(255,255,255,0.95)',
            maxWidth: '800px',
            mx: 'auto',
            fontWeight: 600,
            lineHeight: 1.4
          }}>
            Join 500+ marketers who've stopped guessing and started scaling with psychology-driven ad optimization.
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            onClick={handleFreeScan}
            startIcon={<RocketLaunch />}
            sx={{
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              color: '#7c3aed',
              fontSize: { xs: '1.4rem', md: '1.8rem' },
              px: { xs: 8, md: 12 },
              py: { xs: 3, md: 4 },
              fontWeight: 900,
              textTransform: 'none',
              borderRadius: 4,
              border: '3px solid rgba(255, 255, 255, 0.3)',
              boxShadow: '0 15px 50px rgba(255, 255, 255, 0.3)',
              mb: 6,
              '&:hover': {
                background: 'linear-gradient(135deg, #faf7ff 0%, #f3e8ff 100%)',
                transform: 'translateY(-4px)',
                boxShadow: '0 20px 60px rgba(255, 255, 255, 0.4)',
                color: '#6d28d9'
              },
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            Stop Guessing. Start Scaling. Get Started Free in Under 2 Minutes.
          </Button>
          
          <Typography variant="h6" sx={{ 
            color: 'rgba(255,255,255,0.9)',
            fontSize: { xs: '1.1rem', md: '1.3rem' },
            fontWeight: 600
          }}>
            GDPR-Compliant • Cancel Anytime
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;