import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Modal,
  Fade,
  Backdrop,
  IconButton,
  Skeleton,
  Typography,
  Button
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

// Components
import MetricsHeader from '../components/dashboard/MetricsHeader';
import PlatformSelector from '../components/dashboard/PlatformSelector';
import QuickActions from '../components/dashboard/QuickActions';
import AdInputPanel from '../components/dashboard/AdInputPanel';
import EnhancedAdInputPanel from '../components/dashboard/EnhancedAdInputPanel';
import RecentAnalyses from '../components/RecentAnalyses';
import BatchAnalysis from '../components/BatchAnalysis';
import AnalysisResultsComponent from '../components/AnalysisResults';
import CreativeAnalytics from '../components/shared/CreativeAnalytics';

// Services
import { useAuth } from '../services/authContext';
import creditsService from '../services/creditsService';
import metricsService from '../services/metricsService';
import apiService from '../services/apiService';
import dataService from '../services/dataService';
import creativeControlsService from '../services/creativeControlsService';
import { consumeCredits, getUserCredits, CREDIT_COSTS } from '../utils/creditSystem';
import '../utils/userTierManager'; // Enable console tier management commands

// Components
import CreditDisplay from '../components/CreditDisplay';

const Dashboard = () => {
  const { user } = useAuth();
  
  // Refs for scroll functionality
  const quickActionsRef = useRef(null);
  
  // State Management
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [showInputPanel, setShowInputPanel] = useState(false);
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [currentAdText, setCurrentAdText] = useState('');
  
  // Metrics state
  const [metrics, setMetrics] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(true);
  const [metricsExplanation, setMetricsExplanation] = useState(null);
  
  // Credit system state
  const [creditRefreshTrigger, setCreditRefreshTrigger] = useState(0);
  
  // Creative analytics state
  const [creativeAnalytics, setCreativeAnalytics] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  
  // Scroll to next step after platform selection
  const scrollToNextStep = () => {
    console.log('scrollToNextStep called');
    console.log('quickActionsRef.current:', quickActionsRef.current);
    
    if (quickActionsRef.current) {
      setTimeout(() => {
        console.log('Attempting to scroll to:', quickActionsRef.current);
        
        // Try multiple scroll methods for better compatibility
        try {
          quickActionsRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
          });
        } catch (error) {
          console.error('scrollIntoView failed:', error);
          // Fallback to window.scrollTo
          const rect = quickActionsRef.current.getBoundingClientRect();
          const scrollTop = window.pageYOffset + rect.top - 100; // 100px offset from top
          window.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          });
        }
      }, 500); // Increased delay to ensure DOM is ready
    } else {
      console.warn('quickActionsRef.current is null - element not yet mounted');
    }
  };
  
  // Handle platform selection
  const handlePlatformChange = (platform) => {
    setSelectedPlatform(platform);
    setShowInputPanel(false);
    setAnalysisResult(null);
    toast.success(`${platform.charAt(0).toUpperCase() + platform.slice(1)} platform selected`);
    
    // Auto-scroll to quick actions (next step) after platform selection
    scrollToNextStep();
  };
  
  // Handle analyze click from quick actions
  const handleAnalyzeClick = () => {
    console.log('🔄 Dashboard: handleAnalyzeClick called');
    console.log('📝 Dashboard: selectedPlatform:', selectedPlatform);
    
    if (!selectedPlatform) {
      console.log('❌ Dashboard: No platform selected');
      toast.error('Please select a platform first');
      return;
    }
    
    console.log('✅ Dashboard: Setting showInputPanel to true');
    setShowInputPanel(true);
    setAnalysisResult(null);
    console.log('✅ Dashboard: Input panel should now be visible');
  };
  
  // Handle actual analysis submission
  const handleAnalyze = async (adText, platform) => {
    try {
      // Check if user has credits for analysis using the proper credit system
      console.log('💳 Dashboard: Checking credits for single analysis...');
      
      const userCredits = await getUserCredits(user.id);
      console.log('💳 Dashboard: Current user credits:', userCredits);
      
      // Check for unlimited plan
      const isUnlimited = userCredits.subscriptionTier === 'agency_unlimited' ||
                         userCredits.credits >= 999999 ||
                         userCredits.monthlyAllowance === -1;
      
      if (!isUnlimited) {
        const creditCost = CREDIT_COSTS.BASIC_ANALYSIS || 1;
        console.log(`💰 Dashboard: Analysis will cost ${creditCost} credits`);
        
        if (userCredits.credits < creditCost) {
          const message = userCredits.credits === 0 
            ? 'You have no analysis credits remaining. Please upgrade your plan to continue.'
            : `You need ${creditCost} credits but only have ${userCredits.credits} remaining.`;
          toast.error(message);
          return;
        }
      }
      
      setCurrentAdText(adText);
      setIsAnalyzing(true);
      setShowInputPanel(false);
      
      toast.loading('Analyzing your ad...', { id: 'analysis' });
      
      console.log('🚀 Starting ad analysis...', { adText, platform });
      
      // Use real analysis service
      const analysisData = {
        ad: {
          headline: adText.split('\n')[0] || adText, // First line as headline
          body_text: adText,
          cta: '', // Extract CTA if needed
          platform: platform,
          target_audience: '',
          industry: ''
        }
      };
      
      console.log('📤 Sending data to API:', analysisData);
      
      const result = await apiService.analyzeAd(analysisData);
      
      console.log('📥 Received result from API:', result);
      
      // Transform the result to match expected format for AnalysisResults component
      const transformedResult = {
        original: adText,
        platform: platform,
        originalScore: 60, // Default original score
        score: result.scores?.overall_score || result.analysis?.overall_score || 75,
        improvement: Math.max(0, (result.scores?.overall_score || result.analysis?.overall_score || 75) - 60),
        improvements: Array.isArray(result.feedback) ? result.feedback : [
          result.feedback || 'Analysis completed successfully',
          'Check detailed results for insights'
        ],
        analysis_id: result.analysis_id,
        alternatives: result.alternatives, // Pass alternatives directly at root level
        scores: result.scores, // Pass full scores object
        feedback: result.feedback,
        quick_wins: result.quick_wins
      };
      
      setAnalysisResult(transformedResult);
      
      // Consume credits for successful analysis (only if not unlimited)
      if (!isUnlimited) {
        try {
          const creditResult = await consumeCredits(user.id, 'BASIC_ANALYSIS', 1);
          console.log('✅ Dashboard: Credits consumed successfully:', creditResult);
          
          if (creditResult.success) {
            // Refresh credit display
            setCreditRefreshTrigger(prev => prev + 1);
            
            // Show remaining credits in success message
            if (creditResult.remaining !== 'unlimited') {
              toast.success(`Analysis complete! ${creditResult.remaining} credits remaining.`, { id: 'analysis' });
            } else {
              toast.success('Analysis complete!', { id: 'analysis' });
            }
          } else {
            console.warn('⚠️ Dashboard: Credit consumption failed:', creditResult.error);
            toast.success('Analysis complete!', { id: 'analysis' });
          }
        } catch (creditError) {
          console.error('❌ Dashboard: Error consuming credits:', creditError);
          toast.success('Analysis complete!', { id: 'analysis' });
        }
      } else {
        console.log('♾️ Dashboard: Unlimited plan - no credits consumed');
        toast.success('Analysis complete! (Unlimited plan)', { id: 'analysis' });
      }
      
      // Send to integrations
      try {
        await apiService.sendToIntegrations(user.id, 'analysis_completed', {
          analysis_id: result.analysis_id,
          score: transformedResult.score,
          platform: platform,
          improvement: transformedResult.improvement,
          ad_text: adText,
          insights: transformedResult.improvements.slice(0, 3),
          user_id: user.id,
          timestamp: new Date().toISOString()
        });
        console.log('📤 Analysis data sent to integrations');
      } catch (integrationError) {
        console.warn('⚠️ Failed to send to integrations:', integrationError);
        // Don't show error to user - integrations are background
      }
      
      // Refresh metrics
      fetchMetrics();
      
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error(`Analysis failed: ${error.message}`, { id: 'analysis' });
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  // Handle batch upload
  const handleUploadClick = () => {
    if (!selectedPlatform) {
      toast.error('Please select a platform first');
      return;
    }
    setShowBatchModal(true);
  };
  
  // Handle view history - route to AnalysisHistoryNew page
  const handleHistoryClick = () => {
    window.location.href = '/history';
  };
  
  // Handle view trends - scroll to metrics or show expanded view
  const handleTrendsClick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    toast.success('Viewing performance trends');
  };
  
  // Fetch metrics from API
  const fetchMetrics = async (showSample = false) => {
    try {
      setMetricsLoading(true);
      
      // Get real metrics from the production API
      const rawMetrics = await metricsService.getDashboardMetrics();
      const formattedMetrics = metricsService.formatMetrics(rawMetrics);
      
      // Simple explanation for now
      const explanation = {
        title: rawMetrics.adsAnalyzed === 0 ? "Welcome to Your Dashboard!" : "Your Performance Dashboard",
        message: rawMetrics.adsAnalyzed === 0 
          ? "Complete your first ad analysis to see your performance metrics here."
          : `Analytics based on ${rawMetrics.adsAnalyzed} analyses from the last 30 days.`,
        actionText: rawMetrics.adsAnalyzed === 0 ? "Analyze Your First Ad" : null,
        showSampleOption: rawMetrics.adsAnalyzed === 0
      };
      
      setMetrics(formattedMetrics);
      setMetricsExplanation(explanation);
      
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      // Set empty state on error
      const defaultMetrics = {
        adsAnalyzed: 0,
        adsAnalyzedChange: 0,
        avgImprovement: 0,
        avgImprovementChange: 0,
        avgScore: 0,
        avgScoreChange: 0,
        topPerforming: 0,
        topPerformingChange: 0,
        isNewUser: true
      };
      const formattedMetrics = metricsService.formatMetrics(defaultMetrics);
      const explanation = {
        title: "Unable to Load Dashboard",
        message: "Please check your connection and try again.",
        actionText: "Retry",
        showSampleOption: false
      };
      
      setMetrics(formattedMetrics);
      setMetricsExplanation(explanation);
      toast.error('Failed to load dashboard metrics');
    } finally {
      setMetricsLoading(false);
    }
  };
  
  // Fetch creative analytics data
  const fetchCreativeAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      const analyticsData = await creativeControlsService.getCreativeAnalytics(user.id);
      setCreativeAnalytics(analyticsData);
    } catch (error) {
      console.error('Failed to fetch creative analytics:', error);
      // Set to null on error - component will handle gracefully
      setCreativeAnalytics(null);
    } finally {
      setAnalyticsLoading(false);
    }
  };
  
  // Load metrics on mount and platform change
  useEffect(() => {
    fetchMetrics();
  }, [selectedPlatform]);
  
  // Initialize metrics on component mount
  useEffect(() => {
    fetchMetrics();
  }, []);
  
  // Fetch creative analytics on component mount and after successful analysis
  useEffect(() => {
    fetchCreativeAnalytics();
  }, [user.id]);
  
  // Refresh analytics after analysis completion
  useEffect(() => {
    if (analysisResult) {
      fetchCreativeAnalytics();
    }
  }, [analysisResult]);
  
  // Handle closing input panel
  const handleCloseInputPanel = () => {
    setShowInputPanel(false);
  };
  
  // Handle new analysis after viewing results
  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setShowInputPanel(true);
  };
  
  
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Metrics Header */}
      <MetricsHeader 
        metrics={metrics}
        isLoading={metricsLoading}
      />
      
      {/* Credit Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <Box sx={{ mb: 4 }}>
          <CreditDisplay 
            refreshTrigger={creditRefreshTrigger}
            onUpgrade={() => window.location.href = '/pricing'}
            compact={false}
          />
        </Box>
      </motion.div>
      
      {/* Metrics Explanation for New Users */}
      {metricsExplanation && (metrics?.isNewUser || metrics?.isSample) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Box sx={{ 
            mb: 4, 
            p: 3, 
            bgcolor: metrics?.isSample ? 'rgba(156, 39, 176, 0.08)' : 'rgba(25, 118, 210, 0.08)',
            borderRadius: 3,
            border: '1px solid',
            borderColor: metrics?.isSample ? 'rgba(156, 39, 176, 0.2)' : 'rgba(25, 118, 210, 0.2)'
          }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: 'text.primary' }}>
              {metricsExplanation.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {metricsExplanation.message}
            </Typography>
            {metricsExplanation.showSampleOption && (
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => fetchMetrics(true)}
                  sx={{ textTransform: 'none' }}
                >
                  View Sample Dashboard
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleAnalyzeClick}
                  sx={{ textTransform: 'none' }}
                >
                  {metricsExplanation.actionText}
                </Button>
              </Box>
            )}
            {metricsExplanation.actionText && !metricsExplanation.showSampleOption && (
              <Button
                variant="contained"
                size="small"
                onClick={handleAnalyzeClick}
                sx={{ textTransform: 'none' }}
              >
                {metricsExplanation.actionText}
              </Button>
            )}
          </Box>
        </motion.div>
      )}
      
      {/* Platform Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <PlatformSelector
          selectedPlatform={selectedPlatform}
          onPlatformChange={handlePlatformChange}
          disabled={isAnalyzing}
        />
      </motion.div>
      
      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
      >
        <Box 
          sx={{ 
            mt: 4,
            p: selectedPlatform ? 2 : 0,
            border: selectedPlatform ? '2px dashed #2563eb' : 'none',
            borderRadius: selectedPlatform ? 2 : 0,
            bgcolor: selectedPlatform ? 'rgba(37, 99, 235, 0.05)' : 'transparent',
            transition: 'all 0.3s ease'
          }} 
          ref={quickActionsRef} 
          id="quick-actions-section"
        >
          {selectedPlatform && (
            <Box sx={{ mb: 2, textAlign: 'center' }}>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', duration: 0.5 }}
              >
                <Typography variant="body2" sx={{ color: 'primary.main', fontWeight: 600 }}>
                  🎯 Next: Choose an action below
                </Typography>
              </motion.div>
            </Box>
          )}
          <QuickActions
            onAnalyzeClick={handleAnalyzeClick}
            onUploadClick={handleUploadClick}
            onHistoryClick={handleHistoryClick}
            onTrendsClick={handleTrendsClick}
            platformSelected={!!selectedPlatform}
            disabled={isAnalyzing}
          />
        </Box>
      </motion.div>
      
      {/* Ad Input Panel - Shows when "Analyze Ad" is clicked */}
      <AnimatePresence>
        {(() => {
          console.log('📝 Dashboard Render: showInputPanel =', showInputPanel);
          console.log('📝 Dashboard Render: selectedPlatform =', selectedPlatform);
          console.log('📝 Dashboard Render: Should show input panel =', showInputPanel && selectedPlatform);
          return showInputPanel && selectedPlatform;
        })() && (
          <Box sx={{ mt: 4 }}>
            {console.log('✅ Dashboard Render: Rendering EnhancedAdInputPanel')}
            <EnhancedAdInputPanel
              platform={selectedPlatform}
              onAnalyze={handleAnalyze}
              onClose={handleCloseInputPanel}
              isAnalyzing={isAnalyzing}
            />
          </Box>
        )}
      </AnimatePresence>
      
      {/* Analysis Loading State */}
      <AnimatePresence>
        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ mt: 4 }}>
              <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 3, mb: 2 }} />
              <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 3, mb: 2 }} />
              <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 3 }} />
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Analysis Results - Shows inline after analysis completes */}
      <AnimatePresence>
        {analysisResult && !isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
          >
            <Box sx={{ mt: 4 }}>
              <AnalysisResultsComponent
                originalText={analysisResult.original}
                analysisData={analysisResult}
                onClose={() => setAnalysisResult(null)}
                onNewAnalysis={handleNewAnalysis}
                inline={true}
              />
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Creative Analytics - Shows when analytics data is available */}
      <AnimatePresence>
        {!isAnalyzing && !showInputPanel && creativeAnalytics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <Box sx={{ mt: 4 }}>
              <CreativeAnalytics
                analyticsData={creativeAnalytics}
                isLoading={analyticsLoading}
                onRefresh={fetchCreativeAnalytics}
                selectedPlatform={selectedPlatform}
              />
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Quick Access to Analysis History */}
      {!isAnalyzing && !analysisResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
        >
          <Box sx={{ mt: 6, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Ready to review your past analyses?
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              View all your ad analyses, track performance, and manage your insights.
            </Typography>
            <Button
              variant="outlined"
              size="large"
              onClick={handleHistoryClick}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              View Analysis History
            </Button>
          </Box>
        </motion.div>
      )}
      
      {/* Batch Analysis Modal */}
      <Modal
        open={showBatchModal}
        onClose={() => setShowBatchModal(false)}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
      >
        <Fade in={showBatchModal}>
          <Box sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: { xs: '95%', sm: '90%', md: '80%', lg: '70%' },
            maxWidth: 1200,
            maxHeight: '90vh',
            overflow: 'auto',
            bgcolor: 'background.paper',
            borderRadius: 3,
            boxShadow: 24,
            p: 0,
          }}>
            <IconButton
              onClick={() => setShowBatchModal(false)}
              sx={{
                position: 'absolute',
                right: 8,
                top: 8,
                zIndex: 1,
              }}
            >
              <CloseIcon />
            </IconButton>
            <BatchAnalysis
              onClose={() => setShowBatchModal(false)}
              onBackToDashboard={() => {
                setShowBatchModal(false);
                fetchMetrics();
              }}
            />
          </Box>
        </Fade>
      </Modal>
      
    </Container>
  );
};

export default Dashboard;