import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  LinearProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Fade,
  Grow,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  ListSubheader,
  Collapse,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  ContentCopy,
  AutoAwesome,
  TrendingUp,
  Refresh,
  Download,
  CheckCircle,
  KeyboardArrowRight,
  Lightbulb,
  Analytics,
  Facebook,
  Instagram,
  LinkedIn,
  Twitter,
  MusicNote,
  Google,
  Settings,
  Policy,
  Science,
  Psychology,
  AttachMoney,
  RecordVoiceOver,
  Gavel,
  Folder,
  Add as AddIcon,
  ExpandMore,
  History,
  School
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import { useProjectsWithCounts } from '../hooks/useProjectsNew';
import toast from 'react-hot-toast';
import ComprehensiveAnalysisLoader from '../components/ComprehensiveAnalysisLoader';
import ComprehensiveResults from '../components/ComprehensiveResults';
import useFeatureAccess from '../hooks/useFeatureAccess';
import useCredits from '../hooks/useCredits';

// Platform configurations
const platforms = [
  {
    id: 'facebook',
    name: 'Facebook',
    emoji: '📘',
    color: '#1877F2',
    description: 'General audience, balanced approach'
  },
  {
    id: 'instagram',
    name: 'Instagram',
    emoji: '📷',
    color: '#E4405F',
    description: 'Visual-first, emoji-heavy content'
  },
  {
    id: 'google',
    name: 'Google Ads',
    emoji: 'G',
    color: '#4285F4',
    description: 'Search-focused, keyword optimized'
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    emoji: '💼',
    color: '#0A66C2',
    description: 'Professional tone, B2B focused'
  },
  {
    id: 'twitter',
    name: 'Twitter/X',
    emoji: '🐦',
    color: '#1DA1F2',
    description: 'Concise, trending topics'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    emoji: '🎵',
    color: '#FF0050',
    description: 'Casual, Gen Z language'
  }
];

// Available analysis tools
const availableTools = [
  { id: 'all', name: 'Full Analysis (All Tools)', icon: Analytics, description: 'Run all 9 analysis tools' },
  { id: 'compliance', name: 'Compliance Check', icon: Policy, description: 'Platform policy violations' },
  { id: 'psychology', name: 'Psychology Scorer', icon: Psychology, description: '15 psychological triggers' },
  { id: 'ab-tests', name: 'A/B Test Generator', icon: Science, description: '8 variation angles' },
  { id: 'roi', name: 'ROI Optimizer', icon: AttachMoney, description: 'Premium positioning' },
  { id: 'legal', name: 'Legal Risk Scanner', icon: Gavel, description: 'Legal claim analysis' },
  { id: 'brand-voice', name: 'Brand Voice Check', icon: RecordVoiceOver, description: 'Tone consistency' }
];

// Analysis tips for loading state
const analysisTips = [
  "Headlines with numbers get 36% more clicks",
  "Questions in headlines increase engagement by 23%",
  "The average person sees 5,000 ads per day",
  "Shorter CTAs (2-4 words) convert better",
  "Emotional words boost click-through by 2x",
  "Social proof can increase conversions by 15%",
  "Urgency creates 22% higher click rates",
  "Personalized ads perform 10x better",
  "Video thumbnails with faces get 35% more views",
  "A/B testing can improve performance by 49%"
];

