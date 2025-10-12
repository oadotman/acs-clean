import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for data fetching with standardized state management
 * Provides loading, error, and empty states following the required pattern
 * 
 * @param {Function} fetchFunction - Async function that fetches data
 * @param {*} defaultValue - Default value to initialize data ([] for arrays, {} for objects, 0 for counts)
 * @param {Object} options - Configuration options
 * @param {boolean} options.immediate - Whether to fetch immediately on mount (default: true)
 * @param {Array} options.dependencies - Dependencies that trigger refetch (default: [])
 * @param {boolean} options.keepPreviousData - Whether to keep previous data during refetch (default: false)
 * @param {Function} options.onSuccess - Callback when fetch succeeds
 * @param {Function} options.onError - Callback when fetch fails
 * @param {number} options.retryCount - Number of automatic retries (default: 0)
 * @param {number} options.retryDelay - Delay between retries in ms (default: 1000)
 * 
 * @returns {Object} { data, isLoading, error, refetch, isRefetching }
 */
const useFetch = (
  fetchFunction,
  defaultValue = null,
  options = {}
) => {
  const {
    immediate = true,
    dependencies = [],
    keepPreviousData = false,
    onSuccess = null,
    onError = null,
    retryCount = 0,
    retryDelay = 1000,
    // New: hard timeout for fetches to prevent endless loading (ms)
    timeoutMs = 8000,
  } = options;

  // State management
  const [data, setData] = useState(defaultValue);
  const [isLoading, setIsLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const [isRefetching, setIsRefetching] = useState(false);

  // Refs for tracking mount state and retry attempts
  const isMountedRef = useRef(true);
  const retryAttemptRef = useRef(0);
  const timeoutRef = useRef(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Helper function to check if data is empty
  const isDataEmpty = useCallback((data) => {
    if (data === null || data === undefined) return true;
    if (Array.isArray(data)) return data.length === 0;
    if (typeof data === 'object') return Object.keys(data).length === 0;
    if (typeof data === 'number') return data === 0;
    if (typeof data === 'string') return data.trim() === '';
    return false;
  }, []);

  // Main fetch function with retry logic
  const performFetch = useCallback(async (isRefetch = false) => {
    if (!fetchFunction) {
      console.warn('⚠️ No fetch function provided to useFetch');
      setIsLoading(false);
      setIsRefetching(false);
      return;
    }

    console.log('🚀 useFetch: Starting fetch, isRefetch:', isRefetch);

    try {
      // Set loading states
      if (isRefetch) {
        setIsRefetching(true);
      } else {
        setIsLoading(true);
      }

      // Clear previous error
      setError(null);

      // Call the fetch function with a hard timeout to avoid endless loading
      const timeoutPromise = new Promise((_, reject) => {
        timeoutRef.current = setTimeout(() => {
          reject(new Error(`Request timed out after ${timeoutMs}ms`));
        }, timeoutMs);
      });

      const result = await Promise.race([
        Promise.resolve().then(() => fetchFunction()),
        timeoutPromise,
      ]);

      // Only update state if component is still mounted
      if (!isMountedRef.current) return;

      // Always ensure we have a proper default value
      const finalData = result !== null && result !== undefined ? result : defaultValue;
      
      // Update data state
      setData(finalData);

      // Reset retry attempts on success
      retryAttemptRef.current = 0;

      // Call success callback
      if (onSuccess) {
        onSuccess(finalData);
      }

    } catch (err) {
      console.error('🚨 useFetch error details:', {
        error: err.message,
        stack: err.stack,
        isRefetch,
        functionName: fetchFunction.name,
        timestamp: new Date().toISOString()
      });

      // Only update state if component is still mounted
      if (!isMountedRef.current) {
        console.log('💭 Component unmounted during error, not updating state');
        return;
      }

      // Handle retry logic
      if (retryAttemptRef.current < retryCount) {
        retryAttemptRef.current += 1;
        
        // Set timeout for retry
        timeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            performFetch(isRefetch);
          }
        }, retryDelay);

        return; // Don't set error state during retry
      }

      // Set error state after all retries exhausted
      setError(err);

      // Ensure we have default data even on error
      if (!keepPreviousData || data === null) {
        setData(defaultValue);
      }

      // Call error callback
      if (onError) {
        onError(err);
      }

    } finally {
      // Clear timeout if it exists
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // Only update loading states if component is still mounted
      if (isMountedRef.current) {
        console.log('✅ useFetch: Clearing loading states');
        setIsLoading(false);
        setIsRefetching(false);
      }
      
      // Emergency timeout to ensure loading states are always cleared
      // This is a safety net in case something goes wrong
      setTimeout(() => {
        if (isMountedRef.current) {
          console.log('🚑 Emergency timeout: Forcing loading states to false');
          setIsLoading(false);
          setIsRefetching(false);
        }
      }, 100);
    }
  }, [
    fetchFunction, 
    defaultValue, 
    keepPreviousData, 
    onSuccess, 
    onError, 
    retryCount, 
    retryDelay,
    timeoutMs
    // Removed 'data' dependency to prevent infinite loops
  ]);

  // Refetch function that can be called manually
  const refetch = useCallback(() => {
    retryAttemptRef.current = 0; // Reset retry count for manual refetch
    return performFetch(true);
  }, [performFetch]);

  // Effect for initial fetch and dependency changes
  useEffect(() => {
    if (immediate) {
      performFetch(false);
    }
  }, [immediate, performFetch, ...dependencies]);

  // Return standardized state object
  return {
    // Data state
    data,
    
    // Loading states
    isLoading,
    isRefetching,
    
    // Error state
    error,
    
    // Actions
    refetch,
    
    // Helper properties
    isEmpty: isDataEmpty(data),
    hasError: !!error,
    isSuccess: !isLoading && !error,
    
    // Combined state helpers for easier conditionals
    isInitialLoading: isLoading && !isRefetching,
    canShowContent: !isLoading && !error && !isDataEmpty(data),
    shouldShowEmpty: !isLoading && !error && isDataEmpty(data),
    shouldShowError: !isLoading && !!error,
    shouldShowLoading: isLoading && !isRefetching
  };
};

export default useFetch;
