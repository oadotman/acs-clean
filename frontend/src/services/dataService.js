import { supabase } from '../lib/supabaseClientClean';
import toast from 'react-hot-toast';

class DataService {
  // Simple retry helper for failed requests
  async _withRetry(operation, maxRetries = 2) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        console.warn(`Attempt ${attempt} failed:`, error.message);
        if (attempt === maxRetries) {
          throw error;
        }
        // Wait a bit before retrying
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }

  // User Profile Operations
  async getUserProfile(userId) {
    try {
      console.log('💬 Fetching user profile for:', userId);
      const { data, error } = await this._withRetry(async () => {
        return await supabase
          .from('user_profiles')
          .select('*')
          .eq('id', userId)
          .single();
      });

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching user profile:', error);
        throw new Error('Failed to fetch user profile');
      }

      return data;
    } catch (error) {
      console.error('Error in getUserProfile:', error);
      throw error;
    }
  }

  async updateUserProfile(userId, updates) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', userId)
        .select()
        .single();

      if (error) {
        console.error('Error updating user profile:', error);
        throw new Error('Failed to update profile');
      }

      return data;
    } catch (error) {
      console.error('Error in updateUserProfile:', error);
      throw error;
    }
  }

  // Ad Analysis Operations
  async getAnalysesHistory(userId, limit = 10, offset = 0) {
    try {
      console.log('📊 Fetching analyses history for user:', userId, 'limit:', limit);
      const { data, error } = await this._withRetry(async () => {
        return await supabase
          .from('ad_analyses')
          .select(`
            id,
            headline,
            body_text,
            cta,
            platform,
            target_audience,
            industry,
            overall_score,
            clarity_score,
            persuasion_score,
            emotion_score,
            cta_strength_score,
            platform_fit_score,
            created_at,
            updated_at,
            project_id,
            projects (
              id,
              name,
              client_name
            )
          `)
          .eq('user_id', userId)
          .order('created_at', { ascending: false })
          .range(offset, offset + limit - 1);
      });

      if (error) {
        console.error('Error fetching analyses history:', error);
        throw new Error('Failed to fetch analyses history');
      }

      return data || [];
    } catch (error) {
      console.error('Error in getAnalysesHistory:', error);
      throw error;
    }
  }

  async getAnalysisDetail(analysisId, userId) {
    try {
      const { data, error } = await supabase
        .from('ad_analyses')
        .select(`
          *,
          competitor_benchmarks(*),
          ad_generations(*)
        `)
        .eq('id', analysisId)
        .eq('user_id', userId)
        .single();

      if (error) {
        console.error('Error fetching analysis detail:', error);
        throw new Error('Failed to fetch analysis details');
      }

      return data;
    } catch (error) {
      console.error('Error in getAnalysisDetail:', error);
      throw error;
    }
  }

  async createAnalysis(userId, analysisData) {
    try {
      const { data, error } = await supabase
        .from('ad_analyses')
        .insert({
          user_id: userId,
          project_id: analysisData.project_id || null, // NEW: Add project_id support
          headline: analysisData.headline,
          body_text: analysisData.body_text,
          cta: analysisData.cta,
          platform: analysisData.platform,
          target_audience: analysisData.target_audience,
          industry: analysisData.industry,
          overall_score: 0, // Will be updated by backend processing
          clarity_score: 0,
          persuasion_score: 0,
          emotion_score: 0,
          cta_strength_score: 0,
          platform_fit_score: 0,
          analysis_data: null, // Will contain AI analysis results
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        console.error('Error creating analysis:', error);
        throw new Error('Failed to create analysis');
      }

      return data;
    } catch (error) {
      console.error('Error in createAnalysis:', error);
      throw error;
    }
  }

  async updateAnalysisScores(analysisId, scores) {
    try {
      console.log('📊 Updating analysis scores for ID:', analysisId);
      console.log('📊 Scores data received:', scores);
      console.log('📊 Score types:', {
        overall_score: typeof scores.overall_score,
        clarity_score: typeof scores.clarity_score,
        persuasion_score: typeof scores.persuasion_score,
        emotion_score: typeof scores.emotion_score,
        cta_strength_score: typeof scores.cta_strength_score,
        platform_fit_score: typeof scores.platform_fit_score,
        analysis_data: typeof scores.analysis_data
      });
      
      // Ensure all scores are valid integers (database expects INTEGER fields)
      const convertToInteger = (value) => {
        if (value == null || value === undefined || isNaN(value)) return null;
        return Math.round(Number(value)); // Round to nearest integer
      };
      
      const updateData = {
        overall_score: convertToInteger(scores.overall_score),
        clarity_score: convertToInteger(scores.clarity_score),
        persuasion_score: convertToInteger(scores.persuasion_score),
        emotion_score: convertToInteger(scores.emotion_score),
        cta_strength_score: convertToInteger(scores.cta_strength_score),
        platform_fit_score: convertToInteger(scores.platform_fit_score),
        analysis_data: scores.analysis_data,
        updated_at: new Date().toISOString()
      };
      
      console.log('📊 Final update data:', updateData);
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .update(updateData)
        .eq('id', analysisId)
        .select()
        .single();

      if (error) {
        console.error('❌ Supabase error updating analysis scores:', error);
        console.error('❌ Error details:', {
          message: error.message,
          hint: error.hint,
          details: error.details,
          code: error.code
        });
        throw new Error(`Failed to update analysis scores: ${error.message}`);
      }

      return data;
    } catch (error) {
      console.error('Error in updateAnalysisScores:', error);
      throw error;
    }
  }

  // Competitor Benchmarks Operations
  async addCompetitorBenchmarks(analysisId, competitors) {
    try {
      if (!competitors || competitors.length === 0) return [];

      const benchmarksToInsert = competitors.map(competitor => ({
        analysis_id: analysisId,
        competitor_headline: competitor.headline,
        competitor_body_text: competitor.body_text,
        competitor_cta: competitor.cta,
        competitor_platform: competitor.platform,
        source_url: competitor.source_url || null,
        competitor_overall_score: competitor.overall_score || 0,
        competitor_clarity_score: competitor.clarity_score || 0,
        competitor_emotion_score: competitor.emotion_score || 0,
        competitor_cta_score: competitor.cta_score || 0,
        created_at: new Date().toISOString()
      }));

      const { data, error } = await supabase
        .from('competitor_benchmarks')
        .insert(benchmarksToInsert)
        .select();

      if (error) {
        console.error('Error adding competitor benchmarks:', error);
        throw new Error('Failed to add competitor benchmarks');
      }

      return data;
    } catch (error) {
      console.error('Error in addCompetitorBenchmarks:', error);
      throw error;
    }
  }

  // Ad Generation Operations
  async addGeneratedAlternatives(analysisId, alternatives) {
    try {
      if (!alternatives || alternatives.length === 0) return [];

      const alternativesToInsert = alternatives.map(alt => ({
        analysis_id: analysisId,
        variant_type: alt.variant_type,
        generated_headline: alt.headline,
        generated_body_text: alt.body_text,
        generated_cta: alt.cta,
        improvement_reason: alt.improvement_reason,
        predicted_score: alt.predicted_score || null,
        user_rating: null,
        user_selected: false,
        created_at: new Date().toISOString()
      }));

      const { data, error } = await supabase
        .from('ad_generations')
        .insert(alternativesToInsert)
        .select();

      if (error) {
        console.error('Error adding generated alternatives:', error);
        throw new Error('Failed to add generated alternatives');
      }

      return data;
    } catch (error) {
      console.error('Error in addGeneratedAlternatives:', error);
      throw error;
    }
  }

  async updateAlternativeRating(generationId, rating, selected = false) {
    try {
      const { data, error } = await supabase
        .from('ad_generations')
        .update({
          user_rating: rating,
          user_selected: selected
        })
        .eq('id', generationId)
        .select()
        .single();

      if (error) {
        console.error('Error updating alternative rating:', error);
        throw new Error('Failed to update rating');
      }

      return data;
    } catch (error) {
      console.error('Error in updateAlternativeRating:', error);
      throw error;
    }
  }

  // Real-time subscriptions
  subscribeToUserAnalyses(userId, callback) {
    const channel = supabase
      .channel('user-analyses')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'ad_analyses',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          console.log('Real-time analysis update:', payload);
          callback(payload);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }

  // Utility functions
  async checkUserQuota(userId) {
    try {
      const userProfile = await this.getUserProfile(userId);
      if (!userProfile) return { canAnalyze: false, reason: 'Profile not found' };

      const limits = {
        free: 5,
        basic: 50,
        pro: 200
      };

      const limit = limits[userProfile.subscription_tier] || limits.free;
      const current = userProfile.monthly_analyses || 0;

      return {
        canAnalyze: current < limit,
        current,
        limit,
        remaining: limit - current,
        tier: userProfile.subscription_tier
      };
    } catch (error) {
      console.error('Error checking user quota:', error);
      return { canAnalyze: false, reason: 'Error checking quota' };
    }
  }

  async incrementAnalysisCount(userId) {
    try {
      const { data, error } = await supabase.rpc('increment_user_analysis_count', {
        p_user_id: userId
      });

      if (error) {
        console.error('Error incrementing analysis count:', error);
        // This is handled by the database trigger, so this is just a backup
      }

      return data;
    } catch (error) {
      console.error('Error in incrementAnalysisCount:', error);
      // Non-critical error, analysis count is managed by DB triggers
    }
  }
}

const dataService = new DataService();
export default dataService;
