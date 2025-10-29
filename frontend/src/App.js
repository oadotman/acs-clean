import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, useMediaQuery, CircularProgress, Typography } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import AdAnalysis from './pages/AdAnalysis';
import AnalysisResultsPage from './pages/AnalysisResultsPage';
import BillingCredits from './pages/BillingCredits';
import SimplifiedResults from './pages/SimplifiedResults';
import AnalysisHistory from './pages/AnalysisHistory';
import AnalysisHistoryNew from './pages/AnalysisHistoryNew';
import Reports from './pages/Reports';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Pricing from './pages/Pricing';
import Profile from './pages/Profile';
import LandingPage from './pages/LandingPage';
import ResourcesLanding from './pages/ResourcesLanding';
import ContactUs from './pages/ContactUs';
import About from './pages/About';
import Terms from './pages/Terms';
import Privacy from './pages/Privacy';

// New Dashboard Layout and Pages
import AppLayout from './layout/AppLayout';
import SPALayout from './layout/SPALayout';
import DashboardHome from './pages/DashboardHome';
import Dashboard from './pages/Dashboard';
import ModernDashboard from './pages/ModernDashboard';
import NewAnalysis from './pages/NewAnalysis';

// New AI-Powered Tools
import ComplianceChecker from './pages/ComplianceChecker';
import ROICopyGenerator from './pages/ROICopyGenerator';
import ABTestGenerator from './pages/ABTestGenerator';
import IndustryOptimizer from './pages/IndustryOptimizer';
import PerformanceForensics from './pages/PerformanceForensics';
import PsychologyScorer from './pages/PsychologyScorer';
import BrandVoiceEngine from './pages/BrandVoiceEngine';
import LegalRiskScanner from './pages/LegalRiskScanner';

// New Shared Workflow Pages
import ProjectsList from './pages/ProjectsList';
import ProjectWorkspace from './pages/ProjectWorkspace';

// NEW Projects Feature (for organizing ad analyses)
import ProjectsListNew from './pages/ProjectsListNew';
import ProjectDetailNew from './pages/ProjectDetailNew';

// Resources Pages
import GettingStarted from './pages/resources/GettingStarted';
import TutorialsGuides from './pages/resources/TutorialsGuides';
import CaseStudies from './pages/resources/CaseStudies';

// Coming Soon Pages
import PartnerProgram from './pages/PartnerProgram';
import AffiliateProgram from './pages/AffiliateProgram';


// Services
import { AuthProvider, useAuth } from './services/authContext';

// Debug utilities (available in browser console)
import './utils/supabaseDebug';

// Enhanced wallet blocking
import walletBlocker from './utils/walletBlocker';
import NoWallet from './components/NoWallet';

// Blog
import { BlogProvider } from './contexts/BlogContext';

// Settings
import { SettingsProvider } from './contexts/SettingsContext';

// Support Widget
import SupportWidget from './components/SupportWidget';
import Blog from './pages/Blog';
import BlogPost from './pages/BlogPost';
import BlogCategory from './pages/BlogCategory';

// Agency Pages
import AgencyIntegrations from './pages/agency/Integrations';
import AgencyTeamManagement from './pages/agency/TeamManagement';
import AgencyReportsBranding from './pages/agency/ReportsBranding';
import AgencyWhiteLabelSettings from './pages/agency/WhiteLabelSettings';

// Theme
import { ThemeModeProvider } from './contexts/ThemeContext';
import { WhiteLabelProvider } from './contexts/WhiteLabelContext';

