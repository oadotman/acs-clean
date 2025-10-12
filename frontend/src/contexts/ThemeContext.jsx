import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import { createTheme, ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { alpha } from '@mui/material';
import { useWhiteLabel } from './WhiteLabelContext';

const ThemeContext = createContext();

export const useThemeMode = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeMode must be used within ThemeProvider');
  }
  return context;
};

// Color manipulation helpers
const lightenColor = (color, amount) => {
  const usePound = color[0] === '#';
  const col = usePound ? color.slice(1) : color;
  const num = parseInt(col, 16);
  let r = (num >> 16) + amount * 255;
  let g = (num >> 8 & 0x00FF) + amount * 255;
  let b = (num & 0x0000FF) + amount * 255;
  r = r > 255 ? 255 : r < 0 ? 0 : r;
  g = g > 255 ? 255 : g < 0 ? 0 : g;
  b = b > 255 ? 255 : b < 0 ? 0 : b;
  return (usePound ? '#' : '') + (r << 16 | g << 8 | b).toString(16).padStart(6, '0');
};

const darkenColor = (color, amount) => {
  const usePound = color[0] === '#';
  const col = usePound ? color.slice(1) : color;
  const num = parseInt(col, 16);
  let r = (num >> 16) - amount * 255;
  let g = (num >> 8 & 0x00FF) - amount * 255;
  let b = (num & 0x0000FF) - amount * 255;
  r = r > 255 ? 255 : r < 0 ? 0 : r;
  g = g > 255 ? 255 : g < 0 ? 0 : g;
  b = b > 255 ? 255 : b < 0 ? 0 : b;
  return (usePound ? '#' : '') + (r << 16 | g << 8 | b).toString(16).padStart(6, '0');
};

