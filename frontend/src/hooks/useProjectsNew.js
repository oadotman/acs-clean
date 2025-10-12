import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../services/authContext';
import projectsService from '../services/projectsService';
import toast from 'react-hot-toast';

/**
 * React Query hooks for the NEW Projects feature
 * (Organizing ad analyses by client/campaign/category)
 * 
 * This is separate from the existing useProjects.js (which manages ad_copy_projects)
 */

// ============================================================================
// Query Keys
// ============================================================================

export const PROJECT_QUERY_KEYS = {
  ALL: ['projects-new'],
  LIST: (userId) => ['projects-new', 'list', userId],
  DETAIL: (projectId, userId) => ['projects-new', 'detail', projectId, userId],
  WITH_INSIGHTS: (projectId, userId) => ['projects-new', 'insights', projectId, userId],
  WITH_COUNTS: (userId) => ['projects-new', 'with-counts', userId],
  SEARCH: (userId, searchTerm) => ['projects-new', 'search', userId, searchTerm],
  UNASSIGNED_ANALYSES: (userId) => ['projects-new', 'unassigned', userId],
};

// ============================================================================
// Query Hooks (Read Operations)
// ============================================================================

/**
 * Get all projects for the current user
 */
export const useUserProjects = (options = {}) => {
  const { user } = useAuth();
  
  return useQuery({
    queryKey: PROJECT_QUERY_KEYS.LIST(user?.id),
    queryFn: () => projectsService.getUserProjects(user.id),
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    onError: (error) => {
      console.error('Error fetching projects:', error);
      toast.error('Failed to load projects');
    },
    ...options
  });
};

/**
 * Get a single project by ID with its analyses
 */
export const useProjectDetail = (projectId, options = {}) => {
  const { user } = useAuth();
  
  return useQuery({
    queryKey: PROJECT_QUERY_KEYS.DETAIL(projectId, user?.id),
    queryFn: () => projectsService.getProjectById(projectId, user.id),
    enabled: !!user?.id && !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    onError: (error) => {
      console.error('Error fetching project detail:', error);
      toast.error('Failed to load project details');
    },
    ...options
  });
};

/**
 * Get a project with calculated insights
 */
export const useProjectWithInsights = (projectId, options = {}) => {
  const { user } = useAuth();
  
  return useQuery({
    queryKey: PROJECT_QUERY_KEYS.WITH_INSIGHTS(projectId, user?.id),
    queryFn: () => projectsService.getProjectWithInsights(projectId, user.id),
    enabled: !!user?.id && !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    onError: (error) => {
      console.error('Error fetching project insights:', error);
      toast.error('Failed to load project insights');
    },
    ...options
  });
};

/**
 * Get projects with analysis counts
 */
export const useProjectsWithCounts = (options = {}) => {
  const { user } = useAuth();
  
  return useQuery({
    queryKey: PROJECT_QUERY_KEYS.WITH_COUNTS(user?.id),
    queryFn: () => projectsService.getProjectsWithCounts(user.id),
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    onError: (error) => {
      console.error('Error fetching projects with counts:', error);
      toast.error('Failed to load projects');
    },
    ...options
  });
};

/**
 * Search projects by name, description, or client name
 */
export const useSearchProjects = (searchTerm, options = {}) => {
  const { user } = useAuth();
  
  return useQuery({
    queryKey: PROJECT_QUERY_KEYS.SEARCH(user?.id, searchTerm),
    queryFn: () => projectsService.searchProjects(user.id, searchTerm),
    enabled: !!user?.id,
    staleTime: 1 * 60 * 1000, // 1 minute
    cacheTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
    onError: (error) => {
      console.error('Error searching projects:', error);
      toast.error('Search failed');
    },
    ...options
  });
};

/**
 * Get unassigned analyses (not linked to any project)
 */
export const useUnassignedAnalyses = (options = {}) => {
  const { user } = useAuth();
  
  return useQuery({
    queryKey: PROJECT_QUERY_KEYS.UNASSIGNED_ANALYSES(user?.id),
    queryFn: () => projectsService.getUnassignedAnalyses(user.id),
    enabled: !!user?.id,
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    onError: (error) => {
      console.error('Error fetching unassigned analyses:', error);
      toast.error('Failed to load analyses');
    },
    ...options
  });
};

// ============================================================================
// Mutation Hooks (Write Operations)
// ============================================================================

/**
 * Create a new project
 */
