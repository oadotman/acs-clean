/**
 * Intelligent Orchestration Engine
 * 
 * Analyzes ad copy and intelligently suggests which tools are most relevant.
 * Implements dual processing tracks (Fast Lane + Deep Lane) with smart workflow chaining.
 */

import { 
  DataPassport, 
  ToolInsight,
  ToolProcessor,
  CURRENT_SCHEMA_VERSION 
} from '../types/dataPassport';
import { passportManager } from './passportManager';
import { v4 as uuidv4 } from 'uuid';

export interface ContextAnalyzer {
  id: string;
  analyze(passport: DataPassport): Promise<ContextInsight>;
  priority: number;
  category: 'content' | 'compliance' | 'performance' | 'audience';
}

export interface ContextInsight {
  confidence: number;
  category: string;
  findings: Finding[];
  suggestedTools: ToolSuggestion[];
  urgencyLevel: 'low' | 'medium' | 'high' | 'critical';
  processingTrack: 'fast' | 'deep' | 'both';
}

export interface Finding {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  confidence: number;
  location?: string; // headline, body, cta
  suggestedAction?: string;
}

export interface ToolSuggestion {
  toolId: string;
  confidence: number;
  reasoning: string;
  priority: number;
  prerequisites?: string[];
  estimatedProcessingTime: number;
  track: 'fast' | 'deep';
}

export interface ProcessingResult {
  passportId: string;
  fastTrackResults?: ToolResult[];
  deepTrackResults?: ToolResult[];
  overallScore: number;
  keyFindings: Finding[];
  recommendedActions: RecommendedAction[];
  nextSteps: string[];
}

export interface ToolResult {
  toolId: string;
  executionTime: number;
  success: boolean;
  insights?: ToolInsight;
  error?: string;
}

export interface RecommendedAction {
  id: string;
  type: 'optimization' | 'compliance' | 'testing' | 'analysis';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  estimatedImpact: {
    metric: string;
    expectedChange: number;
    confidence: number;
  };
  requiredTools?: string[];
  timeEstimate: number;
}

/**
 * Context Analyzers Implementation
 */

class ContentContextAnalyzer implements ContextAnalyzer {
  id = 'content_analyzer';
  priority = 1;
  category = 'content' as const;

  async analyze(passport: DataPassport): Promise<ContextInsight> {
    const { adCopy } = passport.payload;
    const findings: Finding[] = [];
    const suggestedTools: ToolSuggestion[] = [];

    // Analyze content characteristics
    const headlineLength = adCopy.headline.length;
    const bodyLength = adCopy.body_text.length;
    const ctaLength = adCopy.cta.length;

    // Check for urgency language
    const urgencyWords = ['now', 'today', 'limited', 'hurry', 'fast', 'urgent', 'deadline'];
    const hasUrgency = urgencyWords.some(word => 
      adCopy.headline.toLowerCase().includes(word) || 
      adCopy.body_text.toLowerCase().includes(word)
    );

    if (hasUrgency) {
      findings.push({
        type: 'urgency_detected',
        severity: 'info',
        message: 'Urgency language detected - may need compliance review',
        confidence: 0.8,
        suggestedAction: 'Run compliance check'
      });

      suggestedTools.push({
        toolId: 'compliance_checker',
        confidence: 0.9,
        reasoning: 'Urgency language requires compliance verification',
        priority: 1,
        estimatedProcessingTime: 15,
        track: 'fast'
      });
    }

    // Check for emotional language
    const emotionalWords = ['amazing', 'incredible', 'transform', 'revolutionary', 'breakthrough'];
    const emotionalCount = emotionalWords.filter(word =>
      adCopy.headline.toLowerCase().includes(word) || 
      adCopy.body_text.toLowerCase().includes(word)
    ).length;

    if (emotionalCount > 0) {
      findings.push({
        type: 'emotional_language',
        severity: 'info',
        message: `${emotionalCount} emotional trigger word(s) found`,
        confidence: 0.7
      });

      suggestedTools.push({
        toolId: 'psychology_scorer',
        confidence: 0.8,
        reasoning: 'Emotional language suggests psychology analysis would be valuable',
        priority: 2,
        estimatedProcessingTime: 20,
        track: 'deep'
      });
    }

    // Platform-specific analysis
    if (adCopy.platform === 'google' && headlineLength > 30) {
      findings.push({
        type: 'headline_length',
        severity: 'warning',
        message: 'Headline may be too long for Google Ads',
        confidence: 0.9,
        location: 'headline',
        suggestedAction: 'Optimize for platform requirements'
      });

      suggestedTools.push({
        toolId: 'performance_forensics',
        confidence: 0.9,
        reasoning: 'Platform optimization needed',
        priority: 1,
        estimatedProcessingTime: 25,
        track: 'fast'
      });
    }

    return {
      confidence: 0.8,
      category: 'content',
      findings,
      suggestedTools,
      urgencyLevel: hasUrgency ? 'high' : 'medium',
      processingTrack: hasUrgency ? 'both' : 'deep'
    };
  }
}

