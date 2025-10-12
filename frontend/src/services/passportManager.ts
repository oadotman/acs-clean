/**
 * Passport Manager Service
 * 
 * Handles the lifecycle of Universal Data Passports including:
 * - Creation and initialization
 * - Version management and migrations
 * - Tool communication and routing
 * - Conflict detection and resolution
 * - Event publishing and subscription
 */

import { 
  DataPassport,
  PassportConfig,
  ToolInsight,
  ConflictRecord,
  PassportEvent,
  PassportEventHandler,
  SchemaRegistry,
  SchemaMigration,
  CURRENT_SCHEMA_VERSION,
  SUPPORTED_SCHEMA_VERSIONS,
  TOOL_CATEGORIES
} from '../types/dataPassport';
import { v4 as uuidv4 } from 'uuid';
import CryptoJS from 'crypto-js';

/**
 * Schema Registry Implementation
 */
class SchemaRegistryImpl implements SchemaRegistry {
  currentVersion = CURRENT_SCHEMA_VERSION;
  supportedVersions = SUPPORTED_SCHEMA_VERSIONS;
  migrations: SchemaMigration[] = [];
  deprecationWarnings = [];

  constructor() {
    this.initializeMigrations();
  }

  private initializeMigrations() {
    // Future migrations will be added here
    // Example:
    // this.migrations.push({
    //   fromVersion: '0.9.0',
    //   toVersion: '1.0.0',
    //   migrationFunction: this.migrateV09ToV10,
    //   isReversible: false,
    //   deprecatedFields: ['oldField'],
    //   newFields: ['newField']
    // });
  }

  canMigrate(fromVersion: string, toVersion: string): boolean {
    return this.migrations.some(m => 
      m.fromVersion === fromVersion && m.toVersion === toVersion
    );
  }

  migrate(data: any, fromVersion: string, toVersion: string): DataPassport {
    const migration = this.migrations.find(m => 
      m.fromVersion === fromVersion && m.toVersion === toVersion
    );
    
    if (!migration) {
      throw new Error(`No migration path from ${fromVersion} to ${toVersion}`);
    }

    return migration.migrationFunction(data);
  }
}

/**
 * Event Bus for Passport Communication
 */
class PassportEventBus {
  private handlers: Map<string, PassportEventHandler[]> = new Map();

  subscribe(eventType: string, handler: PassportEventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    
    this.handlers.get(eventType)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(eventType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  publish(event: PassportEvent): void {
    const handlers = this.handlers.get(event.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error('Error in passport event handler:', error);
        }
      });
    }

    // Also publish to 'all' handlers
    const allHandlers = this.handlers.get('all');
    if (allHandlers) {
      allHandlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error('Error in passport event handler:', error);
        }
      });
    }
  }
}

/**
 * Conflict Detection Engine
 */
class ConflictDetector {
  detectConflicts(passport: DataPassport): ConflictRecord[] {
    const conflicts: ConflictRecord[] = [];
    const insights = passport.insights;

    // Tool disagreement detection
    const toolDisagreements = this.detectToolDisagreements(insights);
    conflicts.push(...toolDisagreements);

    // Policy violation detection
    const policyViolations = this.detectPolicyViolations(insights);
    conflicts.push(...policyViolations);

    // Business rule conflicts
    const businessRuleConflicts = this.detectBusinessRuleConflicts(insights);
    conflicts.push(...businessRuleConflicts);

    return conflicts;
  }

  private detectToolDisagreements(insights: ToolInsight[]): ConflictRecord[] {
    const conflicts: ConflictRecord[] = [];
    
    // Group insights by category
    const insightsByCategory = insights.reduce((acc, insight) => {
      if (!acc[insight.category]) {
        acc[insight.category] = [];
      }
      acc[insight.category].push(insight);
      return acc;
    }, {} as Record<string, ToolInsight[]>);

    // Look for disagreements within each category
    Object.entries(insightsByCategory).forEach(([category, categoryInsights]) => {
      if (categoryInsights.length < 2) return;

      // Check for conflicting recommendations
      const recommendations = categoryInsights
        .flatMap(insight => insight.data.recommendations || []);
      
      const conflictingRecs = this.findConflictingRecommendations(recommendations);
      
      if (conflictingRecs.length > 0) {
        conflicts.push({
          id: uuidv4(),
          timestamp: new Date().toISOString(),
          type: 'tool_disagreement',
          severity: 'medium',
          toolsInvolved: categoryInsights.map(i => i.toolId),
          conflictData: {
            issue: `Conflicting recommendations in ${category}`,
            positions: categoryInsights.map(insight => ({
              toolId: insight.toolId,
              stance: this.summarizeInsightStance(insight),
              confidence: insight.confidence,
              supportingData: insight.data,
              reasoning: insight.data.recommendations?.[0]?.reasoning || 'No reasoning provided'
            })),
            impact: 'May lead to suboptimal ad performance',
            businessContext: `Tools disagree on ${category} approach`
          }
        });
      }
    });

    return conflicts;
  }