export const ThemeModeProvider = ({ children }) => {
  // Get theme preference from localStorage or default to dark
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('themeMode');
    return savedMode || 'dark';
  });

  // Save theme preference to localStorage
  useEffect(() => {
    localStorage.setItem('themeMode', mode);
  }, [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  // Get white-label branding for theme customization
  const whiteLabelContext = useWhiteLabel();
  const branding = whiteLabelContext ? whiteLabelContext.getEffectiveBranding() : null;

  const theme = useMemo(
    () => {
      // Use white-label colors if available and enabled
      const primaryColor = branding?.primaryColor || '#7C3AED';
      const secondaryColor = branding?.secondaryColor || '#A855F7';
      
      return createTheme({
        palette: {
          mode,
          primary: {
            main: primaryColor, // Use white-label primary or default
            light: lightenColor(primaryColor, 0.3),
            dark: darkenColor(primaryColor, 0.3),
            contrastText: mode === 'light' ? '#FFFFFF' : '#F9FAFB',
          },
          secondary: {
            main: secondaryColor, // Use white-label secondary or default
            light: lightenColor(secondaryColor, 0.2),
            dark: darkenColor(secondaryColor, 0.2),
            contrastText: mode === 'light' ? '#FFFFFF' : '#F9FAFB',
          },
          warning: {
            main: '#C084FC', // Bright Gradient Purple for CTAs
            light: '#E9D5FF',
            dark: '#A855F7',
            contrastText: mode === 'light' ? '#0F0B1D' : '#0F0B1D',
          },
          success: {
            main: '#10b981',
            light: '#34d399',
            dark: '#059669',
            contrastText: '#FFFFFF',
          },
          error: {
            main: '#ef4444',
            light: '#f87171',
            dark: '#dc2626',
            contrastText: '#FFFFFF',
          },
          background: {
            default: mode === 'light' ? '#F8F9FA' : '#0F0B1D', // Light gray or Deep Navy/Black
            paper: mode === 'light' ? '#FFFFFF' : '#1A0F2E', // White or slightly lighter for cards
          },
          text: {
            primary: mode === 'light' ? '#1F2937' : '#F9FAFB', // Dark gray or Off-White
            secondary: mode === 'light' ? '#6B7280' : '#E5E7EB', // Medium gray or Cool Gray
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
          divider: mode === 'light' 
            ? 'rgba(0, 0, 0, 0.08)' 
            : 'rgba(168, 85, 247, 0.2)',
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
        spacing: 8,
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
              root: ({ theme }) => ({
                borderRadius: 20,
                border: '1px solid',
                borderColor: mode === 'light' 
                  ? 'rgba(0, 0, 0, 0.08)' 
                  : 'rgba(168, 85, 247, 0.2)',
                boxShadow: mode === 'light'
                  ? '0 4px 12px rgba(0, 0, 0, 0.05)'
                  : '0 10px 40px rgba(124, 58, 237, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                padding: '24px',
                background: mode === 'light' 
                  ? '#FFFFFF'
                  : 'linear-gradient(135deg, #1A0F2E 0%, #0F0B1D 100%)',
                backdropFilter: 'blur(20px)',
                '&:hover': {
                  boxShadow: mode === 'light'
                    ? '0 8px 24px rgba(0, 0, 0, 0.1)'
                    : '0 20px 60px rgba(168, 85, 247, 0.3)',
                  transform: 'translateY(-4px)',
                  borderColor: mode === 'light'
                    ? 'rgba(124, 58, 237, 0.2)'
                    : 'rgba(192, 132, 252, 0.4)',
                },
              }),
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                borderRadius: 20,
                backgroundImage: 'none',
                backgroundColor: mode === 'light' ? '#FFFFFF' : '#1A0F2E',
                border: mode === 'light' 
                  ? '1px solid rgba(0, 0, 0, 0.06)'
                  : '1px solid rgba(168, 85, 247, 0.15)',
              },
              elevation1: {
                boxShadow: mode === 'light'
                  ? '0 2px 8px rgba(0, 0, 0, 0.05)'
                  : '0 10px 40px rgba(124, 58, 237, 0.1)',
              },
              elevation2: {
                boxShadow: mode === 'light'
                  ? '0 4px 16px rgba(0, 0, 0, 0.08)'
                  : '0 20px 60px rgba(168, 85, 247, 0.2)',
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
                  boxShadow: mode === 'light'
                    ? '0 6px 20px rgba(124, 58, 237, 0.25)'
                    : '0 10px 30px rgba(192, 132, 252, 0.4)',
                  transform: 'translateY(-2px)',
                },
              },
              contained: {
                boxShadow: mode === 'light'
                  ? '0 4px 12px rgba(124, 58, 237, 0.2)'
                  : '0 8px 25px rgba(124, 58, 237, 0.3)',
              },
              containedPrimary: {
                background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
                color: '#FFFFFF',
                '&:hover': {
                  background: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)',
                  boxShadow: mode === 'light'
                    ? '0 8px 24px rgba(124, 58, 237, 0.35)'
                    : '0 12px 40px rgba(192, 132, 252, 0.5)',
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
                  backgroundColor: mode === 'light' ? '#FFFFFF' : 'rgba(26, 15, 46, 0.5)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '& fieldset': {
                    borderColor: mode === 'light' 
                      ? 'rgba(0, 0, 0, 0.12)'
                      : 'rgba(168, 85, 247, 0.3)',
                  },
                  '&:hover fieldset': {
                    borderColor: mode === 'light'
                      ? 'rgba(124, 58, 237, 0.4)'
                      : 'rgba(168, 85, 247, 0.5)',
                  },
                  '&.Mui-focused fieldset': {
                    borderWidth: 2,
                    borderColor: '#A855F7',
                    boxShadow: mode === 'light'
                      ? '0 0 0 3px rgba(168, 85, 247, 0.1)'
                      : '0 0 20px rgba(168, 85, 247, 0.3)',
                  },
                },
                '& .MuiInputLabel-root': {
                  fontWeight: 500,
                  color: mode === 'light' ? '#6B7280' : '#E5E7EB',
                },
                '& .MuiOutlinedInput-input': {
                  color: mode === 'light' ? '#1F2937' : '#F9FAFB',
                },
              },
            },
          },
          MuiChip: {
            styleOverrides: {
              root: {
                borderRadius: 10,
                fontWeight: 600,
                backgroundColor: mode === 'light'
                  ? 'rgba(124, 58, 237, 0.08)'
                  : 'rgba(168, 85, 247, 0.15)',
                color: mode === 'light' ? '#7C3AED' : '#C084FC',
                border: mode === 'light'
                  ? '1px solid rgba(124, 58, 237, 0.2)'
                  : '1px solid rgba(168, 85, 247, 0.3)',
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
                backgroundColor: mode === 'light'
                  ? 'rgba(255, 255, 255, 0.9)'
                  : 'rgba(15, 11, 29, 0.8)',
                backdropFilter: 'blur(20px)',
                borderBottom: mode === 'light'
                  ? '1px solid rgba(0, 0, 0, 0.08)'
                  : 'none',
              },
            },
          },
        },
      });
    },
    [mode, branding]
  );

  const value = {
    mode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>{children}</MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