class ComplianceContextAnalyzer implements ContextAnalyzer {
  id = 'compliance_analyzer';
  priority = 2;
  category = 'compliance' as const;

  async analyze(passport: DataPassport): Promise<ContextInsight> {
    const { adCopy } = passport.payload;
    const findings: Finding[] = [];
    const suggestedTools: ToolSuggestion[] = [];

    // Check for potential compliance risks
    const riskWords = [
      'guaranteed', 'promise', 'miracle', 'instant', 'secret', 
      'exclusive', 'only', 'special', 'limited time', 'act now'
    ];

    const detectedRisks = riskWords.filter(word =>
      adCopy.headline.toLowerCase().includes(word.toLowerCase()) ||
      adCopy.body_text.toLowerCase().includes(word.toLowerCase())
    );

    if (detectedRisks.length > 0) {
      findings.push({
        type: 'compliance_risk',
        severity: 'warning',
        message: `Potential compliance issues: ${detectedRisks.join(', ')}`,
        confidence: 0.7,
        suggestedAction: 'Review with compliance checker and legal scanner'
      });

      suggestedTools.push({
        toolId: 'compliance_checker',
        confidence: 0.9,
        reasoning: 'High-risk language detected',
        priority: 1,
        estimatedProcessingTime: 15,
        track: 'fast'
      });

      suggestedTools.push({
        toolId: 'legal_risk_scanner',
        confidence: 0.8,
        reasoning: 'Legal review recommended for risk words',
        priority: 2,
        estimatedProcessingTime: 30,
        track: 'deep'
      });
    }

    // Check for medical/health claims
    const healthWords = ['cure', 'treatment', 'medical', 'health', 'doctor', 'clinical'];
    const hasHealthClaims = healthWords.some(word =>
      adCopy.headline.toLowerCase().includes(word) ||
      adCopy.body_text.toLowerCase().includes(word)
    );

    if (hasHealthClaims) {
      findings.push({
        type: 'health_claims',
        severity: 'error',
        message: 'Potential health claims detected - high compliance risk',
        confidence: 0.9,
        suggestedAction: 'Mandatory legal and compliance review'
      });

      suggestedTools.push({
        toolId: 'legal_risk_scanner',
        confidence: 1.0,
        reasoning: 'Health claims require mandatory legal review',
        priority: 1,
        estimatedProcessingTime: 45,
        track: 'both'
      });
    }

    const urgencyLevel = hasHealthClaims ? 'critical' : 
                         detectedRisks.length > 2 ? 'high' : 
                         detectedRisks.length > 0 ? 'medium' : 'low';

    return {
      confidence: 0.9,
      category: 'compliance',
      findings,
      suggestedTools,
      urgencyLevel,
      processingTrack: hasHealthClaims ? 'both' : 'fast'
    };
  }
}

class PerformanceContextAnalyzer implements ContextAnalyzer {
  id = 'performance_analyzer';
  priority = 3;
  category = 'performance' as const;

