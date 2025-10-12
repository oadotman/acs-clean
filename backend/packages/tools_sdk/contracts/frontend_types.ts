/**
 * Frontend TypeScript API Contracts for AdCopySurge Tools SDK
 * 
 * This file contains TypeScript interfaces and types that define the contract
 * between the frontend application and the tools SDK backend services.
 * 
 * These types ensure type safety and provide excellent developer experience
 * when integrating with the ad copy analysis tools.
 */

// ===== CORE REQUEST/RESPONSE TYPES =====

/**
 * Main request structure for ad copy analysis
 */
export interface AnalysisRequest {
  /** The headline text to analyze */
  headline: string;
  
  /** The main body text content */
  body_text: string;
  
  /** Call-to-action text */
  cta: string;
  
  /** Industry context (optional) */
  industry?: string;
  
  /** Platform context (e.g., "facebook", "google", "linkedin") */
  platform?: string;
  
  /** Target audience description */
  target_audience?: string;
  
  /** Brand guidelines and voice requirements */
  brand_guidelines?: BrandGuidelines;
  
  /** Type of analysis to perform */
  analysis_type: AnalysisType;
  
  /** Custom flow configuration ID (optional) */
  custom_flow_id?: string;
  
  /** Additional metadata for the request */
  request_metadata?: Record<string, any>;
}

/**
 * Unified response structure for ad copy analysis results
 */
export interface AnalysisResponse {
  /** Whether the analysis completed successfully */
  success: boolean;
  
  /** Unique request identifier */
  request_id: string;
  
  /** Total execution time in seconds */
  execution_time: number;
  
  /** Type of analysis performed */
  analysis_type: AnalysisType;
  
  /** Overall quality score (0-100) */
  overall_score: number;
  
  /** Performance potential score (0-100) */
  performance_score: number;
  
  /** Psychological appeal score (0-100) */
  psychology_score: number;
  
  /** Brand alignment score (0-100) */
  brand_score: number;
  
  /** Legal compliance score (0-100) */
  legal_score: number;
  
  /** Key strengths identified */
  strengths: string[];
  
  /** Areas needing improvement */
  weaknesses: string[];
  
  /** Prioritized recommendations */
  recommendations: string[];
  
  /** Detailed results from each tool */
  tool_results: ToolResults;
  
  /** Execution metadata and statistics */
  execution_metadata: ExecutionMetadata;
  
  /** Error messages if any */
  errors?: string[];
  
  /** Warning messages if any */
  warnings?: string[];
}

/**
 * Brand guidelines configuration
 */
export interface BrandGuidelines {
  /** Brand voice characteristics */
  voice_attributes?: string[];
  
  /** Preferred tone (e.g., "professional", "casual", "urgent") */
  tone?: string;
  
  /** Brand personality traits */
  personality_traits?: string[];
  
  /** Messaging priorities and hierarchy */
  messaging_hierarchy?: string[];
  
  /** Required brand phrases or terminology */
  required_phrases?: string[];
  
  /** Prohibited words or phrases */
  prohibited_phrases?: string[];
  
  /** Brand voice examples */
  voice_examples?: string[];
}

/**
 * Available analysis types
 */
export type AnalysisType = 
  | 'comprehensive'  // Complete analysis using all tools
  | 'quick'         // Fast performance and psychology analysis
  | 'compliance'    // Brand and legal compliance focused
  | 'optimization'; // Performance optimization deep dive

/**
 * Tool execution results
 */
export interface ToolResults {
  performance_forensics?: ToolResult;
  psychology_scorer?: ToolResult;
  brand_voice_engine?: ToolResult;
  legal_risk_scanner?: ToolResult;
}

/**
 * Individual tool result structure
 */
export interface ToolResult {
  /** Whether the tool executed successfully */
  success: boolean;
  
  /** Tool-specific scores */
  scores?: Record<string, number>;
  
