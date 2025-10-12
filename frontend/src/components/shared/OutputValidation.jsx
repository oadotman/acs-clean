import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  LinearProgress,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Stack,
  Collapse,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandIcon,
  Info as InfoIcon,
  AutoFixHigh as FixIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Validation rules for different platforms
const PLATFORM_LIMITS = {
  facebook: { headline: 40, body: 125, total: 250 },
  instagram: { headline: 30, body: 125, total: 200 },
  twitter: { headline: 0, body: 280, total: 280 },
  linkedin: { headline: 50, body: 150, total: 300 },
  google: { headline: 30, body: 90, total: 150 },
  tiktok: { headline: 35, body: 100, total: 180 }
};

// Banned words that trigger spam filters
const BANNED_WORDS = [
  // High-risk spam triggers
  'guaranteed', 'free money', 'make money fast', 'get rich quick',
  'miracle', 'breakthrough', 'revolutionary breakthrough', 'life-changing secret',
  'limited time only', 'act now', 'don\\'t wait', 'hurry',
  'click here now', 'buy now', 'order now', 'call now',
  
  // Overused marketing clichés
  'game-changer', 'industry leader', 'cutting-edge', 'state-of-the-art',
  'world-class', 'best-in-class', 'revolutionary', 'groundbreaking',
  'innovative solution', 'next-generation', 'paradigm shift',
  
  // Compliance risks
  'lose weight without', 'cure', 'treatment', 'medical breakthrough',
  'fda approved', 'clinically proven', 'doctor recommended'
];

// Readability scoring (simplified Flesch Reading Ease)
const calculateReadabilityScore = (text) => {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const words = text.split(/\s+/).filter(w => w.length > 0);
  const syllables = words.reduce((acc, word) => {
    return acc + countSyllables(word);
  }, 0);
  
  if (sentences.length === 0 || words.length === 0) return 100;
  
  const avgSentenceLength = words.length / sentences.length;
  const avgSyllablesPerWord = syllables / words.length;
  
  const score = 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgSyllablesPerWord);
  return Math.max(0, Math.min(100, Math.round(score)));
};

const countSyllables = (word) => {
  word = word.toLowerCase();
  let syllables = word.match(/[aeiouy]+/g) || [];
  if (word.endsWith('e')) syllables.pop();
  return Math.max(1, syllables.length);
};

const getReadabilityLevel = (score) => {
  if (score >= 90) return { level: 'Very Easy', color: '#4caf50', icon: '😊' };
  if (score >= 80) return { level: 'Easy', color: '#8bc34a', icon: '🙂' };
  if (score >= 70) return { level: 'Fairly Easy', color: '#ffc107', icon: '😐' };
  if (score >= 60) return { level: 'Standard', color: '#ff9800', icon: '🤔' };
  if (score >= 50) return { level: 'Fairly Difficult', color: '#f44336', icon: '😕' };
  return { level: 'Difficult', color: '#d32f2f', icon: '😰' };
};

