import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
  Collapse,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  alpha,
  useTheme
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  FileUpload as FileIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckIcon,
  ContentCopy as CopyIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import toast from 'react-hot-toast';

const BatchAnalysis = ({ onClose, onBackToDashboard }) => {
  const theme = useTheme();
  const fileInputRef = useRef(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [showIndividualResults, setShowIndividualResults] = useState(false);
  const [copiedStates, setCopiedStates] = useState({});

  // Mock batch analysis results
  const batchResults = {
    campaignName: 'Summer Campaign',
    totalAds: 5,
    averageScore: 78,
    totalIssues: 7,
    criticalIssues: 3,
    highImpactIssues: 4,
    patterns: [
      {
        type: 'critical',
        count: 3,
        description: '3 of 5 ads have weak CTAs (avg score: 4.2/10)',
        detail: 'All three use generic "Shop Now"'
      },
      {
        type: 'critical',
        count: 2,
        description: '2 of 5 ads have same compliance violation',
        detail: 'Both use "guaranteed results" language'
      }
    ],
    individualResults: [
      {
        id: 1,
        original: 'Flash Sale! Get 50% off everything today only!',
        improved: 'Last 6 Hours: Save 50% on Premium Items',
        originalScore: 65,
        improvedScore: 88,
        improvement: 23,
        status: 'completed',
        keyIssues: ['Weak urgency', 'No social proof']
      },
      {
        id: 2,
        original: 'Guaranteed results or your money back!',
        improved: 'Proven track record: Join 10,000+ satisfied customers',
        originalScore: 45,
        improvedScore: 82,
        improvement: 37,
        status: 'completed',
        keyIssues: ['Policy violation', 'Generic claim']
      },
      {
        id: 3,
        original: 'Shop now for the best deals ever!',
        improved: 'Unlock Exclusive Member Pricing - Limited Time',
        originalScore: 58,
        improvedScore: 85,
        improvement: 27,
        status: 'completed',
        keyIssues: ['Weak CTA', 'Vague offer']
      },
      {
        id: 4,
        original: 'Amazing products at unbeatable prices',
        improved: '2,000+ five-star reviews: Premium quality, fair prices',
        originalScore: 52,
        improvedScore: 79,
        improvement: 27,
        status: 'completed',
        keyIssues: ['No specificity', 'Missing social proof']
      },
      {
        id: 5,
        original: 'Don\'t miss out on this incredible opportunity',
        improved: 'Join 15,000+ who saved big this month - Ends tomorrow',
        originalScore: 48,
        improvedScore: 81,
        improvement: 33,
        status: 'completed',
        keyIssues: ['Vague language', 'No deadline']
      }
    ]
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        toast.error('Please upload a CSV file');
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast.error('File size must be less than 5MB');
        return;
      }
      
      setUploadedFile(file);
      toast.success('CSV file uploaded successfully!');
    }
  };

  const handleAnalyzeBatch = () => {
    if (!uploadedFile) return;
    
    setIsAnalyzing(true);
    toast.loading('Analyzing your campaign...', { duration: 10000 });
    
    // Simulate batch analysis process
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysisComplete(true);
      toast.success('Batch analysis complete!');
    }, 10000);
  };

  const handleCopyText = (text, id) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      toast.success('Copied to clipboard!');
      
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
    }).catch(() => {
      toast.error('Failed to copy to clipboard');
    });
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  if (analysisComplete) {
    return (
      <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" fontWeight={700}>
            CAMPAIGN RESULTS: {batchResults.campaignName}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Campaign Summary */}
        <Card elevation={3} sx={{ mb: 4 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" fontWeight={700} color="primary.main">
                    {batchResults.averageScore}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Campaign Average
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" fontWeight={700} color="error.main">
                    {batchResults.totalIssues}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Issues ({batchResults.criticalIssues} critical, {batchResults.highImpactIssues} high-impact)
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Patterns Detected:
                </Typography>
                {batchResults.patterns.map((pattern, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <ErrorIcon sx={{ color: 'error.main', fontSize: '1rem' }} />
                      <Typography variant="body2" fontWeight={600}>
                        {pattern.description}
                      </Typography>
                    </Box>
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ ml: 3, fontStyle: 'italic' }}
                    >
                      → {pattern.detail}
                    </Typography>
                  </Box>
                ))}
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  These are fixable issues we detected across multiple ads.
                  Each ad's improved version addresses these.
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Individual Results Toggle */}
        <Card elevation={2} sx={{ mb: 4 }}>
          <CardContent>
            <Button
              variant="text"
              onClick={() => setShowIndividualResults(!showIndividualResults)}
              endIcon={showIndividualResults ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ 
                textTransform: 'none', 
                fontWeight: 600,
                fontSize: '1.1rem'
              }}
            >
              Show Individual Results ▾
            </Button>
          </CardContent>
        </Card>

        {/* Individual Results Grid */}
        <Collapse in={showIndividualResults}>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {batchResults.individualResults.map((result) => (
              <Grid item xs={12} lg={6} key={result.id}>
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
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" fontWeight={600}>
                        Ad {result.id}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip
                          label={`${result.originalScore} → ${result.improvedScore}`}
                          color={getScoreColor(result.improvedScore)}
                          variant="outlined"
                          size="small"
                        />
                        <Chip
                          label={`+${result.improvement}`}
                          color="success"
                          variant="filled"
                          size="small"
                        />
                      </Box>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Original:
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          p: 1.5,
                          backgroundColor: alpha(theme.palette.error.main, 0.05),
                          borderRadius: 1,
                          mb: 2,
                          border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`
                        }}
                      >
                        "{result.original}"
                      </Typography>

                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Improved:
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          p: 1.5,
                          backgroundColor: alpha(theme.palette.success.main, 0.05),
                          borderRadius: 1,
                          border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`
                        }}
                      >
                        "{result.improved}"
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Key Issues Fixed:
                      </Typography>
                      {result.keyIssues.map((issue, idx) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CheckIcon sx={{ fontSize: '0.875rem', color: 'success.main' }} />
                          <Typography variant="caption">
                            {issue}
                          </Typography>
                        </Box>
                      ))}
                    </Box>

                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={copiedStates[`batch-${result.id}`] ? <CheckIcon /> : <CopyIcon />}
                      onClick={() => handleCopyText(result.improved, `batch-${result.id}`)}
                      disabled={copiedStates[`batch-${result.id}`]}
                      fullWidth
                      sx={{ textTransform: 'none' }}
                    >
                      {copiedStates[`batch-${result.id}`] ? 'Copied ✓' : 'Copy Improved Version'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Collapse>

        {/* Bottom Actions */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', pt: 4 }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => {
              setAnalysisComplete(false);
              setUploadedFile(null);
            }}
            sx={{ fontWeight: 600, textTransform: 'none', px: 4 }}
          >
            Analyze Another Campaign
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={onBackToDashboard}
            sx={{ fontWeight: 600, textTransform: 'none', px: 4 }}
          >
            Back to Dashboard
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Batch Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload a CSV file with 2-20 ads for campaign analysis
        </Typography>
      </Box>

      {/* Upload Section */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".csv"
            style={{ display: 'none' }}
          />
          
          <Box
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: 2,
              borderStyle: 'dashed',
              borderColor: uploadedFile ? 'success.main' : 'primary.main',
              borderRadius: 3,
              p: 6,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: uploadedFile 
                ? alpha(theme.palette.success.main, 0.05)
                : alpha(theme.palette.primary.main, 0.05),
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: uploadedFile
                  ? alpha(theme.palette.success.main, 0.1)
                  : alpha(theme.palette.primary.main, 0.1),
                transform: 'scale(1.02)'
              }
            }}
          >
            {uploadedFile ? (
              <>
                <CheckIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  File uploaded successfully!
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                </Typography>
              </>
            ) : (
              <>
                <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Click to upload CSV file
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or drag and drop your file here
                </Typography>
              </>
            )}
          </Box>
          
          {uploadedFile && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button
                variant="text"
                onClick={() => {
                  setUploadedFile(null);
                  if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                  }
                }}
                sx={{ textTransform: 'none' }}
              >
                Upload different file
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* CSV Format Requirements */}
      <Alert severity="info" sx={{ mb: 4 }}>
        <Typography variant="body2" fontWeight={600} gutterBottom>
          CSV Format Requirements:
        </Typography>
        <Typography variant="body2" component="div">
          • First column: Ad copy text<br />
          • Maximum 20 rows (ads)<br />
          • File size limit: 5MB<br />
          • Header row optional
        </Typography>
      </Alert>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleAnalyzeBatch}
          disabled={!uploadedFile || isAnalyzing}
          startIcon={isAnalyzing ? null : <FileIcon />}
          sx={{
            fontWeight: 700,
            textTransform: 'none',
            px: 4,
            py: 1.5
          }}
        >
          {isAnalyzing ? 'Analyzing Campaign...' : 'Analyze Campaign'}
        </Button>
        
        <Button
          variant="outlined"
          size="large"
          onClick={onClose}
          sx={{
            fontWeight: 600,
            textTransform: 'none',
            px: 4,
            py: 1.5
          }}
        >
          Cancel
        </Button>
      </Box>

      {/* Progress Indicator */}
      {isAnalyzing && (
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Analyzing your campaign...
              </Typography>
              <LinearProgress 
                sx={{ 
                  mb: 2,
                  height: 8,
                  borderRadius: 4
                }} 
              />
              <Typography variant="body2" color="text.secondary">
                Running analysis on multiple ads • This may take up to 30 seconds
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default BatchAnalysis;