// Theme configuration moved to ThemeContext.jsx for light/dark mode support
// Keeping legacy theme reference for compatibility
const legacyTheme = {
  palette: {
    mode: 'dark', // Modern Luxury uses dark mode by default
    primary: {
      main: '#7C3AED', // Vivid Purple
      light: '#A855F7', // Vibrant Lavender
      dark: '#5B21B6',
      contrastText: '#F9FAFB', // Off-White
    },
    secondary: {
      main: '#A855F7', // Accent - Vibrant Lavender
      light: '#C084FC', // CTA Button
      dark: '#7C3AED',
      contrastText: '#F9FAFB',
    },
    // CTA Button color
    warning: {
      main: '#C084FC', // Bright Gradient Purple for CTAs
      light: '#E9D5FF',
      dark: '#A855F7',
      contrastText: '#0F0B1D',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
      contrastText: '#F9FAFB',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
      contrastText: '#F9FAFB',
    },
    background: {
      default: '#0F0B1D', // Deep Navy/Black
      paper: '#1A0F2E', // Slightly lighter for cards
    },
    text: {
      primary: '#F9FAFB', // Off-White
      secondary: '#E5E7EB', // Cool Gray
    },
    grey: {
      50: '#F9FAFB',
      100: '#E5E7EB',
      200: '#D1D5DB',
      300: '#9CA3AF',
      400: '#6B7280',
      500: '#4B5563',
      600: '#374151',
      700: '#1F2937',
      800: '#1A0F2E',
      900: '#0F0B1D',
    },
    divider: 'rgba(168, 85, 247, 0.2)', // Purple divider for Modern Luxury
  },
  typography: {
    fontFamily: '"Inter", "SF Pro Display", "-apple-system", "BlinkMacSystemFont", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 800,
      fontSize: '2.5rem',
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 700,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h4: {
      fontWeight: 700,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.125rem',
      lineHeight: 1.5,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    body1: {
      fontWeight: 400,
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontWeight: 400,
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
      letterSpacing: '0.02em',
    },
    caption: {
      fontWeight: 400,
      fontSize: '0.75rem',
      lineHeight: 1.5,
    },
  },
  spacing: 8, // Base spacing unit (8px)
  shadows: [
    'none',
    '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  ],
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          border: '1px solid',
          borderColor: 'rgba(168, 85, 247, 0.2)',
          boxShadow: '0 10px 40px rgba(124, 58, 237, 0.15)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          padding: '24px',
          background: 'linear-gradient(135deg, #1A0F2E 0%, #0F0B1D 100%)',
          backdropFilter: 'blur(20px)',
          '&:hover': {
            boxShadow: '0 20px 60px rgba(168, 85, 247, 0.3)',
            transform: 'translateY(-4px)',
            borderColor: 'rgba(192, 132, 252, 0.4)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          backgroundImage: 'none',
          backgroundColor: '#1A0F2E',
          border: '1px solid rgba(168, 85, 247, 0.15)',
        },
        elevation1: {
          boxShadow: '0 10px 40px rgba(124, 58, 237, 0.1)',
        },
        elevation2: {
          boxShadow: '0 20px 60px rgba(168, 85, 247, 0.2)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 700,
          fontSize: '1rem',
          padding: '12px 32px',
          boxShadow: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 10px 30px rgba(192, 132, 252, 0.4)',
            transform: 'translateY(-2px)',
          },
        },
        contained: {
          boxShadow: '0 8px 25px rgba(124, 58, 237, 0.3)',
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
          color: '#F9FAFB',
          '&:hover': {
            background: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)',
            boxShadow: '0 12px 40px rgba(192, 132, 252, 0.5)',
          },
        },
        outlined: {
          borderColor: 'rgba(168, 85, 247, 0.5)',
          color: '#C084FC',
          '&:hover': {
            borderColor: '#C084FC',
            backgroundColor: 'rgba(192, 132, 252, 0.1)',
          },
        },
        large: {
          padding: '16px 40px',
          fontSize: '1.125rem',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: 'rgba(26, 15, 46, 0.5)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '& fieldset': {
              borderColor: 'rgba(168, 85, 247, 0.3)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(168, 85, 247, 0.5)',
            },
            '&.Mui-focused fieldset': {
              borderWidth: 2,
              borderColor: '#A855F7',
              boxShadow: '0 0 20px rgba(168, 85, 247, 0.3)',
            },
          },
          '& .MuiInputLabel-root': {
            fontWeight: 500,
            color: '#E5E7EB',
          },
          '& .MuiOutlinedInput-input': {
            color: '#F9FAFB',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          fontWeight: 600,
          backgroundColor: 'rgba(168, 85, 247, 0.15)',
          color: '#C084FC',
          border: '1px solid rgba(168, 85, 247, 0.3)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(15, 11, 29, 0.8)',
          backdropFilter: 'blur(20px)',
        },
      },
    },
  },
};