  /** Tool-specific insights */
  insights?: Record<string, any>;
  
  /** Tool-specific recommendations */
  recommendations?: string[];
  
  /** Generated variations (if applicable) */
  variations?: CopyVariation[];
  
  /** Alternative suggestions (if applicable) */
  alternatives?: Alternative[];
  
  /** Error message if failed */
  error?: string;
  
  /** Execution time for this tool */
  execution_time?: number;
  
  /** Confidence score for the analysis */
  confidence_score?: number;
}

/**
 * Copy variation structure
 */
export interface CopyVariation {
  /** Variation identifier */
  id: string;
  
  /** Type of optimization applied */
  type: string;
  
  /** Modified headline */
  headline: string;
  
  /** Modified body text */
  body_text: string;
  
  /** Modified CTA */
  cta: string;
  
  /** Focus of the optimization */
  optimization_focus: string;
  
  /** Expected improvement score */
  improvement_score?: number;
  
  /** Additional disclaimers (if applicable) */
  disclaimers?: string[];
}

/**
 * Alternative suggestion structure
 */
export interface Alternative {
  /** Original text that was flagged */
  original: string;
  
  /** Suggested alternatives */
  alternatives: string[];
  
  /** Category of the issue */
  category: string;
  
  /** Severity level */
  severity: 'low' | 'medium' | 'high';
  
  /** Reasoning for the suggestion */
  reasoning: string;
  
  /** Impact on persuasion if changed */
  persuasion_impact?: string;
}

/**
 * Execution metadata
 */
export interface ExecutionMetadata {
  /** Tools that executed successfully */
  successful_tools: string[];
  
  /** Tools that failed */
  failed_tools: string[];
  
  /** Execution strategy used */
  execution_strategy: string;
  
  /** Total number of tools attempted */
  total_tools: number;
  
  /** Cache information */
  cached_at?: number;
  
  /** Additional execution details */
  [key: string]: any;
}

// ===== BATCH PROCESSING TYPES =====

/**
 * Batch analysis request
 */
export interface BatchAnalysisRequest {
  /** Array of analysis requests */
  requests: AnalysisRequest[];
  
  /** Batch processing options */
  options?: BatchOptions;
}

/**
 * Batch processing options
 */
export interface BatchOptions {
  /** Maximum parallel executions */
  max_parallel?: number;
  
  /** Continue processing if individual requests fail */
  continue_on_error?: boolean;
  
  /** Priority for batch processing */
  priority?: 'low' | 'normal' | 'high';
}

/**
 * Batch analysis response
 */
export interface BatchAnalysisResponse {
  /** Whether the batch completed successfully */
  success: boolean;
  
  /** Batch identifier */
  batch_id: string;
  
  /** Total execution time */
  total_execution_time: number;
  
  /** Individual analysis results */
  results: AnalysisResponse[];
  
  /** Batch statistics */
  statistics: BatchStatistics;
  
  /** Batch-level errors */
  errors?: string[];
}

/**
 * Batch processing statistics
 */
export interface BatchStatistics {
  /** Total requests processed */
  total_requests: number;
  
  /** Successful analyses */
  successful_analyses: number;
  
  /** Failed analyses */
  failed_analyses: number;
  
  /** Average execution time per request */
  average_execution_time: number;
  
  /** Average overall score */
  average_overall_score: number;
}

// ===== CONFIGURATION TYPES =====

/**
 * Flow configuration for custom analysis
 */
export interface FlowConfiguration {
  /** Unique flow identifier */
  flow_id: string;
  
  /** Human-readable name */
  name: string;
  
  /** Description of the flow */
  description: string;
  
  /** Execution strategy */
  execution_strategy: ExecutionStrategy;
  
  /** Priority level */
  priority: Priority;
  
  /** Maximum parallel workers */
  max_parallel_workers: number;
  
  /** Total timeout in seconds */
  total_timeout?: number;
  
