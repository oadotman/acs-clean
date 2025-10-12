// Using clean Supabase client to avoid timeout issues
import { supabase } from '../lib/supabaseClientClean';
import toast from 'react-hot-toast';

/**
 * ProjectsService - Service layer for managing projects
 * 
 * Projects allow users to organize multiple ad analyses by:
 * - Client (e.g., Nike, Adidas)
 * - Campaign (e.g., Q1 2025, Black Friday)
 * - Category (e.g., Winter Jackets, Running Shoes)
 */
class ProjectsService {
  
  // ============================================================================
  // CRUD Operations
  // ============================================================================

  /**
   * Get all projects for a user
   * @param {string} userId - The authenticated user's ID
   * @returns {Promise<Array>} List of projects
   */
  async getUserProjects(userId) {
    try {
      console.log('📁 Fetching projects for user:', userId);
      
      const { data, error } = await supabase
        .from('projects')
        .select(`
          id,
          name,
          description,
          client_name,
          created_at,
          updated_at
        `)
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('Error fetching projects:', error);
        throw new Error('Failed to fetch projects');
      }

      console.log(`✅ Fetched ${data?.length || 0} projects`);
      return data || [];
    } catch (error) {
      console.error('Error in getUserProjects:', error);
      throw error;
    }
  }

  /**
   * Get a single project with its analyses
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID (for security)
   * @returns {Promise<Object>} Project with analyses
   */
  async getProjectById(projectId, userId) {
    try {
      console.log('📁 Fetching project:', projectId);
      
      // Fetch project details
      const { data: project, error: projectError } = await supabase
        .from('projects')
        .select('*')
        .eq('id', projectId)
        .eq('user_id', userId)
        .single();

      if (projectError) {
        console.error('Error fetching project:', projectError);
        throw new Error('Failed to fetch project details');
      }

      // Fetch analyses linked to this project
      const { data: analyses, error: analysesError } = await supabase
        .from('ad_analyses')
        .select(`
          id,
          headline,
          body_text,
          cta,
          platform,
          overall_score,
          clarity_score,
          persuasion_score,
          emotion_score,
          cta_strength_score,
          platform_fit_score,
          created_at,
          updated_at
        `)
        .eq('project_id', projectId)
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (analysesError) {
        console.warn('Error fetching project analyses:', analysesError);
        // Don't fail the whole request if analyses fetch fails
        return {
          ...project,
          analyses: []
        };
      }

      return {
        ...project,
        analyses: analyses || []
      };
    } catch (error) {
      console.error('Error in getProjectById:', error);
      throw error;
    }
  }

  /**
   * Create a new project
   * @param {string} userId - User ID
   * @param {Object} projectData - Project data (name, description, client_name)
   * @returns {Promise<Object>} Created project
   */
  async createProject(userId, projectData) {
    try {
      console.log('➕ Creating new project:', projectData.name);
      console.log('📋 Project data:', { userId, projectData });
      
      const insertData = {
        user_id: userId,
        name: projectData.name,
        description: projectData.description || null,
        client_name: projectData.client_name || null
      };
      
      console.log('📤 Inserting to Supabase:', insertData);
      
      // Add timeout to prevent hanging
      const insertPromise = supabase
        .from('projects')
        .insert(insertData)
        .select()
        .single();
      
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout after 10 seconds')), 10000)
      );
      
      console.log('⏱️ Waiting for Supabase response (10s timeout)...');
      const { data, error } = await Promise.race([insertPromise, timeoutPromise]);

      if (error) {
        console.error('❌ Supabase error creating project:', {
          message: error.message,
          details: error.details,
          hint: error.hint,
          code: error.code,
          fullError: error
        });
        throw new Error(`Failed to create project: ${error.message}`);
      }

      console.log('✅ Project created successfully:', data);
      toast.success('Project created successfully!');
      return data;
    } catch (error) {
      console.error('💥 Exception in createProject:', {
        message: error.message,
        stack: error.stack,
        fullError: error
      });
      toast.error(`Failed to create project: ${error.message}`);
      throw error;
    }
  }

  /**
   * Update an existing project
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID (for security)
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated project
   */
  async updateProject(projectId, userId, updates) {
    try {
      console.log('✏️ Updating project:', projectId);
      
      const { data, error } = await supabase
        .from('projects')
        .update(updates)
        .eq('id', projectId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) {
        console.error('Error updating project:', error);
        throw new Error('Failed to update project');
      }

      console.log('✅ Project updated');
      toast.success('Project updated successfully!');
      return data;
    } catch (error) {
      console.error('Error in updateProject:', error);
      toast.error('Failed to update project');
      throw error;
    }
  }

  /**
   * Delete a project
   * Note: Analyses are NOT deleted, just unlinked (project_id set to NULL)
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID (for security)
   * @returns {Promise<boolean>} Success status
   */
  async deleteProject(projectId, userId) {
    try {
      console.log('🗑️ Deleting project:', projectId);
      
      // First, unlink all analyses from this project (set project_id to NULL)
      const { error: unlinkError } = await supabase
        .from('ad_analyses')
        .update({ project_id: null })
        .eq('project_id', projectId)
        .eq('user_id', userId);

      if (unlinkError) {
        console.warn('Warning: Could not unlink analyses:', unlinkError);
        // Continue with deletion anyway
      }

      // Now delete the project
      const { error } = await supabase
        .from('projects')
        .delete()
        .eq('id', projectId)
        .eq('user_id', userId);

      if (error) {
        console.error('Error deleting project:', error);
        throw new Error('Failed to delete project');
      }

      console.log('✅ Project deleted');
      toast.success('Project deleted. Your analyses are still available.');
      return true;
    } catch (error) {
      console.error('Error in deleteProject:', error);
      toast.error('Failed to delete project');
      throw error;
    }
  }

  // ============================================================================
  // Analysis Management
  // ============================================================================

  /**
   * Add an analysis to a project
   * @param {string} analysisId - Analysis ID
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID (for security)
   * @returns {Promise<Object>} Updated analysis
   */
  async addAnalysisToProject(analysisId, projectId, userId) {
    try {
      console.log('🔗 Adding analysis to project:', { analysisId, projectId });
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .update({ project_id: projectId })
        .eq('id', analysisId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) {
        console.error('Error adding analysis to project:', error);
        throw new Error('Failed to add analysis to project');
      }

      console.log('✅ Analysis added to project');
      toast.success('Analysis added to project!');
      return data;
    } catch (error) {
      console.error('Error in addAnalysisToProject:', error);
      toast.error('Failed to add analysis to project');
      throw error;
    }
  }

  /**
   * Remove an analysis from a project (unlink)
   * @param {string} analysisId - Analysis ID
   * @param {string} userId - User ID (for security)
   * @returns {Promise<Object>} Updated analysis
   */
  async removeAnalysisFromProject(analysisId, userId) {
    try {
      console.log('🔓 Removing analysis from project:', analysisId);
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .update({ project_id: null })
        .eq('id', analysisId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) {
        console.error('Error removing analysis from project:', error);
        throw new Error('Failed to remove analysis from project');
      }

      console.log('✅ Analysis removed from project');
      toast.success('Analysis removed from project');
      return data;
    } catch (error) {
      console.error('Error in removeAnalysisFromProject:', error);
      toast.error('Failed to remove analysis from project');
      throw error;
    }
  }

  // ============================================================================
  // Project Insights & Analytics
  // ============================================================================

  /**
   * Calculate insights for a project based on its analyses
   * @param {Array} analyses - Project's analyses
   * @returns {Object} Insights object
   */
  _calculateInsights(analyses) {
    if (!analyses || analyses.length === 0) {
      return {
        averageImprovement: 0,
        mostUsedPlatform: null,
        platformCounts: {},
        bestPerformingId: null,
        bestPerformingScore: 0,
        totalAnalyses: 0
      };
    }

    // Calculate average score improvement (score_after - assumed baseline)
    // For now, we'll use overall_score as the "after" score
    // If you have a "before" score field, adjust this logic
    const avgScore = analyses.reduce((sum, a) => sum + (a.overall_score || 0), 0) / analyses.length;
    const averageImprovement = Math.round(avgScore);

    // Count analyses by platform
    const platformCounts = analyses.reduce((counts, analysis) => {
      const platform = analysis.platform || 'Unknown';
      counts[platform] = (counts[platform] || 0) + 1;
      return counts;
    }, {});

    // Find most used platform
    const mostUsedPlatform = Object.entries(platformCounts)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || null;

    // Find best performing analysis (highest overall_score)
    const bestPerforming = analyses.reduce((best, current) => {
      const currentScore = current.overall_score || 0;
      const bestScore = best.overall_score || 0;
      return currentScore > bestScore ? current : best;
    }, analyses[0]);

    return {
      averageImprovement,
      mostUsedPlatform,
      platformCounts,
      bestPerformingId: bestPerforming?.id || null,
      bestPerformingScore: bestPerforming?.overall_score || 0,
      bestPerformingName: bestPerforming?.headline || 'Unknown',
      totalAnalyses: analyses.length
    };
  }

  /**
   * Get project with insights
   * @param {string} projectId - Project ID
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Project with insights
   */
  async getProjectWithInsights(projectId, userId) {
    try {
      const project = await this.getProjectById(projectId, userId);
      const insights = this._calculateInsights(project.analyses);

      return {
        project,
        analyses: project.analyses,
        insights
      };
    } catch (error) {
      console.error('Error in getProjectWithInsights:', error);
      throw error;
    }
  }

  // ============================================================================
  // Search & Filtering
  // ============================================================================

  /**
   * Search projects by name or description
   * @param {string} userId - User ID
   * @param {string} searchTerm - Search term
   * @returns {Promise<Array>} Filtered projects
   */
  async searchProjects(userId, searchTerm = '') {
    try {
      console.log('🔍 Searching projects:', searchTerm);
      
      let query = supabase
        .from('projects')
        .select('*')
        .eq('user_id', userId);

      if (searchTerm && searchTerm.trim()) {
        query = query.or(`name.ilike.%${searchTerm}%,description.ilike.%${searchTerm}%,client_name.ilike.%${searchTerm}%`);
      }

      const { data, error } = await query.order('updated_at', { ascending: false });

      if (error) {
        console.error('Error searching projects:', error);
        throw new Error('Failed to search projects');
      }

      return data || [];
    } catch (error) {
      console.error('Error in searchProjects:', error);
      throw error;
    }
  }

  /**
   * Get projects with analysis counts
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Projects with analysis counts
   */
  async getProjectsWithCounts(userId) {
    try {
      console.log('📊 Fetching projects with counts for user:', userId);
      
      // Get all projects
      const projects = await this.getUserProjects(userId);

      // Get analysis counts for each project
      const projectsWithCounts = await Promise.all(
        projects.map(async (project) => {
          const { count, error } = await supabase
            .from('ad_analyses')
            .select('id', { count: 'exact', head: true })
            .eq('project_id', project.id)
            .eq('user_id', userId);

          if (error) {
            console.warn('Error counting analyses for project:', project.id, error);
            return { ...project, analysisCount: 0 };
          }

          return {
            ...project,
            analysisCount: count || 0
          };
        })
      );

      return projectsWithCounts;
    } catch (error) {
      console.error('Error in getProjectsWithCounts:', error);
      throw error;
    }
  }

  /**
   * Get unassigned analyses (not linked to any project)
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Unassigned analyses
   */
  async getUnassignedAnalyses(userId) {
    try {
      console.log('📋 Fetching unassigned analyses for user:', userId);
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .select(`
          id,
          headline,
          body_text,
          cta,
          platform,
          overall_score,
          created_at
        `)
        .eq('user_id', userId)
        .is('project_id', null)
        .order('created_at', { ascending: false })
        .limit(50);

      if (error) {
        console.error('Error fetching unassigned analyses:', error);
        throw new Error('Failed to fetch unassigned analyses');
      }

      return data || [];
    } catch (error) {
      console.error('Error in getUnassignedAnalyses:', error);
      throw error;
    }
  }
}

// Export singleton instance
const projectsService = new ProjectsService();
export default projectsService;
