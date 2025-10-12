import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Alert } from '@mui/material';
import apiService from '../services/apiService';

const DebugAnalysis = () => {
  const [adText, setAdText] = useState('Test ad for debugging the analysis workflow');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);
      setResult(null);
      
      console.log('🧪 DebugAnalysis: Starting analysis...');
      
      const analysisData = {
        ad: {
          headline: adText.split('\n')[0] || adText,
          body_text: adText,
          cta: 'Click here',
          platform: 'facebook'
        }
      };
      
      console.log('🧪 DebugAnalysis: Calling apiService.analyzeAd...');
      const response = await apiService.analyzeAd(analysisData);
      
      console.log('🧪 DebugAnalysis: Got response:', response);
      setResult(response);
      
    } catch (err) {
      console.error('🧪 DebugAnalysis: Error:', err);
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        🧪 Debug Analysis Workflow
      </Typography>
      
      <TextField
        fullWidth
        multiline
        rows={4}
        label="Ad Text"
        value={adText}
        onChange={(e) => setAdText(e.target.value)}
        sx={{ mb: 3 }}
      />
      
      <Button
        variant="contained"
        onClick={handleAnalyze}
        disabled={isAnalyzing}
        sx={{ mb: 3 }}
      >
        {isAnalyzing ? 'Analyzing...' : 'Test Analysis'}
      </Button>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {result && (
        <Box>
          <Typography variant="h6" gutterBottom>
            ✅ Analysis Result:
          </Typography>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '16px', 
            borderRadius: '4px',
            overflow: 'auto',
            fontSize: '12px'
          }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Box>
      )}
    </Box>
  );
};

export default DebugAnalysis;