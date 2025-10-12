# Data Fetching Hook Documentation

## Overview

The `useFetch` hook provides a standardized way to handle data fetching across the application with consistent loading, error, and empty states. This hook implements the required pattern for all data-fetching components.

## Usage Pattern

All data-fetching pages should implement this exact pattern:

```jsx
// Loading State → show skeleton loaders while waiting for the API response
if (isLoading) return <SkeletonLoader />

// Error State → show "Something went wrong, please try again." if the fetch fails  
if (error) return <ErrorMessage />

// Empty State → if successful but no data, render "No records yet. Start by creating one!"
if (!data || data.length === 0) return <EmptyState />

// Data State → when valid data is returned, display the actual UI
return <DashboardContent data={data} />
```

## useFetch Hook

### Basic Usage

```jsx
import useFetch from '../hooks/useFetch';

const MyComponent = () => {
  const {
    data,
    isLoading,
    error,
    refetch,
    shouldShowEmpty,
    shouldShowError,
    shouldShowLoading
  } = useFetch(
    fetchFunction,      // Async function that fetches data
    defaultValue,       // Default value ([] for arrays, {} for objects, 0 for counts)
    options            // Configuration options
  );

  if (shouldShowLoading) return <SkeletonLoader />;
  if (shouldShowError) return <ErrorMessage onRetry={refetch} />;
  if (shouldShowEmpty) return <EmptyState />;
  
  return <MyContent data={data} />;
};
```

### Parameters

1. **fetchFunction** `(Function)`: Async function that returns data
2. **defaultValue** `(any)`: Default value to initialize data
   - `[]` for arrays
   - `{}` for objects  
   - `0` for counts
   - `null` for single entities
3. **options** `(Object)`: Configuration options

### Options

```jsx
const options = {
  immediate: true,           // Fetch immediately on mount (default: true)
  dependencies: [],          // Dependencies that trigger refetch (default: [])
  keepPreviousData: false,   // Keep previous data during refetch (default: false)
  onSuccess: (data) => {},   // Callback when fetch succeeds
  onError: (error) => {},    // Callback when fetch fails
  retryCount: 0,             // Number of automatic retries (default: 0)
  retryDelay: 1000          // Delay between retries in ms (default: 1000)
};
```

### Return Values

```jsx
{
  // Data state
  data,                    // The fetched data
  
  // Loading states
  isLoading,              // True during initial load or when immediate=true
  isRefetching,           // True during manual refetch
  
  // Error state
  error,                  // Error object if fetch failed
  
  // Actions
  refetch,                // Function to manually refetch data
  
  // Helper properties
  isEmpty,                // True if data is empty/null/undefined
  hasError,               // True if there's an error
  isSuccess,              // True if not loading and no error
  
  // Combined state helpers for easier conditionals
  isInitialLoading,       // True only during initial load
  canShowContent,         // True when data is available and should be shown
  shouldShowEmpty,        // True when empty state should be displayed
  shouldShowError,        // True when error state should be displayed
  shouldShowLoading       // True when loading state should be displayed
}
```

## Implementation Examples

### Dashboard Data Fetching

```jsx
import useFetch from '../hooks/useFetch';
import { SkeletonLoader, ErrorMessage, EmptyState } from '../components/ui';

const Dashboard = () => {
  const { user } = useAuth();
  
  const fetchAnalytics = useCallback(async () => {
    if (!user) return { total_analyses: 0, avg_score_improvement: 0 };
    return await apiService.getDashboardAnalytics();
  }, [user]);

  const {
    data: analytics,
    shouldShowLoading,
    shouldShowError,
    error,
    refetch
  } = useFetch(
    fetchAnalytics,
    { total_analyses: 0, avg_score_improvement: 0 }, // Always provide sensible defaults
    { dependencies: [user] }
  );

  if (shouldShowLoading) return <SkeletonLoader variant="dashboard" />;
  if (shouldShowError) return <ErrorMessage onRetry={refetch} error={error} />;
  
  return <DashboardContent analytics={analytics} />;
};
```

### Analysis Results

