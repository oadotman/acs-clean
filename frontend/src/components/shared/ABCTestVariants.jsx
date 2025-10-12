import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  Divider,
  LinearProgress,
  Alert,
  TextField
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  FileDownload as ExportIcon,
  Refresh as RefreshIcon,
  SwapHoriz as MixIcon,
  CheckCircle as CheckIcon,
  Psychology as BenefitIcon,
  Warning as ProblemIcon,
  AutoStories as StoryIcon,
  MoreVert as MoreIcon,
  Save as SaveIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import UserFeedback from './UserFeedback';

// Variant strategies and their configurations
const VARIANT_STRATEGIES = {
  A: {
    name: 'Benefit-Focused',
    icon: BenefitIcon,
    color: '#4caf50',
    psychology: 'Appeals to desired outcomes and gains',
    structure: 'Leads with the transformation or result',
    bestFor: ['Solution-seekers', 'Warm leads', 'Goal-oriented users'],
    example: '"Get X result in Y time"',
    description: 'Perfect for audiences who understand their problem and want to see the solution benefits upfront.',
    prompt: 'Create benefit-focused ad copy. Lead with the positive transformation and outcomes. Use aspirational, forward-looking language. Focus on what the user will gain, achieve, or become.'
  },
  B: {
    name: 'Problem-Focused',
    icon: ProblemIcon,
    color: '#ff9800',
    psychology: 'Identifies with pain points and frustrations',
    structure: 'Calls out the problem, then presents solution',
    bestFor: ['Pain-aware audiences', 'High urgency situations', 'Frustrated users'],
    example: '"Tired of X? Here\'s how to fix it"',
    description: 'Ideal for audiences experiencing pain who need validation and immediate solutions.',
    prompt: 'Create problem-focused ad copy. Start by identifying a specific pain point or frustration. Show empathy and understanding. Then position your offer as the direct solution to that problem.'
  },
  C: {
    name: 'Story-Driven',
    icon: StoryIcon,
    color: '#9c27b0',
    psychology: 'Creates emotional connection through narrative',
    structure: 'Mini-story or relatable scenario',
    bestFor: ['Building trust', 'Cold audiences', 'Emotional connection'],
    example: '"Sarah was struggling with X until..."',
    description: 'Best for building trust and emotional engagement with audiences who need social proof.',
    prompt: 'Create story-driven ad copy. Tell a brief, relatable story or scenario. Use a narrative structure with a character your audience can relate to. Make it human, emotional, and conversational.'
  }
};

