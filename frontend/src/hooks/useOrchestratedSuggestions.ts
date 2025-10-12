/**
 * React Hook for Orchestrated Suggestions
 * 
 * Provides real-time suggestions and processing results from the orchestration engine.
 * Integrates with React Query for caching and state management.
 */

import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  orchestrationEngine,
  ContextInsight,
  ToolSuggestion,
  ProcessingResult,
  RecommendedAction
} from '../services/orchestrationEngine';
import { 
  passportManager,
  DataPassport,
  PassportConfig,
  PassportEvent
} from '../services/passportManager';
import toast from 'react-hot-toast';

export interface OrchestratedSuggestionsOptions {
  enableFastTrack?: boolean;
  enableDeepTrack?: boolean;
  autoProcess?: boolean;
  maxConcurrency?: number;
  timeout?: number;
}

export interface UseOrchestratedSuggestionsResult {
  // Passport management
  passport: DataPassport | null;
  createPassport: (config: PassportConfig) => void;
  passportMetrics: any;
  
  // Context analysis
  contextInsights: ContextInsight[];
  isAnalyzing: boolean;
  analyzeError: Error | null;
  
  // Tool suggestions
  suggestedTools: ToolSuggestion[];
  
  // Processing
  processingResult: ProcessingResult | null;
  isProcessing: boolean;
  processError: Error | null;
  startProcessing: (options?: OrchestratedSuggestionsOptions) => void;
  
  // Actions and recommendations
  recommendedActions: RecommendedAction[];
  keyFindings: any[];
  nextSteps: string[];
  
  // Events and status
  events: PassportEvent[];
  overallScore: number;
  
  // Utilities
  refresh: () => void;
  clear: () => void;
}

