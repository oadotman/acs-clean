import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AnalysisToolsSelector from './AnalysisToolsSelector';
import { DEFAULT_ENABLED_TOOLS } from '../../constants/analysisTools';

// Mock theme for testing
const theme = createTheme();

const TestWrapper = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('AnalysisToolsSelector', () => {
  const mockWatch = jest.fn();
  const mockSetValue = jest.fn();
  const mockSetShowAdvancedSettings = jest.fn();

  beforeEach(() => {
    mockWatch.mockReturnValue(DEFAULT_ENABLED_TOOLS);
    jest.clearAllMocks();
  });

  const defaultProps = {
    watch: mockWatch,
    setValue: mockSetValue,
    showAdvancedSettings: false,
    setShowAdvancedSettings: mockSetShowAdvancedSettings,
  };

  it('renders with default tools selected', () => {
    render(
      <TestWrapper>
        <AnalysisToolsSelector {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('🔧 Analysis Tools')).toBeInTheDocument();
    expect(screen.getByText('Compliance Checker')).toBeInTheDocument();
    expect(screen.getByText('Legal Risk Scanner')).toBeInTheDocument();
    expect(screen.getByText('Brand Voice Engine')).toBeInTheDocument();
    expect(screen.getByText('Psychology Scorer')).toBeInTheDocument();
  });

  it('shows all available tools', () => {
    render(
      <TestWrapper>
        <AnalysisToolsSelector {...defaultProps} />
      </TestWrapper>
    );

    // Should show all 8 tools
    expect(screen.getByText('Compliance Checker')).toBeInTheDocument();
    expect(screen.getByText('Legal Risk Scanner')).toBeInTheDocument();
    expect(screen.getByText('Brand Voice Engine')).toBeInTheDocument();
    expect(screen.getByText('Psychology Scorer')).toBeInTheDocument();
    expect(screen.getByText('ROI Copy Generator')).toBeInTheDocument();
    expect(screen.getByText('A/B Test Generator')).toBeInTheDocument();
    expect(screen.getByText('Industry Optimizer')).toBeInTheDocument();
    expect(screen.getByText('Performance Forensics')).toBeInTheDocument();
  });

  it('handles tool selection', () => {
    render(
      <TestWrapper>
        <AnalysisToolsSelector {...defaultProps} />
      </TestWrapper>
    );

    const roiTool = screen.getByText('ROI Copy Generator').closest('div[role="button"]');
    fireEvent.click(roiTool);

    expect(mockSetValue).toHaveBeenCalledWith('enabledTools', expect.arrayContaining(['roi_generator']));
  });

  it('handles tool deselection', () => {
    // Mock that compliance is currently selected
    mockWatch.mockReturnValue(['compliance']);

    render(
      <TestWrapper>
        <AnalysisToolsSelector {...defaultProps} />
      </TestWrapper>
    );

    const complianceTool = screen.getByText('Compliance Checker').closest('div[role="button"]');
    fireEvent.click(complianceTool);

    expect(mockSetValue).toHaveBeenCalledWith('enabledTools', []);
  });

  it('toggles advanced settings', () => {
    render(
      <TestWrapper>
        <AnalysisToolsSelector {...defaultProps} />
      </TestWrapper>
    );

    const advancedToggle = screen.getByLabelText('Advanced Settings');
    fireEvent.click(advancedToggle);

    expect(mockSetShowAdvancedSettings).toHaveBeenCalledWith(true);
  });

  it('shows advanced settings when enabled', () => {
    render(
      <TestWrapper>
        <AnalysisToolsSelector 
          {...defaultProps} 
          showAdvancedSettings={true}
        />
      </TestWrapper>
    );

    expect(screen.getByText('Auto-run analysis when saving')).toBeInTheDocument();
  });

  it('applies custom title and subtitle', () => {
    const customTitle = 'Custom Analysis Tools';
    const customSubtitle = 'Select your preferred tools';

    render(
      <TestWrapper>
        <AnalysisToolsSelector 
          {...defaultProps}
          title={customTitle}
          subtitle={customSubtitle}
        />
      </TestWrapper>
    );

    expect(screen.getByText(`🔧 ${customTitle}`)).toBeInTheDocument();
    expect(screen.getByText(customSubtitle)).toBeInTheDocument();
  });
});