  async analyze(passport: DataPassport): Promise<ContextInsight> {
    const { adCopy } = passport.payload;
    const findings: Finding[] = [];
    const suggestedTools: ToolSuggestion[] = [];

    // Analyze CTA strength
    const strongCTAs = ['get started', 'download now', 'try free', 'learn more', 'buy now'];
    const hasStrongCTA = strongCTAs.some(cta => 
      adCopy.cta.toLowerCase().includes(cta)
    );

    if (!hasStrongCTA) {
      findings.push({
        type: 'weak_cta',
        severity: 'warning',
        message: 'CTA could be more action-oriented',
        confidence: 0.6,
        location: 'cta',
        suggestedAction: 'Consider A/B testing stronger CTAs'
      });

      suggestedTools.push({
        toolId: 'ab_test_generator',
        confidence: 0.8,
        reasoning: 'Weak CTA suggests A/B testing opportunities',
        priority: 2,
        estimatedProcessingTime: 20,
        track: 'deep'
      });
    }

    // Check for numbers/statistics
    const hasNumbers = /\d+/.test(adCopy.headline + ' ' + adCopy.body_text);
    if (!hasNumbers) {
      findings.push({
        type: 'lacks_numbers',
        severity: 'info',
        message: 'Consider adding statistics or numbers for credibility',
        confidence: 0.5,
        suggestedAction: 'Add quantifiable benefits'
      });

      suggestedTools.push({
        toolId: 'roi_copy_generator',
        confidence: 0.7,
        reasoning: 'ROI-focused variations might improve performance',
        priority: 3,
        estimatedProcessingTime: 25,
        track: 'deep'
      });
    }

    // Industry-specific optimization
    if (adCopy.industry) {
      suggestedTools.push({
        toolId: 'industry_optimizer',
        confidence: 0.8,
        reasoning: `${adCopy.industry} industry optimization available`,
        priority: 2,
        estimatedProcessingTime: 30,
        track: 'deep'
      });
    }

    return {
      confidence: 0.7,
      category: 'performance',
      findings,
      suggestedTools,
      urgencyLevel: 'medium',
      processingTrack: 'deep'
    };
  }
}

/**
 * Main Orchestration Engine
 */
export class OrchestrationEngine {
  private contextAnalyzers: ContextAnalyzer[] = [];
  private toolRegistry: Map<string, ToolProcessor> = new Map();
  private processingQueue: Map<string, Promise<ProcessingResult>> = new Map();

  constructor() {
    this.initializeAnalyzers();
    this.initializeToolRegistry();
  }

  private initializeAnalyzers(): void {
    this.contextAnalyzers = [
      new ContentContextAnalyzer(),
      new ComplianceContextAnalyzer(),
      new PerformanceContextAnalyzer()
    ].sort((a, b) => a.priority - b.priority);
  }

  private initializeToolRegistry(): void {
    // In a real implementation, these would be actual tool processors
    // For now, we'll create mock processors
    const tools = [
      'compliance_checker',
      'legal_risk_scanner', 
      'brand_voice_engine',
      'psychology_scorer',
      'roi_copy_generator',
      'ab_test_generator',
      'industry_optimizer',
      'performance_forensics'
    ];

    tools.forEach(toolId => {
      this.toolRegistry.set(toolId, new MockToolProcessor(toolId));
    });
  }

  /**
   * Analyze passport and return context insights
   */
  async analyzeContext(passport: DataPassport): Promise<ContextInsight[]> {
    const insights: ContextInsight[] = [];

    for (const analyzer of this.contextAnalyzers) {
      try {
        const insight = await analyzer.analyze(passport);
        insights.push(insight);
      } catch (error) {
        console.error(`Error in ${analyzer.id}:`, error);
      }
    }

    return insights;
  }