export const useOrchestratedSuggestions = (
  passportId?: string,
  options: OrchestratedSuggestionsOptions = {}
): UseOrchestratedSuggestionsResult => {
  const queryClient = useQueryClient();
  const [currentPassportId, setCurrentPassportId] = useState<string | null>(passportId || null);
  const [events, setEvents] = useState<PassportEvent[]>([]);

  // Get passport data
  const { 
    data: passport, 
    error: passportError, 
    refetch: refetchPassport 
  } = useQuery(
    ['passport', currentPassportId],
    () => {
      if (!currentPassportId) return null;
      return passportManager.getPassport(currentPassportId);
    },
    {
      enabled: !!currentPassportId,
      refetchInterval: 2000, // Poll every 2 seconds for updates
      staleTime: 1000 // Consider stale after 1 second
    }
  );

  // Get context insights
  const {
    data: contextInsights = [],
    isLoading: isAnalyzing,
    error: analyzeError,
    refetch: refetchInsights
  } = useQuery(
    ['contextInsights', currentPassportId],
    async () => {
      if (!passport) return [];
      return orchestrationEngine.analyzeContext(passport);
    },
    {
      enabled: !!passport,
      staleTime: 30000 // Cache for 30 seconds
    }
  );

  // Get tool suggestions
  const {
    data: suggestedTools = [],
    refetch: refetchSuggestions
  } = useQuery(
    ['toolSuggestions', currentPassportId],
    async () => {
      if (!passport) return [];
      return orchestrationEngine.getSuggestedTools(passport);
    },
    {
      enabled: !!passport,
      staleTime: 30000
    }
  );

  // Get passport metrics
  const { data: passportMetrics } = useQuery(
    ['passportMetrics', currentPassportId],
    () => {
      if (!currentPassportId) return null;
      return passportManager.getPassportMetrics(currentPassportId);
    },
    {
      enabled: !!currentPassportId,
      refetchInterval: 5000 // Update metrics every 5 seconds
    }
  );

  // Processing mutation
  const {
    mutate: processPassport,
    isLoading: isProcessing,
    error: processError,
    data: processingResult
  } = useMutation(
    ['processPassport', currentPassportId],
    async (processingOptions: OrchestratedSuggestionsOptions) => {
      if (!currentPassportId) {
        throw new Error('No passport ID available');
      }
      
      return orchestrationEngine.processPassport(currentPassportId, {
        enableFastTrack: processingOptions.enableFastTrack ?? options.enableFastTrack ?? true,
        enableDeepTrack: processingOptions.enableDeepTrack ?? options.enableDeepTrack ?? true,
        maxConcurrency: processingOptions.maxConcurrency ?? options.maxConcurrency ?? 3,
        timeout: processingOptions.timeout ?? options.timeout ?? 60000
      });
    },
    {
      onSuccess: (result) => {
        toast.success(`Processing completed with ${result.overallScore.toFixed(1)}% score`);
        
        // Refresh related queries
        queryClient.invalidateQueries(['passport', currentPassportId]);
        queryClient.invalidateQueries(['passportMetrics', currentPassportId]);
      },
      onError: (error) => {
        toast.error(`Processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  );

  // Create passport function
  const createPassport = useCallback((config: PassportConfig) => {
    try {
      const newPassport = passportManager.createPassport(config);
      setCurrentPassportId(newPassport.passportId);
      
      toast.success('Passport created successfully');
      
      // Auto-process if enabled
      if (options.autoProcess) {
        setTimeout(() => {
          processPassport(options);
        }, 1000);
      }
    } catch (error) {
      toast.error(`Failed to create passport: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [options, processPassport]);

  // Subscribe to passport events
  useEffect(() => {
    if (!currentPassportId) return;

    const unsubscribes: (() => void)[] = [];

    // Subscribe to all events for this passport
    const unsubscribeAll = passportManager.subscribe('all', (event) => {
      if (event.passportId === currentPassportId) {
        setEvents(prev => [...prev.slice(-9), event]); // Keep last 10 events
        
        // Handle specific event types
        switch (event.type) {
          case 'processed':
            // Refresh insights when a tool completes processing
            queryClient.invalidateQueries(['contextInsights', currentPassportId]);
            queryClient.invalidateQueries(['toolSuggestions', currentPassportId]);
            break;
          
          case 'conflicted':
            toast.warning('Conflict detected between tools');
            break;
          
          case 'resolved':
            toast.success('Conflict resolved');
            break;
          
          case 'error':
            toast.error(`Processing error: ${event.data?.error || 'Unknown error'}`);
            break;
        }
      }
    });

    unsubscribes.push(unsubscribeAll);

    return () => {
      unsubscribes.forEach(unsub => unsub());
    };
  }, [currentPassportId, queryClient]);

  // Derived values
  const recommendedActions = processingResult?.recommendedActions || [];
  const keyFindings = processingResult?.keyFindings || [];
  const nextSteps = processingResult?.nextSteps || [];
  const overallScore = processingResult?.overallScore || 0;

  // Utility functions
  const refresh = useCallback(() => {
    if (currentPassportId) {
      queryClient.invalidateQueries(['passport', currentPassportId]);
      queryClient.invalidateQueries(['contextInsights', currentPassportId]);
      queryClient.invalidateQueries(['toolSuggestions', currentPassportId]);
      queryClient.invalidateQueries(['passportMetrics', currentPassportId]);
    }
  }, [currentPassportId, queryClient]);

  const clear = useCallback(() => {
    setCurrentPassportId(null);
    setEvents([]);
    queryClient.removeQueries(['passport']);
    queryClient.removeQueries(['contextInsights']);
    queryClient.removeQueries(['toolSuggestions']);
    queryClient.removeQueries(['passportMetrics']);
  }, [queryClient]);

  const startProcessing = useCallback((processingOptions?: OrchestratedSuggestionsOptions) => {
    processPassport(processingOptions || {});
  }, [processPassport]);

  return {
    // Passport management
    passport: passport || null,
    createPassport,
    passportMetrics,
    
    // Context analysis
    contextInsights,
    isAnalyzing,
    analyzeError: analyzeError as Error | null,
    
    // Tool suggestions
    suggestedTools,
    
    // Processing
    processingResult: processingResult || null,
    isProcessing,
    processError: processError as Error | null,
    startProcessing,
    
    // Actions and recommendations
    recommendedActions,
    keyFindings,
    nextSteps,
    
    // Events and status
    events,
    overallScore,
    
    // Utilities
    refresh,
    clear
  };
};

// Helper hook for quick analysis without full orchestration
export const useQuickAnalysis = (adCopy: {
  headline: string;
  body_text: string;
  cta: string;
  platform: string;
  industry?: string;
  target_audience?: string;
}) => {
  const [insights, setInsights] = useState<ContextInsight[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyze = useCallback(async () => {
    if (!adCopy.headline && !adCopy.body_text && !adCopy.cta) return;

    setIsAnalyzing(true);
    try {
      // Create a temporary passport for analysis
      const tempPassport: DataPassport = {
        schemaVersion: '1.0.0',
        projectId: 'temp',
        passportId: 'temp-' + Date.now(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        originTool: 'quick_analysis',
        originUser: 'current',
        payload: {
          adCopy,
          metadata: {
            version: 1,
            contentHash: 'temp',
            wordCount: (adCopy.headline + ' ' + adCopy.body_text + ' ' + adCopy.cta).split(' ').length,
            characterCount: (adCopy.headline + adCopy.body_text + adCopy.cta).length
          }
        },
        insights: [],
        conflicts: [],
        workflow: {
          currentStep: 'analyzing',
          completedSteps: [],
          nextSuggestedSteps: [],
          fastTrackCompleted: false,
          deepTrackCompleted: false
        },
        meta: {
          priority: 'medium',
          routingHints: [],
          processingTime: 0,
          retryCount: 0
        }
      };

      const contextInsights = await orchestrationEngine.analyzeContext(tempPassport);
      setInsights(contextInsights);
    } catch (error) {
      console.error('Quick analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [adCopy]);

  useEffect(() => {
    const debounceTimer = setTimeout(analyze, 500);
    return () => clearTimeout(debounceTimer);
  }, [analyze]);

  return {
    insights,
    isAnalyzing,
    refresh: analyze
  };
};