/**
 * Universal Data Passport System
 * 
 * Every piece of ad copy gets a "passport" that travels through the system.
 * This passport accumulates insights, flags, scores, and recommendations 
 * as it moves between tools.
 */

export interface DataPassport {
  // Core identification
  schemaVersion: string;
  projectId: string;
  passportId: string;
  createdAt: string;
  updatedAt: string;
  
  // Origin tracking
  originTool: string;
  originUser: string;
  
  // Content data
  payload: {
    adCopy: {
      headline: string;
      body_text: string;
      cta: string;
      platform: string;
      industry?: string;
      target_audience?: string;
    };
    metadata: {
      version: number;
      contentHash: string;
      wordCount: number;
      characterCount: number;
    };
  };
  
  // Accumulated insights from tools
  insights: ToolInsight[];
  
  // Conflict tracking and resolution
  conflicts: ConflictRecord[];
  
  // Workflow state
  workflow: {
    currentStep: string;
    completedSteps: string[];
    nextSuggestedSteps: string[];
    fastTrackCompleted: boolean;
    deepTrackCompleted: boolean;
  };
  
  // Performance and routing
  meta: {
    priority: 'low' | 'medium' | 'high' | 'critical';
    routingHints: string[];
    processingTime: number;
    retryCount: number;
    lastError?: string;
  };
}

export interface ToolInsight {
  toolId: string;
  toolVersion: string;
  timestamp: string;
  confidence: number; // 0-1
  category: 'analysis' | 'suggestion' | 'warning' | 'error';
  
  data: {
    scores?: Record<string, number>;
    flags?: string[];
    recommendations?: Recommendation[];
    alternatives?: AlternativeContent[];
  };
  
  // For version compatibility
  schemaVersion: string;
  deprecationNotice?: string;
}

export interface Recommendation {
  id: string;
  type: 'headline' | 'body' | 'cta' | 'platform' | 'general';
  priority: 'low' | 'medium' | 'high';
  impact: 'minor' | 'moderate' | 'major';
  confidence: number;
  title: string;
  description: string;
  reasoning: string;
  suggestedChange?: string;
  estimatedImprovement?: {
    metric: string;
    value: number;
    unit: string;
  };
}

export interface AlternativeContent {
  id: string;
  type: 'variation' | 'optimization' | 'compliance_fix';
  confidence: number;
  headline?: string;
  body_text?: string;
  cta?: string;
  reasoning: string;
  expectedImpact: string;
}

export interface ConflictRecord {
  id: string;
  timestamp: string;
  type: 'tool_disagreement' | 'policy_violation' | 'user_preference' | 'business_rule';
  severity: 'low' | 'medium' | 'high' | 'critical';
  
  // Conflicting parties
  toolsInvolved: string[];
  conflictData: {
    issue: string;
    positions: ConflictPosition[];
    impact: string;
    businessContext?: string;
  };
  
  // Resolution
  resolution?: {
    strategy: 'auto' | 'user_decision' | 'escalated' | 'deferred';
    decision: string;
    reasoning: string;
    resolvedAt: string;
    resolvedBy: string;
  };
}

export interface ConflictPosition {
  toolId: string;
  stance: string;
  confidence: number;
  supportingData: any;
  reasoning: string;
}

/**
 * Schema Registry for Version Management
 */
export interface SchemaRegistry {
  currentVersion: string;
  supportedVersions: string[];
  migrations: SchemaMigration[];
  deprecationWarnings: DeprecationWarning[];
}

export interface SchemaMigration {
  fromVersion: string;
  toVersion: string;
  migrationFunction: (oldData: any) => DataPassport;
  isReversible: boolean;
  deprecatedFields: string[];
  newFields: string[];
}

export interface DeprecationWarning {
  version: string;
  field: string;
  message: string;
  replacementField?: string;
  removalDate: string;
}

/**
 * Passport Creation Utilities
 */
export interface PassportConfig {
  projectId: string;
  originTool: string;
  originUser: string;
  adCopy: {
    headline: string;
    body_text: string;
    cta: string;
    platform: string;
    industry?: string;
    target_audience?: string;
  };
  priority?: 'low' | 'medium' | 'high' | 'critical';
  routingHints?: string[];
}

/**
 * Tool Integration Interface
 */
export interface ToolProcessor {
  toolId: string;
  version: string;
  supportedSchemaVersions: string[];
  
  // Main processing function
  process(passport: DataPassport): Promise<DataPassport>;
  
  // Version compatibility
  canProcess(schemaVersion: string): boolean;
  migrateInput?(oldPassport: any): DataPassport;
  
  // Metadata
  getCapabilities(): ToolCapabilities;
  getHealthStatus(): ToolHealthStatus;
}

export interface ToolCapabilities {
  categories: string[];
  inputTypes: string[];
  outputTypes: string[];
  maxProcessingTime: number;
  supportsRealTime: boolean;
  supportsBatch: boolean;
}

export interface ToolHealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  lastCheck: string;
  responseTime: number;
  errorRate: number;
  message?: string;
}

/**
 * Event System for Tool Communication
 */
export interface PassportEvent {
  eventId: string;
  passportId: string;
  timestamp: string;
  type: 'created' | 'processed' | 'conflicted' | 'resolved' | 'completed' | 'error';
  toolId: string;
  data: any;
  metadata: {
    duration?: number;
    memoryUsage?: number;
    cpuUsage?: number;
  };
}

export type PassportEventHandler = (event: PassportEvent) => void;

/**
 * Constants
 */
export const CURRENT_SCHEMA_VERSION = '1.0.0';
export const SUPPORTED_SCHEMA_VERSIONS = ['1.0.0'];

export const TOOL_CATEGORIES = {
  ANALYSIS: 'analysis',
  GENERATION: 'generation',
  OPTIMIZATION: 'optimization',
  COMPLIANCE: 'compliance',
  PERFORMANCE: 'performance',
  INSIGHTS: 'insights'
} as const;

export const PRIORITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium', 
  HIGH: 'high',
  CRITICAL: 'critical'
} as const;