  private detectPolicyViolations(insights: ToolInsight[]): ConflictRecord[] {
    const conflicts: ConflictRecord[] = [];
    
    insights.forEach(insight => {
      const flags = insight.data.flags || [];
      const policyFlags = flags.filter(flag => 
        flag.includes('policy') || 
        flag.includes('violation') || 
        flag.includes('compliance')
      );

      if (policyFlags.length > 0) {
        conflicts.push({
          id: uuidv4(),
          timestamp: new Date().toISOString(),
          type: 'policy_violation',
          severity: 'high',
          toolsInvolved: [insight.toolId],
          conflictData: {
            issue: 'Policy compliance violations detected',
            positions: [{
              toolId: insight.toolId,
              stance: 'Policy violation detected',
              confidence: insight.confidence,
              supportingData: { flags: policyFlags },
              reasoning: `${insight.toolId} detected potential policy violations: ${policyFlags.join(', ')}`
            }],
            impact: 'Ad may be rejected or account suspended',
            businessContext: 'Platform compliance requirements'
          }
        });
      }
    });

    return conflicts;
  }

  private detectBusinessRuleConflicts(insights: ToolInsight[]): ConflictRecord[] {
    // Placeholder for business rule conflict detection
    // Would integrate with user's business rules and organizational policies
    return [];
  }

  private findConflictingRecommendations(recommendations: any[]): any[] {
    // Simplified conflict detection
    // In a real implementation, this would use more sophisticated logic
    const conflicting = [];
    
    for (let i = 0; i < recommendations.length; i++) {
      for (let j = i + 1; j < recommendations.length; j++) {
        const rec1 = recommendations[i];
        const rec2 = recommendations[j];
        
        if (rec1.type === rec2.type && 
            rec1.suggestedChange && 
            rec2.suggestedChange &&
            rec1.suggestedChange !== rec2.suggestedChange) {
          conflicting.push([rec1, rec2]);
        }
      }
    }
    
    return conflicting;
  }

  private summarizeInsightStance(insight: ToolInsight): string {
    const recs = insight.data.recommendations || [];
    if (recs.length === 0) return 'No specific stance';
    
    return recs[0].title || 'Recommendation available';
  }
}

/**
 * Main Passport Manager Class
 */
export class PassportManager {
  private schemaRegistry: SchemaRegistryImpl;
  private eventBus: PassportEventBus;
  private conflictDetector: ConflictDetector;
  private passports: Map<string, DataPassport> = new Map();

  constructor() {
    this.schemaRegistry = new SchemaRegistryImpl();
    this.eventBus = new PassportEventBus();
    this.conflictDetector = new ConflictDetector();
  }

  /**
   * Create a new data passport
   */
  createPassport(config: PassportConfig): DataPassport {
    const passportId = uuidv4();
    const now = new Date().toISOString();
    
    // Generate content hash for deduplication
    const contentString = `${config.adCopy.headline}|${config.adCopy.body_text}|${config.adCopy.cta}`;
    const contentHash = CryptoJS.SHA256(contentString).toString();

    const passport: DataPassport = {
      schemaVersion: CURRENT_SCHEMA_VERSION,
      projectId: config.projectId,
      passportId,
      createdAt: now,
      updatedAt: now,
      originTool: config.originTool,
      originUser: config.originUser,
      
      payload: {
        adCopy: { ...config.adCopy },
        metadata: {
          version: 1,
          contentHash,
          wordCount: this.countWords(contentString),
          characterCount: contentString.length
        }
      },

      insights: [],
      conflicts: [],

      workflow: {
        currentStep: 'created',
        completedSteps: [],
        nextSuggestedSteps: ['analysis'],
        fastTrackCompleted: false,
        deepTrackCompleted: false
      },

      meta: {
        priority: config.priority || 'medium',
        routingHints: config.routingHints || [],
        processingTime: 0,
        retryCount: 0
      }
    };

    // Store passport
    this.passports.set(passportId, passport);

    // Publish creation event
    this.publishEvent({
      eventId: uuidv4(),
      passportId,
      timestamp: now,
      type: 'created',
      toolId: config.originTool,
      data: { config },
      metadata: {}
    });

    return passport;
  }

  /**
   * Get passport by ID
   */
  getPassport(passportId: string): DataPassport | undefined {
    return this.passports.get(passportId);
  }