const ABCTestVariants = ({
  variants = [],
  onGenerate,
  onRegenerateVariant,
  onSaveVariant,
  onMixAndMatch,
  onFeedbackSubmit,
  isGenerating = false,
  platform = 'facebook'
}) => {
  const [copiedStates, setCopiedStates] = useState({});
  const [showMixDialog, setShowMixDialog] = useState(false);
  const [exportMenuAnchor, setExportMenuAnchor] = useState(null);
  const [editingVariant, setEditingVariant] = useState(null);
  const [editedContent, setEditedContent] = useState({});

  // Handle copying variant to clipboard
  const handleCopy = (variantKey, text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [variantKey]: true }));
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [variantKey]: false }));
      }, 2000);
    });
  };

  // Handle export menu
  const handleExportMenuClick = (event) => {
    setExportMenuAnchor(event.currentTarget);
  };

  const handleExportMenuClose = () => {
    setExportMenuAnchor(null);
  };

  // Export functions
  const exportAsCSV = () => {
    const csvContent = [
      ['Version', 'Strategy', 'Headline', 'Body Text', 'CTA', 'Best For'],
      ...variants.map(variant => [
        variant.version,
        variant.strategy,
        variant.headline || '',
        variant.body_text || '',
        variant.cta || '',
        VARIANT_STRATEGIES[variant.version]?.bestFor.join('; ') || ''
      ])
    ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `abc-test-variants-${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    handleExportMenuClose();
  };

  const exportAsText = () => {
    const textContent = variants.map(variant => {
      const strategy = VARIANT_STRATEGIES[variant.version];
      return `VERSION ${variant.version}: ${strategy?.name}\n` +
             `Strategy: ${strategy?.psychology}\n` +
             `Best for: ${strategy?.bestFor.join(', ')}\n\n` +
             `Headline: ${variant.headline || ''}\n` +
             `Body: ${variant.body_text || ''}\n` +
             `CTA: ${variant.cta || ''}\n` +
             `\n${'='.repeat(50)}\n`;
    }).join('\n');

    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `abc-test-variants-${Date.now()}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
    handleExportMenuClose();
  };

  const copyAllToClipboard = () => {
    const allContent = variants.map(variant => {
      const strategy = VARIANT_STRATEGIES[variant.version];
      return `VERSION ${variant.version}: ${strategy?.name}\n${variant.headline || ''}\n\n${variant.body_text || ''}\n\n${variant.cta || ''}`;
    }).join('\n\n' + '='.repeat(30) + '\n\n');

    navigator.clipboard.writeText(allContent);
    handleExportMenuClose();
  };

  // Handle editing
  const handleEdit = (variant) => {
    setEditingVariant(variant.version);
    setEditedContent({
      headline: variant.headline || '',
      body_text: variant.body_text || '',
      cta: variant.cta || ''
    });
  };

  const handleSaveEdit = () => {
    // Update the variant with edited content
    // This would typically call a parent function to update the variants
    setEditingVariant(null);
    setEditedContent({});
  };

  const VariantCard = ({ variant, isLoading = false }) => {
    const strategy = VARIANT_STRATEGIES[variant.version];
    const IconComponent = strategy?.icon || BenefitIcon;
    const isCopied = copiedStates[variant.version];
    const isEditing = editingVariant === variant.version;

    const fullText = `${variant.headline || ''}\n\n${variant.body_text || ''}\n\n${variant.cta || ''}`.trim();

    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: variant.version.charCodeAt(0) * 0.1 }}
      >
        <Card 
          variant="outlined"
          sx={{
            height: '100%',
            border: `2px solid ${strategy?.color}20`,
            borderTop: `4px solid ${strategy?.color}`,
            position: 'relative',
            '&:hover': {
              boxShadow: `0 8px 25px ${strategy?.color}30`,
              transform: 'translateY(-2px)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          {isLoading && (
            <LinearProgress 
              sx={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                right: 0,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: strategy?.color
                }
              }} 
            />
          )}

          <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconComponent sx={{ color: strategy?.color, fontSize: '1.5rem' }} />
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: strategy?.color }}>
                    VERSION {variant.version}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                    {strategy?.name}
                  </Typography>
                </Box>
              </Box>
              
              <Chip
                label={`${variant.score || 85}/100`}
                size="small"
                sx={{
                  backgroundColor: `${strategy?.color}20`,
                  color: strategy?.color,
                  fontWeight: 600
                }}
              />
            </Box>

            {/* Strategy Info */}
            <Box sx={{ mb: 2, p: 2, backgroundColor: `${strategy?.color}08`, borderRadius: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                {strategy?.psychology}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {strategy?.description}
              </Typography>
            </Box>

            {/* Ad Content */}
            <Box sx={{ flex: 1, mb: 2 }}>
              {isEditing ? (
                <Stack spacing={2}>
                  <TextField
                    label="Headline"
                    value={editedContent.headline}
                    onChange={(e) => setEditedContent(prev => ({ ...prev, headline: e.target.value }))}
                    fullWidth
                    size="small"
                  />
                  <TextField
                    label="Body Text"
                    value={editedContent.body_text}
                    onChange={(e) => setEditedContent(prev => ({ ...prev, body_text: e.target.value }))}
                    fullWidth
                    multiline
                    rows={4}
                    size="small"
                  />
                  <TextField
                    label="CTA"
                    value={editedContent.cta}
                    onChange={(e) => setEditedContent(prev => ({ ...prev, cta: e.target.value }))}
                    fullWidth
                    size="small"
                  />
                </Stack>
              ) : (
                <Box>
                  {variant.headline && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                        HEADLINE
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary' }}>
                        {variant.headline}
                      </Typography>
                    </Box>
                  )}
                  
                  {variant.body_text && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                        BODY TEXT
                      </Typography>
                      <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                        {variant.body_text}
                      </Typography>
                    </Box>
                  )}
                  
                  {variant.cta && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                        CALL-TO-ACTION
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: strategy?.color }}>
                        {variant.cta}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </Box>

            {/* Best For Section */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, mb: 1, display: 'block' }}>
                BEST FOR:
              </Typography>
              <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                {strategy?.bestFor.map((item, index) => (
                  <Chip
                    key={index}
                    label={item}
                    size="small"
                    variant="outlined"
                    sx={{
                      fontSize: '0.7rem',
                      height: '24px',
                      borderColor: strategy?.color,
                      color: strategy?.color
                    }}
                  />
                ))}
              </Stack>
            </Box>

            {/* Action Buttons */}
            <Stack spacing={1}>
              {isEditing ? (
                <Stack direction="row" spacing={1}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={handleSaveEdit}
                    sx={{ 
                      backgroundColor: strategy?.color, 
                      '&:hover': { backgroundColor: strategy?.color + 'DD' },
                      flex: 1
                    }}
                  >
                    Save
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setEditingVariant(null)}
                    sx={{ color: strategy?.color, borderColor: strategy?.color }}
                  >
                    Cancel
                  </Button>
                </Stack>
              ) : (
                <Stack direction="row" spacing={1}>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={isCopied ? <CheckIcon /> : <CopyIcon />}
                    onClick={() => handleCopy(variant.version, fullText)}
                    disabled={isCopied}
                    sx={{ 
                      backgroundColor: strategy?.color, 
                      '&:hover': { backgroundColor: strategy?.color + 'DD' },
                      flex: 1
                    }}
                  >
                    {isCopied ? 'Copied!' : 'Copy'}
                  </Button>
                  
                  <Tooltip title="Edit this variant">
                    <IconButton
                      size="small"
                      onClick={() => handleEdit(variant)}
                      sx={{ color: strategy?.color }}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Regenerate this variant">
                    <IconButton
                      size="small"
                      onClick={() => onRegenerateVariant && onRegenerateVariant(variant.version)}
                      sx={{ color: strategy?.color }}
                    >
                      <RefreshIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Stack>
              )}

              <Button
                variant="outlined"
                size="small"
                onClick={() => onSaveVariant && onSaveVariant(variant)}
                sx={{ 
                  textTransform: 'none',
                  color: strategy?.color,
                  borderColor: strategy?.color
                }}
              >
                Use This Version
              </Button>
            </Stack>

            {/* User Feedback */}
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <UserFeedback
                generatedCopy={{
                  headline: variant.headline,
                  body: variant.body_text,
                  cta: variant.cta
                }}
                analysisId={`abc_variant_${variant.version}`}
                onFeedbackSubmit={onFeedbackSubmit}
                platform={platform}
                compact={true}
              />
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  if (!variants || variants.length === 0) {
    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Generate A/B/C Test Variants
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create 3 strategic variants to test different psychological approaches
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={onGenerate}
            disabled={isGenerating}
            startIcon={isGenerating ? null : <RefreshIcon />}
            sx={{ px: 4 }}
          >
            {isGenerating ? 'Generating Variants...' : 'Generate A/B/C Test Variants'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Card variant="outlined" sx={{ mb: 3, backgroundColor: 'rgba(25, 118, 210, 0.02)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                🧪 A/B/C Test Results - Ready to Test!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Three strategic variants designed to test different psychological approaches with your audience
              </Typography>
            </Box>
            
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                startIcon={<ExportIcon />}
                onClick={handleExportMenuClick}
              >
                Export All 3
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<MixIcon />}
                onClick={() => setShowMixDialog(true)}
              >
                Mix & Match
              </Button>
              
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={onGenerate}
                disabled={isGenerating}
              >
                Regenerate All
              </Button>
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {/* Variants Grid */}
      <Grid container spacing={3}>
        {variants.map((variant) => (
          <Grid item xs={12} lg={4} key={variant.version}>
            <VariantCard variant={variant} isLoading={isGenerating} />
          </Grid>
        ))}
      </Grid>

      {/* Testing Tips */}
      <Card variant="outlined" sx={{ mt: 3, backgroundColor: 'rgba(76, 175, 80, 0.02)' }}>
        <CardContent>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: 'success.main' }}>
            💡 Testing Tips for Best Results
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Start with Equal Budget
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Split your ad spend equally between all 3 variants for the first 48-72 hours
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Track Key Metrics
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Monitor CTR, conversion rate, and cost per conversion - not just clicks
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Let Data Decide
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Wait for statistical significance before choosing a winner (minimum 100 conversions)
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Export Menu */}
      <Menu
        anchorEl={exportMenuAnchor}
        open={Boolean(exportMenuAnchor)}
        onClose={handleExportMenuClose}
      >
        <MenuItem onClick={exportAsCSV}>
          <ExportIcon sx={{ mr: 1 }} />
          Export as CSV
        </MenuItem>
        <MenuItem onClick={exportAsText}>
          <ExportIcon sx={{ mr: 1 }} />
          Export as Text File
        </MenuItem>
        <MenuItem onClick={copyAllToClipboard}>
          <CopyIcon sx={{ mr: 1 }} />
          Copy All to Clipboard
        </MenuItem>
      </Menu>

      {/* Mix & Match Dialog */}
      <Dialog open={showMixDialog} onClose={() => setShowMixDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <MixIcon />
              <Typography variant="h6">Mix & Match Elements</Typography>
            </Box>
            <IconButton onClick={() => setShowMixDialog(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 3 }}>
            Combine the best elements from different variants to create your perfect ad copy
          </Alert>
          
          {/* Mix and match interface would go here */}
          <Typography variant="body2">
            Mix & Match functionality coming soon! For now, copy elements manually from each variant.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMixDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ABCTestVariants;