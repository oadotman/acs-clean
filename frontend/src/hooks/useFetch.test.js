import { renderHook, act, waitFor } from '@testing-library/react';
import useFetch from './useFetch';

// Mock data for testing
const mockData = { id: 1, name: 'Test Item' };
const mockError = new Error('Fetch failed');

describe('useFetch Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Functionality', () => {
    it('should initialize with default values', () => {
      const fetchFunction = jest.fn();
      const defaultValue = [];

      const { result } = renderHook(() => 
        useFetch(fetchFunction, defaultValue, { immediate: false })
      );

      expect(result.current.data).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(result.current.isEmpty).toBe(true);
    });

    it('should fetch data on mount when immediate is true', async () => {
      const fetchFunction = jest.fn().mockResolvedValue(mockData);
      const defaultValue = null;

      const { result } = renderHook(() => 
        useFetch(fetchFunction, defaultValue, { immediate: true })
      );

      expect(result.current.isLoading).toBe(true);
      expect(fetchFunction).toHaveBeenCalledTimes(1);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBe(null);
      expect(result.current.isEmpty).toBe(false);
    });

    it('should not fetch data on mount when immediate is false', () => {
      const fetchFunction = jest.fn();
      const defaultValue = [];

      renderHook(() => 
        useFetch(fetchFunction, defaultValue, { immediate: false })
      );

      expect(fetchFunction).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle fetch errors correctly', async () => {
      const fetchFunction = jest.fn().mockRejectedValue(mockError);
      const defaultValue = [];

      const { result } = renderHook(() => 
        useFetch(fetchFunction, defaultValue)
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toEqual(mockError);
      expect(result.current.data).toEqual(defaultValue);
      expect(result.current.hasError).toBe(true);
      expect(result.current.shouldShowError).toBe(true);
    });

    it('should retry on failure when retryCount is set', async () => {
      const fetchFunction = jest.fn()
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, null, { 
          retryCount: 1,
          retryDelay: 100 
        })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      }, { timeout: 2000 });

      expect(fetchFunction).toHaveBeenCalledTimes(2);
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBe(null);
    });
  });

  describe('State Helpers', () => {
    it('should provide correct state helpers for loading state', () => {
      const fetchFunction = jest.fn().mockImplementation(() => 
        new Promise(() => {}) // Never resolves
      );

      const { result } = renderHook(() => 
        useFetch(fetchFunction, [])
      );

      expect(result.current.shouldShowLoading).toBe(true);
      expect(result.current.shouldShowError).toBe(false);
      expect(result.current.shouldShowEmpty).toBe(false);
      expect(result.current.canShowContent).toBe(false);
    });

    it('should provide correct state helpers for error state', async () => {
      const fetchFunction = jest.fn().mockRejectedValue(mockError);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, [])
      );

      await waitFor(() => {
        expect(result.current.shouldShowError).toBe(true);
      });

      expect(result.current.shouldShowLoading).toBe(false);
      expect(result.current.shouldShowEmpty).toBe(false);
      expect(result.current.canShowContent).toBe(false);
    });

    it('should provide correct state helpers for empty state', async () => {
      const fetchFunction = jest.fn().mockResolvedValue([]);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, [])
      );

      await waitFor(() => {
        expect(result.current.shouldShowEmpty).toBe(true);
      });

      expect(result.current.shouldShowLoading).toBe(false);
      expect(result.current.shouldShowError).toBe(false);
      expect(result.current.canShowContent).toBe(false);
    });

    it('should provide correct state helpers for success state', async () => {
      const fetchFunction = jest.fn().mockResolvedValue([mockData]);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, [])
      );

      await waitFor(() => {
        expect(result.current.canShowContent).toBe(true);
      });

      expect(result.current.shouldShowLoading).toBe(false);
      expect(result.current.shouldShowError).toBe(false);
      expect(result.current.shouldShowEmpty).toBe(false);
    });
  });

  describe('Refetch Functionality', () => {
    it('should refetch data when refetch is called', async () => {
      const fetchFunction = jest.fn().mockResolvedValue(mockData);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, null)
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(fetchFunction).toHaveBeenCalledTimes(1);

      act(() => {
        result.current.refetch();
      });

      expect(result.current.isRefetching).toBe(true);

      await waitFor(() => {
        expect(result.current.isRefetching).toBe(false);
      });

      expect(fetchFunction).toHaveBeenCalledTimes(2);
    });
  });

  describe('Dependencies', () => {
    it('should refetch when dependencies change', async () => {
      const fetchFunction = jest.fn().mockResolvedValue(mockData);
      let userId = 1;

      const { result, rerender } = renderHook(() => 
        useFetch(fetchFunction, null, { dependencies: [userId] })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(fetchFunction).toHaveBeenCalledTimes(1);

      // Change dependency
      userId = 2;
      rerender();

      await waitFor(() => {
        expect(fetchFunction).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Callbacks', () => {
    it('should call onSuccess callback when fetch succeeds', async () => {
      const fetchFunction = jest.fn().mockResolvedValue(mockData);
      const onSuccess = jest.fn();

      renderHook(() => 
        useFetch(fetchFunction, null, { onSuccess })
      );

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(mockData);
      });
    });

    it('should call onError callback when fetch fails', async () => {
      const fetchFunction = jest.fn().mockRejectedValue(mockError);
      const onError = jest.fn();

      renderHook(() => 
        useFetch(fetchFunction, null, { onError })
      );

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(mockError);
      });
    });
  });

  describe('Data Types', () => {
    it('should handle array data correctly', async () => {
      const arrayData = [{ id: 1 }, { id: 2 }];
      const fetchFunction = jest.fn().mockResolvedValue(arrayData);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, [])
      );

      await waitFor(() => {
        expect(result.current.data).toEqual(arrayData);
        expect(result.current.isEmpty).toBe(false);
      });
    });

    it('should handle object data correctly', async () => {
      const objectData = { count: 5, items: [] };
      const fetchFunction = jest.fn().mockResolvedValue(objectData);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, {})
      );

      await waitFor(() => {
        expect(result.current.data).toEqual(objectData);
        expect(result.current.isEmpty).toBe(false);
      });
    });

    it('should handle number data correctly', async () => {
      const numberData = 42;
      const fetchFunction = jest.fn().mockResolvedValue(numberData);

      const { result } = renderHook(() => 
        useFetch(fetchFunction, 0)
      );

      await waitFor(() => {
        expect(result.current.data).toBe(numberData);
        expect(result.current.isEmpty).toBe(false);
      });
    });
  });
});

/*
To run these tests, add the following to your package.json scripts:

"scripts": {
  "test": "react-scripts test",
  "test:hooks": "react-scripts test src/hooks"
}

Then run:
npm run test:hooks

These tests cover:
- Basic functionality and initialization
- Error handling and retry logic
- State helpers for different states
- Refetch functionality
- Dependency-based refetching
- Success and error callbacks
- Different data types (arrays, objects, numbers)

The tests ensure the hook behaves correctly in all scenarios and provides
the right state helpers for the UI components.
*/
