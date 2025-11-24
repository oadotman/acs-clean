import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  AlertTitle,
  Divider,
  Chip,
  Stack,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore,
  BugReport,
  CheckCircle,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh,
  ContentCopy
} from '@mui/icons-material';
import apiService from '../services/apiService';
import sharedWorkflowService from '../services/sharedWorkflowService';
import { supabase } from '../lib/supabaseClient';

const AnalysisDebugPage = () => {
  const [testPhase, setTestPhase] = useState('idle');
  const [logs, setLogs] = useState([]);
  const [testData, setTestData] = useState({
    headline: 'Test Headline for Debugging',
    bodyText: 'This is a test ad body text for debugging the analysis workflow. It should be long enough to trigger proper analysis.',
    cta: 'Click Here',
    platform: 'facebook',
    targetAudience: 'Test Audience',
    industry: 'Test Industry'
  });
  const [results, setResults] = useState({
    phase1: null, // Frontend state check
    phase2: null, // API service check
    phase3: null, // Backend endpoint check
    phase4: null, // Network request check
    phase5: null  // Full analysis result
  });
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const addLog = (message, type = 'info', data = null) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = {
      timestamp,
      message,
      type, // 'info', 'success', 'error', 'warning'
      data
    };
    setLogs(prev => [...prev, logEntry]);
    
    // Also log to console with appropriate method
    const consoleMessage = `[${timestamp}] ${message}`;
    switch(type) {
      case 'error':
        console.error(consoleMessage, data);
        break;
      case 'warning':
        console.warn(consoleMessage, data);
        break;
      case 'success':
        console.log('✅', consoleMessage, data);
        break;
      default:
        console.log(consoleMessage, data);
    }
  };

  const clearLogs = () => {
    setLogs([]);
    setResults({
      phase1: null,
      phase2: null,
      phase3: null,
      phase4: null,
      phase5: null
    });
    setError(null);
  };

  // Phase 1: Check Frontend State & Auth
  const testPhase1 = async () => {
    addLog('🔍 Phase 1: Testing Frontend State & Authentication', 'info');
    
    try {
      // Check Supabase auth
      const { data: { session } } = await supabase.auth.getSession();
      addLog('Supabase session check', session ? 'success' : 'warning', {
        hasSession: !!session,
        hasUser: !!session?.user,
        userId: session?.user?.id
      });
      
      // Check API service configuration
      addLog('API Service baseURL check', 'info', {
        baseURL: apiService.baseURL
      });
      
      if (!apiService.baseURL.startsWith('http')) {
        addLog('⚠️ API baseURL missing protocol', 'warning');
      } else {
        addLog('✅ API baseURL configured correctly', 'success');
      }
      
      setResults(prev => ({
        ...prev,
        phase1: {
          success: true,
          hasAuth: !!session,
          apiConfigured: apiService.baseURL.startsWith('http')
        }
      }));
      
      return true;
    } catch (err) {
      addLog('❌ Phase 1 failed', 'error', err);
      setResults(prev => ({ ...prev, phase1: { success: false, error: err.message } }));
      return false;
    }
  };

  // Phase 2: Test API Service Method
  const testPhase2 = async () => {
    addLog('🔍 Phase 2: Testing API Service analyzeAd Method', 'info');
    
    try {
      // Check if method exists
      if (typeof apiService.analyzeAd !== 'function') {
        throw new Error('apiService.analyzeAd is not a function');
      }
      addLog('✅ apiService.analyzeAd method exists', 'success');
      
      // Prepare test data
      const analysisData = {
        ad: {
          headline: testData.headline,
          body_text: testData.bodyText,
          cta: testData.cta,
          platform: testData.platform,
          industry: testData.industry,
          target_audience: testData.targetAudience
        },
        competitor_ads: []
      };
      
      addLog('Prepared analysis data', 'info', analysisData);
      
      setResults(prev => ({
        ...prev,
        phase2: {
          success: true,
          methodExists: true,
          dataFormatted: true
        }
      }));
      
      return { success: true, analysisData };
    } catch (err) {
      addLog('❌ Phase 2 failed', 'error', err);
      setResults(prev => ({ ...prev, phase2: { success: false, error: err.message } }));
      return { success: false };
    }
  };

  // Phase 3: Test Network Request (without waiting for response)
  const testPhase3 = async (analysisData) => {
    addLog('🔍 Phase 3: Testing Network Request', 'info');
    
    try {
      addLog('Sending POST request to /api/ads/analyze', 'info');
      
      // Monitor network activity
      const startTime = Date.now();
      
      // Try to make the request
      const requestPromise = apiService.post('/ads/analyze', analysisData);
      
      addLog('Request initiated successfully', 'success', {
        endpoint: '/ads/analyze',
        method: 'POST'
      });
      
      setResults(prev => ({
        ...prev,
        phase3: {
          success: true,
          requestSent: true,
          endpoint: '/api/ads/analyze'
        }
      }));
      
      return { success: true, requestPromise, startTime };
    } catch (err) {
      addLog('❌ Phase 3 failed - Request not sent', 'error', err);
      setResults(prev => ({ ...prev, phase3: { success: false, error: err.message } }));
      return { success: false };
    }
  };

  // Phase 4: Wait for Backend Response
  const testPhase4 = async (requestPromise, startTime) => {
    addLog('🔍 Phase 4: Waiting for Backend Response', 'info');
    
    try {
      const response = await requestPromise;
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      addLog(`✅ Backend response received in ${duration}ms`, 'success', {
        duration,
        hasAnalysisId: !!response.analysis_id,
        hasScores: !!response.scores,
        hasAlternatives: !!response.alternatives
      });
      
      setResults(prev => ({
        ...prev,
        phase4: {
          success: true,
          duration,
          response
        }
      }));
      
      return { success: true, response };
    } catch (err) {
      addLog('❌ Phase 4 failed - Backend error', 'error', {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data
      });
      
      setResults(prev => ({
        ...prev,
        phase4: {
          success: false,
          error: err.message,
          status: err.response?.status,
          details: err.response?.data
        }
      }));
      
      return { success: false, error: err };
    }
  };

  // Phase 5: Test sharedWorkflowService (alternative path)
  const testPhase5Alternative = async () => {
    addLog('🔍 Phase 5 (Alternative): Testing sharedWorkflowService', 'info');
    
    try {
      const analysisData = {
        headline: testData.headline,
        body_text: testData.bodyText,
        cta: testData.cta,
        platform: testData.platform,
        industry: testData.industry,
        target_audience: testData.targetAudience
      };
      
      addLog('Calling sharedWorkflowService.startAdhocAnalysis', 'info');
      
      const response = await sharedWorkflowService.startAdhocAnalysis(analysisData);
      
      addLog('✅ sharedWorkflowService analysis completed', 'success', response);
      
      setResults(prev => ({
        ...prev,
        phase5: {
          success: true,
          method: 'sharedWorkflowService',
          response
        }
      }));
      
      return { success: true, response };
    } catch (err) {
      addLog('❌ Phase 5 failed', 'error', err);
      setResults(prev => ({ ...prev, phase5: { success: false, error: err.message } }));
      return { success: false };
    }
  };

  // Run all tests sequentially
  const runFullWorkflowTest = async () => {
    setIsRunning(true);
    setTestPhase('running');
    clearLogs();
    
    addLog('🚀 Starting Complete Workflow Test', 'info');
    addLog('═══════════════════════════════════════', 'info');
    
    try {
      // Phase 1
      setTestPhase('phase1');
      const phase1Result = await testPhase1();
      if (!phase1Result) {
        throw new Error('Phase 1 failed - stopping test');
      }
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Phase 2
      setTestPhase('phase2');
      const phase2Result = await testPhase2();
      if (!phase2Result.success) {
        throw new Error('Phase 2 failed - stopping test');
      }
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Phase 3 & 4
      setTestPhase('phase3');
      const phase3Result = await testPhase3(phase2Result.analysisData);
      if (!phase3Result.success) {
        throw new Error('Phase 3 failed - stopping test');
      }
      
      setTestPhase('phase4');
      const phase4Result = await testPhase4(phase3Result.requestPromise, phase3Result.startTime);
      
      if (phase4Result.success) {
        addLog('═══════════════════════════════════════', 'success');
        addLog('🎉 All phases completed successfully!', 'success');
        setTestPhase('success');
      } else {
        // Try alternative path
        addLog('═══════════════════════════════════════', 'warning');
        addLog('⚠️ Main path failed, trying alternative...', 'warning');
        setTestPhase('phase5');
        await testPhase5Alternative();
        setTestPhase('partial');
      }
      
    } catch (err) {
      addLog('═══════════════════════════════════════', 'error');
      addLog('❌ Workflow test failed', 'error', err);
      setError(err.message);
      setTestPhase('failed');
    } finally {
      setIsRunning(false);
    }
  };

  // Quick test buttons
  const quickTestApiService = async () => {
    setIsRunning(true);
    clearLogs();
    
    try {
      const analysisData = {
        ad: {
          headline: testData.headline,
          body_text: testData.bodyText,
          cta: testData.cta,
          platform: testData.platform
        }
      };
      
      addLog('🧪 Quick Test: apiService.analyzeAd', 'info');
      const response = await apiService.analyzeAd(analysisData);
      addLog('✅ Success!', 'success', response);
    } catch (err) {
      addLog('❌ Failed', 'error', err);
    } finally {
      setIsRunning(false);
    }
  };

  const getPhaseStatus = (phase) => {
    if (!results[phase]) return 'pending';
    return results[phase].success ? 'success' : 'error';
  };

  const getPhaseIcon = (phase) => {
    const status = getPhaseStatus(phase);
    switch(status) {
      case 'success': return <CheckCircle color="success" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <WarningIcon color="disabled" />;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
          <BugReport fontSize="large" color="primary" />
          <Typography variant="h4" fontWeight={700}>
            Ad Analysis Workflow Debugger
          </Typography>
        </Box>

        {/* Test Configuration */}
        <Paper variant="outlined" sx={{ p: 3, mb: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Test Configuration
          </Typography>
          <Stack spacing={2}>
            <TextField
              label="Headline"
              value={testData.headline}
              onChange={(e) => setTestData({ ...testData, headline: e.target.value })}
              fullWidth
              size="small"
            />
            <TextField
              label="Body Text"
              value={testData.bodyText}
              onChange={(e) => setTestData({ ...testData, bodyText: e.target.value })}
              fullWidth
              multiline
              rows={3}
              size="small"
            />
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                label="CTA"
                value={testData.cta}
                onChange={(e) => setTestData({ ...testData, cta: e.target.value })}
                size="small"
              />
              <FormControl size="small">
                <InputLabel>Platform</InputLabel>
                <Select
                  value={testData.platform}
                  label="Platform"
                  onChange={(e) => setTestData({ ...testData, platform: e.target.value })}
                >
                  <MenuItem value="facebook">Facebook</MenuItem>
                  <MenuItem value="instagram">Instagram</MenuItem>
                  <MenuItem value="google">Google</MenuItem>
                  <MenuItem value="linkedin">LinkedIn</MenuItem>
                  <MenuItem value="tiktok">TikTok</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Stack>
        </Paper>

        {/* Test Controls */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            size="large"
            onClick={runFullWorkflowTest}
            disabled={isRunning}
            startIcon={isRunning ? <LinearProgress /> : <BugReport />}
          >
            {isRunning ? 'Running Tests...' : 'Run Complete Test'}
          </Button>
          <Button
            variant="outlined"
            onClick={quickTestApiService}
            disabled={isRunning}
          >
            Quick Test: API Service
          </Button>
          <Button
            variant="outlined"
            onClick={clearLogs}
            startIcon={<Refresh />}
          >
            Clear Logs
          </Button>
        </Box>

        {/* Test Progress */}
        {isRunning && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Current Phase: <Chip label={testPhase} size="small" color="primary" />
            </Typography>
            <LinearProgress />
          </Box>
        )}

        {/* Phase Results */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Test Results
          </Typography>
          <Stack spacing={1}>
            {['phase1', 'phase2', 'phase3', 'phase4', 'phase5'].map((phase, index) => (
              <Card key={phase} variant="outlined">
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 1.5 }}>
                  {getPhaseIcon(phase)}
                  <Typography variant="body1" sx={{ flex: 1 }}>
                    Phase {index + 1}: {phase.replace('phase', '')}
                  </Typography>
                  {results[phase] && (
                    <Chip 
                      label={results[phase].success ? 'Pass' : 'Fail'}
                      color={results[phase].success ? 'success' : 'error'}
                      size="small"
                    />
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>

        {/* Logs */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              Test Logs ({logs.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ maxHeight: 400, overflow: 'auto', bgcolor: 'grey.900', p: 2, borderRadius: 1 }}>
              <List dense>
                {logs.map((log, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography
                            variant="caption"
                            sx={{
                              color: log.type === 'error' ? 'error.light' :
                                     log.type === 'success' ? 'success.light' :
                                     log.type === 'warning' ? 'warning.light' :
                                     'info.light',
                              fontFamily: 'monospace'
                            }}
                          >
                            [{log.timestamp}]
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: log.type === 'error' ? 'error.light' :
                                     log.type === 'success' ? 'success.light' :
                                     log.type === 'warning' ? 'warning.light' :
                                     'grey.300',
                              fontFamily: 'monospace'
                            }}
                          >
                            {log.message}
                          </Typography>
                          {log.data && (
                            <Tooltip title="Copy data to clipboard">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  navigator.clipboard.writeText(JSON.stringify(log.data, null, 2));
                                }}
                              >
                                <ContentCopy fontSize="small" sx={{ color: 'grey.500' }} />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      }
                      secondary={
                        log.data && (
                          <Typography
                            variant="caption"
                            component="pre"
                            sx={{
                              color: 'grey.400',
                              fontFamily: 'monospace',
                              fontSize: '0.7rem',
                              mt: 0.5,
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-all'
                            }}
                          >
                            {JSON.stringify(log.data, null, 2)}
                          </Typography>
                        )
                      }
                    />
                  </ListItem>
                ))}
                {logs.length === 0 && (
                  <Typography variant="body2" sx={{ color: 'grey.500', textAlign: 'center', py: 2 }}>
                    No logs yet. Run a test to see diagnostics.
                  </Typography>
                )}
              </List>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Instructions */}
        <Alert severity="info" sx={{ mt: 3 }}>
          <AlertTitle>How to Use This Debugger</AlertTitle>
          <Typography variant="body2">
            1. Click "Run Complete Test" to test the entire workflow from frontend to backend<br />
            2. Check each phase's result to identify where the failure occurs<br />
            3. Review logs for detailed diagnostic information<br />
            4. Open browser DevTools Network tab to see actual HTTP requests<br />
            5. Check browser console for additional error details
          </Typography>
        </Alert>
      </Paper>
    </Container>
  );
};

export default AnalysisDebugPage;
