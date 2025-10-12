import React from 'react';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Avatar,
  Stack,
  Divider,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  Psychology,
  Security,
  Speed,
  People
} from '@mui/icons-material';

const About = () => {
  const theme = useTheme();
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  
  const values = [
    {
      icon: <Analytics />,
      title: "Data-Driven Results",
      description: "Every recommendation is backed by proven marketing intelligence and performance data."
    },
    {
      icon: <Speed />,
      title: "Lightning Fast",
      description: "Get comprehensive analysis and optimization suggestions in seconds, not hours."
    },
    {
      icon: <Security />,
      title: "Privacy First", 
      description: "Your campaigns and data remain completely private and secure with enterprise-grade protection."
    },
    {
      icon: <Psychology />,
      title: "Psychology-Focused",
      description: "Our tools understand what drives human behavior and purchasing decisions."
    }
  ];

  const team = [
    {
      name: "Alex Johnson",
      role: "Founder & CEO",
      initials: "AJ",
      bio: "Former marketing director at 3 Fortune 500 companies. Built AdCopySurge after seeing teams waste millions on underperforming campaigns."
    },
    {
      name: "Sarah Martinez",
      role: "Head of Product",
      initials: "SM", 
      bio: "Ex-Google product manager with 8 years optimizing advertising platforms. Expert in conversion psychology."
    },
    {
      name: "David Chen",
      role: "CTO",
      initials: "DC",
      bio: "Previously lead engineer at marketing automation companies. Specialist in real-time data processing and AI systems."
    },
    {
      name: "Maria Rodriguez",
      role: "Head of Customer Success",
      initials: "MR",
      bio: "Helped 500+ marketing teams improve their campaigns. Former agency owner who understands client needs."
    }
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Container maxWidth="lg" sx={{ py: 8 }}>
        {/* Hero Section */}
        <Box textAlign="center" sx={{ mb: 8 }}>
          <Typography variant="h2" component="h1" sx={{ fontWeight: 800, mb: 3 }}>
            About AdCopySurge
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto', mb: 4 }}>
            We're on a mission to eliminate wasted ad spend and help marketers create campaigns that actually convert.
          </Typography>
          <Typography variant="body1" sx={{ maxWidth: 600, mx: 'auto', fontSize: '1.1rem', lineHeight: 1.7 }}>
            Founded in 2023, AdCopySurge was born from frustration with the marketing industry's trial-and-error approach. 
            We believe every marketing dollar should be backed by intelligence, not guesswork.
          </Typography>
        </Box>

        {/* Our Story */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 4, textAlign: 'center' }}>
            Our Story
          </Typography>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8, mb: 3 }}>
                After watching countless marketing teams burn through budgets on campaigns that looked good but performed poorly, 
                our founders realized the industry needed a better way.
              </Typography>
              <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8, mb: 3 }}>
                Traditional marketing tools focus on creation, not optimization. They help you make ads, 
                but don't tell you if those ads will actually drive revenue.
              </Typography>
              <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
                That's why we built AdCopySurge - the first comprehensive marketing intelligence platform that analyzes 
                every aspect of your campaigns before you spend a dollar.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={prefersReducedMotion ? {} : { opacity: 0, y: 30 }}
                whileInView={prefersReducedMotion ? {} : { opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                viewport={{ once: true }}
              >
                <Card 
                  elevation={3} 
                  sx={{ 
                    p: 4, 
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white'
                  }}
                >
                  <motion.div
                    initial={prefersReducedMotion ? {} : { scale: 0 }}
                    whileInView={prefersReducedMotion ? {} : { scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.4, type: "spring", stiffness: 200 }}
                    viewport={{ once: true }}
                  >
                    <TrendingUp sx={{ fontSize: 60, mb: 2, opacity: 0.9 }} />
                  </motion.div>
                  <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
                    $<CountUp end={50} duration={2.5} />M+
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    Ad Spend Optimized
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Our customers have collectively saved millions in wasted ad spend while increasing their ROI by an average of <CountUp end={300} duration={2} />%.
                  </Typography>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </Box>

        {/* Our Values */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 4, textAlign: 'center' }}>
            What We Stand For
          </Typography>
          <Grid container spacing={4}>
            {values.map((value, index) => (
              <Grid item xs={12} md={6} key={index}>
                <motion.div
                  initial={prefersReducedMotion ? {} : { opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={prefersReducedMotion ? {} : { opacity: 1, x: 0 }}
                  whileHover={prefersReducedMotion ? {} : { 
                    y: -8, 
                    transition: { type: "spring", stiffness: 300 } 
                  }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card 
                    elevation={2} 
                    sx={{ 
                      height: '100%', 
                      p: 3,
                      cursor: 'pointer',
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': {
                        boxShadow: '0 20px 40px rgba(37, 99, 235, 0.15)'
                      }
                    }}
                  >
                    <CardContent sx={{ p: 0 }}>
                      <Stack direction="row" spacing={2} alignItems="flex-start">
                        <motion.div
                          whileHover={prefersReducedMotion ? {} : { rotate: 360 }}
                          transition={{ duration: 0.6 }}
                        >
                          <Box
                            sx={{
                              p: 2,
                              borderRadius: 2,
                              backgroundColor: 'primary.main',
                              color: 'white'
                            }}
                          >
                            {React.cloneElement(value.icon, { sx: { fontSize: 24 } })}
                          </Box>
                        </motion.div>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                            {value.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {value.description}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Divider sx={{ my: 6 }} />

        {/* Team Section */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            Meet Our Team
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ textAlign: 'center', mb: 6 }}>
            Marketing veterans who've been in your shoes
          </Typography>
          <Grid container spacing={4}>
            {team.map((member, index) => (
              <Grid item xs={12} md={6} lg={3} key={index}>
                <motion.div
                  initial={prefersReducedMotion ? {} : { opacity: 0, y: 50 }}
                  whileInView={prefersReducedMotion ? {} : { opacity: 1, y: 0 }}
                  whileHover={prefersReducedMotion ? {} : { 
                    y: -10,
                    transition: { type: "spring", stiffness: 300 }
                  }}
                  transition={{ duration: 0.6, delay: index * 0.15 }}
                  viewport={{ once: true }}
                >
                  <Card 
                    elevation={2} 
                    sx={{ 
                      textAlign: 'center', 
                      p: 3,
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': {
                        boxShadow: '0 20px 40px rgba(37, 99, 235, 0.15)'
                      }
                    }}
                  >
                    <motion.div
                      whileHover={prefersReducedMotion ? {} : { scale: 1.1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <Avatar
                        sx={{
                          width: 80,
                          height: 80,
                          mx: 'auto',
                          mb: 2,
                          bgcolor: 'primary.main',
                          fontSize: '1.5rem',
                          fontWeight: 600
                        }}
                      >
                        {member.initials}
                      </Avatar>
                    </motion.div>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {member.name}
                    </Typography>
                    <Typography variant="subtitle2" color="primary.main" sx={{ mb: 2, fontWeight: 500 }}>
                      {member.role}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {member.bio}
                    </Typography>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Mission Statement */}
        <Box 
          sx={{ 
            textAlign: 'center',
            p: 6,
            borderRadius: 4,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}
        >
          <People sx={{ fontSize: 48, mb: 2, opacity: 0.9 }} />
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            Our Mission
          </Typography>
          <Typography variant="h6" sx={{ maxWidth: 600, mx: 'auto', opacity: 0.95, lineHeight: 1.6 }}>
            To eliminate wasted marketing spend by giving every marketer access to professional-grade 
            campaign intelligence, regardless of budget or company size.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default About;
