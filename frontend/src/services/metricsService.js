// Dashboard Metrics Service
// Handles fetching real dashboard metrics from the backend API

import api from './apiService';

class MetricsService {
  /**
   * Get dashboard metrics for the current user
   * @param {number} periodDays - Number of days to include in metrics (default: 30)
   * @returns {Promise<Object>} Dashboard metrics
   */
  async getDashboardMetrics(periodDays = 30) {
    const data = await api.get(`/dashboard/metrics?period_days=${periodDays}`);
    return data;
  }

  /**
   * Get detailed dashboard metrics with breakdowns
   * @param {number} periodDays - Number of days to include
   * @returns {Promise<Object>} Detailed metrics
   */
  async getDetailedMetrics(periodDays = 30) {
    const data = await api.get(`/dashboard/metrics/detailed?period_days=${periodDays}`);
    return data;
  }

  /**
   * Get high-level summary metrics
   * @returns {Promise<Object>} Summary metrics
   */
  async getSummaryMetrics() {
    const data = await api.get('/dashboard/metrics/summary');
    return data;
  }

  /**
   * Check if user has any analysis data
   * @returns {Promise<boolean>} Whether user has performed analyses
   */
  async hasAnalysisData() {
    const summary = await this.getSummaryMetrics();
    return summary.totalAnalyses > 0;
  }

  /**
   * Format metrics for display (handle edge cases, rounding, etc.)
   * @param {Object} metrics - Raw metrics from API
   * @returns {Object} Formatted metrics
   */
  formatMetrics(metrics) {
    const formatChange = (value) => {
      if (value === null || value === undefined || !isFinite(value)) {
        return 0;
      }
      return Math.round(value * 10) / 10; // Round to 1 decimal place
    };

    const formatScore = (value) => {
      if (value === null || value === undefined || !isFinite(value)) {
        return 0;
      }
      return Math.round(value);
    };

    return {
      adsAnalyzed: formatScore(metrics.adsAnalyzed || 0),
      adsAnalyzedChange: formatChange(metrics.adsAnalyzedChange || 0),
      avgImprovement: Math.round((metrics.avgImprovement || 0) * 10) / 10,
      avgImprovementChange: formatChange(metrics.avgImprovementChange || 0),
      avgScore: formatScore(metrics.avgScore || 0),
      avgScoreChange: formatChange(metrics.avgScoreChange || 0),
      topPerforming: formatScore(metrics.topPerforming || 0),
      topPerformingChange: formatChange(metrics.topPerformingChange || 0),
      periodStart: metrics.periodStart,
      periodEnd: metrics.periodEnd,
      periodDays: metrics.periodDays || 30
    };
  }
}

// Export singleton instance
const metricsService = new MetricsService();
export default metricsService;