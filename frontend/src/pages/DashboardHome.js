import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Container,
  Paper,
  Grid,
  Chip,
  Divider,
  alpha,
  useTheme
} from '@mui/material';
import {
  AccessTime as ClockIcon,
  CloudUpload as UploadIcon,
  Analytics as AnalyticsIcon,
  Security as ComplianceIcon,
  Psychology as PsychologyIcon,
  Gavel as LegalIcon,
  RecordVoiceOver as BrandIcon,
  TrendingUp as ROIIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import creditsService from '../services/creditsService';
import AnalysisLoadingModal from '../components/AnalysisLoadingModal';
import AnalysisResultsComponent from '../components/AnalysisResults';
import BatchAnalysis from '../components/BatchAnalysis';
import RecentAnalyses from '../components/RecentAnalyses';
import ExportModal from '../components/ExportModal';
import toast from 'react-hot-toast';

const DashboardHome = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const [adText, setAdText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [showBatchAnalysis, setShowBatchAnalysis] = useState(false);
  const [showRecentAnalyses, setShowRecentAnalyses] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'results', 'batch', 'history'

  const exampleAd = "Flash Sale! 50% off everything. Shop now!";

  const handleTryExample = () => {
    setAdText(exampleAd);
  };

  const handleAnalyzeNow = () => {
    if (!adText.trim()) return;
    
    try {
      // Check if user can perform analysis
      if (!creditsService.canPerformAction('single_analysis', 1)) {
        const credits = creditsService.getCredits();
        if (credits.current <= 0) {
          toast.error('You have no credits remaining. Please upgrade your plan.');
        } else {
          toast.error('Daily limit reached. Try again tomorrow or upgrade your plan.');
        }
        return;
      }
      
      // Use credit for analysis
      creditsService.useCredits(1, 'single');
      setIsAnalyzing(true);
      toast.success('Credit used. Analysis starting...');
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleAnalysisComplete = () => {
    setIsAnalyzing(false);
    setAnalysisComplete(true);
  };

  const handleCloseModal = () => {
    setIsAnalyzing(false);
  };

  const handleNewAnalysis = () => {
    setAnalysisComplete(false);
    setAdText('');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setAnalysisComplete(false);
    setShowBatchAnalysis(false);
    setShowRecentAnalyses(false);
    setAdText('');
  };

  const handleShowBatchAnalysis = () => {
    setCurrentView('batch');
    setShowBatchAnalysis(true);
  };

  const handleShowHistory = () => {
    setCurrentView('history');
    setShowRecentAnalyses(true);
  };

  const handleViewAnalysis = (analysis) => {
    // Would load specific analysis data and show results
    setAdText(analysis.original);
    setAnalysisComplete(true);
    setCurrentView('results');
  };

  const checkItems = [
    { icon: ComplianceIcon, text: 'Facebook/Google compliance' },
    { icon: PsychologyIcon, text: 'Psychology triggers' },
    { icon: LegalIcon, text: 'Legal risk assessment' },
    { icon: BrandIcon, text: 'Brand voice consistency' },
    { icon: ROIIcon, text: 'ROI optimization' },
    { icon: AnalyticsIcon, text: 'Platform best practices' }
  ];

  // Show different views based on current state
  if (currentView === 'results' && analysisComplete) {
    return (
      <AnalysisResultsComponent
        originalText={adText}
        onClose={handleBackToDashboard}
        onNewAnalysis={handleNewAnalysis}
        onExport={() => setShowExportModal(true)}
      />
    );
  }

  if (currentView === 'batch' && showBatchAnalysis) {
    return (
      <BatchAnalysis
        onClose={handleBackToDashboard}
        onBackToDashboard={handleBackToDashboard}
      />
    );
  }

  if (currentView === 'history' && showRecentAnalyses) {
    return (
      <RecentAnalyses
        onClose={handleBackToDashboard}
        onViewAnalysis={handleViewAnalysis}
        onNewAnalysis={handleNewAnalysis}
      />
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box 
        sx={{ 
          textAlign: 'center',
          py: 8,
          minHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}
      >
        {/* Header */}
        <Typography 
          variant="h2" 
          component="h1" 
          fontWeight={800}
          color="primary.main"
          gutterBottom
        >
          AdCopySurge
        </Typography>
        
        <Typography 
          variant="h4" 
          component="h2" 
          fontWeight={700}
          color="text.primary"
          sx={{ mb: 3 }}
        >
          Improve Your Ad Copy in 15 Seconds
        </Typography>

        {/* Description */}
        <Typography 
          variant="h6" 
          color="text.secondary"
          sx={{ mb: 1, fontWeight: 500 }}
        >
          Paste your ad below and we'll:
        </Typography>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1" color="text.secondary">• Fix compliance violations</Typography>
          <Typography variant="body1" color="text.secondary">• Strengthen psychology triggers</Typography>
          <Typography variant="body1" color="text.secondary">• Optimize your call-to-action</Typography>
          <Typography variant="body1" color="text.secondary">• Generate A/B test variations</Typography>
        </Box>

        {/* Input Section */}
        <Paper 
          elevation={3}
          sx={{ 
            p: 4, 
            mb: 3,
            maxWidth: 800,
            mx: 'auto',
            border: 2,
            borderColor: alpha(theme.palette.primary.main, 0.1),
            '&:focus-within': {
              borderColor: theme.palette.primary.main,
              boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
            }
          }}
        >
          <TextField
            fullWidth
            multiline
            rows={8}
            placeholder="Paste your ad copy here..."
            value={adText}
            onChange={(e) => setAdText(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                fontSize: '1.1rem',
                '& fieldset': { border: 'none' },
                '&:hover fieldset': { border: 'none' },
                '&.Mui-focused fieldset': { border: 'none' }
              }
            }}
          />
          
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{ mt: 2, fontStyle: 'italic' }}
          >
            Example: "Flash Sale! 50% off everything. Shop now!"
          </Typography>
        </Paper>

        {/* Batch Upload Option */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
            Or: 
            <Button 
              variant="text" 
              startIcon={<UploadIcon />}
              onClick={handleShowBatchAnalysis}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Upload CSV
            </Button>
            {' '}for batch analysis (2-20 ads)
          </Typography>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 4 }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleAnalyzeNow}
            disabled={!adText.trim() || isAnalyzing}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 700,
              textTransform: 'none',
              borderRadius: 3,
              boxShadow: 3,
              '&:hover': {
                boxShadow: 6,
                transform: 'translateY(-1px)'
              }
            }}
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze Now'}
          </Button>
          
          <Button
            variant="outlined"
            size="large"
            onClick={handleTryExample}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              textTransform: 'none',
              borderRadius: 3
            }}
          >
            Try Example Ad
          </Button>
        </Box>

        {/* Info Footer */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
          <AnalyticsIcon sx={{ fontSize: '1.25rem', color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            9 specialized tools • Results in ~15 seconds
          </Typography>
        </Box>
      </Box>

      {/* Below-fold Section */}
      <Box sx={{ py: 8, borderTop: 1, borderColor: 'divider' }}>
        <Typography 
          variant="h4" 
          textAlign="center" 
          fontWeight={700}
          color="text.primary"
          sx={{ mb: 6 }}
        >
          What We Check:
        </Typography>
        
        <Grid container spacing={4} sx={{ mb: 6 }}>
          {checkItems.map((item, index) => {
            const IconComponent = item.icon;
            return (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 2,
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: alpha(theme.palette.success.main, 0.05),
                    border: 1,
                    borderColor: alpha(theme.palette.success.main, 0.2)
                  }}
                >
                  <CheckIcon sx={{ color: 'success.main', fontSize: '1.25rem' }} />
                  <IconComponent sx={{ color: 'text.secondary', fontSize: '1.25rem' }} />
                  <Typography variant="body1" fontWeight={500}>
                    {item.text}
                  </Typography>
                </Box>
              </Grid>
            );
          })}
        </Grid>

        {/* Stats */}
        <Box 
          sx={{ 
            textAlign: 'center',
            p: 4,
            backgroundColor: alpha(theme.palette.primary.main, 0.05),
            borderRadius: 3,
            position: 'relative'
          }}
        >
          <Typography variant="h6" fontWeight={600} color="text.primary" gutterBottom>
            2,891 ads analyzed this week • Avg improvement: +22 points
          </Typography>
          <Button
            variant="text"
            onClick={handleShowHistory}
            sx={{ 
              textTransform: 'none', 
              fontWeight: 500,
              mt: 1
            }}
          >
            View Recent Analyses →
          </Button>
        </Box>
      </Box>

      {/* Analysis Loading Modal */}
      <AnalysisLoadingModal
        open={isAnalyzing}
        onClose={handleCloseModal}
        onComplete={handleAnalysisComplete}
        adText={adText}
      />

      {/* Export Modal */}
      <ExportModal
        open={showExportModal}
        onClose={() => setShowExportModal(false)}
        analysisData={{ original: adText }}
      />
    </Container>
  );
};

export default DashboardHome;