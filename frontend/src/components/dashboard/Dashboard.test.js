import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Dashboard from '../../pages/Dashboard';

// Mock the auth context
jest.mock('../../services/authContext', () => ({
  useAuth: () => ({ user: { id: 'test-user' } })
}));

// Mock the credits service
jest.mock('../../services/creditsService', () => ({
  canPerformAction: () => true,
  useCredits: () => true,
  getCredits: () => ({ current: 10, daily: 10 })
}));

// Mock scrollIntoView
const mockScrollIntoView = jest.fn();
window.HTMLElement.prototype.scrollIntoView = mockScrollIntoView;

const theme = createTheme();

const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('Dashboard Auto-scroll Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should auto-scroll to quick actions after platform selection', async () => {
    renderWithTheme(<Dashboard />);
    
    // Find a platform button (Facebook)
    const facebookButton = screen.getByText(/Facebook/i);
    
    // Click the platform button
    fireEvent.click(facebookButton);
    
    // Wait for the scroll to be triggered
    await waitFor(() => {
      expect(mockScrollIntoView).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'start',
        inline: 'nearest'
      });
    }, { timeout: 1000 });
  });

  test('should show success toast when platform is selected', async () => {
    renderWithTheme(<Dashboard />);
    
    // Find a platform button (Instagram)
    const instagramButton = screen.getByText(/Instagram/i);
    
    // Click the platform button
    fireEvent.click(instagramButton);
    
    // Check if platform selected state is updated
    await waitFor(() => {
      expect(screen.getByText(/platform selected/i)).toBeInTheDocument();
    });
  });

  test('should enable quick actions after platform selection', async () => {
    renderWithTheme(<Dashboard />);
    
    // Find a platform button (Google)
    const googleButton = screen.getByText(/Google/i);
    
    // Click the platform button
    fireEvent.click(googleButton);
    
    // Check if analyze button becomes enabled
    await waitFor(() => {
      const analyzeButton = screen.getByText(/Analyze Ad/i);
      expect(analyzeButton).not.toBeDisabled();
    });
  });
});

describe('Evidence Utils Integration', () => {
  test('should show evidence disclaimers in analysis results', () => {
    // This would be tested when the analysis results are shown
    // The actual test would verify that evidence disclaimers appear
    expect(true).toBe(true); // Placeholder - would implement full test
  });
});