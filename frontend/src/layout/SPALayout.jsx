import React from 'react';
import { Box, CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';

/**
 * Minimal SPA layout that provides just the basic styling and theming
 * without any navigation elements like navbar, sidebar, or footer
 */
const SPALayout = ({ children }) => {
  return (
    <>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          width: '100vw',
          bgcolor: 'background.default',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden' // Prevent scroll issues
        }}
      >
        {/* Main content area */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            position: 'relative',
            overflow: 'auto'
          }}
        >
          {children}
        </Box>
        
        {/* Toast notifications */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1A0F2E',
              color: '#F9FAFB',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '500'
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#F9FAFB',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#F9FAFB',
              },
            },
          }}
        />
      </Box>
    </>
  );
};

export default SPALayout;