const NewAnalysis = () => {
  const { user } = useAuth();
  const { hasAccess, checkUsage, showUpgrade, commonAccess, FEATURES } = useFeatureAccess();
  const { executeWithCredits, hasEnoughCredits, getCreditRequirement, CREDIT_COSTS } = useCredits();
  const location = useLocation();
  const navigate = useNavigate();
  const isSPAMode = location.pathname === '/analysis/spa';
  const [step, setStep] = useState('input'); // 'input', 'comprehensive-analyzing', 'comprehensive-results'
  const [adCopy, setAdCopy] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [comprehensiveResults, setComprehensiveResults] = useState(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [currentTip, setCurrentTip] = useState(0);
  const [results, setResults] = useState(null);
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [refinementType, setRefinementType] = useState('');
  const [showRefineDialog, setShowRefineDialog] = useState(false);
  const [showCopySuccess, setShowCopySuccess] = useState(false);
  const [selectedTools, setSelectedTools] = useState(['all']);
  const [showToolSelector, setShowToolSelector] = useState(false);
  const textareaRef = useRef(null);
  
  // Brand voice state
  const [brandVoice, setBrandVoice] = useState({
    tone: 'conversational',
    personality: 'friendly',
    formality: 'casual',
    targetAudience: '',
    brandValues: '',
    pastAds: '' // For learning from existing content
  });
  
  // Brand voice collapsible state
  const [brandVoiceExpanded, setBrandVoiceExpanded] = useState(false);
  
  // Project selection state
  const [selectedProjectId, setSelectedProjectId] = useState('');
  // Control the project selector menu explicitly
  const [projectMenuOpen, setProjectMenuOpen] = useState(false);
  
  // Fetch projects for the dropdown
  const { data: projects = [], isLoading: projectsLoading, refetch: refetchProjects } = useProjectsWithCounts();
  
  // Debug logging (in useEffect to avoid excessive logs)
  useEffect(() => {
    console.log('🌐 NewAnalysis mounted/updated');
    console.log('📁 Projects data:', projects);
    console.log('📁 Projects loading:', projectsLoading);
    console.log('📁 Current selectedProjectId:', selectedProjectId);
    console.log('📁 Projects count:', projects.length);
    if (projects.length > 0) {
      console.log('📁 First project structure:', projects[0]);
      console.log('📁 Project IDs:', projects.map(p => p.id));
    }
    
    // Auto-clear invalid selectedProjectId to prevent MUI errors
    if (selectedProjectId && !projectsLoading && projects.length > 0 && !projects.find(p => p.id === selectedProjectId)) {
      console.warn('⚠️ Selected project ID not found in projects list, clearing selection');
      setSelectedProjectId('');
    }
    // Also clear if projects finished loading and no projects exist with the selected ID
    if (selectedProjectId && !projectsLoading && projects.length === 0) {
      console.warn('⚠️ No projects available, clearing selected project ID');
      setSelectedProjectId('');
    }
  }, [projects, selectedProjectId, projectsLoading]);
  
  // Check if a project was pre-selected (from Project Detail page, query param, or returning from project creation)
  useEffect(() => {
    // Check URL query params first
    const params = new URLSearchParams(location.search);
    const projectIdFromQuery = params.get('projectId');
    
    if (projectIdFromQuery) {
      console.log('📁 Pre-selecting project from URL:', projectIdFromQuery);
      setSelectedProjectId(projectIdFromQuery);
    } else if (location.state?.projectId) {
      setSelectedProjectId(location.state.projectId);
    }
    
    // Restore state if returning from project creation
    const returnToAnalysis = sessionStorage.getItem('returnToAnalysis');
    const savedProjectId = sessionStorage.getItem('selectedProjectId');
    const savedAdCopy = sessionStorage.getItem('analysisAdCopy');
    const savedPlatform = sessionStorage.getItem('analysisPlatform');
    
    if (returnToAnalysis === 'true') {
      console.log('🔙 Returning from project creation');
      
      // Force refresh projects list to include the newly created project
      console.log('🔄 Refreshing projects list...');
      refetchProjects();
      
      if (savedProjectId) {
        // Small delay to ensure projects are refreshed before setting selection
        setTimeout(() => {
          // Double-check that the project exists in the list
          refetchProjects().then(() => {
            const projectExists = projects.find(p => p.id === savedProjectId);
            if (projectExists) {
              setSelectedProjectId(savedProjectId);
              console.log('📁 Restored selected project:', savedProjectId);
            } else {
              console.log('⚠️ Project not found in list, forcing another refresh...');
              // If still not found, wait a bit more and try again
              setTimeout(() => {
                refetchProjects().then(() => {
                  const projectExistsRetry = projects.find(p => p.id === savedProjectId);
                  if (projectExistsRetry) {
                    setSelectedProjectId(savedProjectId);
                    console.log('📁 Restored selected project on retry:', savedProjectId);
                  } else {
                    console.log('❌ Project still not found, clearing selection');
                    setSelectedProjectId('');
                  }
                });
              }, 500);
            }
          });
        }, 200);
      }
      if (savedAdCopy) {
        setAdCopy(savedAdCopy);
        console.log('📝 Restored ad copy');
      }
      if (savedPlatform) {
        setSelectedPlatform(savedPlatform);
        console.log('🎯 Restored platform:', savedPlatform);
      }
      
      // Clear session storage
      sessionStorage.removeItem('returnToAnalysis');
      sessionStorage.removeItem('selectedProjectId');
      sessionStorage.removeItem('analysisAdCopy');
      sessionStorage.removeItem('analysisPlatform');
    }
  }, [location.state, location.search]);

  // Handle ad copy paste/input
  const handleAdCopyChange = (event) => {
    const text = event.target.value;
    setAdCopy(text);
  };

  // Handle platform selection
  const handlePlatformSelect = (platformId) => {
    setSelectedPlatform(platformId);
    // Auto-focus textarea after platform selection
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }, 100);
  };

  // Comprehensive analysis
  const runAnalysis = async () => {
    // Check if user has enough credits for a full analysis
    if (!hasEnoughCredits('FULL_ANALYSIS')) {
      // Toast will be shown automatically by the credit system
      return;
    }
    
    // Execute analysis with credit consumption
    const result = await executeWithCredits(
      'FULL_ANALYSIS',
      async () => {
        // This is where the actual analysis would happen
        setStep('comprehensive-analyzing');
        toast.success('Starting comprehensive analysis with 9 AI tools...');
        return { success: true };
      },
      { showToasts: true }
    );
    
    if (!result.success) {
      console.error('Analysis failed:', result.error);
    }
  };

  // Handle completion of comprehensive analysis
  const handleComprehensiveAnalysisComplete = (results) => {
    console.log('🎯 Analysis complete! Results received:', results);
    console.log('📊 Analysis ID:', results?.analysis_id);
    
    // Initialize improvement count if not present
    results.improvementCount = results.improvementCount || 0;
    setComprehensiveResults(results);
    
    // Show results in the current component using ComprehensiveResults
    setStep('comprehensive-results');
    toast.success('Comprehensive analysis complete! 🎉');
    
    console.log('✅ Results will be displayed using ComprehensiveResults component');
  };

  // Handle further improvement requests
  const handleFurtherImprove = async (currentCopy) => {
    try {
      const currentCount = comprehensiveResults.improvementCount || 0;
      
      if (currentCount >= 4) {
        toast.error('Maximum improvements reached (4/4)');
        return;
      }

      // Show that we're improving
      toast('Generating further improvements...', { icon: '🔄' });
      
      // Simulate improvement generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Generate improved copy based on current iteration
      const improvements = [
        { type: 'clarity', text: 'Enhanced clarity and readability' },
        { type: 'urgency', text: 'Increased urgency and scarcity elements' },
        { type: 'emotion', text: 'Strengthened emotional connection' },
        { type: 'cta', text: 'Optimized call-to-action effectiveness' }
      ];
      
      const currentImprovement = improvements[currentCount] || improvements[3];
      
      // Apply progressive improvements
      let improvedCopy = currentCopy;
      const currentScore = comprehensiveResults.improved?.score || 71;
      const newScore = Math.min(95, currentScore + (3 + Math.floor(Math.random() * 3)));
      
      // Apply different types of improvements based on iteration
      switch (currentCount) {
        case 0:
          improvedCopy = improvedCopy.replace(/\b(get|save)\b/gi, (match) => 
            match.toLowerCase() === 'get' ? 'Unlock' : 'Save Up To');
          break;
        case 1:
          improvedCopy = improvedCopy.replace(/today/gi, 'right now')
                                  .replace(/limited time/gi, '24 hours only');
          break;
        case 2:
          improvedCopy = improvedCopy.replace(/click/gi, 'tap')
                                  .replace(/now/gi, 'instantly');
          break;
        case 3:
          improvedCopy = improvedCopy.replace(/products/gi, 'premium items')
                                  .replace(/sale/gi, 'exclusive deal');
          break;
        default:
          improvedCopy = improvedCopy + ' ✨';
      }
      
      // Update the comprehensive results with the new improvement
      const updatedResults = {
        ...comprehensiveResults,
        improvementCount: currentCount + 1,
        improved: {
          ...comprehensiveResults.improved,
          copy: improvedCopy,
          score: newScore
        },
        keyImprovements: [
          ...(comprehensiveResults.keyImprovements || []),
          `Iteration ${currentCount + 1}: ${currentImprovement.text}`
        ]
      };
      
      setComprehensiveResults(updatedResults);
      toast.success(`Further improvement complete! (${currentCount + 1}/4) ✨`);
      
    } catch (error) {
      console.error('Further improve error:', error);
      toast.error('Failed to generate further improvements');
    }
  };

  // Generate improved copy (mock)
  const generateImprovedCopy = (original) => {
    // Clean the original copy first - remove any formatting characters
    let cleaned = original.replace(/[|\n\r]+/g, ' ')
                         .replace(/\s+/g, ' ')
                         .trim();
    
    // If it's a sample/template text, create a realistic ad example instead
    if (cleaned.includes('REVISED FLOW') || cleaned.includes('Make Your Ads') || cleaned.length < 20) {
      cleaned = "Get 50% off all products today! Limited time offer - shop now and save big on thousands of items. Click here to start shopping.";
    }
    
    let improved = cleaned;
    
    // Common improvements
    improved = improved.replace(/Learn More/gi, 'Get Started Free')
                      .replace(/Click Here/gi, 'Shop Now')
                      .replace(/Check it out/gi, 'Shop the Sale')
                      .replace(/Limited time offer/gi, 'Limited-time flash sale ends midnight')
                      .replace(/Get (\d+)% off/gi, '🔥 $1% OFF EVERYTHING TODAY!')
                      .replace(/thousands of items/gi, '1,000+ products');
    
    // Platform-specific optimizations
    if (selectedPlatform === 'twitter') {
      // Keep it concise for Twitter
      improved = improved.substring(0, 240) + (improved.length > 240 ? '...' : '');
    } else if (selectedPlatform === 'linkedin') {
      // Add professional tone
      improved = improved.replace(/amazing/gi, 'exceptional')
                        .replace(/awesome/gi, 'outstanding')
                        .replace(/shop now/gi, 'explore solutions');
    } else if (selectedPlatform === 'instagram') {
      // Add visual elements
      if (!improved.includes('🔥')) {
        improved = improved.replace(/!/g, '! ✨');
      }
    } else if (selectedPlatform === 'google') {
      // Focus on search intent
      improved = improved.replace(/save big/gi, 'save money on premium products');
    }
    
    return improved.replace(/\s+/g, ' ').trim();
  };

  // Generate improvement explanations
  const generateImprovements = (original) => {
    const platformName = platforms.find(p => p.id === selectedPlatform)?.name || 'this platform';
    
    // Detect what was actually changed and create specific explanations
    const improvements = [];
    
    if (original.toLowerCase().includes('click here')) {
      improvements.push('CTA: Changed weak "Click here" to action-oriented "Shop Now" for 3x higher click-through rates');
    } else {
      improvements.push('CTA: Strengthened call-to-action language to drive immediate action');
    }
    
    if (original.includes('%')) {
      improvements.push('Headline: Added emoji and urgency ("🔥 50% OFF EVERYTHING TODAY!") to create immediate visual interest and FOMO');
    } else {
      improvements.push('Headline: Made more specific and benefit-focused to grab attention');
    }
    
    if (original.toLowerCase().includes('limited time') || original.toLowerCase().includes('offer')) {
      improvements.push('Urgency: Added specific deadline ("ends midnight") because scarcity drives 23% more conversions');
    } else {
      improvements.push('Urgency: Added time-sensitive elements to encourage immediate action');
    }
    
    if (original.toLowerCase().includes('thousands')) {
      improvements.push('Credibility: Made benefits more specific ("1,000+ products") to build trust and show scale');
    } else {
      improvements.push('Body: Enhanced clarity and readability with shorter, punchier sentences');
    }
    
    // Add platform-specific improvement
    let platformSpecific = "";
    switch (selectedPlatform) {
      case 'twitter':
        platformSpecific = "Length: Optimized for Twitter's 280 character limit while maintaining impact";
        break;
      case 'linkedin':
        platformSpecific = "Tone: Enhanced professional language and replaced casual terms for B2B credibility";
        break;
      case 'instagram':
        platformSpecific = "Visual appeal: Added strategic emojis (✨) to increase engagement by 25%";
        break;
      case 'google':
        platformSpecific = "Keywords: Optimized for search intent with benefit-focused language for better ad relevance";
        break;
      case 'facebook':
        platformSpecific = "Balance: Optimized tone and length for Facebook's diverse audience demographics";
        break;
      case 'tiktok':
        platformSpecific = "Voice: Adapted casual, authentic tone that resonates with TikTok's Gen Z audience";
        break;
      default:
        platformSpecific = `Platform optimization: Tailored content and tone for ${platformName} best practices`;
    }
    
    return [...improvements, platformSpecific];
  };

  // Generate alternatives
  const generateAlternatives = (original) => {
    return [
      {
        approach: "Direct/Bold",
        score: 87,
        copy: original.replace(/\?/g, '!').toUpperCase().substring(0, original.length)
      },
      {
        approach: "Story-Driven",
        score: 84,
        copy: `Imagine this: ${original.toLowerCase()}`
      },
      {
        approach: "Question-Based",
        score: 86,
        copy: `What if ${original.toLowerCase().replace(/\./g, '?')}`
      }
    ];
  };

  // Get impact text for improvements
  const getImpactText = (category) => {
    const impactMap = {
      'Headline': 'Headlines drive 73% of first impressions',
      'CTA': 'Action-oriented CTAs get 3x more clicks', 
      'Body': 'Shorter copy increases readability by 58%',
      'Length': 'Platform-optimized length boosts engagement',
      'Tone': 'Professional tone builds 2x more trust',
      'Visual appeal': 'Emojis increase engagement by 25%',
      'Keywords': 'Search-optimized copy gets 40% more visibility',
      'Balance': 'Audience-matched tone improves conversion rates',
      'Voice': 'Gen Z tone increases relatability by 3x',
      'Platform optimization': 'Platform-specific copy performs 45% better'
    };
    return impactMap[category] || 'Optimized for better performance';
  };

  // Copy to clipboard
  const copyToClipboard = async (text, isPrimary = false) => {
    try {
      await navigator.clipboard.writeText(text);
      if (isPrimary) {
        setShowCopySuccess(true);
        setTimeout(() => setShowCopySuccess(false), 3000);
      } else {
        toast.success('Copied to clipboard!');
      }
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  // Refine functionality
  const handleRefine = async (type) => {
    setIsRefining(true);
    setRefinementType(type);
    
    await new Promise(resolve => setTimeout(resolve, 10000)); // 10 second wait
    
    // Mock refined version
    const refinedCopy = `${results.improved.copy} [Refined: ${type}]`;
    setResults({
      ...results,
      improved: {
        ...results.improved,
        copy: refinedCopy,
        score: Math.min(95, results.improved.score + 3)
      }
    });
    
    setIsRefining(false);
    toast.success('Refinement complete!');
  };

  // Tip rotation during analysis
  useEffect(() => {
    let tipInterval;
    if (step === 'analyzing') {
      tipInterval = setInterval(() => {
        setCurrentTip((prev) => (prev + 1) % analysisTips.length);
      }, 3000);
    }
    return () => clearInterval(tipInterval);
  }, [step]);

  // Auto-focus textarea
  useEffect(() => {
    if (textareaRef.current && step === 'input') {
      textareaRef.current.focus();
    }
  }, [step]);

  if (step === 'analyzing') {
    return (
      <Container 
        maxWidth={isSPAMode ? false : "md"} 
        sx={{ 
          py: isSPAMode ? 4 : 8,
          px: isSPAMode ? 2 : 3,
          minHeight: isSPAMode ? '100vh' : 'auto',
          display: 'flex',
          alignItems: isSPAMode ? 'center' : 'flex-start'
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 4 }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 4 }}>
              🎯 Analyzing your ad...
            </Typography>
            
            <Box sx={{ mb: 4 }}>
              <LinearProgress
                variant="determinate"
                value={analysisProgress}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(124, 58, 237, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(45deg, #7C3AED, #A855F7)',
                    borderRadius: 4
                  }
                }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {Math.round(analysisProgress)}% complete
              </Typography>
            </Box>

            <Stack spacing={1} sx={{ mb: 4, textAlign: 'left', maxWidth: 300, mx: 'auto' }}>
              {['Headline clarity', 'CTA effectiveness', 'Emotional appeal', 'Readability score'].map((item, index) => (
                <Box key={item} display="flex" alignItems="center" gap={1}>
                  {analysisProgress > (index + 1) * 25 ? (
                    <CheckCircle color="success" fontSize="small" />
                  ) : (
                    <CircularProgress size={16} thickness={6} />
                  )}
                  <Typography variant="body2">{item}</Typography>
                </Box>
              ))}
            </Stack>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentTip}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Lightbulb fontSize="small" />
                    <Typography variant="body2">
                      <strong>Tip:</strong> {analysisTips[currentTip]}
                    </Typography>
                  </Box>
                </Alert>
              </motion.div>
            </AnimatePresence>

            {analysisProgress > 50 && (
              <Button
                variant="outlined"
                size="small"
                onClick={() => setStep('input')}
                sx={{ mt: 2 }}
              >
                Analyze different ad instead
              </Button>
            )}
          </Paper>
        </motion.div>
      </Container>
    );
  }

  if (step === 'results' && results) {
    const scoreImprovement = results.improved.score - results.original.score;
    
    return (
      <Container 
        maxWidth={isSPAMode ? false : "lg"} 
        sx={{ 
          py: isSPAMode ? 2 : 4,
          px: isSPAMode ? 2 : 3,
          minHeight: isSPAMode ? '100vh' : 'auto'
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Score Header */}
          <Paper sx={{ p: 4, mb: 4, textAlign: 'center', borderRadius: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
              Your Ad Score: {results.original.score}/100 → {results.improved.score}/100 
              <Chip 
                label={`+${scoreImprovement} points ✨`}
                sx={{ ml: 2, bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontWeight: 700 }}
              />
            </Typography>
          </Paper>

          {/* Side-by-side comparison */}
          <Grid container spacing={4} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card sx={{ 
                height: '100%', 
                border: '2px solid', 
                borderColor: 'grey.300',
                position: 'relative'
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.secondary' }}>
                      ORIGINAL
                    </Typography>
                    <Chip 
                      label={`${results.original.score}/100`}
                      color="warning"
                      size="small"
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>
                  <Paper sx={{ 
                    p: 2, 
                    minHeight: 120, 
                    bgcolor: 'grey.50', 
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'grey.200'
                  }}>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace',
                        fontSize: '0.95rem'
                      }}
                    >
                      {results.original.copy.replace(/\|/g, '').trim()}
                    </Typography>
                  </Paper>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card sx={{ 
                height: '100%', 
                border: '2px solid', 
                borderColor: 'success.main', 
                bgcolor: 'success.light',
                position: 'relative'
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                      IMPROVED
                    </Typography>
                    <Chip 
                      label={`${results.improved.score}/100`}
                      color="success"
                      size="small"
                      sx={{ fontWeight: 600, color: 'white' }}
                    />
                  </Box>
                  <Paper sx={{ 
                    p: 2, 
                    minHeight: 120, 
                    bgcolor: 'white', 
                    borderRadius: 2,
                    border: '2px solid',
                    borderColor: 'success.main',
                    boxShadow: '0 0 10px rgba(34, 197, 94, 0.2)'
                  }}>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace',
                        fontSize: '0.95rem',
                        fontWeight: 500
                      }}
                    >
                      {results.improved.copy.replace(/\|/g, '').trim()}
                    </Typography>
                  </Paper>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* What we improved */}
          <Paper sx={{ p: 4, mb: 4, borderRadius: 4, border: '1px solid', borderColor: 'primary.light' }}>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              🎯 What We Improved:
            </Typography>
            <Stack spacing={3}>
              {results.improved.improvements.map((improvement, index) => {
                const [category, description] = improvement.split(': ');
                return (
                  <Box key={index} sx={{ 
                    p: 2, 
                    borderLeft: '4px solid',
                    borderColor: 'primary.main',
                    bgcolor: 'rgba(124, 58, 237, 0.05)',
                    borderRadius: '0 8px 8px 0'
                  }}>
                    <Typography variant="body1" sx={{ fontWeight: 600, color: 'primary.main', mb: 1 }}>
                      {category}:
                    </Typography>
                    <Typography variant="body2" sx={{ lineHeight: 1.6, mb: 1 }}>
                      {description}
                    </Typography>
                    {/* Add impact explanation */}
                    <Typography variant="caption" sx={{ 
                      color: 'success.main', 
                      fontWeight: 500,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5
                    }}>
                      📈 {getImpactText(category)}
                    </Typography>
                  </Box>
                );
              })}
            </Stack>
          </Paper>

          {/* Primary action - Copy button */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <AnimatePresence mode="wait">
              {!showCopySuccess ? (
                <motion.div
                  key="copy-button"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.2 }}
                >
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<ContentCopy sx={{ fontSize: '1.5rem' }} />}
                    onClick={() => copyToClipboard(results.improved.copy, true)}
                    sx={{
                      py: 3,
                      px: 8,
                      fontSize: '1.3rem',
                      fontWeight: 800,
                      borderRadius: 4,
                      background: 'linear-gradient(45deg, #7C3AED, #A855F7)',
                      boxShadow: '0 8px 32px rgba(124, 58, 237, 0.3)',
                      border: '2px solid rgba(255, 255, 255, 0.2)',
                      position: 'relative',
                      overflow: 'hidden',
                      '&:before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: '-100%',
                        width: '100%',
                        height: '100%',
                        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                        animation: 'shimmer 2s infinite'
                      },
                      '&:hover': {
                        background: 'linear-gradient(45deg, #6D28D9, #9333EA)',
                        transform: 'translateY(-4px)',
                        boxShadow: '0 12px 40px rgba(124, 58, 237, 0.4)'
                      },
                      '&:active': {
                        transform: 'translateY(-2px)'
                      },
                      transition: 'all 0.3s ease',
                      '@keyframes shimmer': {
                        '0%': { left: '-100%' },
                        '100%': { left: '100%' }
                      }
                    }}
                  >
                    📋 Copy Improved Version
                  </Button>
                </motion.div>
              ) : (
                <motion.div
                  key="success-state"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.2 }}
                >
                  <Paper sx={{ p: 3, bgcolor: 'success.light', borderRadius: 3, maxWidth: 400, mx: 'auto' }}>
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1} mb={2}>
                      <CheckCircle color="success" fontSize="large" />
                      <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                        ✓ Copied to clipboard!
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Ready to paste into {platforms.find(p => p.id === selectedPlatform)?.name || selectedPlatform}
                    </Typography>
                    <Stack direction="row" spacing={2} justifyContent="center">
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => setStep('input')}
                        sx={{ minWidth: 120 }}
                      >
                        Analyze Another Ad
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => setShowCopySuccess(false)}
                        sx={{ minWidth: 80 }}
                      >
                        Done
                      </Button>
                    </Stack>
                  </Paper>
                </motion.div>
              )}
            </AnimatePresence>
          </Box>

          {/* Secondary actions */}
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => setShowRefineDialog(true)}
                disabled={isRefining}
              >
                {isRefining ? 'Refining...' : '↻ Refine Further'}
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AutoAwesome />}
                onClick={() => setShowAlternatives(true)}
              >
                🔄 See 3 Alternatives
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Download />}
                onClick={() => toast.success('PDF report downloaded!')}
              >
                📄 Export PDF Report
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => setStep('input')}
              >
                ← Analyze Another
              </Button>
            </Grid>
          </Grid>
        </motion.div>

        {/* Refinement Dialog */}
        <Dialog 
          open={showRefineDialog}
          onClose={() => setShowRefineDialog(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>What would you like to adjust?</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              {[
                'Make it more casual',
                'Make it more professional', 
                'Shorter (less than 50 words)',
                'Add urgency/scarcity',
                'Emphasize different benefit'
              ].map((option) => (
                <Button
                  key={option}
                  variant="outlined"
                  fullWidth
                  onClick={() => {
                    handleRefine(option);
                    setShowRefineDialog(false);
                  }}
                  sx={{ justifyContent: 'flex-start' }}
                  disabled={isRefining}
                >
                  {option}
                </Button>
              ))}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowRefineDialog(false)}>
              Cancel
            </Button>
          </DialogActions>
        </Dialog>

        {/* Alternatives Dialog */}
        <Dialog
          open={showAlternatives}
          onClose={() => setShowAlternatives(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>3 Alternative Versions</DialogTitle>
          <DialogContent>
            <Grid container spacing={3} sx={{ pt: 2 }}>
              {results.alternatives.map((alt, index) => (
                <Grid item xs={12} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          APPROACH {index + 1}: {alt.approach}
                        </Typography>
                        <Chip label={`Score: ${alt.score}/100`} color="primary" />
                      </Box>
                      <Typography variant="body1" sx={{ mb: 3 }}>
                        {alt.copy}
                      </Typography>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<ContentCopy />}
                        onClick={() => copyToClipboard(alt.copy)}
                      >
                        Copy This Version
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowAlternatives(false)}>
              ← Back to Main Results
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    );
  }

  if (step === 'comprehensive-analyzing') {
    return (
      <ComprehensiveAnalysisLoader
        adCopy={adCopy}
        platform={selectedPlatform}
        brandVoice={brandVoice}
        onComplete={handleComprehensiveAnalysisComplete}
      />
    );
  }

  if (step === 'comprehensive-results' && comprehensiveResults) {
    return (
      <ComprehensiveResults
        results={comprehensiveResults}
        adCopy={adCopy}
        platform={selectedPlatform}
        onBack={() => setStep('input')}
        onFurtherImprove={handleFurtherImprove}
      />
    );
  }

  // Input step (default)
  return (
    <Container 
      maxWidth={isSPAMode ? false : "md"} 
      sx={{ 
        py: isSPAMode ? 1 : 4,
        px: isSPAMode ? 2 : 3,
        minHeight: isSPAMode ? '100vh' : 'auto',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: isSPAMode ? 'flex-start' : 'flex-start'
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Mode Switch Button - Only show in SPA mode */}
        {isSPAMode && (
          <Box sx={{ position: 'absolute', top: 16, right: 16, zIndex: 1000 }}>
            <Button
              component="a"
              href="/analysis/new"
              variant="outlined"
              size="small"
              sx={{
                borderColor: 'rgba(168, 85, 247, 0.3)',
                color: '#A855F7',
                fontSize: '0.75rem',
                padding: '4px 12px',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#A855F7',
                  bgcolor: 'rgba(168, 85, 247, 0.1)'
                }
              }}
            >
              🏠 Full App Mode
            </Button>
          </Box>
        )}

        <Box textAlign="center" sx={{ mb: isSPAMode ? 2 : 4, mt: isSPAMode ? 2 : 0 }}>
          <Typography 
            variant={isSPAMode ? "h4" : "h2"}
            sx={{ 
              fontWeight: 800, 
              mb: 1,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            Make Your Ads Convert Better
          </Typography>
          {isSPAMode && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              🎯 AI-powered ad copy optimization in seconds
            </Typography>
          )}
        </Box>

        {/* Platform Selection */}
        <Paper sx={{ p: 4, borderRadius: 4, mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
            Select your ad platform:
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 4 }}>
            {platforms.map((platform) => (
              <Grid item xs={6} sm={4} md={2} key={platform.id}>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card
                    sx={{
                      cursor: 'pointer',
                      textAlign: 'center',
                      p: 2,
                      height: '100%',
                      border: '2px solid',
                      borderColor: selectedPlatform === platform.id ? platform.color : 'transparent',
                      bgcolor: selectedPlatform === platform.id 
                        ? `${platform.color}10` 
                        : 'background.paper',
                      boxShadow: selectedPlatform === platform.id 
                        ? `0 0 20px ${platform.color}30`
                        : 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: platform.color,
                        boxShadow: `0 0 15px ${platform.color}20`,
                        bgcolor: `${platform.color}08`
                      }
                    }}
                    onClick={() => handlePlatformSelect(platform.id)}
                  >
                    <Typography 
                      variant="h3" 
                      sx={{ 
                        mb: 1,
                        fontSize: '2rem'
                      }}
                    >
                      {platform.emoji}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: selectedPlatform === platform.id ? 600 : 500,
                        color: selectedPlatform === platform.id ? platform.color : 'text.primary',
                        fontSize: '0.75rem'
                      }}
                    >
                      {platform.name.replace(' Ads', '').replace('/', '/')}
                    </Typography>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>

          {/* Platform selection status */}
          <AnimatePresence>
            {selectedPlatform && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Box 
                  sx={{ 
                    p: 2, 
                    mb: 3, 
                    bgcolor: `${platforms.find(p => p.id === selectedPlatform)?.color}10`, 
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: `${platforms.find(p => p.id === selectedPlatform)?.color}30`
                  }}
                >
                  <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                    <CheckCircle 
                      sx={{ color: platforms.find(p => p.id === selectedPlatform)?.color }} 
                    />
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 600,
                        color: platforms.find(p => p.id === selectedPlatform)?.color
                      }}
                    >
                      ✓ Platform: {platforms.find(p => p.id === selectedPlatform)?.name}
                    </Typography>
                  </Box>
                  <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    sx={{ display: 'block', textAlign: 'center', mt: 0.5 }}
                  >
                    {platforms.find(p => p.id === selectedPlatform)?.description}
                  </Typography>
                </Box>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Project Selector */}
          {selectedPlatform && user && (
            <Box sx={{ mb: 3 }}>
              <Box>
                <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Folder fontSize="small" />
                  Organize in Project (Optional)
                </Typography>
                <TextField
                  select
                  fullWidth
                  value={selectedProjectId && !projectsLoading && projects.find((pr) => pr.id === selectedProjectId) ? selectedProjectId : ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    console.log('🚨 TextField onChange triggered!');
                    console.log('📎 Project selector changed:', value);
                    
                    if (value === 'create-new') {
                      console.log('➕ Redirecting to projects page');
                      // Save current state
                      sessionStorage.setItem('returnToAnalysis', 'true');
                      sessionStorage.setItem('analysisAdCopy', adCopy);
                      sessionStorage.setItem('analysisPlatform', selectedPlatform);
                      setProjectMenuOpen(false);
                      navigate('/projects?action=create');
                    } else {
                      console.log('📁 Selected project:', value);
                      setSelectedProjectId(value);
                      setProjectMenuOpen(false);
                    }
                  }}
                  SelectProps={{
                    open: projectMenuOpen,
                    onOpen: () => setProjectMenuOpen(true),
                    onClose: () => setProjectMenuOpen(false),
                    MenuProps: { disablePortal: true },
                    renderValue: (selected) => {
                      if (!selected) return 'No project (standalone analysis)';
                      const p = projects.find((pr) => pr.id === selected);
                      return p ? p.name : '';
                    }
                  }}
                  variant="outlined"
                  sx={{ bgcolor: 'background.paper' }}
                >
                  <MenuItem value="">
                    <em>No project (standalone analysis)</em>
                  </MenuItem>
                  
                  {projectsLoading ? (
                    <MenuItem disabled>
                      <CircularProgress size={16} sx={{ mr: 1 }} />
                      Loading projects...
                    </MenuItem>
                  ) : (
                    <>
                      {projects.map((project) => (
                        <MenuItem 
                          key={project.id} 
                          value={project.id}
                          onClick={() => {
                            console.log('✅ MenuItem click select project:', project.id);
                            setSelectedProjectId(project.id);
                            setProjectMenuOpen(false);
                          }}
                        >
                          <Box display="flex" alignItems="center" gap={1} width="100%">
                            <Folder fontSize="small" sx={{ color: 'primary.main' }} />
                            <Box flex={1}>
                              <Typography variant="body2">{project.name}</Typography>
                              {project.client_name && (
                                <Typography variant="caption" color="text.secondary">
                                  {project.client_name}
                                </Typography>
                              )}
                            </Box>
                            <Chip 
                              label={`${project.analysisCount || 0} ads`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </MenuItem>
                      ))}
                      
                      <MenuItem 
                        value="create-new" 
                        sx={{ color: 'primary.main' }}
                        onClick={() => {
                          console.log('➕ Create New Project selected from menu');
                          sessionStorage.setItem('returnToAnalysis', 'true');
                          sessionStorage.setItem('analysisAdCopy', adCopy);
                          sessionStorage.setItem('analysisPlatform', selectedPlatform);
                          setProjectMenuOpen(false);
                          navigate('/projects?action=create');
                        }}
                      >
                        <Box display="flex" alignItems="center" gap={1}>
                          <AddIcon fontSize="small" />
                          Create New Project
                        </Box>
                      </MenuItem>
                    </>
                  )}
                </TextField>
              </Box>
              
              {selectedProjectId && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  ✓ This analysis will be saved to project: {projects.find(p => p.id === selectedProjectId)?.name}
                </Typography>
              )}
            </Box>
          )}

        </Paper>

        {/* Enhanced Brand Voice Configuration */}
        {selectedPlatform && (
          <Paper sx={{ borderRadius: 4, mb: 4, overflow: 'hidden' }}>
            <Accordion 
              expanded={brandVoiceExpanded} 
              onChange={(event, isExpanded) => setBrandVoiceExpanded(isExpanded)}
              sx={{ 
                boxShadow: 'none',
                '&:before': { display: 'none' },
                border: 'none'
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMore />}
                sx={{ 
                  p: 4,
                  bgcolor: 'rgba(124, 58, 237, 0.05)',
                  '&:hover': { bgcolor: 'rgba(124, 58, 237, 0.08)' },
                  transition: 'background-color 0.2s ease'
                }}
              >
                <Box display="flex" alignItems="center" gap={1} flex={1}>
                  <RecordVoiceOver color="primary" />
                  <Box flex={1}>
                    <Typography variant="h5" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Brand Voice & Learning (Optional)
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {brandVoiceExpanded 
                        ? 'Configure your brand voice and let AI learn from your past successful ads'
                        : 'Help AI understand your brand personality and learn from past content'
                      }
                    </Typography>
                  </Box>
                  {!brandVoiceExpanded && (
                    <Chip 
                      label="Enhanced AI Learning" 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                      sx={{ ml: 2 }}
                    />
                  )}
                </Box>
              </AccordionSummary>
              
              <AccordionDetails sx={{ p: 4, pt: 2 }}>
                {/* Past Ads Learning Section */}
                <Box sx={{ mb: 4 }}>
                  <Paper variant="outlined" sx={{ p: 3, bgcolor: 'rgba(34, 197, 94, 0.05)', border: '1px dashed rgba(34, 197, 94, 0.3)' }}>
                    <Box display="flex" alignItems="center" gap={1} sx={{ mb: 2 }}>
                      <School color="success" />
                      <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                        🎯 Learn from Your Past Successful Ads
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Paste 3-5 examples of your best-performing ads to help our AI understand your successful writing patterns, tone, and style.
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Past Successful Ad Examples"
                      placeholder={`Example format:
                      
Ad 1: "Transform your business with our revolutionary CRM software. Join 10,000+ companies already seeing 40% better customer retention. Start your free trial today!"
                      
Ad 2: "Stop losing customers to poor follow-up. Our automated system keeps every lead engaged until they buy. See results in 30 days or your money back."
                      
(Add 3-5 of your best ads...)`}
                      value={brandVoice.pastAds}
                      onChange={(e) => setBrandVoice(prev => ({ ...prev, pastAds: e.target.value }))}
                      variant="outlined"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          bgcolor: 'background.paper'
                        }
                      }}
                      helperText="The more successful ad examples you provide, the better our AI can match your winning style and tone"
                    />
                  </Paper>
                </Box>
                
                {/* Traditional Brand Voice Settings */}
                <Box>
                  <Box display="flex" alignItems="center" gap={1} sx={{ mb: 3 }}>
                    <RecordVoiceOver color="primary" />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Brand Voice Characteristics
                    </Typography>
                  </Box>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Tone</InputLabel>
                        <Select
                          value={brandVoice.tone}
                          onChange={(e) => setBrandVoice(prev => ({ ...prev, tone: e.target.value }))}
                          label="Tone"
                        >
                          <MenuItem value="professional">Professional</MenuItem>
                          <MenuItem value="conversational">Conversational</MenuItem>
                          <MenuItem value="playful">Playful</MenuItem>
                          <MenuItem value="authoritative">Authoritative</MenuItem>
                          <MenuItem value="empathetic">Empathetic</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Personality</InputLabel>
                        <Select
                          value={brandVoice.personality}
                          onChange={(e) => setBrandVoice(prev => ({ ...prev, personality: e.target.value }))}
                          label="Personality"
                        >
                          <MenuItem value="friendly">Friendly</MenuItem>
                          <MenuItem value="confident">Confident</MenuItem>
                          <MenuItem value="innovative">Innovative</MenuItem>
                          <MenuItem value="trustworthy">Trustworthy</MenuItem>
                          <MenuItem value="energetic">Energetic</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Formality</InputLabel>
                        <Select
                          value={brandVoice.formality}
                          onChange={(e) => setBrandVoice(prev => ({ ...prev, formality: e.target.value }))}
                          label="Formality"
                        >
                          <MenuItem value="casual">Casual</MenuItem>
                          <MenuItem value="semi-formal">Semi-formal</MenuItem>
                          <MenuItem value="formal">Formal</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Target Audience"
                        placeholder="e.g., Tech-savvy millennials, Small business owners"
                        value={brandVoice.targetAudience}
                        onChange={(e) => setBrandVoice(prev => ({ ...prev, targetAudience: e.target.value }))}
                        variant="outlined"
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Brand Values"
                        placeholder="e.g., Innovation, Sustainability, Quality"
                        value={brandVoice.brandValues}
                        onChange={(e) => setBrandVoice(prev => ({ ...prev, brandValues: e.target.value }))}
                        variant="outlined"
                      />
                    </Grid>
                  </Grid>
                </Box>
                
                {/* Brand Voice Status Indicator */}
                {(brandVoice.pastAds.trim() || brandVoice.targetAudience.trim() || brandVoice.brandValues.trim()) && (
                  <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(124, 58, 237, 0.05)', borderRadius: 2 }}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <CheckCircle sx={{ color: 'success.main', fontSize: '1.2rem' }} />
                      <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                        Brand Voice Configuration Active
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      {brandVoice.pastAds.trim() ? '✅ Learning from past ads • ' : ''}
                      {brandVoice.targetAudience.trim() ? '✅ Target audience defined • ' : ''}
                      {brandVoice.brandValues.trim() ? '✅ Brand values set' : ''}
                    </Typography>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          </Paper>
        )}

        {/* Ad Copy Input */}
        <Paper sx={{ 
          p: 4, 
          borderRadius: 4, 
          mb: 4,
          opacity: selectedPlatform ? 1 : 0.6,
          transition: 'opacity 0.3s ease'
        }}>
          <Box textAlign="center" sx={{ mb: 3 }}>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
              Paste Your Ad Copy
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedPlatform ? `Optimized for ${platforms.find(p => p.id === selectedPlatform)?.name}` : 'Select a platform first'}
            </Typography>
          </Box>
          <TextField
            ref={textareaRef}
            fullWidth
            multiline
            rows={8}
            placeholder={selectedPlatform 
              ? `Paste your ${platforms.find(p => p.id === selectedPlatform)?.name} ad copy here...

Example:
Get 50% off all products today! Limited time offer - shop now and save big on thousands of items. Click here to start shopping.`
              : "Select a platform first, then paste your ad copy here..."
            }
            value={adCopy}
            onChange={handleAdCopyChange}
            disabled={!selectedPlatform}
            variant="outlined"
            sx={{
              mb: 3,
              '& .MuiOutlinedInput-root': {
                fontSize: '1.1rem',
                lineHeight: 1.6,
                borderRadius: 3,
                bgcolor: selectedPlatform ? 'background.paper' : 'grey.50',
                '&:hover fieldset': {
                  borderColor: selectedPlatform ? 'primary.main' : 'grey.400',
                  borderWidth: selectedPlatform ? 2 : 1
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                  borderWidth: 2,
                  boxShadow: selectedPlatform ? '0 0 0 3px rgba(124, 58, 237, 0.1)' : 'none'
                },
                '&.Mui-disabled': {
                  bgcolor: 'grey.100'
                }
              },
              '& .MuiOutlinedInput-input': {
                '&::placeholder': {
                  opacity: selectedPlatform ? 0.7 : 0.5
                }
              }
            }}
          />

          {/* Status indicators */}
          <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box display="flex" alignItems="center" gap={2}>
              {/* Platform status */}
              <Box display="flex" alignItems="center" gap={1}>
                {selectedPlatform ? (
                  <CheckCircle color="success" fontSize="small" />
                ) : (
                  <Box 
                    sx={{ 
                      width: 20, 
                      height: 20, 
                      borderRadius: '50%', 
                      border: '2px solid', 
                      borderColor: 'grey.300',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'grey.500' }}>1</Typography>
                  </Box>
                )}
                <Typography variant="body2" color={selectedPlatform ? 'success.main' : 'text.secondary'}>
                  Platform: {selectedPlatform ? platforms.find(p => p.id === selectedPlatform)?.name : 'Not selected'}
                </Typography>
              </Box>

              {/* Ad copy status */}
              <Box display="flex" alignItems="center" gap={1}>
                {adCopy.trim().length > 10 ? (
                  <CheckCircle color="success" fontSize="small" />
                ) : (
                  <Box 
                    sx={{ 
                      width: 20, 
                      height: 20, 
                      borderRadius: '50%', 
                      border: '2px solid', 
                      borderColor: selectedPlatform ? 'primary.light' : 'grey.300',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="caption" sx={{ fontSize: '0.7rem', color: selectedPlatform ? 'primary.main' : 'grey.500' }}>2</Typography>
                  </Box>
                )}
                <Typography variant="body2" color={adCopy.trim().length > 10 ? 'success.main' : 'text.secondary'}>
                  Ad copy: {adCopy.trim().length > 10 ? 'Added' : 'Waiting for input'}
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Credit cost indicator */}
          {selectedPlatform && adCopy.trim().length > 10 && (
            <Box textAlign="center" sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                💳 Analysis cost: {getCreditRequirement('FULL_ANALYSIS')} credit{getCreditRequirement('FULL_ANALYSIS') !== 1 ? 's' : ''}
              </Typography>
            </Box>
          )}

          {/* Analyze button */}
          <Box textAlign="center">
            <Button
              variant="contained"
              size="large"
              disabled={!selectedPlatform || !adCopy.trim() || adCopy.trim().length < 10}
              onClick={runAnalysis}
              endIcon={<KeyboardArrowRight />}
              sx={{
                py: 2,
                px: 6,
                fontSize: '1.2rem',
                fontWeight: 700,
                borderRadius: 3,
                background: (selectedPlatform && adCopy.trim().length > 10)
                  ? 'linear-gradient(45deg, #7C3AED, #A855F7)'
                  : 'linear-gradient(45deg, #9CA3AF, #6B7280)',
                animation: (selectedPlatform && adCopy.trim().length > 10) 
                  ? 'pulse 2s infinite' 
                  : 'none',
                '&:hover': {
                  background: (selectedPlatform && adCopy.trim().length > 10)
                    ? 'linear-gradient(45deg, #6D28D9, #9333EA)'
                    : 'linear-gradient(45deg, #9CA3AF, #6B7280)',
                  transform: (selectedPlatform && adCopy.trim().length > 10) ? 'translateY(-2px)' : 'none',
                  boxShadow: (selectedPlatform && adCopy.trim().length > 10) 
                    ? '0 8px 25px rgba(124, 58, 237, 0.3)' 
                    : 'none'
                },
                '&:disabled': {
                  background: 'linear-gradient(45deg, #9CA3AF, #6B7280)',
                  transform: 'none'
                },
                transition: 'all 0.3s ease',
                '@keyframes pulse': {
                  '0%': {
                    boxShadow: '0 0 0 0 rgba(124, 58, 237, 0.4)'
                  },
                  '70%': {
                    boxShadow: '0 0 0 10px rgba(124, 58, 237, 0)'
                  },
                  '100%': {
                    boxShadow: '0 0 0 0 rgba(124, 58, 237, 0)'
                  }
                }
              }}
            >
              {!selectedPlatform 
                ? 'Select Platform First'
                : !adCopy.trim() || adCopy.trim().length < 10
                  ? 'Add Your Ad Copy'
                  : 'Analyze Now →'
              }
            </Button>
          </Box>
        </Paper>

        {/* Other platform option */}
        <Box textAlign="center" sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Don't see your platform?
          </Typography>
          <Button
            variant="outlined"
            size="small"
            onClick={() => toast('More platforms coming soon! For now, select the closest match.', { icon: 'ℹ️' })}
            sx={{ 
              borderRadius: 20,
              textTransform: 'none',
              borderColor: 'grey.400',
              color: 'text.secondary',
              '&:hover': {
                borderColor: 'primary.main',
                color: 'primary.main'
              }
            }}
          >
            Other platform not listed?
          </Button>
        </Box>

        {/* Alternative Access */}
        {!isSPAMode && (
          <Box textAlign="center">
            <Link
              component="a"
              href="/analysis/spa"
              target="_blank"
              variant="body2"
              sx={{ 
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
                color: 'primary.main'
              }}
            >
              🚀 Open in SPA Mode
            </Link>
          </Box>
        )}
      </motion.div>
    </Container>
  );
};

export default NewAnalysis;