const queryClient = new QueryClient();

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  // Show loading while checking authentication
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
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function LegacyAppLayout({ children }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const isMobile = useMediaQuery('(max-width:960px)');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isAuthPage = ['/login', '/register'].includes(location.pathname);
  const isLandingPage = location.pathname === '/';
  const showSidebar = isAuthenticated && !isAuthPage && !isLandingPage;
  const showNavbar = true; // Show navbar on all pages

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      {showSidebar && (
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          variant={isMobile ? 'temporary' : 'permanent'}
        />
      )}
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        {/* Top Navbar */}
        {showNavbar && (
          <Navbar onSidebarToggle={handleSidebarToggle} showSidebarToggle={showSidebar && isMobile} />
        )}
        
        {/* Page Content */}
        <Box
          sx={{
            flexGrow: 1,
            pt: isAuthPage || isLandingPage ? 0 : 2,
            pb: 0, // Remove bottom padding since footer will handle spacing
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <Box sx={{ flexGrow: 1 }}>
            {children}
          </Box>
          {/* Footer - show on all pages except auth pages */}
          {!isAuthPage && !isAuthenticated && <Footer />}
        </Box>
      </Box>
    </Box>
  );
}

function App() {
  return (
    <NoWallet>
      <QueryClientProvider client={queryClient}>
        <WhiteLabelProvider>
          <ThemeModeProvider>
            <CssBaseline />
            <SettingsProvider>
              <AuthProvider>
                <BlogProvider>
                <Router>
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<LegacyAppLayout><LandingPage /></LegacyAppLayout>} />
                <Route path="/login" element={<LegacyAppLayout><Login /></LegacyAppLayout>} />
                <Route path="/register" element={<LegacyAppLayout><Register /></LegacyAppLayout>} />
                <Route path="/forgot-password" element={<LegacyAppLayout><ForgotPassword /></LegacyAppLayout>} />
                <Route path="/pricing" element={<LegacyAppLayout><Pricing /></LegacyAppLayout>} />
                
                {/* Resources Routes - accessible to all users */}
                <Route path="/resources" element={<LegacyAppLayout><ResourcesLanding /></LegacyAppLayout>} />
                <Route path="/resources/api" element={<LegacyAppLayout><div>API Documentation - Coming Soon</div></LegacyAppLayout>} />
                <Route path="/resources/getting-started" element={<LegacyAppLayout><GettingStarted /></LegacyAppLayout>} />
                <Route path="/resources/tutorials" element={<LegacyAppLayout><TutorialsGuides /></LegacyAppLayout>} />
                <Route path="/resources/case-studies" element={<LegacyAppLayout><CaseStudies /></LegacyAppLayout>} />
                <Route path="/resources/videos" element={<LegacyAppLayout><div>Videos - Coming Soon</div></LegacyAppLayout>} />
                <Route path="/resources/blog" element={<Navigate to="/blog" replace />} />
                <Route path="/blog" element={<LegacyAppLayout><Blog /></LegacyAppLayout>} />
                <Route path="/blog/:slug" element={<LegacyAppLayout><BlogPost /></LegacyAppLayout>} />
                <Route path="/blog/category/:category" element={<LegacyAppLayout><BlogCategory /></LegacyAppLayout>} />
                <Route path="/blog/tag/:tag" element={<LegacyAppLayout><BlogCategory /></LegacyAppLayout>} />
                
                {/* Legal and Company Pages */}
                <Route path="/privacy" element={<LegacyAppLayout><Privacy /></LegacyAppLayout>} />
                <Route path="/terms" element={<LegacyAppLayout><Terms /></LegacyAppLayout>} />
                <Route path="/contact" element={<LegacyAppLayout><ContactUs /></LegacyAppLayout>} />
                <Route path="/about" element={<LegacyAppLayout><About /></LegacyAppLayout>} />
                
                {/* Coming Soon Pages */}
                <Route path="/partners" element={<LegacyAppLayout><PartnerProgram /></LegacyAppLayout>} />
                <Route path="/partner-program" element={<LegacyAppLayout><PartnerProgram /></LegacyAppLayout>} />
                <Route path="/affiliates" element={<LegacyAppLayout><AffiliateProgram /></LegacyAppLayout>} />
                <Route path="/affiliate-program" element={<LegacyAppLayout><AffiliateProgram /></LegacyAppLayout>} />
                
                {/* Single Page Application Routes - No authentication required */}
                <Route path="/analysis/spa" element={<SPALayout><NewAnalysis /></SPALayout>} />
                
                {/* All Protected Routes - Using AppLayout */}
                <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                  <Route path="/dashboard" element={<ModernDashboard />} />
                  <Route path="/dashboard-old" element={<Dashboard />} />
                  <Route path="/dashboard-legacy" element={<DashboardHome />} />
                  <Route path="/analysis/new" element={<NewAnalysis />} />
                  {/* Projects Feature */}
                  <Route path="/projects" element={<ProjectsListNew />} />
                  <Route path="/projects/:id" element={<ProjectDetailNew />} />
                  <Route path="/history" element={<AnalysisHistoryNew />} />
                  <Route path="/profile" element={<Profile />} />
                  {/* Redirect old /team route to new /agency/team */}
                  <Route path="/team" element={<Navigate to="/agency/team" replace />} />
                  <Route path="/billing" element={<BillingCredits />} />
                  {/* Agency Routes */}
                  <Route path="/agency/integrations" element={<AgencyIntegrations />} />
                  <Route path="/agency/team" element={<AgencyTeamManagement />} />
                  <Route path="/agency/reports" element={<AgencyReportsBranding />} />
                  <Route path="/agency/white-label" element={<AgencyWhiteLabelSettings />} />
                  {/* Analysis Results */}
                  <Route path="/results/:analysisId" element={<AnalysisResultsPage />} />
                  <Route path="/results/simple/:projectId" element={<SimplifiedResults />} />
                  <Route path="/reports" element={<Reports />} />
                  {/* AI-Powered Tools */}
                  <Route path="/compliance-checker" element={<ComplianceChecker />} />
                  <Route path="/roi-generator" element={<ROICopyGenerator />} />
                  <Route path="/ab-test-generator" element={<ABTestGenerator />} />
                  <Route path="/industry-optimizer" element={<IndustryOptimizer />} />
                  <Route path="/performance-forensics" element={<PerformanceForensics />} />
                  <Route path="/psychology-scorer" element={<PsychologyScorer />} />
                  <Route path="/brand-voice-engine" element={<BrandVoiceEngine />} />
                  <Route path="/legal-risk-scanner" element={<LegalRiskScanner />} />
                  {/* Workspace Routes */}
                  <Route path="/project/new/workspace" element={<ProjectWorkspace />} />
                  <Route path="/project/:projectId/workspace" element={<ProjectWorkspace />} />
                </Route>
                
                
                {/* Redirects */}
                <Route path="/app" element={<Navigate to="/analysis/new" replace />} />
                </Routes>
                <Toaster position="top-right" />
                {/* <SupportWidget /> */} {/* Disabled until AWS SES is configured */}
              </Router>
              </BlogProvider>
            </AuthProvider>
          </SettingsProvider>
        </ThemeModeProvider>
      </WhiteLabelProvider>
    </QueryClientProvider>
    </NoWallet>
  );
}

export default App;