  /**
   * Get suggested tools based on context analysis
   */
  async getSuggestedTools(passport: DataPassport): Promise<ToolSuggestion[]> {
    const contextInsights = await this.analyzeContext(passport);
    
    // Collect all tool suggestions
    const allSuggestions = contextInsights.flatMap(insight => insight.suggestedTools);
    
    // Deduplicate and prioritize
    const toolMap = new Map<string, ToolSuggestion>();
    
    allSuggestions.forEach(suggestion => {
      const existing = toolMap.get(suggestion.toolId);
      if (!existing || suggestion.confidence > existing.confidence) {
        toolMap.set(suggestion.toolId, suggestion);
      }
    });

    return Array.from(toolMap.values())
      .sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Process passport through dual tracks
   */
  async processPassport(
    passportId: string, 
    options: {
      enableFastTrack?: boolean;
      enableDeepTrack?: boolean;
      maxConcurrency?: number;
      timeout?: number;
    } = {}
  ): Promise<ProcessingResult> {
    const {
      enableFastTrack = true,
      enableDeepTrack = true,
      maxConcurrency = 3,
      timeout = 60000
    } = options;

    // Check if already processing
    if (this.processingQueue.has(passportId)) {
      return this.processingQueue.get(passportId)!;
    }

    const processingPromise = this._processPassportInternal(
      passportId, 
      { enableFastTrack, enableDeepTrack, maxConcurrency, timeout }
    );

    this.processingQueue.set(passportId, processingPromise);

    try {
      const result = await processingPromise;
      return result;
    } finally {
      this.processingQueue.delete(passportId);
    }
  }

  private async _processPassportInternal(
    passportId: string,
    options: {
      enableFastTrack: boolean;
      enableDeepTrack: boolean;
      maxConcurrency: number;
      timeout: number;
    }
  ): Promise<ProcessingResult> {
    const passport = passportManager.getPassport(passportId);
    if (!passport) {
      throw new Error(`Passport ${passportId} not found`);
    }

    const suggestedTools = await this.getSuggestedTools(passport);
    const fastTrackTools = suggestedTools.filter(t => t.track === 'fast' || t.track === undefined);
    const deepTrackTools = suggestedTools.filter(t => t.track === 'deep');

    const result: ProcessingResult = {
      passportId,
      overallScore: 0,
      keyFindings: [],
      recommendedActions: [],
      nextSteps: []
    };

    // Fast Track Processing
    if (options.enableFastTrack && fastTrackTools.length > 0) {
      result.fastTrackResults = await this.runToolsBatch(
        passport, 
        fastTrackTools.slice(0, 3), // Limit to top 3 for fast track
        options.maxConcurrency,
        options.timeout / 2 // Half timeout for fast track
      );
    }

    // Deep Track Processing 
    if (options.enableDeepTrack && deepTrackTools.length > 0) {
      result.deepTrackResults = await this.runToolsBatch(
        passport,
        deepTrackTools,
        options.maxConcurrency,
        options.timeout
      );
    }

    // Generate overall assessment
    result.overallScore = this.calculateOverallScore(result);
    result.keyFindings = this.extractKeyFindings(passport);
    result.recommendedActions = this.generateRecommendedActions(passport, result);
    result.nextSteps = this.determineNextSteps(passport, result);

    return result;
  }

  private async runToolsBatch(
    passport: DataPassport,
    tools: ToolSuggestion[],
    maxConcurrency: number,
    timeout: number
  ): Promise<ToolResult[]> {
    const results: ToolResult[] = [];
    const semaphore = new Array(maxConcurrency).fill(null);
    
    const processPool = tools.map(async (toolSuggestion) => {
      const startTime = Date.now();
      
      try {
        const tool = this.toolRegistry.get(toolSuggestion.toolId);
        if (!tool) {
          return {
            toolId: toolSuggestion.toolId,
            executionTime: 0,
            success: false,
            error: 'Tool not found'
          };
        }

        // Process with timeout
        const processedPassport = await Promise.race([
          tool.process(passport),
          new Promise<never>((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), timeout)
          )
        ]);

        const executionTime = Date.now() - startTime;

        // Add insights to passport manager
        if (processedPassport.insights.length > passport.insights.length) {
          const newInsights = processedPassport.insights.slice(passport.insights.length);
          for (const insight of newInsights) {
            passportManager.addInsight(passport.passportId, insight);
          }
        }

        return {
          toolId: toolSuggestion.toolId,
          executionTime,
          success: true,
          insights: processedPassport.insights[processedPassport.insights.length - 1]
        };

      } catch (error) {
        return {
          toolId: toolSuggestion.toolId,
          executionTime: Date.now() - startTime,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    });

    const batchResults = await Promise.all(processPool);
    results.push(...batchResults);

    return results;
  }

  private calculateOverallScore(result: ProcessingResult): number {
    // Combine scores from all successful tool results
    const allResults = [
      ...(result.fastTrackResults || []),
      ...(result.deepTrackResults || [])
    ];

    const successfulResults = allResults.filter(r => r.success && r.insights);
    if (successfulResults.length === 0) return 0;

    const scores = successfulResults
      .map(r => r.insights?.data.scores || {})
      .map(scores => Object.values(scores))
      .flat()
      .filter(score => typeof score === 'number');

    if (scores.length === 0) return 0;

    return scores.reduce((sum, score) => sum + score, 0) / scores.length;
  }

  private extractKeyFindings(passport: DataPassport): Finding[] {
    // Extract top findings from all insights
    return passport.insights
      .flatMap(insight => [
        ...(insight.data.recommendations?.map(rec => ({
          type: rec.type,
          severity: rec.priority === 'high' ? 'warning' : 'info',
          message: rec.title,
          confidence: insight.confidence,
          suggestedAction: rec.suggestedChange
        })) || []),
        ...(insight.data.flags?.map(flag => ({
          type: 'flag',
          severity: 'warning',
          message: flag,
          confidence: insight.confidence
        })) || [])
      ] as Finding[])
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 5); // Top 5 findings
  }

  private generateRecommendedActions(
    passport: DataPassport, 
    result: ProcessingResult
  ): RecommendedAction[] {
    const actions: RecommendedAction[] = [];

    // Generate actions based on insights
    passport.insights.forEach(insight => {
      insight.data.recommendations?.forEach(rec => {
        actions.push({
          id: uuidv4(),
          type: this.mapRecommendationType(rec.type),
          priority: rec.priority,
          title: rec.title,
          description: rec.description,
          estimatedImpact: rec.estimatedImprovement ? {
            metric: rec.estimatedImprovement.metric,
            expectedChange: rec.estimatedImprovement.value,
            confidence: rec.confidence || 0.7
          } : {
            metric: 'performance',
            expectedChange: 10,
            confidence: 0.5
          },
          timeEstimate: 15
        });
      });
    });

    return actions
      .sort((a, b) => {
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      })
      .slice(0, 8); // Top 8 actions
  }

  private mapRecommendationType(recType: string): 'optimization' | 'compliance' | 'testing' | 'analysis' {
    if (recType.includes('compliance') || recType.includes('policy')) return 'compliance';
    if (recType.includes('test') || recType.includes('variation')) return 'testing';
    if (recType.includes('analysis') || recType.includes('insight')) return 'analysis';
    return 'optimization';
  }

  private determineNextSteps(
    passport: DataPassport, 
    result: ProcessingResult
  ): string[] {
    const steps: string[] = [];
    
    // Check for unresolved conflicts
    const unresolvedConflicts = passport.conflicts.filter(c => !c.resolution);
    if (unresolvedConflicts.length > 0) {
      steps.push('Resolve conflicts between tool recommendations');
    }

    // Check workflow completeness
    if (!passport.workflow.fastTrackCompleted && result.fastTrackResults) {
      steps.push('Complete fast track analysis');
    }

    if (!passport.workflow.deepTrackCompleted && result.deepTrackResults) {
      steps.push('Complete deep analysis');
    }

    // Suggest additional tools
    const processedTools = passport.insights.map(i => i.toolId);
    const availableTools = Array.from(this.toolRegistry.keys());
    const remainingTools = availableTools.filter(t => !processedTools.includes(t));

    if (remainingTools.length > 0) {
      steps.push(`Consider running: ${remainingTools.slice(0, 3).join(', ')}`);
    }

    return steps;
  }
}

/**
 * Mock Tool Processor for testing
 */
class MockToolProcessor implements ToolProcessor {
  toolId: string;
  version = '1.0.0';
  supportedSchemaVersions = [CURRENT_SCHEMA_VERSION];

