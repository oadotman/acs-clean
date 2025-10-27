import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Tabs,
  Tab,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  RadioGroup,
  Radio,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Checkbox,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  BarChart as ReportsIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Palette as PaletteIcon,
  Preview as PreviewIcon,
  Add as AddIcon,
  AutoAwesome as AIIcon,
  PictureAsPdf as PDFIcon,
  Description as DOCXIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

// Import services
import { useAuth } from '../../services/authContext';
import { supabase } from '../../lib/supabaseClientClean';
import { useWhiteLabel } from '../../contexts/WhiteLabelContext';
import { BrandLogo, CompanyName } from '../../components/whiteLabel/BrandingComponents';
import toast from 'react-hot-toast';

const AgencyReportsBranding = () => {
  const { user } = useAuth();
  const { effectiveBranding, settings: whiteLabelSettings } = useWhiteLabel();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [analyses, setAnalyses] = useState([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(true);
  
  // Report creation state
  const [reportType, setReportType] = useState('');
  const [reportTitle, setReportTitle] = useState('');
  const [selectedAnalyses, setSelectedAnalyses] = useState([]);
  const [executiveSummary, setExecutiveSummary] = useState('');
  const [generatingReport, setGeneratingReport] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [reportPreview, setReportPreview] = useState(null);
  const [editMode, setEditMode] = useState(false);
  
  // Brand settings state - now integrated with white-label context
  const [brandSettings, setBrandSettings] = useState({
    companyName: effectiveBranding.companyName || 'Your Agency',
    logo: effectiveBranding.logo || null,
    primaryColor: effectiveBranding.primaryColor || '#2563eb',
    secondaryColor: effectiveBranding.secondaryColor || '#7c3aed',
    includeFooter: false,
    defaultFormat: 'pdf',
    includePoweredBy: effectiveBranding.showPoweredBy !== false
  });

  // Load user's analyses and sync with white-label settings
  useEffect(() => {
    if (user) {
      loadUserAnalyses();
    }
  }, [user]);
  
  // Sync brand settings with white-label context
  useEffect(() => {
    setBrandSettings(prev => {
      const next = {
        ...prev,
        companyName: effectiveBranding.companyName || prev.companyName,
        logo: effectiveBranding.logo || prev.logo,
        primaryColor: effectiveBranding.primaryColor || prev.primaryColor,
        secondaryColor: effectiveBranding.secondaryColor || prev.secondaryColor,
        includePoweredBy: effectiveBranding.showPoweredBy !== false
      };
      
      // Only update if values actually changed to prevent unnecessary re-renders
      const hasChanged = (
        next.companyName !== prev.companyName ||
        next.logo !== prev.logo ||
        next.primaryColor !== prev.primaryColor ||
        next.secondaryColor !== prev.secondaryColor ||
        next.includePoweredBy !== prev.includePoweredBy
      );
      
      if (hasChanged) {
        console.log('🎨 Synced brand settings with white-label context:', effectiveBranding);
        return next;
      }
      
      return prev;
    });
  }, [effectiveBranding]);

  const loadUserAnalyses = async () => {
    try {
      setLoadingAnalyses(true);
      console.log('📊 Reports: Loading analyses for user:', user?.id);
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .select(`
          id,
          headline,
          body_text,
          cta,
          platform,
          overall_score,
          clarity_score,
          persuasion_score,
          emotion_score,
          cta_strength_score,
          platform_fit_score,
          created_at,
          projects (name)
        `)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(50);

      console.log('📊 Reports: Supabase response:', { data, error, userID: user?.id });
      
      if (error) {
        console.error('Error loading analyses:', error);
        toast.error('Failed to load analyses');
      } else {
        console.log('📊 Reports: Found', data?.length || 0, 'analyses');
        
        // Debug: Check score values
        if (data?.length > 0) {
          console.log('📊 First analysis sample:', {
            headline: data[0].headline,
            overall_score: data[0].overall_score,
            clarity_score: data[0].clarity_score,
            scores_type: typeof data[0].overall_score,
            raw_data: data[0]
          });
          
          const nullScores = data.filter(a => a.overall_score === null || a.overall_score === undefined);
          if (nullScores.length > 0) {
            console.warn('⚠️ Found', nullScores.length, 'analyses with null scores');
          }
        }
        
        setAnalyses(data || []);
      }
    } catch (error) {
      console.error('Error loading analyses:', error);
      toast.error('Failed to load analyses');
    } finally {
      setLoadingAnalyses(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleReportTypeChange = (event) => {
    setReportType(event.target.value);
    setSelectedAnalyses([]);
    
    // Set default title based on report type
    const defaultTitles = {
      'before': 'Ad Performance Audit & Recommendations',
      'before-after': 'Before/After Ad Analysis Report',
      'single': 'Ad Analysis Report',
      'multi': 'Multi-Analysis Comparison Report'
    };
    setReportTitle(defaultTitles[event.target.value] || '');
  };

  const handleAnalysisSelection = (analysisId) => {
    setSelectedAnalyses(prev => {
      if (prev.includes(analysisId)) {
        return prev.filter(id => id !== analysisId);
      } else {
        // Limit based on report type
        const maxSelections = {
          'before': 1,
          'before-after': 2,
          'single': 1,
          'multi': 5
        };
        const max = maxSelections[reportType] || 1;
        
        if (prev.length >= max) {
          toast.warning(`Maximum ${max} analyses allowed for this report type`);
          return prev;
        }
        return [...prev, analysisId];
      }
    });
  };

  const generateAISummary = async () => {
    if (selectedAnalyses.length === 0) {
      toast.error('Please select analyses first');
      return;
    }

    setLoading(true);
    try {
      // Get selected analyses data
      const selectedData = analyses.filter(a => selectedAnalyses.includes(a.id));
      
      // Simple AI-like summary generation
      let summary = '';
      if (reportType === 'before' && selectedData.length === 1) {
        const analysis = selectedData[0];
        const score = analysis.overall_score || 0;
        const issues = [];
        
        console.log('📊 Generating summary for analysis:', { analysis, score });
        
        // Identify specific problems - handle null/undefined scores
        if ((analysis.clarity_score || 0) < 7) issues.push('unclear messaging that confuses your audience');
        if ((analysis.persuasion_score || 0) < 7) issues.push('weak persuasive elements that fail to convince');
        if ((analysis.emotion_score || 0) < 7) issues.push('lack of emotional connection with potential customers');
        if ((analysis.cta_strength_score || 0) < 7) issues.push('weak call-to-action that doesn\'t drive conversions');
        if ((analysis.platform_fit_score || 0) < 7) issues.push('poor platform optimization reducing visibility');
        
        summary = `**AUDIT FINDINGS:** Your current ad is performing at ${score.toFixed(1)}/10, significantly below industry benchmarks. `;
        
        if (issues.length > 0) {
          summary += `Key issues identified: ${issues.join(', ')}. `;
        }
        
        if (score < 6) {
          summary += `This low performance is likely costing you thousands in wasted ad spend and missed conversions. `;
        } else if (score < 8) {
          summary += `While functional, significant improvements are needed to maximize ROI. `;
        }
        
        summary += `Our analysis shows clear opportunities to boost performance by 30-50% through targeted optimizations. Ready to see how we can transform this ad into a high-converting powerhouse?`;
      } else if (reportType === 'before-after' && selectedData.length === 2) {
        const [first, second] = selectedData;
        const improvement = second.overall_score - first.overall_score;
        summary = `This before/after analysis shows ${improvement > 0 ? 'significant improvements' : 'areas for optimization'} in ad performance. `;
        summary += `The overall score ${improvement > 0 ? 'increased' : 'decreased'} by ${Math.abs(improvement).toFixed(1)} points, `;
        summary += `with notable changes in clarity, persuasion, and emotional appeal metrics.`;
      } else if (reportType === 'single' && selectedData.length === 1) {
        const analysis = selectedData[0];
        summary = `This comprehensive analysis reveals an overall performance score of ${analysis.overall_score.toFixed(1)}/10. `;
        summary += `Key strengths include ${analysis.clarity_score > 7 ? 'clear messaging' : ''} ${analysis.persuasion_score > 7 ? 'and persuasive content' : ''}. `;
        summary += `Recommendations focus on improving ${analysis.overall_score < 7 ? 'overall effectiveness' : 'specific performance areas'}.`;
      } else if (reportType === 'multi') {
        const avgScore = selectedData.reduce((sum, a) => sum + a.overall_score, 0) / selectedData.length;
        summary = `This multi-analysis comparison examines ${selectedData.length} different ad variations with an average performance score of ${avgScore.toFixed(1)}/10. `;
        summary += `The analysis identifies top-performing elements and provides actionable insights for campaign optimization.`;
      }
      
      setExecutiveSummary(summary);
      toast.success('AI summary generated!');
    } catch (error) {
      console.error('Error generating summary:', error);
      toast.error('Failed to generate AI summary');
    } finally {
      setLoading(false);
    }
  };

  const generatePreview = async () => {
    if (!reportType || selectedAnalyses.length === 0 || !reportTitle) {
      toast.error('Please complete all required fields');
      return;
    }

    setLoading(true);
    try {
      // Get selected analyses data
      const selectedData = analyses.filter(a => selectedAnalyses.includes(a.id));
      
      console.log('📋 Generating preview with data:', {
        reportType,
        selectedAnalyses: selectedAnalyses.length,
        selectedData: selectedData.length,
        reportTitle,
        executiveSummary: executiveSummary ? 'Present' : 'Empty'
      });
      
      // Generate report preview
      const preview = {
        type: reportType,
        title: reportTitle,
        summary: executiveSummary,
        analyses: selectedData,
        branding: brandSettings,
        createdAt: new Date().toLocaleDateString(),
        createdBy: user?.email || 'User'
      };
      
      console.log('📋 Preview generated:', preview);
      
      setReportPreview(preview);
      setShowPreview(true);
      setEditMode(false); // Reset edit mode
      toast.success('Preview generated!');
    } catch (error) {
      console.error('Error generating preview:', error);
      toast.error('Failed to generate preview');
    } finally {
      setLoading(false);
    }
  };

  const generateDOCXReport = async () => {
    if (!reportPreview) {
      toast.error('Please generate preview first');
      return;
    }

    setGeneratingReport(true);
    try {
      // Try to dynamically import docx library - if it fails, offer alternative
      try {
        const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = await import('docx');
        
        // Create DOCX document
        const doc = new Document({
          sections: [{
            properties: {},
            children: [
              // Company name header
              new Paragraph({
                children: [
                  new TextRun({
                    text: brandSettings.companyName,
                    bold: true,
                    size: 32,
                    color: brandSettings.primaryColor.replace('#', '')
                  })
                ],
                heading: HeadingLevel.HEADING_1,
                alignment: AlignmentType.CENTER
              }),
              
              // Report title
              new Paragraph({
                children: [
                  new TextRun({
                    text: reportPreview.title,
                    bold: true,
                    size: 24
                  })
                ],
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 400, after: 200 }
              }),
              
              // Date
              new Paragraph({
                children: [
                  new TextRun({
                    text: `Generated: ${reportPreview.createdAt}`,
                    size: 20,
                    italics: true
                  })
                ],
                spacing: { after: 400 }
              }),
              
              // Executive Summary
              ...(reportPreview.summary ? [
                new Paragraph({
                  children: [
                    new TextRun({
                      text: 'Executive Summary',
                      bold: true,
                      size: 22
                    })
                  ],
                  heading: HeadingLevel.HEADING_3,
                  spacing: { before: 400, after: 200 }
                }),
                new Paragraph({
                  children: [
                    new TextRun({
                      text: reportPreview.summary,
                      size: 20
                    })
                  ],
                  spacing: { after: 400 }
                })
              ] : []),
              
              // Analysis Results
              new Paragraph({
                children: [
                  new TextRun({
                    text: `Analysis Results (${reportPreview.analyses.length})`,
                    bold: true,
                    size: 22
                  })
                ],
                heading: HeadingLevel.HEADING_3,
                spacing: { before: 400, after: 200 }
              }),
              
              // Individual analyses
              ...reportPreview.analyses.flatMap((analysis, index) => [
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `${index + 1}. ${analysis.headline || 'Untitled Analysis'}`,
                      bold: true,
                      size: 20
                    })
                  ],
                  spacing: { before: 200, after: 100 }
                }),
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `Platform: ${analysis.platform} | Score: ${(analysis.overall_score || 0).toFixed(1)}/10 | Created: ${new Date(analysis.created_at).toLocaleDateString()}`,
                      size: 18,
                      italics: true
                    })
                  ],
                  spacing: { after: 200 }
                })
              ]),
              
              // Footer
              ...(brandSettings.includePoweredBy ? [
                new Paragraph({
                  children: [
                    new TextRun({
                      text: 'Powered by AdCopySurge',
                      size: 16,
                      italics: true,
                      color: '808080'
                    })
                  ],
                  alignment: AlignmentType.CENTER,
                  spacing: { before: 800 }
                })
              ] : [])
            ]
          }]
        });
        
        // Generate and download the document
        const blob = await Packer.toBlob(doc);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const fileName = `${reportPreview.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.docx`;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        toast.success('DOCX report generated successfully!');
        
      } catch (importError) {
        console.log('docx library not available, generating RTF report instead:', importError);
        
        // Fallback: Generate a Rich Text Format document
        const rtfContent = generateRTFReport(reportPreview, brandSettings);
        
        const blob = new Blob([rtfContent], { type: 'application/rtf' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const fileName = `${reportPreview.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.rtf`;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        toast.success('RTF report generated successfully! (DOCX library not available)');
      }
      
    } catch (error) {
      console.error('Error generating DOCX report:', error);
      toast.error('Failed to generate DOCX report. Please try again.');
    } finally {
      setGeneratingReport(false);
    }
  };

  const generatePDFReport = async () => {
    if (!reportPreview) {
      toast.error('Please generate preview first');
      return;
    }

    setGeneratingReport(true);
    try {
      // Try to dynamically import jsPDF - if it fails, offer alternative
      try {
        const jsPDF = (await import('jspdf')).default;
        
        // Create PDF document
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        
        // Add header with branding
        const primaryColor = brandSettings.primaryColor.replace('#', '');
        const r = parseInt(primaryColor.substr(0, 2), 16);
        const g = parseInt(primaryColor.substr(2, 2), 16);
        const b = parseInt(primaryColor.substr(4, 2), 16);
        pdf.setFillColor(r, g, b);
        pdf.rect(0, 0, pageWidth, 25, 'F');
        
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(20);
        pdf.text(brandSettings.companyName, 15, 18);
        
        // Add report title
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(16);
        pdf.text(reportPreview.title, 15, 40);
        
        // Add date
        pdf.setFontSize(10);
        pdf.text(`Generated: ${reportPreview.createdAt}`, 15, 50);
        
        let yPosition = 65;
        
        // Add executive summary
        if (reportPreview.summary) {
          pdf.setFontSize(12);
          pdf.text('Executive Summary', 15, yPosition);
          yPosition += 10;
          
          pdf.setFontSize(10);
          const summaryLines = pdf.splitTextToSize(reportPreview.summary, pageWidth - 30);
          pdf.text(summaryLines, 15, yPosition);
          yPosition += summaryLines.length * 5 + 15;
        }
        
        // Add analyses data
        pdf.setFontSize(12);
        pdf.text('Analysis Results', 15, yPosition);
        yPosition += 15;
        
        reportPreview.analyses.forEach((analysis, index) => {
          if (yPosition > pageHeight - 50) {
            pdf.addPage();
            yPosition = 25;
          }
          
          pdf.setFontSize(11);
          pdf.text(`${index + 1}. ${analysis.headline || 'Untitled Analysis'}`, 15, yPosition);
          yPosition += 8;
          
          pdf.setFontSize(9);
          const score = (analysis.overall_score || 0).toFixed(1);
          pdf.text(`Platform: ${analysis.platform} | Score: ${score}/10`, 15, yPosition);
          yPosition += 6;
          
          pdf.text(`Created: ${new Date(analysis.created_at).toLocaleDateString()}`, 15, yPosition);
          yPosition += 10;
        });
        
        // Add footer
        if (brandSettings.includePoweredBy) {
          pdf.setFontSize(8);
          pdf.setTextColor(128, 128, 128);
          pdf.text('Powered by AdCopySurge', 15, pageHeight - 10);
        }
        
        // Save the PDF
        const fileName = `${reportPreview.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.pdf`;
        pdf.save(fileName);
        
        toast.success('PDF report generated successfully!');
        
      } catch (importError) {
        console.log('jsPDF not available, generating text report instead:', importError);
        
        // Fallback: Generate a simple text report
        const reportText = generateTextReport(reportPreview, brandSettings);
        
        // Create a downloadable text file
        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const fileName = `${reportPreview.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.txt`;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        toast.success('Text report generated successfully! (PDF library not available)');
      }
      
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report. Please try again.');
    } finally {
      setGeneratingReport(false);
    }
  };

  // Helper function to generate RTF report as DOCX fallback
  const generateRTFReport = (preview, settings) => {
    let rtf = '{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}\\f0\\fs24 ';
    
    // Company name header
    rtf += `{\\fs36\\b\\qc ${settings.companyName}\\par}`;
    rtf += '\\par';
    
    // Report title
    rtf += `{\\fs28\\b ${preview.title}\\par}`;
    rtf += '\\par';
    
    // Date
    rtf += `{\\fs20\\i Generated: ${preview.createdAt}\\par}`;
    rtf += '\\par\\par';
    
    // Executive Summary
    if (preview.summary) {
      rtf += '{\\fs24\\b Executive Summary\\par}';
      rtf += '\\par';
      rtf += `{\\fs20 ${preview.summary.replace(/[{}\\]/g, '')}\\par}`;
      rtf += '\\par\\par';
    }
    
    // Analysis Results
    rtf += `{\\fs24\\b Analysis Results (${preview.analyses.length})\\par}`;
    rtf += '\\par';
    
    preview.analyses.forEach((analysis, index) => {
      rtf += `{\\fs20\\b ${index + 1}. ${(analysis.headline || 'Untitled Analysis').replace(/[{}\\]/g, '')}\\par}`;
      rtf += `{\\fs18\\i Platform: ${analysis.platform} | Score: ${(analysis.overall_score || 0).toFixed(1)}/10 | Created: ${new Date(analysis.created_at).toLocaleDateString()}\\par}`;
      rtf += '\\par';
    });
    
    // Footer
    if (settings.includePoweredBy) {
      rtf += '\\par\\par';
      rtf += '{\\fs16\\i\\qc Powered by AdCopySurge\\par}';
    }
    
    rtf += '}';
    return rtf;
  };

  // Helper function to generate text report as fallback
  const generateTextReport = (preview, settings) => {
    let report = `\n`;
    report += `${'='.repeat(60)}\n`;
    report += `${settings.companyName.toUpperCase()}\n`;
    report += `${'='.repeat(60)}\n\n`;
    report += `${preview.title}\n`;
    report += `Generated: ${preview.createdAt}\n\n`;
    
    if (preview.summary) {
      report += `EXECUTIVE SUMMARY\n`;
      report += `${'-'.repeat(20)}\n`;
      report += `${preview.summary}\n\n`;
    }
    
    report += `ANALYSIS RESULTS (${preview.analyses.length})\n`;
    report += `${'-'.repeat(30)}\n\n`;
    
    preview.analyses.forEach((analysis, index) => {
      report += `${index + 1}. ${analysis.headline || 'Untitled Analysis'}\n`;
      report += `   Platform: ${analysis.platform}\n`;
      report += `   Score: ${(analysis.overall_score || 0).toFixed(1)}/10\n`;
      report += `   Created: ${new Date(analysis.created_at).toLocaleDateString()}\n\n`;
    });
    
    if (settings.includePoweredBy) {
      report += `\n${'='.repeat(60)}\n`;
      report += `Powered by AdCopySurge\n`;
    }
    
    return report;
  };

  const handleSettingChange = (field, value) => {
    setBrandSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLogoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Logo file must be smaller than 5MB');
        return;
      }
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        handleSettingChange('logo', e.target.result);
        toast.success('Logo uploaded successfully!');
      };
      reader.onerror = () => {
        toast.error('Failed to read logo file');
      };
      reader.readAsDataURL(file);
    }
  };

  const saveBrandSettings = () => {
    // Save to localStorage or database
    localStorage.setItem('adcopysurge-brand-settings', JSON.stringify(brandSettings));
    toast.success('Brand settings saved!');
  };

  const reportTypes = [
    {
      id: 'before',
      name: 'Before (Audit/Critique)',
      description: 'Analyze current ad performance to show prospects what\'s wrong - perfect for lead generation',
      recommended: false,
      icon: '🔍',
      maxAnalyses: 1,
      useCase: 'Prospect Outreach'
    },
    {
      id: 'before-after',
      name: 'Before/After Comparison',
      description: 'Perfect for client pitches - compare original vs optimized ads',
      recommended: true,
      icon: '📊',
      maxAnalyses: 2,
      useCase: 'Client Presentation'
    },
    {
      id: 'single',
      name: 'Single Analysis Report',
      description: 'Comprehensive breakdown of one ad analysis',
      icon: '📋',
      maxAnalyses: 1,
      useCase: 'Detailed Review'
    },
    {
      id: 'multi',
      name: 'Multi-Analysis Comparison',
      description: 'Compare multiple ad variations side-by-side',
      icon: '⚖️',
      maxAnalyses: 5,
      useCase: 'A/B/C Testing Review'
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <ReportsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            📊 Reports
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
          Create professional reports from your ad analyses with AI-powered insights.
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          aria-label="Reports management tabs"
        >
          <Tab label="Create Report" id="tab-0" aria-controls="tabpanel-0" />
          <Tab label="Settings" id="tab-1" aria-controls="tabpanel-1" />
        </Tabs>
      </Box>

      {/* Create Report Tab */}
      {tabValue === 0 && (
        <Box role="tabpanel" id="tabpanel-0" aria-labelledby="tab-0">
          {!reportType ? (
            <Card>
              <CardContent>
                <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
                  📊 Create New Report
                </Typography>
                
                <Typography variant="body1" sx={{ mb: 4 }}>
                  Choose Report Type:
                </Typography>
                
                <RadioGroup
                  value={reportType}
                  onChange={handleReportTypeChange}
                  sx={{ mb: 4 }}
                >
                  {reportTypes.map((type) => (
                    <Paper 
                      key={type.id}
                      sx={{ 
                        p: 2, 
                        mb: 2, 
                        cursor: 'pointer',
                        border: reportType === type.id ? '2px solid' : '1px solid',
                        borderColor: reportType === type.id ? 'primary.main' : (type.id === 'before' ? 'warning.main' : 'divider'),
                        backgroundColor: type.id === 'before' ? 'warning.50' : 'background.paper',
                        '&:hover': {
                          borderColor: type.id === 'before' ? 'warning.main' : 'primary.main',
                          backgroundColor: 'action.hover'
                        }
                      }}
                      onClick={() => setReportType(type.id)}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Radio
                          checked={reportType === type.id}
                          onChange={handleReportTypeChange}
                          value={type.id}
                        />
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                              {type.icon} {type.name}
                            </Typography>
                            {type.recommended && (
                              <Chip label="Recommended for pitch" size="small" color="primary" />
                            )}
                            {type.useCase && (
                              <Chip label={type.useCase} size="small" color="secondary" variant="outlined" />
                            )}
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {type.description}
                          </Typography>
                        </Box>
                      </Box>
                    </Paper>
                  ))}
                </RadioGroup>
                
                {reportType === 'before' && (
                  <Alert severity="warning" sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      💪 Agency Power Move!
                    </Typography>
                    <Typography variant="body2">
                      The "Before" report is your secret weapon for winning new clients. Send this as a <strong>free audit</strong> to prospects to show them exactly what's wrong with their current ads. 
                      It positions you as the expert, creates urgency, and makes them realize they're losing money every day they don't fix these issues.
                    </Typography>
                  </Alert>
                )}
                
                <Button 
                  variant="contained" 
                  size="large" 
                  disabled={!reportType}
                  onClick={() => {/* Already handled by selection */}}
                >
                  Continue →
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {reportTypes.find(t => t.id === reportType)?.icon} {reportTypes.find(t => t.id === reportType)?.name}
                      </Typography>
                      <Button size="small" onClick={() => setReportType('')}>← Back</Button>
                    </Box>
                    
                    <TextField
                      label="Report Title"
                      fullWidth
                      value={reportTitle}
                      onChange={(e) => setReportTitle(e.target.value)}
                      placeholder="e.g., Q4 Ad Performance Analysis"
                      sx={{ mb: 3 }}
                      required
                    />
                    
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                      Select Analyses ({selectedAnalyses.length}/{reportTypes.find(t => t.id === reportType)?.maxAnalyses})
                    </Typography>
                    
                    {loadingAnalyses ? (
                      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                      </Box>
                    ) : analyses.length === 0 ? (
                      <Alert severity="info" sx={{ mb: 3 }}>
                        No analyses found. Please create some ad analyses first to generate reports.
                      </Alert>
                    ) : (
                      <Paper sx={{ maxHeight: 300, overflow: 'auto', mb: 3 }}>
                        <List>
                          {analyses.map((analysis) => (
                            <ListItemButton
                              key={analysis.id}
                              onClick={() => handleAnalysisSelection(analysis.id)}
                              selected={selectedAnalyses.includes(analysis.id)}
                            >
                              <Checkbox
                                checked={selectedAnalyses.includes(analysis.id)}
                                tabIndex={-1}
                                disableRipple
                              />
                              <ListItemText
                                primary={analysis.headline || 'Untitled Analysis'}
                                secondary={
                                  <Box>
                                    <Typography variant="caption" display="block">
                                      Score: {(analysis.overall_score || 0).toFixed(1)}/10 • {analysis.platform} • {new Date(analysis.created_at).toLocaleDateString()}
                                    </Typography>
                                    {analysis.projects?.name && (
                                      <Chip label={analysis.projects.name} size="small" sx={{ mt: 0.5 }} />
                                    )}
                                  </Box>
                                }
                              />
                            </ListItemButton>
                          ))}
                        </List>
                      </Paper>
                    )}
                    
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          Executive Summary
                        </Typography>
                        <Button
                          size="small"
                          startIcon={<AIIcon />}
                          onClick={generateAISummary}
                          disabled={loading || selectedAnalyses.length === 0}
                          variant="outlined"
                        >
                          {loading ? <CircularProgress size={16} /> : 'Generate with AI'}
                        </Button>
                      </Box>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        value={executiveSummary}
                        onChange={(e) => setExecutiveSummary(e.target.value)}
                        placeholder="Provide a high-level overview of the analysis results..."
                      />
                    </Box>
                    
                    <Divider sx={{ mb: 3 }} />
                    
                    <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
                      <Button
                        variant="outlined"
                        size="large"
                        startIcon={loading ? <CircularProgress size={20} /> : <PreviewIcon />}
                        onClick={generatePreview}
                        disabled={loading || !reportType || selectedAnalyses.length === 0 || !reportTitle}
                        fullWidth
                      >
                        {loading ? 'Generating...' : 'Preview & Edit'}
                      </Button>
                      
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                          variant="contained"
                          size="large"
                          startIcon={generatingReport ? <CircularProgress size={20} /> : <PDFIcon />}
                          onClick={generatePDFReport}
                          disabled={generatingReport || !reportPreview}
                          sx={{ flex: 1 }}
                          color="primary"
                        >
                          {generatingReport ? 'Generating...' : 'PDF'}
                        </Button>
                        
                        <Button
                          variant="contained"
                          size="large"
                          startIcon={generatingReport ? <CircularProgress size={20} /> : <DOCXIcon />}
                          onClick={generateDOCXReport}
                          disabled={generatingReport || !reportPreview}
                          sx={{ flex: 1 }}
                          color="secondary"
                        >
                          {generatingReport ? 'Generating...' : 'DOCX'}
                        </Button>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        📋 Report Preview
                      </Typography>
                      {reportPreview && (
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button size="small" onClick={() => setEditMode(!editMode)} color={editMode ? 'primary' : 'inherit'}>
                            {editMode ? '✓ Done' : '✏️ Edit'}
                          </Button>
                          <Button size="small" onClick={() => setShowPreview(!showPreview)}>
                            {showPreview ? 'Hide' : 'Show'}
                          </Button>
                        </Box>
                      )}
                    </Box>
                    
                    {!reportPreview ? (
                      <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                          Click "Preview & Edit" to generate a preview of your report
                        </Typography>
                      </Box>
                    ) : (
                      <Box sx={{ 
                        p: 3, 
                        bgcolor: 'grey.100', // Changed from white to light grey for better contrast
                        borderRadius: 1, 
                        border: '1px solid',
                        borderColor: 'divider',
                        minHeight: 400,
                        maxHeight: 600,
                        overflow: 'auto'
                      }}>
                        {/* Report Header */}
                        <Box sx={{ 
                          p: 2, 
                          mb: 3, 
                          bgcolor: brandSettings.primaryColor,
                          color: 'white',
                          borderRadius: 1
                        }}>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {brandSettings.companyName}
                          </Typography>
                        </Box>
                        
                        {/* Report Title */}
                        {editMode ? (
                          <TextField
                            fullWidth
                            variant="outlined"
                            value={reportPreview.title}
                            onChange={(e) => setReportPreview(prev => ({ ...prev, title: e.target.value }))}
                            sx={{ mb: 2 }}
                            InputProps={{
                              sx: { fontSize: '1.5rem', fontWeight: 600 }
                            }}
                          />
                        ) : (
                          <Typography variant="h5" sx={{ 
                            fontWeight: 600, 
                            mb: 1,
                            color: 'text.primary' // Ensure strong contrast
                          }}>
                            {reportPreview.title}
                          </Typography>
                        )}
                        <Typography variant="body2" sx={{ 
                          mb: 3,
                          color: 'text.primary', // Changed from text.secondary for better contrast
                          fontWeight: 500
                        }}>
                          Generated: {reportPreview.createdAt}
                        </Typography>
                        
                        {/* Executive Summary */}
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" sx={{ 
                            fontWeight: 600, 
                            mb: 2,
                            color: 'text.primary' // Ensure strong contrast
                          }}>
                            Executive Summary
                          </Typography>
                          {editMode ? (
                            <TextField
                              fullWidth
                              multiline
                              rows={4}
                              variant="outlined"
                              value={reportPreview.summary || ''}
                              onChange={(e) => setReportPreview(prev => ({ ...prev, summary: e.target.value }))}
                              placeholder="Enter executive summary..."
                            />
                          ) : (
                            <Paper sx={{ p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                              <Typography variant="body2" sx={{ 
                                whiteSpace: 'pre-wrap',
                                color: 'text.primary',
                                fontWeight: 500,
                                lineHeight: 1.6
                              }}>
                                {reportPreview.summary || 'No summary provided'}
                              </Typography>
                            </Paper>
                          )}
                        </Box>
                        
                        {/* Analyses Summary */}
                        <Typography variant="subtitle1" sx={{ 
                          fontWeight: 600, 
                          mb: 2,
                          color: 'text.primary' // Ensure strong contrast
                        }}>
                          Analysis Results ({reportPreview.analyses.length})
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          {reportPreview.analyses.map((analysis, index) => (
                            <Paper key={analysis.id} sx={{ 
                              p: 2, 
                              border: '1px solid', 
                              borderColor: 'divider',
                              bgcolor: 'background.paper'
                            }}>
                              <Typography variant="subtitle2" sx={{ 
                                fontWeight: 600, 
                                mb: 1,
                                color: 'text.primary'
                              }}>
                                {index + 1}. {analysis.headline || 'Untitled Analysis'}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                                <Typography variant="caption" sx={{ 
                                  color: 'text.secondary',
                                  fontWeight: 500
                                }}>
                                  Platform: {analysis.platform}
                                </Typography>
                                <Typography variant="caption" sx={{ 
                                  color: 'primary.main',
                                  fontWeight: 600
                                }}>
                                  Score: {(analysis.overall_score || 0).toFixed(1)}/10
                                </Typography>
                                <Typography variant="caption" sx={{ 
                                  color: 'text.secondary',
                                  fontWeight: 500
                                }}>
                                  Created: {new Date(analysis.created_at).toLocaleDateString()}
                                </Typography>
                              </Box>
                            </Paper>
                          ))}
                        </Box>
                        
                        {/* Footer */}
                        {brandSettings.includePoweredBy && (
                          <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                            <Typography variant="caption" color="text.secondary">
                              Powered by AdCopySurge
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Box>
      )}

      {/* Settings Tab */}
      {tabValue === 1 && (
        <Box role="tabpanel" id="tabpanel-1" aria-labelledby="tab-1">
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                    🎨 BRANDING
                  </Typography>
                  
                  <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        label="Company Name"
                        fullWidth
                        value={brandSettings.companyName}
                        onChange={(e) => handleSettingChange('companyName', e.target.value)}
                        placeholder="Your Agency Name"
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Box>
                        <input
                          type="file"
                          accept="image/*"
                          style={{ display: 'none' }}
                          id="logo-upload"
                          onChange={handleLogoUpload}
                        />
                        <label htmlFor="logo-upload">
                          <Button
                            variant="outlined"
                            component="span"
                            startIcon={<UploadIcon />}
                            fullWidth
                            sx={{ height: 56 }}
                          >
                            {brandSettings.logo ? 'Change Logo' : 'Upload Logo'}
                          </Button>
                        </label>
                        {brandSettings.logo && (
                          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ 
                              width: 48, 
                              height: 48, 
                              border: '1px solid', 
                              borderColor: 'divider', 
                              borderRadius: 1,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              bgcolor: 'white',
                              overflow: 'hidden'
                            }}>
                              <img 
                                src={brandSettings.logo} 
                                alt="Logo preview" 
                                style={{ 
                                  maxWidth: '100%', 
                                  maxHeight: '100%', 
                                  objectFit: 'contain',
                                  display: 'block'
                                }}
                              />
                            </Box>
                            <Button 
                              size="small" 
                              color="error" 
                              onClick={() => handleSettingChange('logo', null)}
                            >
                              Remove
                            </Button>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Primary Color"
                        type="color"
                        fullWidth
                        value={brandSettings.primaryColor}
                        onChange={(e) => handleSettingChange('primaryColor', e.target.value)}
                        InputProps={{
                          sx: { height: 56 }
                        }}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Secondary Color"
                        type="color"
                        fullWidth
                        value={brandSettings.secondaryColor}
                        onChange={(e) => handleSettingChange('secondaryColor', e.target.value)}
                        InputProps={{
                          sx: { height: 56 }
                        }}
                      />
                    </Grid>
                  </Grid>
                  
                  <Divider sx={{ mb: 3 }} />
                  
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                    📤 EXPORT PREFERENCES
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                        Available Export Formats:
                      </Typography>
                      <Box sx={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
                        gap: 2,
                        p: 2,
                        bgcolor: 'grey.50',
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'divider'
                      }}>
                        <Box sx={{ textAlign: 'center' }}>
                          <PDFIcon sx={{ fontSize: 32, color: 'error.main', mb: 1 }} />
                          <Typography variant="caption" display="block" sx={{ fontWeight: 600, color: 'text.primary' }}>
                            PDF
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Professional
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'center' }}>
                          <DOCXIcon sx={{ fontSize: 32, color: 'info.main', mb: 1 }} />
                          <Typography variant="caption" display="block" sx={{ fontWeight: 600, color: 'text.primary' }}>
                            DOCX
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Editable
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'center' }}>
                          <DownloadIcon sx={{ fontSize: 32, color: 'warning.main', mb: 1 }} />
                          <Typography variant="caption" display="block" sx={{ fontWeight: 600, color: 'text.primary' }}>
                            RTF/TXT
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Fallback
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={!brandSettings.includePoweredBy}
                            onChange={(e) => handleSettingChange('includePoweredBy', !e.target.checked)}
                          />
                        }
                        label='Include "Powered by AdCopySurge"'
                        sx={{ 
                          '& .MuiFormControlLabel-label': {
                            textDecoration: !brandSettings.includePoweredBy ? 'line-through' : 'none'
                          }
                        }}
                      />
                    </Grid>
                  </Grid>
                  
                  <Divider sx={{ my: 3 }} />
                  
                  <Button
                    variant="contained"
                    onClick={saveBrandSettings}
                    startIcon={<SettingsIcon />}
                  >
                    Save Settings
                  </Button>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    📋 Brand Preview
                  </Typography>
                  <Box 
                    sx={{ 
                      p: 2, 
                      bgcolor: brandSettings.primaryColor, 
                      color: 'white',
                      borderRadius: 1,
                      mb: 2
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {brandSettings.companyName}
                    </Typography>
                    <Typography variant="body2">Sample Report Header</Typography>
                  </Box>
                  
                  <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Your reports will use these brand settings for consistent professional appearance.
                    </Typography>
                  </Box>
                  
                  {!brandSettings.includePoweredBy && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      White-label reports hide "Powered by AdCopySurge" branding
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Container>
  );
}

export default AgencyReportsBranding;
