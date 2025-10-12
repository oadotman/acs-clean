import React, { createContext, useContext, useState, useEffect } from 'react';

const SettingsContext = createContext();

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

const SETTINGS_STORAGE_KEY = 'adcopysurge_ui_settings';

const defaultSettings = {
  showAdvancedSettings: true, // Default to showing advanced settings
  autoSave: false,
  compactView: false,
  darkMode: false,
  notifications: {
    browser: true,
    email: true,
    analysis_complete: true,
    project_shared: true
  },
  analysis: {
    autoAnalyze: true,
    saveResultsHistory: true,
    showDetailedScores: true
  }
};

export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState(defaultSettings);
  const [loading, setLoading] = useState(true);

  // Load settings from localStorage on initialization
  useEffect(() => {
    try {
      const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
      if (stored) {
        const parsedSettings = JSON.parse(stored);
        setSettings(prev => ({
          ...prev,
          ...parsedSettings
        }));
      }
    } catch (error) {
      console.warn('Failed to load settings from localStorage:', error);
      // Continue with default settings
    } finally {
      setLoading(false);
    }
  }, []);

  // Save settings to localStorage whenever they change
  const updateSettings = (updates) => {
    setSettings(prev => {
      const newSettings = {
        ...prev,
        ...updates
      };
      
      // Save to localStorage
      try {
        localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(newSettings));
      } catch (error) {
        console.warn('Failed to save settings to localStorage:', error);
      }
      
      return newSettings;
    });
  };

  // Convenience methods for common settings
  const toggleAdvancedSettings = () => {
    updateSettings({ showAdvancedSettings: !settings.showAdvancedSettings });
  };

  const setAdvancedSettings = (show) => {
    updateSettings({ showAdvancedSettings: show });
  };

  const updateAnalysisSettings = (analysisUpdates) => {
    updateSettings({
      analysis: {
        ...settings.analysis,
        ...analysisUpdates
      }
    });
  };

  const updateNotificationSettings = (notificationUpdates) => {
    updateSettings({
      notifications: {
        ...settings.notifications,
        ...notificationUpdates
      }
    });
  };

  // Reset to defaults
  const resetSettings = () => {
    setSettings(defaultSettings);
    try {
      localStorage.removeItem(SETTINGS_STORAGE_KEY);
    } catch (error) {
      console.warn('Failed to remove settings from localStorage:', error);
    }
  };

  const value = {
    settings,
    loading,
    updateSettings,
    toggleAdvancedSettings,
    setAdvancedSettings,
    updateAnalysisSettings,
    updateNotificationSettings,
    resetSettings,
    // Convenient boolean getters
    showAdvancedSettings: settings.showAdvancedSettings,
    autoSave: settings.autoSave,
    compactView: settings.compactView,
    darkMode: settings.darkMode
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

export default SettingsContext;
