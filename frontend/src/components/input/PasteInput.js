import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  CircularProgress,
  Typography,
  Paper,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
} from '@mui/material';
import { ContentPaste, AutoFixHigh, CheckCircle } from '@mui/icons-material';
import toast from 'react-hot-toast';
import apiService from '../../services/apiService';

const PasteInput = ({ onAdCopiesParsed, onClear, defaultPlatform = 'facebook' }) => {
  const [pastedText, setPastedText] = useState('');
  const [parsing, setParsing] = useState(false);
  const [platform, setPlatform] = useState(defaultPlatform);
  const [parseResults, setParseResults] = useState(null);

  // Simple client-side parsing as fallback
  const parseClientSide = (text) => {
    // Split by double newlines to separate different ads
    const sections = text.split(/\n\s*\n/).filter(section => section.trim());
    
    const ads = sections.map((section, index) => {
      const lines = section.split('\n').map(line => line.trim()).filter(line => line);
      
      // Simple heuristics to identify headline, body, and CTA
      let headline = '', body_text = '', cta = '';
      
      if (lines.length >= 3) {
        // If we have 3+ lines, assume first is headline, last is CTA, middle is body
        headline = lines[0].replace(/^(headline:|title:)/i, '').trim();
        cta = lines[lines.length - 1].replace(/^(cta:|call to action:|action:)/i, '').trim();
        body_text = lines.slice(1, -1).join(' ').replace(/^(body:|description:|text:)/i, '').trim();
      } else if (lines.length === 2) {
        // 2 lines: headline and CTA or headline and body
        headline = lines[0];
        if (lines[1].length < 50) {
          cta = lines[1]; // Likely a CTA if short
        } else {
          body_text = lines[1]; // Likely body text if long
          cta = 'Learn More'; // Default CTA
        }
      } else if (lines.length === 1) {
        // Single line - could be a headline
        headline = lines[0];
        body_text = 'Compelling description goes here';
        cta = 'Get Started';
      }
      
      return {
        headline: headline || `Ad Copy ${index + 1}`,
        body_text: body_text || 'Add your compelling ad description here',
        cta: cta || 'Learn More',
        platform: platform,
        industry: '',
        target_audience: ''
      };
    });
    
    return { ads, warning: ads.length > 0 ? null : 'Could not parse the text. Please check the format.' };
  };

  const handleParse = async () => {
    if (!pastedText.trim()) {
      toast.error('Please paste some ad copy text to parse');
      return;
    }

    setParsing(true);
    try {
      // Try backend parsing first with timeout
      try {
        // Add timeout to prevent hanging
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Backend parsing timeout')), 15000); // 15 second timeout
        });
        
        const parsePromise = apiService.parsePastedCopy(pastedText, platform);
        const results = await Promise.race([parsePromise, timeoutPromise]);
        
        if (results.ads && results.ads.length > 0) {
          setParseResults(results);
          onAdCopiesParsed(results.ads);
          toast.success(`🎉 Parsed ${results.ads.length} ad${results.ads.length > 1 ? 's' : ''} successfully!`);
          return;
        }
      } catch (backendError) {
        console.warn('Backend parsing failed, using client-side fallback:', backendError);
        toast('Using offline parsing mode...', { icon: 'ℹ️' });
      }
      
      // Fallback to client-side parsing
      console.log('🔧 Attempting client-side parsing...');
      const results = parseClientSide(pastedText);
      console.log('📊 Client-side parsing results:', results);
      
      if (results.ads && results.ads.length > 0) {
        setParseResults(results);
        onAdCopiesParsed(results.ads);
        toast.success(`🎉 Parsed ${results.ads.length} ad${results.ads.length > 1 ? 's' : ''} successfully! (Client-side parsing)`);
      } else {
        toast.error('No ad copy could be parsed from the provided text');
      }
    } catch (error) {
      console.error('Parsing failed completely:', error);
      toast.error('Failed to parse ad copy. Please check the format and try again.');
    } finally {
      setParsing(false);
    }
  };

  const handleClear = () => {
    setPastedText('');
    setParseResults(null);
    if (onClear) onClear();
  };

  const exampleTexts = [
    "🚀 Finally, A CRM That Actually Works\nTired of juggling spreadsheets, missed follow-ups, and losing track of leads? Our AI-powered CRM automatically captures every interaction, predicts your best opportunities, and closes deals 3x faster. Join 50,000+ sales professionals who've increased their revenue by 40% in just 3 months.\nStart Your Free 14-Day Trial",
    "⚡ Stop Wasting $1,000s on Facebook Ads That Don't Convert\nMost businesses burn through their ad budget because they're targeting the wrong people with the wrong message. Our proprietary audience intelligence platform identifies your highest-value customers and creates laser-focused campaigns that deliver 5x ROI. Case study: Sarah's boutique went from $2k to $50k/month in 6 months.\nGet Your Free Strategy Session",
    "🎯 Transform Your Body in 90 Days (Without Giving Up Your Favorite Foods)\nForget extreme diets and 2-hour gym sessions. Our science-backed nutrition system and 20-minute workouts have helped 25,000+ busy professionals lose 15-50 lbs while eating foods they love. Dr. Martinez lost 35 lbs and kept it off for 2 years.\nClaim Your Spot (Only 100 Left)"
  ];

  return (
    <Box>
      {!parseResults ? (
        <Box>
          {/* Instructions */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>How to use:</strong> Paste ad copy from any source (Facebook, Google, CSV, email, etc.). 
              Our AI will automatically detect and extract headlines, body text, and call-to-actions.
            </Typography>
          </Alert>

          <Grid container spacing={3}>
            {/* Platform Selection */}
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Target Platform</InputLabel>
                <Select
                  value={platform}
                  label="Target Platform"
                  onChange={(e) => setPlatform(e.target.value)}
                >
                  <MenuItem value="facebook">Facebook Ads</MenuItem>
                  <MenuItem value="google">Google Ads</MenuItem>
                  <MenuItem value="linkedin">LinkedIn Ads</MenuItem>
                  <MenuItem value="tiktok">TikTok Ads</MenuItem>
                  <MenuItem value="instagram">Instagram Ads</MenuItem>
                  <MenuItem value="twitter">Twitter Ads</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Main paste area */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={12}
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Paste your ad copy here...&#10;&#10;Examples:&#10;• Multiple ads separated by blank lines&#10;• Facebook ad exports&#10;• CSV data&#10;• Any text containing headlines, descriptions, and CTAs&#10;&#10;The AI will automatically detect and parse the structure."
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    backgroundColor: 'rgba(0, 0, 0, 0.02)',
                  }
                }}
              />
            </Grid>

            {/* Examples */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom color="text.secondary">
                Quick Examples (click to use):
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {exampleTexts.map((example, index) => (
                  <Chip
                    key={index}
                    label={`Example ${index + 1}`}
                    variant="outlined"
                    clickable
                    size="small"
                    onClick={() => setPastedText(example)}
                    sx={{ fontSize: '0.75rem' }}
                  />
                ))}
              </Box>
            </Grid>

            {/* Actions */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={handleClear}
                  disabled={!pastedText && !parseResults}
                >
                  Clear
                </Button>
                <Button
                  variant="contained"
                  startIcon={parsing ? <CircularProgress size={20} /> : <AutoFixHigh />}
                  onClick={handleParse}
                  disabled={parsing || !pastedText.trim()}
                  sx={{ minWidth: 140 }}
                >
                  {parsing ? 'Parsing...' : 'Parse Ad Copy'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      ) : (
        <Box>
          {/* Parse Success */}
          <Alert severity="success" sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle fontSize="small" />
              <Typography variant="body2">
                Successfully parsed <strong>{parseResults.ads.length}</strong> ad copy{parseResults.ads.length > 1 ? ' entries' : ''}.
                {parseResults.warning && ` ${parseResults.warning}`}
              </Typography>
            </Box>
          </Alert>

          {/* Parse Summary */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              📋 Parse Results
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {parseResults.ads.map((ad, index) => (
                <Chip
                  key={index}
                  label={`Ad ${index + 1}: ${ad.headline?.substring(0, 30) || 'Untitled'}${ad.headline?.length > 30 ? '...' : ''}`}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Paper>

          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              startIcon={<ContentPaste />}
              onClick={handleClear}
            >
              Parse More Copy
            </Button>
            <Typography variant="body2" color="success.main" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle fontSize="small" />
              Ready to review and analyze
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default PasteInput;
