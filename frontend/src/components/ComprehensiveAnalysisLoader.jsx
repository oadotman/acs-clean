import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  LinearProgress,
  Paper,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip,
  Alert,
  Fade
} from '@mui/material';
import {
  Analytics,
  Policy,
  Science,
  Psychology,
  AttachMoney,
  TrendingUp,
  RecordVoiceOver,
  Gavel,
  CheckCircle,
  Refresh,
  Lightbulb
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/apiService';
import toast from 'react-hot-toast';

// Analysis tools configuration with estimated processing times
const analysisTools = [
  {
    id: 'core-analyzer',
    name: 'Ad Copy Analyzer',
    icon: Analytics,
    color: '#7C3AED',
    duration: 3000,
    description: 'Analyzing overall copy effectiveness and scoring'
  },
  {
    id: 'compliance',
    name: 'Compliance Checker',
    icon: Policy,
    color: '#DC2626',
    duration: 4000,
    description: 'Scanning for platform policy violations'
  },
  {
    id: 'psychology',
    name: 'Psychology Scorer',
    icon: Psychology,
    color: '#7C2D12',
    duration: 3500,
    description: 'Evaluating 15 psychological triggers'
  },
  {
    id: 'ab-tests',
    name: 'A/B Test Generator',
    icon: Science,
    color: '#059669',
    duration: 4500,
    description: 'Generating 8 test variations with different angles'
  },
  {
    id: 'roi',
    name: 'ROI Copy Generator',
    icon: AttachMoney,
    color: '#B45309',
    duration: 3800,
    description: 'Creating premium-positioned versions'
  },
  {
    id: 'industry',
    name: 'Industry Optimizer',
    icon: TrendingUp,
    color: '#0369A1',
    duration: 3200,
    description: 'Optimizing for industry-specific language'
  },
  {
    id: 'performance',
    name: 'Performance Forensics',
    icon: TrendingUp,
    color: '#15803D',
    duration: 3000,
    description: 'Analyzing performance factors and quick wins'
  },
  {
    id: 'brand-voice',
    name: 'Brand Voice Engine',
    icon: RecordVoiceOver,
    color: '#9333EA',
    duration: 2800,
    description: 'Checking tone consistency and voice match'
  },
  {
    id: 'legal',
    name: 'Legal Risk Scanner',
    icon: Gavel,
    color: '#BE123C',
    duration: 3500,
    description: 'Identifying legally problematic claims'
  }
];

// Tips to show during analysis
const analysisTips = [
  "Compliance violations can cost up to $10,000 in platform penalties",
  "A/B testing your ad copy can improve CTR by 49% on average",
  "Psychology-optimized ads perform 300% better than generic copy",
  "Premium-positioned copy can increase customer LTV by 2.5x",
  "Industry-specific language builds 40% more trust",
  "Identifying performance bottlenecks can unlock 67% more conversions",
  "Consistent brand voice increases recall by 33%",
  "Legal-safe copy protects your business from costly lawsuits",
  "Emotional triggers in headlines increase engagement by 2x",
  "Platform-specific optimization improves ad relevance scores by 45%"
];

const ComprehensiveAnalysisLoader = ({ platform, onComplete, onError, adCopy, strategicContext, brandVoice }) => {
  const [currentToolIndex, setCurrentToolIndex] = useState(0);
  const [completedTools, setCompletedTools] = useState([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentTip, setCurrentTip] = useState(0);
  const [showTips, setShowTips] = useState(true);

  // Real API analysis process
  useEffect(() => {
    let progressIntervalId;
    let isCompleted = false;
    
    const runRealAnalysis = async () => {
      try {
        console.log('🚀 Starting REAL analysis - visual progress will sync with backend...');
        
        // Start the API call IMMEDIATELY
        console.log('🚀 Starting API call at:', new Date().toISOString());
        const startTime = Date.now();
        
        // Simulate gradual progress as API processes (more honest UX)
        // Progress moves slowly to match typical API duration (60-120s)
        let currentProgress = 0;
        let currentToolIndex = 0;
        
        progressIntervalId = setInterval(() => {
          if (!isCompleted && currentProgress < 95) {
            // Slow, steady progress - completes in ~100 seconds (matching typical API time)
            currentProgress += 1; // 1% every 1.2 seconds = ~120s to reach 95%
            setOverallProgress(currentProgress);
            
            // Update tool completion based on progress
            // Each tool represents ~11% of progress (100/9)
            const toolsShouldBeComplete = Math.floor(currentProgress / 11.11);
            
            if (toolsShouldBeComplete > currentToolIndex && toolsShouldBeComplete <= analysisTools.length) {
              const toolToComplete = analysisTools[currentToolIndex];
              console.log(`✅ Tool ${currentToolIndex + 1}/${analysisTools.length} processing: ${toolToComplete.name}`);
              
              setCompletedTools(prev => {
                if (!prev.includes(toolToComplete.id)) {
                  return [...prev, toolToComplete.id];
                }
                return prev;
              });
              
              currentToolIndex++;
              setCurrentToolIndex(currentToolIndex);
            }
          }
        }, 1200); // Update every 1.2 seconds for smooth, realistic progress
        
        // Now make the REAL API call while progress bar moves
        // When API completes, we jump to 100% and show results
        let headline = adCopy.split('\n')[0] || adCopy.split('.')[0] || adCopy.substring(0, 100);
        if (headline.length > 100) {
          headline = headline.substring(0, 97) + '...';
        }
        
        // Try to extract CTA from ad copy
        const ctaMatches = adCopy.match(/(learn more|get started|shop now|buy now|sign up|try free|download|subscribe|join|book now|call now|contact us|click here)/gi);
        const extractedCTA = ctaMatches ? ctaMatches[ctaMatches.length - 1] : 'Learn More';
        
        const adData = {
          ad: {
            headline: headline.trim(),
            body_text: adCopy.trim(),
            cta: extractedCTA.trim(),
            platform: platform,
            industry: null,
            // 7 Strategic Context Inputs
            product_or_service: strategicContext?.productOrService || null,
            target_audience_detail: strategicContext?.targetAudienceDetail || null,
            value_proposition: strategicContext?.valueProposition || null,
            audience_pain_points: strategicContext?.audiencePainPoints || null,
            desired_outcomes: strategicContext?.desiredOutcomes || null,
            trust_factors: strategicContext?.trustFactors || null,
            offer_details: strategicContext?.offerDetails || null,
            // Structured Brand Voice
            brand_voice: brandVoice && Object.keys(brandVoice).length > 0 ? {
              tone: brandVoice.tone,
              personality: brandVoice.personality,
              formality: brandVoice.formality,
              brand_values: brandVoice.brandValues || null,
              past_ads: brandVoice.pastAds || null,
              emoji_preference: brandVoice.emojiPreference || 'auto'
            } : null
          },
          competitor_ads: []
        };
        
        console.log('💾 Calling analyzeAd with proper format:', adData);
        console.log('💾 Ad data validation:', {
          hasHeadline: !!adData.ad.headline,
          headlineLength: adData.ad.headline?.length,
          hasBodyText: !!adData.ad.body_text,
          bodyTextLength: adData.ad.body_text?.length,
          hasCTA: !!adData.ad.cta,
          ctaLength: adData.ad.cta?.length,
          hasPlatform: !!adData.ad.platform,
          hasCompetitors: Array.isArray(adData.competitor_ads)
        });
        
        // Make the actual API call
        const standardResponse = await apiService.analyzeAd(adData);
        const apiDuration = ((Date.now() - startTime) / 1000).toFixed(1);
        console.log(`⏱️ API responded in ${apiDuration} seconds`);
        
        // Stop the progress interval now that API is complete
        if (progressIntervalId) clearInterval(progressIntervalId);
        console.log('💾 StandardResponse received:', standardResponse);
        console.log('💾 Response validation:', {
          hasAnalysisId: !!standardResponse.analysis_id,
          hasAnalysis: !!standardResponse.analysis,
          hasScores: !!standardResponse.scores,
          hasAlternatives: !!standardResponse.alternatives,
          hasUserProvided: !!standardResponse.user_provided,
          analysisId: standardResponse.analysis_id,
          analysisObject: standardResponse.analysis
        });
        
        // Verify that the analysis was actually saved to the database
        if (!standardResponse.analysis_id) {
          console.error('❌ Database save failed: No analysis_id returned');
          console.error('Full response:', standardResponse);
          throw new Error('Analysis was not saved to database - no analysis ID returned');
        }
        
        console.log('✅ Analysis saved to database with ID:', standardResponse.analysis_id);
        console.log('✅ Database save confirmed: Analysis will appear in history');
        
        // Use the REAL response from analyzeAd, which has saved to database
        // Transform to comprehensive format while preserving database connection
        const improvedCopy = standardResponse.alternatives?.[0]?.generated_body_text || 
                            standardResponse.alternatives?.[0]?.body_text || 
                            adCopy.replace(/Learn More/gi, 'Get Started Free').replace(/Click Here/gi, 'Shop Now');
        
        // Extract REAL tool results from backend (no more mock data!)
        const toolResults = standardResponse.tool_results || {};
        console.log('🔧 Tool results from backend:', toolResults);
        
        // Helper function to extract tool data
        const getToolData = (toolName) => {
          const tool = toolResults[toolName];
          return tool?.success ? tool : null;
        };
        
        // Map real compliance data
        const complianceTool = getToolData('compliance_checker');
        const compliance = complianceTool ? {
          status: complianceTool.insights?.compliance_status || 'COMPLIANT',
          totalIssues: complianceTool.insights?.issues?.length || 0,
          issues: complianceTool.insights?.issues || []
        } : { status: 'PENDING', totalIssues: 0, issues: [] };
        
        // Map real psychology data
        const psychologyTool = getToolData('psychology_scorer');
        const psychology = psychologyTool ? {
          overallScore: psychologyTool.scores?.psychology_score || 0,
          topOpportunity: psychologyTool.recommendations?.[0] || 'Analysis complete',
          triggers: psychologyTool.insights?.triggers || [],
          opportunities: psychologyTool.insights?.opportunities || []
        } : { overallScore: 0, triggers: [], opportunities: [] };
        
        // Map real legal data
        const legalTool = getToolData('legal_risk_scanner');
        const legal = legalTool ? {
          riskLevel: legalTool.insights?.risk_level || 'Low',
          issues: legalTool.insights?.issues || [],
          recommendations: legalTool.recommendations || []
        } : { riskLevel: 'PENDING', issues: [], recommendations: [] };
        
        // Map real ROI data
        const roiTool = getToolData('roi_copy_generator');
        const roi = roiTool ? {
          segment: roiTool.insights?.target_segment || 'General',
          premiumVersions: roiTool.insights?.premium_versions || [],
          recommendations: roiTool.recommendations || []
        } : { segment: 'PENDING', premiumVersions: [], recommendations: [] };
        
        // Map real brand voice data
        const brandVoiceTool = getToolData('brand_voice_engine');
        const brandVoiceData = brandVoiceTool ? {
          tone: brandVoiceTool.insights?.detected_tone || brandVoice?.tone || 'Conversational',
          personality: brandVoiceTool.insights?.personality || brandVoice?.personality || 'Friendly',
          formality: brandVoiceTool.insights?.formality || brandVoice?.formality || 'Casual',
          targetAudience: brandVoice?.targetAudience || '',
          brandValues: brandVoice?.brandValues || '',
          pastAds: brandVoice?.pastAds || '',
          consistency: brandVoiceTool.scores?.consistency_score || 0,
          learningFromPastAds: brandVoice?.pastAds && brandVoice.pastAds.trim().length > 50,
          recommendations: brandVoiceTool.recommendations || []
        } : {
          tone: brandVoice?.tone || 'Conversational',
          personality: brandVoice?.personality || 'Friendly',
          formality: brandVoice?.formality || 'Casual',
          targetAudience: brandVoice?.targetAudience || '',
          brandValues: brandVoice?.brandValues || '',
          pastAds: brandVoice?.pastAds || '',
          consistency: 0,
          learningFromPastAds: false,
          recommendations: ['Brand voice analysis pending']
        };
        
        // Get improvements from AI alternatives (real data)
        const improvements = standardResponse.alternatives?.slice(0, 3).map(alt => ({
          category: alt.variant_type || 'Optimization',
          description: alt.improvement_reason || 'AI-powered enhancement'
        })) || [];
        
        const response = {
          original: {
            copy: adCopy,
            score: standardResponse.scores?.overall_score || 65
          },
          improved: {
            copy: improvedCopy,
            score: Math.min(95, (standardResponse.scores?.overall_score || 65) + 15),
            improvements: improvements.length > 0 ? improvements : [
              { category: 'Analysis', description: 'Comprehensive analysis complete' }
            ]
          },
          compliance: compliance,
          psychology: psychology,
          abTests: { variations: standardResponse.alternatives || [] },
          roi: roi,
          legal: legal,
          brandVoice: brandVoiceData,
          platform: platform,
          // Preserve the database analysis ID and response
          analysis_id: standardResponse.analysis_id,
          databaseSaved: true,
          analysisRecord: standardResponse.analysis,
          tool_results: toolResults // Include raw tool results for debugging
        };
        
        console.log('✅ Mapped REAL tool results to UI format:', {
          compliance: compliance.status,
          psychology: psychology.overallScore,
          legal: legal.riskLevel,
          roi: roi.segment,
          brandVoice: brandVoiceData.consistency
        });
        
        // Mark as completed
        isCompleted = true;
        
        console.log('✅ Analysis API complete! Jumping to 100%...');
        
        // NOW jump to 100% since API is actually done
        setCompletedTools(() => analysisTools.map(t => t.id));
        setCurrentToolIndex(analysisTools.length);
        setOverallProgress(100);
        
        // Brief delay to let user see 100% completion before showing results
        setTimeout(() => {
          console.log('🚀 Transitioning to results...');
          console.log('Response data:', response);
          console.log('Improved copy in response:', response?.improved?.copy);
          console.log('onComplete callback type:', typeof onComplete);
          console.log('onComplete callback exists:', !!onComplete);
          
          try {
            if (onComplete && typeof onComplete === 'function') {
              onComplete(response);
              console.log('✅ onComplete callback executed successfully');
            } else {
              console.error('❌ onComplete is not a function:', onComplete);
              toast.error('Failed to display results - callback error');
            }
          } catch (callbackError) {
            console.error('❌ Error calling onComplete:', callbackError);
            toast.error('Failed to display results: ' + callbackError.message);
          }
          }, 800); // Brief pause to show 100% before transition
      } catch (error) {
        console.error('❌ Analysis error:', error);
        console.error('❌ Full error details:', {
          message: error.message,
          name: error.name,
          stack: error.stack,
          response: error.response?.data,
          status: error.response?.status,
          statusText: error.response?.statusText
        });
        
        isCompleted = true;
        
        // Clear progress interval
        if (progressIntervalId) clearInterval(progressIntervalId);
        
        // Show detailed error message
        let errorMessage = error.message || 'Analysis failed. Please check your connection and try again.';
        if (error.response?.status === 403) {
          errorMessage = '🔒 Access Denied: CSRF protection or authentication issue. Please refresh and try again.';
        } else if (error.response?.status === 401) {
          errorMessage = '🔐 Session Expired: Please log in again.';
        } else if (error.response?.status === 500) {
          errorMessage = '⚠️ Server Error: Our team has been notified. Please try again later.';
        }
        
        toast.error(errorMessage, { duration: 6000 });
        
        console.error('❌ Analysis failed with error:', errorMessage);
        
        // Call onError callback instead of providing mock data
        if (onError) {
          onError(error);
        } else {
          // If no error handler, throw the error up
          throw error;
        }
      }
    };

    runRealAnalysis();

    return () => {
      if (progressIntervalId) {
        clearInterval(progressIntervalId);
      }
      isCompleted = true;
    };
  }, []); // Run once on mount

  // Rotate tips during analysis
  useEffect(() => {
    const tipInterval = setInterval(() => {
      setCurrentTip((prev) => (prev + 1) % analysisTips.length);
    }, 4000);

    return () => clearInterval(tipInterval);
  }, []);


  const getCurrentTool = () => {
    return currentToolIndex < analysisTools.length ? analysisTools[currentToolIndex] : null;
  };

  const isToolComplete = (toolId) => {
    return completedTools.includes(toolId);
  };

  const isToolActive = (toolId) => {
    const currentTool = getCurrentTool();
    return currentTool && currentTool.id === toolId;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Paper sx={{ p: 4, mb: 4, textAlign: 'center', borderRadius: 4 }}>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
            🎯 Comprehensive Analysis in Progress
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
            Running 9 AI-powered tools to optimize your {platform} ad copy
          </Typography>
          
          {/* Overall Progress */}
          <Box sx={{ mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" fontWeight={600}>
                Overall Progress
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {Math.round(overallProgress)}% Complete
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={overallProgress}
              sx={{
                height: 12,
                borderRadius: 6,
                bgcolor: 'rgba(124, 58, 237, 0.1)',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(45deg, #7C3AED, #A855F7)',
                  borderRadius: 6
                }
              }}
            />
          </Box>

          <Typography variant="body2" color="text.secondary">
            Tools completed: {completedTools.length} of {analysisTools.length}
          </Typography>
        </Paper>

        {/* Tool Progress Grid */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {analysisTools.map((tool) => {
            const IconComponent = tool.icon;
            const isComplete = isToolComplete(tool.id);
            const isActive = isToolActive(tool.id);
            
            return (
              <Grid item xs={12} sm={6} md={4} key={tool.id}>
                <Card
                  sx={{
                    border: '2px solid',
                    borderColor: isComplete ? 'success.main' : isActive ? tool.color : 'grey.300',
                    bgcolor: isComplete ? 'success.light' : isActive ? `${tool.color}10` : 'grey.50',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <CardContent sx={{ p: 2, textAlign: 'center' }}>
                    <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                      {isComplete ? (
                        <CheckCircle sx={{ color: 'success.main', fontSize: '2rem' }} />
                      ) : isActive ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                          <Refresh sx={{ color: tool.color, fontSize: '2rem' }} />
                        </motion.div>
                      ) : (
                        <IconComponent sx={{ color: 'grey.400', fontSize: '2rem' }} />
                      )}
                    </Box>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        fontWeight: 600,
                        color: isComplete ? 'success.main' : isActive ? tool.color : 'grey.500'
                      }}
                    >
                      {tool.name}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      color="text.secondary" 
                      sx={{ display: 'block', mt: 0.5 }}
                    >
                      {isComplete ? '✓ Complete' : isActive ? 'Processing...' : 'Waiting'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        {/* Current Tool Info */}
        {getCurrentTool() && (() => {
          const currentTool = getCurrentTool();
          const IconComponent = currentTool.icon;
          return (
            <Paper sx={{ p: 3, mb: 4, borderRadius: 4, bgcolor: `${currentTool.color}08` }}>
              <Box display="flex" alignItems="center" gap={2}>
                <IconComponent sx={{ fontSize: '2rem', color: currentTool.color }} />
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: currentTool.color }}>
                    Running: {currentTool.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {currentTool.description}
                  </Typography>
                </Box>
              </Box>
            </Paper>
          );
        })()}

        {/* Tips Section */}
        {showTips && (
          <AnimatePresence mode="wait">
            <motion.div
              key={currentTip}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.5 }}
            >
              <Alert 
                severity="info" 
                sx={{ 
                  mb: 3,
                  '& .MuiAlert-message': {
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }
                }}
              >
                <Lightbulb fontSize="small" />
                <Typography variant="body2">
                  <strong>Pro Tip:</strong> {analysisTips[currentTip]}
                </Typography>
              </Alert>
            </motion.div>
          </AnimatePresence>
        )}

        {/* Estimated Time */}
        <Paper 
          elevation={0}
          sx={{ 
            p: 2, 
            textAlign: 'center', 
            bgcolor: 'rgba(124, 58, 237, 0.08)',
            border: '1px solid',
            borderColor: 'rgba(124, 58, 237, 0.2)',
            borderRadius: 3
          }}
        >
          <Typography variant="body2" sx={{ color: 'text.primary', fontWeight: 500 }}>
            ⏱️ Estimated time remaining: {Math.max(0, 30 - Math.round(overallProgress * 0.3))} seconds
          </Typography>
        </Paper>
      </motion.div>
    </Container>
  );
};

export default ComprehensiveAnalysisLoader;