  /** Continue on individual tool errors */
  continue_on_error: boolean;
  
  /** Output aggregation strategy */
  output_aggregation_strategy: string;
  
  /** Flow steps configuration */
  steps: FlowStep[];
}

/**
 * Individual flow step
 */
export interface FlowStep {
  /** Tool name to execute */
  tool_name: string;
  
  /** Tool class name */
  tool_class: string;
  
  /** Tool configuration */
  config: ToolConfig;
  
  /** Dependencies on other tools */
  dependencies: string[];
  
  /** Parallel execution group */
  parallel_group?: string;
  
  /** Whether this step is required */
  required: boolean;
  
  /** Timeout override for this step */
  timeout_override?: number;
  
  /** Number of retry attempts */
  retry_count: number;
}

/**
 * Tool configuration
 */
export interface ToolConfig {
  /** Tool name */
  name: string;
  
  /** Tool type */
  tool_type: string;
  
  /** Execution timeout */
  timeout: number;
  
  /** Tool-specific parameters */
  parameters: Record<string, any>;
}

/**
 * Execution strategies
 */
export type ExecutionStrategy = 'sequential' | 'parallel' | 'mixed';

/**
 * Priority levels
 */
export type Priority = 'low' | 'normal' | 'high' | 'critical';

// ===== SYSTEM STATUS TYPES =====

/**
 * System health status
 */
export interface HealthStatus {
  /** Overall system status */
  status: 'healthy' | 'degraded' | 'unhealthy';
  
  /** Health check timestamp */
  timestamp: number;
  
  /** Individual tool health */
  tools: Record<string, boolean>;
  
  /** System statistics */
  statistics: SystemStatistics;
  
  /** Active executions count */
  active_executions: number;
  
  /** Any system issues */
  issues?: string[];
}

/**
 * System statistics
 */
export interface SystemStatistics {
  /** Total analyses performed */
  total_analyses: number;
  
  /** Analyses in last 24 hours */
  analyses_24h: number;
  
  /** Average response time */
  average_response_time: number;
  
  /** Success rate percentage */
  success_rate: number;
  
  /** Cache hit rate */
  cache_hit_rate: number;
  
  /** Memory usage percentage */
  memory_usage: number;
  
  /** CPU usage percentage */
  cpu_usage: number;
}

// ===== ERROR TYPES =====

/**
 * API error response
 */
export interface ApiError {
  /** Error type */
  error_type: string;
  
  /** Human-readable error message */
  message: string;
  
  /** Error details */
  details?: Record<string, any>;
  
  /** Request ID for tracking */
  request_id?: string;
  
  /** Timestamp of error */
  timestamp: number;
  
  /** Stack trace (development only) */
  stack_trace?: string;
}

/**
 * Validation error details
 */
export interface ValidationError {
  /** Field that failed validation */
  field: string;
  
  /** Validation rule that was violated */
  rule: string;
  
  /** Error message */
  message: string;
  
  /** Received value */
  received_value?: any;
  
  /** Expected value format */
  expected_format?: string;
}

// ===== ANALYTICS TYPES =====

/**
 * Usage analytics data
 */
export interface UsageAnalytics {
  /** Time period for analytics */
  period: string;
  
  /** Analysis type usage breakdown */
  analysis_type_usage: Record<AnalysisType, number>;
  
  /** Tool usage statistics */
  tool_usage: Record<string, ToolUsageStats>;
  
  /** Performance metrics */
  performance_metrics: PerformanceMetrics;
  
  /** Industry breakdown */
  industry_breakdown: Record<string, number>;
  
  /** Platform breakdown */
  platform_breakdown: Record<string, number>;
}

/**
 * Tool usage statistics
 */
export interface ToolUsageStats {
  /** Total executions */
  total_executions: number;
  
  /** Success rate */
  success_rate: number;
  
  /** Average execution time */
  average_execution_time: number;
  
