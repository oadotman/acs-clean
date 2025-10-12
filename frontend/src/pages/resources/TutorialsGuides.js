import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardMedia,
  Button,
  Stack,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  InputAdornment,
  Tab,
  Tabs
} from '@mui/material';
import {
  CheckCircle,
  ExpandMore,
  Search as SearchIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Star,
  TrendingUp,
  Security,
  Psychology,
  Science,
  Gavel,
  Business,
  RecordVoiceOver,
  Analytics,
  FilterList
} from '@mui/icons-material';
import StartIcon from '../../components/icons/StartIcon';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/authContext';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tutorial-tabpanel-${index}`}
      aria-labelledby={`tutorial-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const TutorialsGuides = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const tutorials = [
    {
      id: 1,
      title: "Writing Compliant Facebook Ads in 2024",
      description: "Master Facebook's advertising policies and create ads that never get rejected",
      category: "Compliance",
      level: "Beginner",
      duration: "15 min",
      author: "Sarah Chen, Marketing Expert",
      featured: true,
      steps: [
        "Understanding Facebook's core advertising policies",
        "Common violations that cause ad rejection",
        "Using AdCopySurge Compliance Checker effectively",
        "Creating compliant copy that converts",
        "Best practices for ongoing compliance"
      ],
      tools: ["Compliance Checker", "Legal Risk Scanner"],
      image: "/api/placeholder/400/200"
    },
    {
      id: 2,
      title: "Generating High-Converting A/B Test Variations",
      description: "Learn to create 5-10 compelling ad variations that test different psychological angles",
      category: "Testing",
      level: "Intermediate",
      duration: "20 min",
      author: "Mike Rodriguez, Growth Specialist",
      featured: true,
      steps: [
        "Setting up effective A/B testing frameworks",
        "Using psychological triggers in ad variations",
        "Leveraging the A/B Test Generator tool",
        "Analyzing performance data correctly",
        "Scaling winning variations"
      ],
      tools: ["A/B Test Generator", "Psychology Scorer"],
      image: "/api/placeholder/400/200"
    },
    {
      id: 3,
      title: "ROI-Focused Copy for High-Value Customers",
      description: "Create premium positioning copy that attracts profitable customers",
      category: "Revenue",
      level: "Advanced",
      duration: "25 min",
      author: "Jennifer Liu, Revenue Optimizer",
      featured: true,
      steps: [
        "Identifying high-value customer segments",
        "Crafting premium positioning messages",
        "Using the ROI Copy Generator effectively",
        "Testing price sensitivity in copy",
        "Measuring true customer lifetime value impact"
      ],
      tools: ["ROI Copy Generator", "Industry Optimizer"],
      image: "/api/placeholder/400/200"
    },
    {
      id: 4,
      title: "Psychology-Driven Ad Copy That Converts",
      description: "Master the 15+ psychological triggers that drive purchase decisions",
      category: "Psychology",
      level: "Intermediate",
      duration: "18 min",
      author: "Dr. Alex Thompson, Behavioral Psychologist",
      steps: [
        "Understanding the psychology of purchasing decisions",
        "Implementing urgency and scarcity effectively",
        "Using social proof and authority triggers",
        "Creating emotional connections with copy",
        "Measuring psychological impact with our scorer"
      ],
      tools: ["Psychology Scorer", "Brand Voice Engine"],
      image: "/api/placeholder/400/200"
    },
    {
      id: 5,
      title: "Industry-Specific Copy Optimization",
      description: "Adapt your messaging to industry-specific language and pain points",
      category: "Targeting",
      level: "Intermediate",
      duration: "22 min",
      author: "David Park, Industry Specialist",
      steps: [
        "Researching industry-specific terminology",
        "Identifying sector-specific pain points",
        "Using the Industry Optimizer tool",
        "Creating resonant messaging frameworks",
        "Testing across different market segments"
      ],
      tools: ["Industry Optimizer", "Performance Forensics"],
      image: "/api/placeholder/400/200"
    },
    {
      id: 6,
      title: "Brand Voice Consistency Across Campaigns",
      description: "Maintain consistent brand voice while optimizing for performance",
      category: "Branding",
      level: "Advanced",
      duration: "30 min",
      author: "Emma Wilson, Brand Strategist",
      steps: [
        "Defining your brand voice characteristics",
        "Setting up brand voice profiles",
        "Using the Brand Voice Engine",
        "Balancing consistency with optimization",
        "Training the AI on your specific tone"
      ],
      tools: ["Brand Voice Engine", "Ad Copy Analyzer"],
      image: "/api/placeholder/400/200"
    }
  ];

  const quickGuides = [
    {
      title: "5-Minute Compliance Check",
      description: "Quickly scan any ad copy for policy violations",
      duration: "5 min",
      difficulty: "Easy",
      tools: ["Compliance Checker"]
    },
    {
      title: "Instant Psychology Score",
      description: "Get immediate feedback on psychological triggers",
      duration: "3 min",
      difficulty: "Easy",
      tools: ["Psychology Scorer"]
    },
    {
      title: "One-Click A/B Variations",
      description: "Generate multiple ad variations instantly",
      duration: "2 min",
      difficulty: "Easy",
      tools: ["A/B Test Generator"]
    },
    {
      title: "Performance Forensics Deep-Dive",
      description: "Understand why ads succeed or fail",
      duration: "10 min",
      difficulty: "Medium",
      tools: ["Performance Forensics"]
    }
  ];

  const categories = ["All", "Compliance", "Testing", "Revenue", "Psychology", "Targeting", "Branding"];
  
  const filteredTutorials = tutorials.filter(tutorial => {
    const matchesSearch = tutorial.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tutorial.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = tabValue === 0 || tutorial.category === categories[tabValue];
    return matchesSearch && matchesCategory;
  });

  const TutorialCard = ({ tutorial }) => (
    <Card
      elevation={3}
      sx={{
        height: '100%',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        position: 'relative',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 8
        }
      }}
      onClick={() => navigate(`/resources/tutorial/${tutorial.id}`)}
    >
      {tutorial.featured && (
        <Chip
          label="Featured"
          color="primary"
          size="small"
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 1,
            fontWeight: 600
          }}
        />
      )}
      
      <CardMedia
        component="div"
        height="140"
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white'
        }}
      >
        <Typography variant="h4" sx={{ fontWeight: 800 }}>
          {tutorial.category === 'Compliance' && '🛡️'}
          {tutorial.category === 'Testing' && '🧪'}
          {tutorial.category === 'Revenue' && '💰'}
          {tutorial.category === 'Psychology' && '🧠'}
          {tutorial.category === 'Targeting' && '🎯'}
          {tutorial.category === 'Branding' && '🎨'}
        </Typography>
      </CardMedia>
      
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <Chip
            label={tutorial.category}
            size="small"
            variant="outlined"
            color="primary"
          />
          <Chip
            label={tutorial.level}
            size="small"
            color={
              tutorial.level === 'Beginner' ? 'success' :
              tutorial.level === 'Intermediate' ? 'warning' : 'error'
            }
          />
        </Stack>
        
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
          {tutorial.title}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
          {tutorial.description}
        </Typography>
        
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ScheduleIcon fontSize="inherit" />
            {tutorial.duration}
          </Typography>
          <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <PersonIcon fontSize="inherit" />
            {tutorial.author.split(',')[0]}
          </Typography>
        </Stack>
        
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          Tools used: {tutorial.tools.join(', ')}
        </Typography>
        
        <Button
          fullWidth
          variant="contained"
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            if (isAuthenticated) {
              navigate(`/resources/tutorial/${tutorial.id}`);
            } else {
              navigate('/register');
            }
          }}
        >
          {isAuthenticated ? 'Start Tutorial' : 'Sign Up to Access'}
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
                📚 Tutorials & Guides
              </Typography>
              <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
                Master ad copy optimization with step-by-step tutorials and expert guides
              </Typography>
              <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)', maxWidth: 600 }}>
                From beginner basics to advanced techniques, learn how to use all 9 tools effectively 
                and achieve consistent 300%+ ROAS improvements.
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
                  onClick={() => document.getElementById('featured-tutorials').scrollIntoView({ behavior: 'smooth' })}
                >
                  Browse Featured Tutorials
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    '&:hover': {
                      borderColor: 'white',
                      backgroundColor: 'rgba(255,255,255,0.1)'
                    }
                  }}
                  onClick={() => document.getElementById('quick-guides').scrollIntoView({ behavior: 'smooth' })}
                >
                  Quick Guides
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
                  📖 Tutorial Stats
                </Typography>
                <Stack spacing={1}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="body2">Total Tutorials</Typography>
                    <Typography variant="body2" fontWeight={600}>25+</Typography>
                  </Stack>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="body2">Average Duration</Typography>
                    <Typography variant="body2" fontWeight={600}>18 min</Typography>
                  </Stack>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="body2">Completion Rate</Typography>
                    <Typography variant="body2" fontWeight={600}>94%</Typography>
                  </Stack>
                </Stack>
                <Chip label="Updated Weekly" color="success" size="small" sx={{ mt: 2 }} />
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Search and Filter */}
        <Box sx={{ mb: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} alignItems="center">
              <TextField
                fullWidth
                placeholder="Search tutorials..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                sx={{ maxWidth: { md: 400 } }}
              />
              
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ minWidth: 0 }}
              >
                {categories.map((category, index) => (
                  <Tab key={category} label={category} />
                ))}
              </Tabs>
            </Stack>
          </Paper>
        </Box>

        {/* Featured Tutorials */}
        <Box id="featured-tutorials" sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            ⭐ Featured Tutorials
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Our most popular and impactful tutorials
          </Typography>
          
          <Grid container spacing={4}>
            {filteredTutorials.slice(0, 3).map((tutorial) => (
              <Grid item xs={12} md={4} key={tutorial.id}>
                <TutorialCard tutorial={tutorial} />
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Quick Guides */}
        <Box id="quick-guides" sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            ⚡ Quick Guides
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Get results in under 10 minutes with these focused guides
          </Typography>
          
          <Grid container spacing={3}>
            {quickGuides.map((guide, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Card elevation={2} sx={{ p: 3, height: '100%' }}>
                  <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'success.light',
                        color: 'success.main',
                        width: 40,
                        height: 40
                      }}
                    >
                      ⚡
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {guide.title}
                      </Typography>
                      <Stack direction="row" spacing={1}>
                        <Chip label={guide.duration} size="small" color="info" />
                        <Chip 
                          label={guide.difficulty} 
                          size="small" 
                          color={guide.difficulty === 'Easy' ? 'success' : 'warning'} 
                        />
                      </Stack>
                    </Box>
                  </Stack>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {guide.description}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Tools: {guide.tools.join(', ')}
                  </Typography>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* All Tutorials */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            📋 All Tutorials
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            {filteredTutorials.length} tutorial{filteredTutorials.length !== 1 ? 's' : ''} available
          </Typography>
          
          <Grid container spacing={4}>
            {filteredTutorials.map((tutorial) => (
              <Grid item xs={12} md={6} lg={4} key={tutorial.id}>
                <TutorialCard tutorial={tutorial} />
              </Grid>
            ))}
          </Grid>
          
          {filteredTutorials.length === 0 && (
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                No tutorials found matching your search
              </Typography>
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchQuery('');
                  setTabValue(0);
                }}
                sx={{ mt: 2 }}
              >
                Clear Filters
              </Button>
            </Paper>
          )}
        </Box>

        {/* Tutorial Request */}
        <Box sx={{ mb: 4 }}>
          <Paper
            sx={{
              p: 4,
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              textAlign: 'center'
            }}
          >
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              📝 Request a Tutorial
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
              Can't find what you're looking for? Let us know what tutorial you'd like to see next. 
              We create new content based on user requests.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                component={Link}
                to="/contact"
                variant="contained"
                size="large"
              >
                Request Tutorial
              </Button>
              <Button
                component={Link}
                to="/resources/case-studies"
                variant="outlined"
                size="large"
              >
                View Case Studies
              </Button>
            </Stack>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
};

export default TutorialsGuides;