const OutputValidation = ({ 
  generatedCopy,
  platform = 'facebook',
  onAutoFix,
  onRegenerate,
  showDetailedReport = true,
  compact = false
}) => {
  const [validationResults, setValidationResults] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  // Validate the generated copy
  const validateCopy = (copy) => {
    if (!copy || typeof copy !== 'object') return null;

    const results = {
      overallScore: 0,
      issues: [],
      warnings: [],
      passed: [],
      metrics: {}
    };

    const text = `${copy.headline || ''} ${copy.body || ''}`.trim();
    const limits = PLATFORM_LIMITS[platform] || PLATFORM_LIMITS.facebook;

    // 1. Character limit check
    const charCount = text.length;
    results.metrics.characterCount = charCount;
    results.metrics.characterLimit = limits.total;
    
    if (charCount > limits.total) {
      results.issues.push({
        type: 'length',
        severity: 'high',
        message: `Copy exceeds ${platform} character limit (${charCount}/${limits.total})`,
        suggestion: 'Shorten the text or split into multiple ads'
      });
    } else if (charCount > limits.total * 0.9) {
      results.warnings.push({
        type: 'length',
        severity: 'medium',
        message: `Copy is close to character limit (${charCount}/${limits.total})`,
        suggestion: 'Consider shortening for better mobile display'
      });
    } else {
      results.passed.push({
        type: 'length',
        message: `Character count within limits (${charCount}/${limits.total})`
      });
    }

    // 2. CTA presence check
    const ctaPatterns = /\b(learn more|get started|try now|buy now|shop now|sign up|download|subscribe|contact us|call now|book now|order now|join now|discover|explore|find out|see how|get|start|try|shop|buy|call|book|order|join)\b/gi;
    const hasCTA = ctaPatterns.test(text);
    results.metrics.hasCTA = hasCTA;
    
    if (!hasCTA && platform !== 'twitter') {
      results.warnings.push({
        type: 'cta',
        severity: 'medium',
        message: 'No clear call-to-action detected',
        suggestion: 'Add a compelling CTA to drive action'
      });
    } else if (hasCTA) {
      results.passed.push({
        type: 'cta',
        message: 'Clear call-to-action present'
      });
    }

    // 3. Banned words check
    const foundBanned = [];
    BANNED_WORDS.forEach(word => {
      const regex = new RegExp(`\\b${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      if (regex.test(text)) {
        foundBanned.push(word);
      }
    });
    
    results.metrics.bannedWordsFound = foundBanned;
    
    if (foundBanned.length > 0) {
      results.issues.push({
        type: 'banned_words',
        severity: foundBanned.length > 2 ? 'high' : 'medium',
        message: `Contains ${foundBanned.length} potentially problematic word(s)`,
        suggestion: 'Replace spam-trigger words with alternatives',
        details: foundBanned
      });
    } else {
      results.passed.push({
        type: 'banned_words',
        message: 'No spam-trigger words detected'
      });
    }

    // 4. Readability check
    const readabilityScore = calculateReadabilityScore(text);
    const readability = getReadabilityLevel(readabilityScore);
    results.metrics.readability = {
      score: readabilityScore,
      level: readability.level,
      color: readability.color,
      icon: readability.icon
    };
    
    if (readabilityScore < 60) {
      results.warnings.push({
        type: 'readability',
        severity: 'medium',
        message: `Text may be too complex (${readabilityScore}/100)`,
        suggestion: 'Use shorter sentences and simpler words'
      });
    } else {
      results.passed.push({
        type: 'readability',
        message: `Good readability score (${readabilityScore}/100)`
      });
    }

    // 5. Emoji count check
    const emojiCount = (text.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu) || []).length;
    results.metrics.emojiCount = emojiCount;
    
    if (emojiCount > 5) {
      results.warnings.push({
        type: 'emojis',
        severity: 'low',
        message: `High emoji count (${emojiCount}) may look unprofessional`,
        suggestion: 'Consider reducing emoji usage'
      });
    } else if (emojiCount > 0) {
      results.passed.push({
        type: 'emojis',
        message: `Appropriate emoji usage (${emojiCount})`
      });
    }

    // Calculate overall score
    const totalChecks = results.issues.length + results.warnings.length + results.passed.length;
    const passedChecks = results.passed.length;
    const warningPenalty = results.warnings.length * 0.5;
    const issuePenalty = results.issues.length;
    
    results.overallScore = Math.max(0, Math.round(
      ((passedChecks - warningPenalty - issuePenalty) / totalChecks) * 100
    ));

    return results;
  };

  // Run validation when copy changes
  useEffect(() => {
    if (generatedCopy) {
      setIsValidating(true);
      // Simulate async validation
      setTimeout(() => {
        const results = validateCopy(generatedCopy);
        setValidationResults(results);
        setIsValidating(false);
      }, 500);
    }
  }, [generatedCopy, platform]);

  const getScoreColor = (score) => {
    if (score >= 90) return '#4caf50';
    if (score >= 70) return '#ff9800';
    return '#f44336';
  };

  const getScoreIcon = (score) => {
    if (score >= 90) return <CheckIcon sx={{ color: '#4caf50' }} />;
    if (score >= 70) return <WarningIcon sx={{ color: '#ff9800' }} />;
    return <ErrorIcon sx={{ color: '#f44336' }} />;
  };

  if (!generatedCopy || !validationResults) {
    return null;
  }

  if (compact) {
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge 
              badgeContent={validationResults.issues.length + validationResults.warnings.length}
              color={validationResults.issues.length > 0 ? 'error' : 'warning'}
              invisible={validationResults.issues.length + validationResults.warnings.length === 0}
            >
              <AssessmentIcon color="primary" />
            </Badge>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" fontWeight={600}>
                Quality Score: {validationResults.overallScore}/100
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={validationResults.overallScore} 
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'grey.300',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(validationResults.overallScore)
                  }
                }} 
              />
            </Box>
            {validationResults.issues.length > 0 && (
              <Button
                size="small"
                variant="outlined"
                color="error"
                startIcon={<FixIcon />}
                onClick={onAutoFix}
                sx={{ textTransform: 'none' }}
              >
                Auto Fix
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      variant="outlined" 
      sx={{ 
        mb: 3,
        border: validationResults.issues.length > 0 ? '2px solid #f44336' : 
               validationResults.warnings.length > 0 ? '2px solid #ff9800' : '2px solid #4caf50'
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Quality Validation Report
            </Typography>
            {getScoreIcon(validationResults.overallScore)}
          </Box>
          
          <Stack direction="row" spacing={1}>
            {validationResults.issues.length > 0 && (
              <Button
                variant="contained"
                color="error"
                size="small"
                startIcon={<FixIcon />}
                onClick={onAutoFix}
                sx={{ textTransform: 'none' }}
              >
                Auto Fix Issues
              </Button>
            )}
            <Button
              variant="outlined"
              size="small"
              startIcon={<RefreshIcon />}
              onClick={onRegenerate}
              sx={{ textTransform: 'none' }}
            >
              Regenerate
            </Button>
          </Stack>
        </Box>

        {/* Overall Score */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Typography variant="body1" fontWeight={600}>
              Overall Quality Score
            </Typography>
            <Chip 
              label={`${validationResults.overallScore}/100`}
              sx={{ 
                backgroundColor: getScoreColor(validationResults.overallScore),
                color: 'white',
                fontWeight: 600
              }}
            />
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={validationResults.overallScore} 
            sx={{ 
              height: 10, 
              borderRadius: 5,
              backgroundColor: 'grey.300',
              '& .MuiLinearProgress-bar': {
                backgroundColor: getScoreColor(validationResults.overallScore)
              }
            }} 
          />
        </Box>

        {/* Issues Summary */}
        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Chip 
            icon={<ErrorIcon />}
            label={`${validationResults.issues.length} Issues`}
            color="error"
            variant={validationResults.issues.length > 0 ? 'filled' : 'outlined'}
          />
          <Chip 
            icon={<WarningIcon />}
            label={`${validationResults.warnings.length} Warnings`}
            color="warning"
            variant={validationResults.warnings.length > 0 ? 'filled' : 'outlined'}
          />
          <Chip 
            icon={<CheckIcon />}
            label={`${validationResults.passed.length} Passed`}
            color="success"
            variant={validationResults.passed.length > 0 ? 'filled' : 'outlined'}
          />
        </Stack>

        {/* Critical Issues */}
        <AnimatePresence>
          {validationResults.issues.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Critical Issues Found
                </Typography>
                {validationResults.issues.map((issue, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                    • {issue.message}
                  </Typography>
                ))}
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Warnings */}
        <AnimatePresence>
          {validationResults.warnings.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Optimization Opportunities
                </Typography>
                {validationResults.warnings.map((warning, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                    • {warning.message}
                  </Typography>
                ))}
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Detailed Report Toggle */}
        {showDetailedReport && (
          <>
            <Button
              variant="text"
              size="small"
              onClick={() => setShowDetails(!showDetails)}
              endIcon={
                <ExpandIcon 
                  sx={{ 
                    transform: showDetails ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s'
                  }} 
                />
              }
              sx={{ mb: 1, textTransform: 'none' }}
            >
              {showDetails ? 'Hide' : 'Show'} Detailed Analysis
            </Button>

            <Collapse in={showDetails} timeout="auto" unmountOnExit>
              <Divider sx={{ mb: 2 }} />
              
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Detailed Metrics
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`Character Count: ${validationResults.metrics.characterCount}/${validationResults.metrics.characterLimit}`}
                    secondary={`Platform: ${platform.toUpperCase()}`}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <span style={{ fontSize: '1.2rem' }}>{validationResults.metrics.readability.icon}</span>
                  </ListItemIcon>
                  <ListItemText 
                    primary={`Readability: ${validationResults.metrics.readability.level}`}
                    secondary={`Score: ${validationResults.metrics.readability.score}/100`}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckIcon color={validationResults.metrics.hasCTA ? 'success' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`Call-to-Action: ${validationResults.metrics.hasCTA ? 'Present' : 'Missing'}`}
                  />
                </ListItem>
                
                {validationResults.metrics.bannedWordsFound.length > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <WarningIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Flagged Words Found"
                      secondary={validationResults.metrics.bannedWordsFound.join(', ')}
                    />
                  </ListItem>
                )}
                
                <ListItem>
                  <ListItemIcon>
                    <span>😊</span>
                  </ListItemIcon>
                  <ListItemText 
                    primary={`Emoji Usage: ${validationResults.metrics.emojiCount} emojis`}
                    secondary={validationResults.metrics.emojiCount > 5 ? 'Consider reducing' : 'Appropriate level'}
                  />
                </ListItem>
              </List>
            </Collapse>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default OutputValidation;