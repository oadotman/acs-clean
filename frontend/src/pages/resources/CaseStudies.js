import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  Button,
  Stack,
  Avatar,
  Chip,
  LinearProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tab,
  Tabs,
  Badge
} from '@mui/material';
import {
  TrendingUp,
  ExpandMore,
  AttachMoney,
  Speed,
  Security,
  Psychology,
  Business,
  Timeline,
  CheckCircle,
  Star,
  ArrowUpward,
  CompareArrows
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`case-study-tabpanel-${index}`}
      aria-labelledby={`case-study-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const CaseStudies = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const caseStudies = [
    {
      id: 1,
      company: "TechGadgets Pro",
      industry: "E-commerce",
      category: "E-commerce",
      logo: "🏪",
      description: "Leading electronics retailer transforms Facebook ad performance",
      challenge: "Facebook ads were getting rejected due to policy violations, wasting $10K+ monthly ad spend",
      solution: "Used Compliance Checker and Legal Risk Scanner to ensure all ads meet platform guidelines",
      results: {
        roasIncrease: 450,
        costReduction: 35,
        conversionIncrease: 280,
        timeframe: "90 days"
      },
      keyMetrics: [
        { label: "ROAS", before: "1.2x", after: "5.4x", improvement: "+350%" },
        { label: "CPM", before: "$12.50", after: "$8.10", improvement: "-35%" },
        { label: "Conversion Rate", before: "1.8%", after: "5.0%", improvement: "+178%" },
        { label: "Policy Approvals", before: "65%", after: "98%", improvement: "+51%" }
      ],
      toolsUsed: ["Compliance Checker", "Legal Risk Scanner", "A/B Test Generator"],
      testimonial: {
        text: "AdCopySurge saved us from constant policy violations. Our ROAS went from 1.2x to 5.4x in just 90 days!",
        author: "Maria Rodriguez",
        position: "Marketing Director"
      },
      featured: true
    },
    {
      id: 2,
      company: "CloudSync SaaS",
      industry: "Software",
      category: "SaaS",
      logo: "☁️",
      description: "B2B SaaS company increases enterprise customer acquisition",
      challenge: "Generic messaging wasn't resonating with enterprise customers, low conversion rates",
      solution: "Used ROI Copy Generator and Industry Optimizer to create premium positioning copy",
      results: {
        roasIncrease: 320,
        costReduction: 42,
        conversionIncrease: 185,
        timeframe: "60 days"
      },
      keyMetrics: [
        { label: "ROAS", before: "2.1x", after: "6.7x", improvement: "+219%" },
        { label: "CAC", before: "$450", after: "$260", improvement: "-42%" },
        { label: "Enterprise Leads", before: "12/mo", after: "34/mo", improvement: "+183%" },
        { label: "Trial-to-Paid", before: "8%", after: "23%", improvement: "+188%" }
      ],
      toolsUsed: ["ROI Copy Generator", "Industry Optimizer", "Psychology Scorer"],
      testimonial: {
        text: "The ROI-focused copy helped us attract enterprise customers who actually convert at premium pricing.",
        author: "James Chen",
        position: "Growth Lead"
      },
      featured: true
    },
    {
      id: 3,
      company: "FitLife Supplements",
      industry: "Health & Wellness",
      category: "E-commerce",
      logo: "💪",
      description: "Supplement brand navigates compliance while maximizing conversions",
      challenge: "Health claims were causing ad rejections and legal concerns across platforms",
      solution: "Leveraged Legal Risk Scanner and Brand Voice Engine for compliant yet compelling copy",
      results: {
        roasIncrease: 275,
        costReduction: 28,
        conversionIncrease: 156,
        timeframe: "45 days"
      },
      keyMetrics: [
        { label: "ROAS", before: "1.8x", after: "4.95x", improvement: "+175%" },
        { label: "Ad Approval Rate", before: "45%", after: "92%", improvement: "+104%" },
        { label: "Conversion Rate", before: "2.1%", after: "5.4%", improvement: "+157%" },
        { label: "Revenue/Visitor", before: "$2.40", after: "$6.80", improvement: "+183%" }
      ],
      toolsUsed: ["Legal Risk Scanner", "Brand Voice Engine", "Compliance Checker"],
      testimonial: {
        text: "Finally, we can make compelling claims about our products without worrying about ad rejection or legal issues.",
        author: "Sarah Kim",
        position: "Marketing Manager"
      },
      featured: false
    },
    {
      id: 4,
      company: "GrowthHacker Agency",
      industry: "Marketing Agency",
      category: "Agency",
      logo: "🚀",
      description: "Digital agency scales client results using systematic optimization",
      challenge: "Inconsistent results across client campaigns, no systematic approach to optimization",
      solution: "Implemented full AdCopySurge workflow for all client campaigns",
      results: {
        roasIncrease: 385,
        costReduction: 31,
        conversionIncrease: 240,
        timeframe: "120 days"
      },
      keyMetrics: [
        { label: "Client ROAS Avg", before: "2.3x", after: "8.9x", improvement: "+287%" },
        { label: "Client Retention", before: "68%", after: "94%", improvement: "+38%" },
        { label: "Campaign Success", before: "72%", after: "96%", improvement: "+33%" },
        { label: "Revenue per Client", before: "$2.1K", after: "$5.8K", improvement: "+176%" }
      ],
      toolsUsed: ["All 9 Tools", "Performance Forensics", "Unified Dashboard"],
      testimonial: {
        text: "AdCopySurge became our secret weapon. We can now guarantee results to clients with confidence.",
        author: "Alex Rodriguez",
        position: "Agency Founder"
      },
      featured: true
    }
  ];

  const industries = ["All", "E-commerce", "SaaS", "Agency", "Health & Wellness"];
  
  const filteredCaseStudies = caseStudies.filter(study => {
    if (tabValue === 0) return true;
    return study.category === industries[tabValue];
  });

  const overallStats = {
    totalCustomers: 500,
    averageRoasIncrease: 358,
    totalAdSpendSaved: 2.4,
    averageTimeToResults: 72
  };

  const CaseStudyCard = ({ study }) => (
    <Card
      elevation={study.featured ? 6 : 3}
      sx={{
        height: '100%',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        position: 'relative',
        border: study.featured ? '2px solid' : '1px solid',
        borderColor: study.featured ? 'primary.main' : 'divider',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: study.featured ? 12 : 8
        }
      }}
      onClick={() => navigate(`/resources/case-study/${study.id}`)}
    >
      {study.featured && (
        <Chip
          label="Featured Success"
          color="primary"
          size="small"
          sx={{
            position: 'absolute',
            top: -8,
            right: 16,
            fontWeight: 600,
            zIndex: 1
          }}
        />
      )}
      
      <CardContent sx={{ p: 3 }}>
        {/* Company Header */}
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
          <Avatar
            sx={{
              bgcolor: 'primary.light',
              width: 48,
              height: 48,
              fontSize: '1.5rem'
            }}
          >
            {study.logo}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              {study.company}
            </Typography>
            <Stack direction="row" spacing={1}>
              <Chip label={study.industry} size="small" variant="outlined" />
              <Chip 
                label={`+${study.results.roasIncrease}% ROAS`} 
                size="small" 
                color="success" 
              />
            </Stack>
          </Box>
        </Stack>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {study.description}
        </Typography>

        {/* Key Results */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
            🎯 Key Results in {study.results.timeframe}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center' }}>
                <Typography variant="h5" color="success.main" fontWeight={700}>
                  +{study.results.roasIncrease}%
                </Typography>
                <Typography variant="caption">ROAS Increase</Typography>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center' }}>
                <Typography variant="h5" color="primary.main" fontWeight={700}>
                  -{study.results.costReduction}%
                </Typography>
                <Typography variant="caption">Cost Reduction</Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        {/* Tools Used */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
            Tools Used:
          </Typography>
          <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
            {study.toolsUsed.map((tool, index) => (
              <Chip
                key={index}
                label={tool}
                size="small"
                variant="outlined"
                color="secondary"
                sx={{ fontSize: '0.7rem', height: 20 }}
              />
            ))}
          </Stack>
        </Box>

        {/* Testimonial */}
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            backgroundColor: 'rgba(37, 99, 235, 0.02)',
            border: '1px solid rgba(37, 99, 235, 0.1)'
          }}
        >
          <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>
            "{study.testimonial.text}"
          </Typography>
          <Typography variant="caption" color="text.secondary">
            — {study.testimonial.author}, {study.testimonial.position}
          </Typography>
        </Paper>

        <Button
          fullWidth
          variant="contained"
          size="small"
          sx={{ mt: 2 }}
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/resources/case-study/${study.id}`);
          }}
        >
          Read Full Case Study
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 6, md: 8 },
          mb: 4
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 800,
                  mb: 2,
                  fontSize: { xs: '2rem', md: '2.5rem' }
                }}
              >
                📊 Success Stories & Case Studies
              </Typography>
              <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
                Real businesses, real results, real ROI improvements using AdCopySurge
              </Typography>
              <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)', maxWidth: 600 }}>
                Discover how companies across industries are achieving 300%+ ROAS increases, 
                reducing costs, and scaling their marketing with our 9-tool optimization suite.
              </Typography>
              
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button
                  variant="contained"
                  size="large"
                  sx={{
                    background: 'linear-gradient(45deg, #FFD700 0%, #FFA000 100%)',
                    color: '#000',
                    fontWeight: 800,
                    '&:hover': {
                      background: 'linear-gradient(45deg, #FFC700 0%, #FF8F00 100%)',
                    }
                  }}
                  onClick={() => document.getElementById('case-studies').scrollIntoView({ behavior: 'smooth' })}
                >
                  Explore Success Stories
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  component={Link}
                  to="/register"
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    '&:hover': {
                      borderColor: 'white',
                      backgroundColor: 'rgba(255,255,255,0.1)'
                    }
                  }}
                >
                  Start Your Success Story
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={8}
                sx={{
                  p: 3,
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 3,
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" color="text.primary" sx={{ mb: 2 }}>
                  📈 Overall Impact
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="h4" color="success.main" fontWeight={800}>
                      +{overallStats.averageRoasIncrease}%
                    </Typography>
                    <Typography variant="caption">Avg ROAS Increase</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h4" color="primary.main" fontWeight={800}>
                      {overallStats.totalCustomers}+
                    </Typography>
                    <Typography variant="caption">Success Stories</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h4" color="warning.main" fontWeight={800}>
                      ${overallStats.totalAdSpendSaved}M+
                    </Typography>
                    <Typography variant="caption">Ad Spend Saved</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h4" color="error.main" fontWeight={800}>
                      {overallStats.averageTimeToResults}
                    </Typography>
                    <Typography variant="caption">Days to Results</Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Industry Filter Tabs */}
        <Box sx={{ mb: 4 }}>
          <Paper sx={{ p: 2 }}>
            <Stack direction="row" alignItems="center" justifyContent="center">
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ flexGrow: 1 }}
              >
                {industries.map((industry, index) => (
                  <Tab 
                    key={industry} 
                    label={industry}
                    sx={{ fontWeight: 600 }}
                  />
                ))}
              </Tabs>
            </Stack>
          </Paper>
        </Box>

        {/* Featured Case Study Highlight */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            🌟 Featured Success Story
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Our most impressive transformation
          </Typography>
          
          {filteredCaseStudies.filter(study => study.featured).slice(0, 1).map((study) => (
            <Paper key={study.id} elevation={8} sx={{ p: 4, mb: 4 }}>
              <Grid container spacing={4} alignItems="center">
                <Grid item xs={12} md={6}>
                  <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'primary.main',
                        width: 64,
                        height: 64,
                        fontSize: '2rem'
                      }}
                    >
                      {study.logo}
                    </Avatar>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
                        {study.company}
                      </Typography>
                      <Stack direction="row" spacing={1}>
                        <Chip label={study.industry} color="primary" />
                        <Chip label="Featured" color="secondary" />
                      </Stack>
                    </Box>
                  </Stack>
                  
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    The Challenge
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 3 }}>
                    {study.challenge}
                  </Typography>
                  
                  <Typography variant="h6" color="primary.main" sx={{ mb: 2 }}>
                    The Solution
                  </Typography>
                  <Typography variant="body1">
                    {study.solution}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" sx={{ mb: 3, textAlign: 'center' }}>
                    📊 Results in {study.results.timeframe}
                  </Typography>
                  <Grid container spacing={3}>
                    {study.keyMetrics.map((metric, index) => (
                      <Grid item xs={6} key={index}>
                        <Paper
                          variant="outlined"
                          sx={{
                            p: 2,
                            textAlign: 'center',
                            backgroundColor: 'rgba(37, 99, 235, 0.02)'
                          }}
                        >
                          <Typography variant="subtitle2" color="text.secondary">
                            {metric.label}
                          </Typography>
                          <Typography variant="h6" color="error.main" sx={{ textDecoration: 'line-through' }}>
                            {metric.before}
                          </Typography>
                          <ArrowUpward color="success" sx={{ fontSize: '1rem', my: 0.5 }} />
                          <Typography variant="h5" color="success.main" fontWeight={700}>
                            {metric.after}
                          </Typography>
                          <Chip
                            label={metric.improvement}
                            size="small"
                            color="success"
                            sx={{ mt: 1 }}
                          />
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                  
                  <Paper
                    sx={{
                      p: 3,
                      mt: 3,
                      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
                    }}
                  >
                    <Typography variant="body1" sx={{ fontStyle: 'italic', mb: 2 }}>
                      "{study.testimonial.text}"
                    </Typography>
                    <Typography variant="subtitle2" color="text.secondary">
                      — {study.testimonial.author}, {study.testimonial.position}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Paper>
          ))}
        </Box>

        {/* All Case Studies */}
        <Box id="case-studies" sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            📋 All Success Stories
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            {filteredCaseStudies.length} case stud{filteredCaseStudies.length !== 1 ? 'ies' : 'y'} available
          </Typography>
          
          <Grid container spacing={4}>
            {filteredCaseStudies.map((study) => (
              <Grid item xs={12} md={6} lg={4} key={study.id}>
                <CaseStudyCard study={study} />
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Get Started CTA */}
        <Box sx={{ mb: 4 }}>
          <Paper
            sx={{
              p: 4,
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              textAlign: 'center'
            }}
          >
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              🎯 Ready to Create Your Success Story?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
              Join hundreds of successful businesses already using AdCopySurge to transform their marketing ROI. 
              Start your free account and see results in 72 hours or less.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                component={Link}
                to="/register"
                variant="contained"
                size="large"
                startIcon={<TrendingUp />}
              >
                Start Your Success Story
              </Button>
              <Button
                component={Link}
                to="/resources/getting-started"
                variant="outlined"
                size="large"
                startIcon={<Timeline />}
              >
                Learn How It Works
              </Button>
            </Stack>
            
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={4}
              justifyContent="center"
              sx={{ mt: 4, opacity: 0.8 }}
            >
              <Stack direction="row" spacing={1} alignItems="center">
                <CheckCircle color="success" fontSize="small" />
                <Typography variant="body2">No credit card required</Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center">
                <CheckCircle color="success" fontSize="small" />
                <Typography variant="body2">Setup in 2 minutes</Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center">
                <CheckCircle color="success" fontSize="small" />
                <Typography variant="body2">Results in 72 hours</Typography>
              </Stack>
            </Stack>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
};

export default CaseStudies;