```jsx
const AnalysisResults = () => {
  const { analysisId } = useParams();
  
  const fetchAnalysis = useCallback(async () => {
    if (!analysisId) throw new Error('Analysis ID required');
    return await apiService.getAnalysisDetail(analysisId);
  }, [analysisId]);

  const {
    data: analysis,
    shouldShowLoading,
    shouldShowError,
    shouldShowEmpty,
    error,
    refetch
  } = useFetch(
    fetchAnalysis,
    null,
    { 
      dependencies: [analysisId],
      retryCount: 1,
      retryDelay: 2000
    }
  );

  if (shouldShowLoading) return <SkeletonLoader variant="analysis" />;
  if (shouldShowError) return <ErrorMessage onRetry={refetch} />;
  if (shouldShowEmpty) return <EmptyState variant="analysis" />;
  
  return <AnalysisContent analysis={analysis} />;
};
```

### List with Empty State

```jsx
const AnalysesList = () => {
  const fetchAnalyses = useCallback(async () => {
    return await dataService.getAnalysesHistory(user.id, 10, 0);
  }, [user]);

  const { data: analyses, shouldShowLoading, shouldShowError, shouldShowEmpty } = useFetch(
    fetchAnalyses,
    [], // Always initialize arrays as empty array
    { dependencies: [user] }
  );

  if (shouldShowLoading) return <SkeletonLoader variant="list" count={5} />;
  if (shouldShowError) return <ErrorMessage />;
  if (shouldShowEmpty) {
    return (
      <EmptyState
        variant="analysis"
        title="No analyses yet"
        description="Start by analyzing your first ad to get AI-powered insights."
        actionText="Create Your First Analysis"
        onAction={() => navigate('/analyze')}
      />
    );
  }
  
  return <AnalysesList analyses={analyses} />;
};
```

## Best Practices

### 1. Always Provide Default Values

```jsx
// ✅ Good - prevents UI from breaking
useFetch(fetchAnalytics, { total_analyses: 0, avg_score: 0 })
useFetch(fetchList, [])
useFetch(fetchCount, 0)

// ❌ Bad - can cause undefined errors
useFetch(fetchAnalytics, null)
useFetch(fetchList, null)
```

### 2. Use Meaningful Dependencies

```jsx
// ✅ Good - refetches when user changes
useFetch(fetchUserData, defaultValue, { dependencies: [user] })

// ❌ Bad - may cause unnecessary refetches
useFetch(fetchUserData, defaultValue, { dependencies: [user, someUnrelatedState] })
```

### 3. Handle Null Safety

```jsx
// ✅ Good - safe access with nullish coalescing
<Typography>{analytics?.total_analyses ?? 0}</Typography>
<Typography>{subscription?.monthly_analyses ?? 0}</Typography>

// ❌ Bad - can cause errors if data is null
<Typography>{analytics.total_analyses}</Typography>
```

### 4. Implement Proper Error Handling

```jsx
const fetchData = useCallback(async () => {
  if (!requiredParam) {
    throw new Error('Required parameter missing');
  }
  return await apiService.getData(requiredParam);
}, [requiredParam]);
```

### 5. Use State Helpers for Cleaner Code

```jsx
// ✅ Good - use provided state helpers
if (shouldShowLoading) return <SkeletonLoader />;
if (shouldShowError) return <ErrorMessage />;
if (shouldShowEmpty) return <EmptyState />;

// ❌ Avoid complex conditionals
if (isLoading && !isRefetching) return <SkeletonLoader />;
if (!isLoading && error) return <ErrorMessage />;
```

## State Management Rules

1. **Always initialize state with sensible defaults** (`[]` for lists, `{}` for objects, `0` for counts)
2. **Ensure isLoading is set to false** after API call resolves, even if response is empty
3. **Include error handling** - show "Something went wrong, please try again." if fetch fails
4. **Keep components reusable** so the same structure works across different dashboard sections

## Component Integration

The hook works seamlessly with our UI components:

- **SkeletonLoader**: Different variants for different page types
- **ErrorMessage**: Consistent error display with retry functionality
- **EmptyState**: Contextual empty states with call-to-action buttons

This pattern ensures consistent user experience across the entire application while maintaining clean, maintainable code.