  /**
   * Add insight to passport
   */
  addInsight(passportId: string, insight: ToolInsight): DataPassport {
    const passport = this.passports.get(passportId);
    if (!passport) {
      throw new Error(`Passport ${passportId} not found`);
    }

    // Validate schema compatibility
    if (!this.isSchemaCompatible(insight.schemaVersion)) {
      throw new Error(`Insight schema version ${insight.schemaVersion} is not compatible`);
    }

    // Add insight
    passport.insights.push(insight);
    passport.updatedAt = new Date().toISOString();

    // Detect new conflicts
    const newConflicts = this.conflictDetector.detectConflicts(passport);
    if (newConflicts.length > 0) {
      passport.conflicts.push(...newConflicts);
      
      // Publish conflict events
      newConflicts.forEach(conflict => {
        this.publishEvent({
          eventId: uuidv4(),
          passportId,
          timestamp: new Date().toISOString(),
          type: 'conflicted',
          toolId: insight.toolId,
          data: { conflict },
          metadata: {}
        });
      });
    }

    // Update workflow
    this.updateWorkflow(passport, insight.toolId);

    // Publish processed event
    this.publishEvent({
      eventId: uuidv4(),
      passportId,
      timestamp: new Date().toISOString(),
      type: 'processed',
      toolId: insight.toolId,
      data: { insight },
      metadata: {}
    });

    return passport;
  }

  /**
   * Resolve conflict
   */
  resolveConflict(
    passportId: string, 
    conflictId: string, 
    resolution: {
      strategy: 'auto' | 'user_decision' | 'escalated' | 'deferred';
      decision: string;
      reasoning: string;
      resolvedBy: string;
    }
  ): DataPassport {
    const passport = this.passports.get(passportId);
    if (!passport) {
      throw new Error(`Passport ${passportId} not found`);
    }

    const conflict = passport.conflicts.find(c => c.id === conflictId);
    if (!conflict) {
      throw new Error(`Conflict ${conflictId} not found`);
    }

    // Add resolution
    conflict.resolution = {
      ...resolution,
      resolvedAt: new Date().toISOString()
    };

    passport.updatedAt = new Date().toISOString();

    // Publish resolution event
    this.publishEvent({
      eventId: uuidv4(),
      passportId,
      timestamp: new Date().toISOString(),
      type: 'resolved',
      toolId: 'conflict_resolver',
      data: { conflictId, resolution },
      metadata: {}
    });

    return passport;
  }

  /**
   * Subscribe to passport events
   */
  subscribe(eventType: string, handler: PassportEventHandler): () => void {
    return this.eventBus.subscribe(eventType, handler);
  }

  /**
   * Get passports by project
   */
  getPassportsByProject(projectId: string): DataPassport[] {
    return Array.from(this.passports.values())
      .filter(p => p.projectId === projectId);
  }

  /**
   * Get passport metrics
   */
  getPassportMetrics(passportId: string): {
    insightCount: number;
    conflictCount: number;
    unresolvedConflicts: number;
    averageConfidence: number;
    processingTime: number;
  } {
    const passport = this.passports.get(passportId);
    if (!passport) {
      throw new Error(`Passport ${passportId} not found`);
    }

    const unresolvedConflicts = passport.conflicts.filter(c => !c.resolution).length;
    const averageConfidence = passport.insights.length > 0
      ? passport.insights.reduce((sum, i) => sum + i.confidence, 0) / passport.insights.length
      : 0;

    return {
      insightCount: passport.insights.length,
      conflictCount: passport.conflicts.length,
      unresolvedConflicts,
      averageConfidence,
      processingTime: passport.meta.processingTime
    };
  }

  // Private helper methods
  private countWords(text: string): number {
    return text.trim().split(/\s+/).length;
  }

  private isSchemaCompatible(version: string): boolean {
    return this.schemaRegistry.supportedVersions.includes(version);
  }

  private updateWorkflow(passport: DataPassport, toolId: string): void {
    if (!passport.workflow.completedSteps.includes(toolId)) {
      passport.workflow.completedSteps.push(toolId);
    }

    // Simple workflow logic - could be much more sophisticated
    const analysisTools = ['compliance', 'legal_scanner', 'performance_forensics'];
    const completedAnalysisTools = passport.workflow.completedSteps
      .filter(step => analysisTools.includes(step));

    if (completedAnalysisTools.length >= 2) {
      passport.workflow.fastTrackCompleted = true;
    }

    if (completedAnalysisTools.length === analysisTools.length) {
      passport.workflow.deepTrackCompleted = true;
    }

    // Update current step
    if (passport.workflow.fastTrackCompleted && !passport.workflow.deepTrackCompleted) {
      passport.workflow.currentStep = 'deep_analysis';
    } else if (passport.workflow.deepTrackCompleted) {
      passport.workflow.currentStep = 'completed';
    }
  }

  private publishEvent(event: PassportEvent): void {
    this.eventBus.publish(event);
  }
}

// Singleton instance
export const passportManager = new PassportManager();

// Export types for external use
export type {
  DataPassport,
  ToolInsight,
  ConflictRecord,
  PassportEvent,
  PassportConfig
} from '../types/dataPassport';