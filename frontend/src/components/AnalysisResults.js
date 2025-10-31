import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Divider,
  Collapse,
  IconButton,
  alpha,
  useTheme,
  Alert
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ContentCopy as CopyIcon,
  FileDownload as ExportIcon,
  Science as ABTestIcon,
  CheckCircle as CheckIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  TrendingUp as ImprovementIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import { 
  formatWithEvidence, 
  determineEvidenceLevel, 
  EVIDENCE_LEVELS 
} from '../utils/evidenceUtils';
import UserFeedback from './shared/UserFeedback';
import ABCTestVariants from './shared/ABCTestVariants';
import ABCTestingGrid from './shared/ABCTestingGrid';
import creativeControlsService from '../services/creativeControlsService';

const AnalysisResults = ({ originalText, analysisData, onClose, onNewAnalysis, onExport }) => {
  const theme = useTheme();
  const [showAllChanges, setShowAllChanges] = useState(false);
  const [copiedStates, setCopiedStates] = useState({});
  const [showVariations, setShowVariations] = useState(false);
  
  // A/B/C Testing state
  const [abcVariants, setAbcVariants] = useState([]);
  const [isGeneratingABC, setIsGeneratingABC] = useState(false);
  const [showABCResults, setShowABCResults] = useState(false);

  // Handle feedback submission
  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      await creativeControlsService.submitFeedback(feedbackData);
      console.log('Feedback submitted successfully:', feedbackData);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  // A/B/C Testing handlers
  const handleGenerateABCVariants = async () => {
    console.log('🧪 Generating A/B/C test variants from analysis results...');
    
    const adData = {
      headline: results.improved.text.split('\n')[0] || '',
      body_text: results.improved.text,
      cta: '',
      platform: analysisData?.platform || 'facebook',
      industry: 'general',
      target_audience: ''
    };
    
    setIsGeneratingABC(true);
    
    try {
      const result = await creativeControlsService.generateABCVariants(adData, {});
      if (result.success) {
        setAbcVariants(result.variants || []);
        setShowABCResults(true);
        setShowVariations(false); // Hide the old variations
      }
    } catch (error) {
      console.error('Failed to generate A/B/C variants:', error);
    } finally {
      setIsGeneratingABC(false);
    }
  };

  const handleRegenerateABCVariant = async (variantType) => {
    console.log(`🔄 Regenerating variant ${variantType} from analysis results...`);
    
    const adData = {
      headline: results.improved.text.split('\n')[0] || '',
      body_text: results.improved.text,
      cta: '',
      platform: analysisData?.platform || 'facebook',
      industry: 'general',
      target_audience: ''
    };
    
    try {
      const result = await creativeControlsService.regenerateABCVariant(adData, variantType, {});
      if (result.success) {
        // Update the specific variant in the array
        setAbcVariants(prev => prev.map(v => 
          v.version === variantType ? result.data.variant : v
        ));
      }
    } catch (error) {
      console.error(`Failed to regenerate variant ${variantType}:`, error);
    }
  };
  
  // Determine evidence level for this analysis
  const evidenceLevel = determineEvidenceLevel({ 
    isSimulated: false, // Now using real AI-powered analysis
    sampleSize: 1000,
    confidence: 0.85
  });

  // Handle real AI analysis data format from ProductionAIService
  const results = analysisData ? {
    original: {
      score: analysisData.originalScore || 60,
      text: analysisData.original || originalText || "Flash Sale! 50% off everything. Shop now!",
      sections: [
        { text: originalText || "Flash Sale! 50% off everything. Shop now!", type: "ad_text", issues: ["Original text"] }
      ]
    },
    improved: {
      score: analysisData.score || analysisData.fullAnalysis?.scores?.overall_score || 75,
      scoreImprovement: analysisData.improvement || Math.max(0, (analysisData.score || 75) - (analysisData.originalScore || 60)),
      text: (() => {
        // Try to get the best alternative from AI analysis
        // Backend returns alternatives directly, not in fullAnalysis
        const alternatives = analysisData.alternatives || analysisData.fullAnalysis?.alternatives || [];
        if (alternatives.length > 0) {
          const bestAlt = alternatives.reduce((best, current) => 
            (current.predicted_score || 0) > (best.predicted_score || 0) ? current : best
          );
          return `${bestAlt.headline}\n\n${bestAlt.body_text}\n\n${bestAlt.cta}`;
        }
        return analysisData.improved || "Analysis completed successfully";
      })(),
      sections: []
    },
    keyImprovements: (() => {
      if (analysisData.fullAnalysis?.feedback) {
        // Split feedback into bullet points if it's a string
        if (typeof analysisData.fullAnalysis.feedback === 'string') {
          return analysisData.fullAnalysis.feedback.split('\n')
            .filter(line => line.trim().length > 0)
            .map(line => line.replace(/^[•-]\s*/, '').trim())
            .slice(0, 5); // Limit to 5 key improvements
        }
        return analysisData.fullAnalysis.feedback.slice(0, 5);
      }
      return analysisData.improvements || [
        "Analysis completed with AI-powered insights",
        "Improved scoring based on platform best practices"
      ];
    })(),
    variations: (() => {
      // Backend returns alternatives directly, not in fullAnalysis
      console.log('🔍 AnalysisResults: analysisData =', analysisData);
      console.log('🔍 AnalysisResults: analysisData.alternatives =', analysisData?.alternatives);
      console.log('🔍 AnalysisResults: analysisData.fullAnalysis?.alternatives =', analysisData?.fullAnalysis?.alternatives);
      
      const alternatives = analysisData.alternatives || analysisData.fullAnalysis?.alternatives || [];
      console.log('🔍 AnalysisResults: Final alternatives =', alternatives);
      console.log('🔍 AnalysisResults: alternatives.length =', alternatives.length);
      
      if (alternatives.length > 0) {
        const mapped = alternatives.map((alt, index) => ({
          name: alt.variant_type || `Variation ${index + 1}`,
          score: alt.predicted_score || 75,
          text: `${alt.headline}\n\n${alt.body_text}\n\n${alt.cta}`,
          description: alt.improvement_reason || "AI-generated alternative"
        }));
        console.log('✅ AnalysisResults: Mapped variations =', mapped);
        return mapped;
      }
      console.log('❌ AnalysisResults: No alternatives found, returning empty array');
      return [];
    })()
  } : {
    // NO MOCK DATA - Only show error state if no analysisData
    original: {
      score: 0,
      text: originalText || "No analysis data available",
      sections: [
        { text: originalText || "No analysis data available", type: "ad_text", issues: ["No analysis performed"] }
      ]
    },
    improved: {
      score: 0,
      scoreImprovement: 0,
      text: "No analysis data available",
      sections: []
    },
    keyImprovements: [
      "No analysis data available - please run an analysis first"
    ],
    variations: []
  };

  const handleCopyText = (text, id = 'main') => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      toast.success('Copied to clipboard!');
      
      // Reset button state after 2 seconds
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
    }).catch(() => {
      toast.error('Failed to copy to clipboard');
    });
  };

  const handleExport = () => {
    if (onExport) {
      onExport();
    } else {
      toast.success('Export functionality coming soon!');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          YOUR AD ANALYSIS
        </Typography>
        
      </Box>

      {/* Main Comparison Card */}
      <Card elevation={3} sx={{ mb: 4, overflow: 'hidden' }}>
        <CardContent sx={{ p: 0 }}>
          <Grid container>
            {/* Original Column */}
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 4, backgroundColor: alpha(theme.palette.error.main, 0.05) }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h5" fontWeight={700} sx={{ flexGrow: 1 }}>
                    ORIGINAL
                  </Typography>
                  <Chip
                    label={`${results.original.score}/100`}
                    color={getScoreColor(results.original.score)}
                    variant="filled"
                    sx={{ fontWeight: 700, fontSize: '1rem' }}
                  />
                </Box>

                <Box sx={{ mb: 3 }}>
                  {results.original.sections.map((section, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontWeight: 600,
                          mb: 1,
                          p: 1,
                          backgroundColor: alpha(theme.palette.grey[500], 0.1),
                          borderRadius: 1
                        }}
                      >
                        {section.text}
                      </Typography>
                      {section.issues?.map((issue, idx) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                          <WarningIcon sx={{ fontSize: '0.875rem', color: 'error.main' }} />
                          <Typography variant="caption" color="error.main" fontStyle="italic">
                            [{issue}]
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  ))}
                </Box>
              </Box>
            </Grid>

            {/* Improved Column */}
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 4, backgroundColor: alpha(theme.palette.success.main, 0.05) }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h5" fontWeight={700} sx={{ flexGrow: 1 }}>
                    RECOMMENDED VERSION
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={`${results.improved.score}/100`}
                      color={getScoreColor(results.improved.score)}
                      variant="filled"
                      sx={{ fontWeight: 700, fontSize: '1rem' }}
                    />
                    <Chip
                      icon={<ImprovementIcon />}
                      label={`+${results.improved.scoreImprovement}`}
                      color="success"
                      variant="outlined"
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>
                </Box>

                <Box sx={{ mb: 3 }}>
                  {results.improved.sections.map((section, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontWeight: 600,
                          mb: 1,
                          p: 1,
                          backgroundColor: alpha(theme.palette.success.main, 0.1),
                          borderRadius: 1
                        }}
                      >
                        {section.text}
                      </Typography>
                      {section.improvements?.map((improvement, idx) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                          <CheckIcon sx={{ fontSize: '0.875rem', color: 'success.main' }} />
                          <Typography variant="caption" color="success.dark" fontStyle="italic">
                            [{improvement}]
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  ))}
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Key Improvements Section */}
      <Card elevation={2} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <CheckIcon sx={{ color: 'success.main' }} />
            <Typography variant="h6" fontWeight={600}>
              Key Improvements
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            {results.keyImprovements.slice(0, showAllChanges ? undefined : 2).map((improvement, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckIcon sx={{ fontSize: '1rem', color: 'success.main' }} />
                <Typography variant="body2">{improvement}</Typography>
              </Box>
            ))}
          </Box>

          {results.keyImprovements.length > 2 && (
            <Button
              variant="text"
              onClick={() => setShowAllChanges(!showAllChanges)}
              endIcon={showAllChanges ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              {showAllChanges ? 'Show Less' : `See all ${results.keyImprovements.length} changes`}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <Card elevation={2} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={copiedStates.main ? <CheckIcon /> : <CopyIcon />}
              onClick={() => handleCopyText(results.improved.text)}
              disabled={copiedStates.main}
              sx={{
                fontWeight: 700,
                textTransform: 'none',
                minWidth: 200
              }}
            >
              {copiedStates.main ? 'Copied ✓' : 'Copy Improved Version'}
            </Button>
            
            <Button
              variant="outlined"
              size="large"
              startIcon={<ExportIcon />}
              onClick={handleExport}
              sx={{
                fontWeight: 600,
                textTransform: 'none'
              }}
            >
              Export Report
            </Button>
            
            <Button
              variant="outlined"
              size="large"
              startIcon={<ABTestIcon />}
              onClick={handleGenerateABCVariants}
              disabled={isGeneratingABC}
              sx={{
                fontWeight: 600,
                textTransform: 'none',
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  borderColor: 'primary.dark',
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                }
              }}
            >
              {isGeneratingABC ? 'Generating...' : 'Generate A/B/C Tests'}
            </Button>
            
            <Button
              variant="text"
              size="large"
              onClick={() => setShowVariations(!showVariations)}
              sx={{
                fontWeight: 600,
                textTransform: 'none',
                color: 'text.secondary'
              }}
            >
              {showVariations ? 'Hide' : 'Show'} Legacy Variations
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* User Feedback Section */}
      <UserFeedback
        generatedCopy={{
          headline: results.improved.text.split('\n')[0] || '',
          body: results.improved.text,
          cta: ''
        }}
        analysisId={analysisData?.analysis_id || `analysis_${Date.now()}`}
        onFeedbackSubmit={handleFeedbackSubmit}
        platform={analysisData?.platform || 'facebook'}
        compact={false}
      />

      {/* NEW Dynamic A/B/C Testing Grid */}
      {(() => {
        console.log('🎨 AnalysisResults: Checking if should render ABCTestingGrid');
        console.log('🎨 AnalysisResults: results.variations =', results.variations);
        console.log('🎨 AnalysisResults: results.variations.length =', results.variations?.length);
        const shouldRender = results.variations && results.variations.length > 0;
        console.log('🎨 AnalysisResults: Should render =', shouldRender);
        return shouldRender;
      })() && (
        <Card elevation={3} sx={{ mb: 4 }}>
          <CardContent>
            {console.log('✅ AnalysisResults: Rendering ABCTestingGrid with variations:', results.variations)}
            <ABCTestingGrid
              originalCopy={{
                headline: originalText?.split('\n')[0] || '',
                body_text: originalText || '',
                cta: ''
              }}
              improvedCopy={{
                headline: results.improved.text.split('\n')[0] || '',
                body_text: results.improved.text.split('\n').slice(1).join('\n') || '',
                cta: '',
                score: results.improved.score
              }}
              variations={analysisData?.alternatives || results.variations}
              platform={analysisData?.platform || 'facebook'}
              onImprove={(variation) => {
                console.log('Further improve:', variation);
                toast('Iterative improvement coming soon!', { icon: '🚀' });
              }}
              onExport={(variations) => {
                console.log('Export variations:', variations);
                if (onExport) onExport();
              }}
              isLoading={false}
            />
          </CardContent>
        </Card>
      )}

      {/* OLD A/B/C Test Results (Legacy - kept for compatibility) */}
      <AnimatePresence>
        {showABCResults && abcVariants.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
          >
            <ABCTestVariants
              variants={abcVariants}
              onGenerate={handleGenerateABCVariants}
              onRegenerateVariant={handleRegenerateABCVariant}
              onSaveVariant={(variant) => console.log('Save variant:', variant)}
              onFeedbackSubmit={handleFeedbackSubmit}
              isGenerating={isGeneratingABC}
              platform={analysisData?.platform || 'facebook'}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* A/B Variations Section */}
      <Collapse in={showVariations}>
        <Card elevation={2} sx={{ mb: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6" fontWeight={600}>
                A/B TEST VARIATIONS (Optional)
              </Typography>
              <IconButton onClick={() => setShowVariations(false)}>
                <ExpandLessIcon />
              </IconButton>
            </Box>

            <Grid container spacing={3}>
              {results.variations.map((variation, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card 
                    variant="outlined"
                    sx={{ 
                      height: '100%',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        boxShadow: 3,
                        transform: 'translateY(-2px)'
                      }
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {variation.name}
                        </Typography>
                        <Chip
                          label={`${variation.score}/100`}
                          color={getScoreColor(variation.score)}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          mb: 2,
                          p: 2,
                          backgroundColor: alpha(theme.palette.grey[100], 0.5),
                          borderRadius: 1,
                          fontFamily: 'monospace',
                          fontSize: '0.875rem',
                          color: 'text.primary'
                        }}
                      >
                        {variation.text.split('\\n').map((line, idx) => (
                          <React.Fragment key={idx}>
                            {line}
                            {idx < variation.text.split('\\n').length - 1 && <br />}
                          </React.Fragment>
                        ))}
                      </Typography>
                      
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                        {variation.description}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleCopyText(variation.text, `variation-${index}`)}
                          startIcon={copiedStates[`variation-${index}`] ? <CheckIcon /> : <CopyIcon />}
                          disabled={copiedStates[`variation-${index}`]}
                          sx={{ textTransform: 'none', flex: 1 }}
                        >
                          {copiedStates[`variation-${index}`] ? 'Copied ✓' : 'Copy'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Collapse>

      {/* Bottom Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', pt: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={onNewAnalysis}
          sx={{
            fontWeight: 600,
            textTransform: 'none',
            px: 4
          }}
        >
          Analyze Another Ad
        </Button>
        
        <Button
          variant="outlined"
          size="large"
          onClick={onClose}
          sx={{
            fontWeight: 600,
            textTransform: 'none',
            px: 4
          }}
        >
          Back to Dashboard
        </Button>
      </Box>
    </Box>
  );
};

export default AnalysisResults;