export const useCreateProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (projectData) => {
      console.log('🎯 useCreateProject mutation called with:', { userId: user.id, projectData });
      return projectsService.createProject(user.id, projectData);
    },
    onSuccess: (newProject) => {
      console.log('✅ useCreateProject mutation succeeded:', newProject);
      // Invalidate all project list queries
      queryClient.invalidateQueries({ queryKey: PROJECT_QUERY_KEYS.ALL });
      
      // Add the new project to the cache
      queryClient.setQueryData(
        PROJECT_QUERY_KEYS.DETAIL(newProject.id, user.id),
        { ...newProject, analyses: [] }
      );
      
      toast.success('Project created successfully!');
    },
    onError: (error) => {
      console.error('❌ useCreateProject mutation failed:', {
        message: error.message,
        stack: error.stack,
        fullError: error
      });
      toast.error(`Failed to create project: ${error.message}`);
    }
  });
};

/**
 * Update an existing project
 */
export const useUpdateProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ projectId, updates }) => 
      projectsService.updateProject(projectId, user.id, updates),
    onSuccess: (updatedProject, { projectId }) => {
      // Update the specific project in cache
      queryClient.setQueryData(
        PROJECT_QUERY_KEYS.DETAIL(projectId, user.id),
        (oldData) => {
          if (!oldData) return updatedProject;
          return { ...oldData, ...updatedProject };
        }
      );
      
      // Invalidate list queries to show updated data
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.LIST(user.id) 
      });
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.WITH_COUNTS(user.id) 
      });
      
      toast.success('Project updated successfully!');
    },
    onError: (error) => {
      console.error('Error updating project:', error);
      toast.error('Failed to update project');
    }
  });
};

/**
 * Delete a project
 */
export const useDeleteProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (projectId) => projectsService.deleteProject(projectId, user.id),
    onSuccess: (_, projectId) => {
      // Remove project from cache
      queryClient.removeQueries({ 
        queryKey: PROJECT_QUERY_KEYS.DETAIL(projectId, user.id) 
      });
      
      // Update list caches by removing the deleted project
      queryClient.setQueryData(
        PROJECT_QUERY_KEYS.LIST(user.id),
        (oldData) => {
          if (!oldData) return oldData;
          return oldData.filter(project => project.id !== projectId);
        }
      );
      
      // Invalidate all project queries to ensure consistency
      queryClient.invalidateQueries({ queryKey: PROJECT_QUERY_KEYS.ALL });
      
      // Invalidate unassigned analyses (deleted project's analyses are now unassigned)
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.UNASSIGNED_ANALYSES(user.id) 
      });
      
      toast.success('Project deleted. Analyses remain available.');
    },
    onError: (error) => {
      console.error('Error deleting project:', error);
      toast.error('Failed to delete project');
    }
  });
};

/**
 * Add an analysis to a project
 */
export const useAddAnalysisToProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ analysisId, projectId }) => 
      projectsService.addAnalysisToProject(analysisId, projectId, user.id),
    onSuccess: (_, { projectId }) => {
      // Invalidate project detail to refetch with new analysis
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.DETAIL(projectId, user.id) 
      });
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.WITH_INSIGHTS(projectId, user.id) 
      });
      
      // Invalidate project counts
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.WITH_COUNTS(user.id) 
      });
      
      // Invalidate unassigned analyses
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.UNASSIGNED_ANALYSES(user.id) 
      });
      
      toast.success('Analysis added to project!');
    },
    onError: (error) => {
      console.error('Error adding analysis to project:', error);
      toast.error('Failed to add analysis');
    }
  });
};

/**
 * Remove an analysis from a project
 */
export const useRemoveAnalysisFromProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ analysisId, projectId }) => 
      projectsService.removeAnalysisFromProject(analysisId, user.id),
    onSuccess: (_, { projectId }) => {
      // Invalidate project detail
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.DETAIL(projectId, user.id) 
      });
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.WITH_INSIGHTS(projectId, user.id) 
      });
      
      // Invalidate project counts
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.WITH_COUNTS(user.id) 
      });
      
      // Invalidate unassigned analyses (removed analysis is now unassigned)
      queryClient.invalidateQueries({ 
        queryKey: PROJECT_QUERY_KEYS.UNASSIGNED_ANALYSES(user.id) 
      });
      
      toast.success('Analysis removed from project');
    },
    onError: (error) => {
      console.error('Error removing analysis from project:', error);
      toast.error('Failed to remove analysis');
    }
  });
};

// ============================================================================
// Helper Hooks
// ============================================================================

/**
 * Refresh all project data
 */
export const useRefreshProjects = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.invalidateQueries({ queryKey: PROJECT_QUERY_KEYS.ALL });
    toast.success('Projects refreshed!');
  };
};

/**
 * Check if a project name already exists
 */
export const useCheckProjectNameExists = () => {
  const { user } = useAuth();
  const { data: projects = [] } = useUserProjects();
  
  return (name) => {
    return projects.some(
      project => project.name.toLowerCase() === name.toLowerCase()
    );
  };
};

/**
 * Get project by ID from cache (without refetching)
 */
export const useProjectFromCache = (projectId) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return queryClient.getQueryData(
    PROJECT_QUERY_KEYS.DETAIL(projectId, user?.id)
  );
};