  constructor(toolId: string) {
    this.toolId = toolId;
  }

  async process(passport: DataPassport): Promise<DataPassport> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 500));

    // Generate mock insight
    const insight: ToolInsight = {
      toolId: this.toolId,
      toolVersion: this.version,
      timestamp: new Date().toISOString(),
      confidence: 0.7 + Math.random() * 0.3,
      category: 'analysis',
      schemaVersion: CURRENT_SCHEMA_VERSION,
      data: {
        scores: {
          [`${this.toolId}_score`]: Math.round((0.5 + Math.random() * 0.5) * 100)
        },
        recommendations: [{
          id: uuidv4(),
          type: 'general',
          priority: 'medium',
          impact: 'moderate',
          confidence: 0.8,
          title: `${this.toolId} recommendation`,
          description: `Optimization suggestion from ${this.toolId}`,
          reasoning: `Based on ${this.toolId} analysis`
        }]
      }
    };

    // Add insight to passport copy
    const updatedPassport = {
      ...passport,
      insights: [...passport.insights, insight],
      updatedAt: new Date().toISOString()
    };

    return updatedPassport;
  }

  canProcess(schemaVersion: string): boolean {
    return this.supportedSchemaVersions.includes(schemaVersion);
  }

  getCapabilities() {
    return {
      categories: ['analysis'],
      inputTypes: ['ad_copy'],
      outputTypes: ['insights'],
      maxProcessingTime: 30000,
      supportsRealTime: true,
      supportsBatch: false
    };
  }

  getHealthStatus() {
    return {
      status: 'healthy' as const,
      lastCheck: new Date().toISOString(),
      responseTime: 200 + Math.random() * 300,
      errorRate: Math.random() * 0.05
    };
  }
}

// Singleton instance
export const orchestrationEngine = new OrchestrationEngine();