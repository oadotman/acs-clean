# UI Components Documentation

This directory contains standardized UI components for consistent data fetching states across the application.

## Components Overview

- **SkeletonLoader**: Loading state components with different variants
- **ErrorMessage**: Error state components with retry functionality
- **EmptyState**: Empty state components with call-to-action buttons

## SkeletonLoader

Provides consistent loading skeletons for different page types.

### Usage

```jsx
import { SkeletonLoader } from '../components/ui';

// Dashboard loading
<SkeletonLoader variant="dashboard" maxWidth="xl" />

// Analysis page loading
<SkeletonLoader variant="analysis" maxWidth="lg" />

// Profile page loading
<SkeletonLoader variant="profile" maxWidth="md" />

// List loading
<SkeletonLoader variant="list" count={5} />

// Card grid loading
<SkeletonLoader variant="card" count={6} />

// Form loading
<SkeletonLoader variant="form" count={4} />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `'dashboard'` | Skeleton type: 'dashboard', 'analysis', 'profile', 'list', 'card', 'form' |
| `count` | `number` | `1` | Number of items to show (for list/card variants) |
| `maxWidth` | `string` | `'lg'` | Maximum width of container |
| `sx` | `object` | `{}` | Additional styling |

### Variants

- **dashboard**: Full dashboard layout with header, stats cards, and content sections
- **analysis**: Analysis results page with scores and alternatives sections
- **profile**: Profile page with personal info and subscription details
- **list**: Repeated list items
- **card**: Grid of cards
- **form**: Form fields with labels

## ErrorMessage

Displays consistent error messages with retry functionality.

### Usage

```jsx
import { ErrorMessage } from '../components/ui';

// Page-level error
<ErrorMessage
  variant="page"
  title="Failed to load data"
  message="We couldn't load your data. Please try again."
  error={error}
  onRetry={refetch}
  maxWidth="lg"
/>

// Inline error
<ErrorMessage
  variant="inline"
  title="Upload failed"
  message="The file could not be uploaded."
  onRetry={() => uploadFile()}
/>

// Compact error
<ErrorMessage
  variant="compact"
  message="Connection error"
  onRetry={retry}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `'default'` | Error display type: 'default', 'page', 'inline', 'compact' |
| `title` | `string` | `'Something went wrong'` | Error title |
| `message` | `string` | `'Please try again...'` | Error message |
| `error` | `Error` | `null` | Error object for development details |
| `onRetry` | `function` | `null` | Retry function |
| `onHome` | `function` | `null` | Navigate home function |
| `onSupport` | `function` | `null` | Contact support function |
| `showActions` | `boolean` | `true` | Show action buttons |
| `showDetails` | `boolean` | `false` | Show error details (dev mode) |
| `maxWidth` | `string` | `'sm'` | Maximum width |
| `sx` | `object` | `{}` | Additional styling |

### Variants

- **page**: Full-page error with large icon and multiple action buttons
- **inline**: Alert-style error for inline use
- **compact**: Minimal error for small spaces
- **default**: Standard error display

## EmptyState

Displays consistent empty states with contextual messaging and actions.

### Usage

```jsx
import { EmptyState } from '../components/ui';

// Analysis empty state
<EmptyState
  variant="analysis"
  title="No analyses yet"
  description="Start by analyzing your first ad to get insights."
  actionText="Create Analysis"
  onAction={() => navigate('/analyze')}
/>

// Custom empty state
<EmptyState
  variant="generic"
  title="No data found"
  description="Try adjusting your filters or create new content."
  actionText="Get Started"
  onAction={handleAction}
  size="large"
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `'analysis'` | Empty state type: 'analysis', 'history', 'reports', 'templates', 'generic' |
| `title` | `string` | `null` | Custom title (overrides variant default) |
| `description` | `string` | `null` | Custom description (overrides variant default) |
| `actionText` | `string` | `null` | Custom action text (overrides variant default) |
| `onAction` | `function` | `null` | Action button callback |
| `size` | `string` | `'medium'` | Size: 'small', 'medium', 'large' |

### Variants

- **analysis**: For analysis-related empty states
- **history**: For analysis history empty states
- **reports**: For reports/analytics empty states
- **templates**: For template library empty states
- **generic**: Generic empty state

## Integration with useFetch Hook

These components are designed to work seamlessly with the `useFetch` hook:

```jsx
const MyComponent = () => {
  const {
    data,
    shouldShowLoading,
    shouldShowError,
    shouldShowEmpty,
    error,
    refetch
  } = useFetch(fetchData, []);

  if (shouldShowLoading) {
    return <SkeletonLoader variant="dashboard" />;
  }

  if (shouldShowError) {
    return (
      <ErrorMessage
        variant="page"
        title="Failed to load dashboard"
        message="We couldn't load your data. Please try again."
        error={error}
        onRetry={refetch}
      />
    );
  }

  if (shouldShowEmpty) {
    return (
      <EmptyState
        variant="analysis"
        title="No data yet"
        description="Start by creating your first item."
        actionText="Get Started"
        onAction={() => navigate('/create')}
      />
    );
  }

  return <MyContent data={data} />;
};
```

## Styling Guidelines

All components follow the app's design system:

- **Colors**: Use theme palette colors
- **Typography**: Use Material-UI typography variants
- **Spacing**: Use consistent spacing units
- **Animations**: Subtle animations for better UX
- **Responsiveness**: All components are responsive by default

## Best Practices

### 1. Choose the Right Variant

```jsx
// ✅ Good - choose appropriate variant for context
<SkeletonLoader variant="dashboard" />  // For dashboard pages
<SkeletonLoader variant="list" />       // For list pages
<ErrorMessage variant="page" />         // For full-page errors
<ErrorMessage variant="inline" />       // For form errors
```

### 2. Provide Meaningful Messages

```jsx
// ✅ Good - specific, actionable messages
<EmptyState
  title="No analyses found"
  description="You haven't run any ad analyses yet. Create your first analysis to get started."
  actionText="Create First Analysis"
/>

// ❌ Bad - generic, unhelpful messages
<EmptyState
  title="No data"
  description="Nothing here."
  actionText="Click here"
/>
```

### 3. Handle Retry Actions Properly

```jsx
// ✅ Good - proper retry handling
<ErrorMessage
  onRetry={refetch}
  message="Failed to load data. Please try again."
/>

// ❌ Bad - no retry action
<ErrorMessage
  message="Something went wrong."
/>
```

### 4. Use Appropriate Sizes

```jsx
// ✅ Good - match size to context
<EmptyState size="large" />   // For main content areas
<EmptyState size="small" />   // For sidebar or compact areas
```

## Accessibility

All components follow accessibility best practices:

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **ARIA labels**: Screen reader friendly
- **Keyboard navigation**: Full keyboard support
- **Color contrast**: WCAG AA compliant
- **Focus management**: Proper focus indicators

## Testing

Components include comprehensive testing:

```jsx
// Test loading state
expect(screen.getByTestId('skeleton-dashboard')).toBeInTheDocument();

// Test error state with retry
const retryButton = screen.getByText('Try Again');
fireEvent.click(retryButton);
expect(mockRefetch).toHaveBeenCalled();

// Test empty state action
const actionButton = screen.getByText('Create Analysis');
fireEvent.click(actionButton);
expect(mockNavigate).toHaveBeenCalledWith('/analyze');
```

This standardized approach ensures consistent user experience and maintainable code across the entire application.