  /** Average confidence score */
  average_confidence: number;
}

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  /** Average overall score */
  average_overall_score: number;
  
  /** Score distribution */
  score_distribution: Record<string, number>;
  
  /** Most common recommendations */
  top_recommendations: Array<{ recommendation: string; frequency: number }>;
  
  /** Average improvement potential */
  average_improvement_potential: number;
}

// ===== UTILITY TYPES =====

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  /** Data items */
  data: T[];
  
  /** Pagination metadata */
  pagination: {
    /** Current page number */
    page: number;
    
    /** Items per page */
    per_page: number;
    
    /** Total number of items */
    total_items: number;
    
    /** Total number of pages */
    total_pages: number;
    
    /** Whether there are more pages */
    has_next: boolean;
    
    /** Whether there are previous pages */
    has_prev: boolean;
  };
}

/**
 * Sort options
 */
export interface SortOptions {
  /** Field to sort by */
  field: string;
  
  /** Sort direction */
  direction: 'asc' | 'desc';
}

/**
 * Filter options
 */
export interface FilterOptions {
  /** Field to filter by */
  field: string;
  
  /** Filter operator */
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'in';
  
  /** Filter value */
  value: any;
}

// ===== API ENDPOINTS TYPES =====

/**
 * Available API endpoints
 */
export interface ApiEndpoints {
  /** Analysis endpoints */
  analysis: {
    /** Single copy analysis */
    single: '/api/v1/analysis/single';
    
    /** Batch analysis */
    batch: '/api/v1/analysis/batch';
    
    /** Quick performance check */
    quick: '/api/v1/analysis/quick';
  };
  
  /** Health and status endpoints */
  health: {
    /** System health check */
    status: '/api/v1/health/status';
    
    /** Individual tool health */
    tools: '/api/v1/health/tools';
    
    /** System metrics */
    metrics: '/api/v1/health/metrics';
  };
  
  /** Configuration endpoints */
  config: {
    /** List flow configurations */
    flows: '/api/v1/config/flows';
    
    /** Get specific flow */
    flow: '/api/v1/config/flows/:id';
    
    /** Create custom flow */
    create: '/api/v1/config/flows';
    
    /** Validate flow */
    validate: '/api/v1/config/flows/validate';
  };
  
  /** Analytics endpoints */
  analytics: {
    /** Usage statistics */
    usage: '/api/v1/analytics/usage';
    
    /** Performance metrics */
    performance: '/api/v1/analytics/performance';
    
    /** System statistics */
    system: '/api/v1/analytics/system';
  };
}

// ===== CONSTANTS =====

/**
 * Analysis type descriptions
 */
export const ANALYSIS_TYPE_DESCRIPTIONS: Record<AnalysisType, string> = {
  comprehensive: 'Complete analysis using all tools for maximum insights',
  quick: 'Fast performance and psychology analysis for quick optimization',
  compliance: 'Focus on brand alignment and legal compliance',
  optimization: 'Deep dive into performance metrics and psychological triggers'
};

/**
 * Tool names
 */
export const TOOL_NAMES = {
  PERFORMANCE_FORENSICS: 'performance_forensics',
  PSYCHOLOGY_SCORER: 'psychology_scorer',
  BRAND_VOICE_ENGINE: 'brand_voice_engine',
  LEGAL_RISK_SCANNER: 'legal_risk_scanner'
} as const;

/**
 * Score thresholds
 */
export const SCORE_THRESHOLDS = {
  EXCELLENT: 90,
  GOOD: 75,
  AVERAGE: 60,
  POOR: 40,
  CRITICAL: 25
} as const;

/**
 * Default configuration values
 */
export const DEFAULT_CONFIG = {
  ANALYSIS_TYPE: 'comprehensive' as AnalysisType,
  TIMEOUT: 120,
  MAX_PARALLEL_WORKERS: 4,
  CACHE_TTL: 300,
  MAX_RECOMMENDATIONS: 10
} as const;