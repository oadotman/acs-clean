import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../services/authContext';
import projectService from '../services/projectService';
import toast from 'react-hot-toast';

// Query keys
export const QUERY_KEYS = {
  PROJECTS: 'projects',
  PROJECT: 'project',
  PROJECT_SEARCH: 'projectSearch'
};

// Hook to get user's projects
export const useProjects = (options = {}) => {
  const { user } = useAuth();
  
  return useQuery(
    [QUERY_KEYS.PROJECTS, user?.id],
    () => projectService.getUserProjects(user.id),
    {
      enabled: !!user?.id,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
      onError: (error) => {
        console.error('Error fetching projects:', error);
        toast.error('Failed to load projects');
      },
      ...options
    }
  );
};

// Hook to get a specific project
export const useProject = (projectId, options = {}) => {
  const { user } = useAuth();
  
  return useQuery(
    [QUERY_KEYS.PROJECT, projectId, user?.id],
    () => projectService.getProjectById(projectId, user.id),
    {
      enabled: !!user?.id && !!projectId,
      staleTime: 2 * 60 * 1000, // 2 minutes
      cacheTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
      onError: (error) => {
        console.error('Error fetching project:', error);
        toast.error('Failed to load project details');
      },
      ...options
    }
  );
};

// Hook to search projects
export const useProjectSearch = (searchTerm, statusFilter, options = {}) => {
  const { user } = useAuth();
  
  return useQuery(
    [QUERY_KEYS.PROJECT_SEARCH, user?.id, searchTerm, statusFilter],
    () => projectService.searchProjects(user.id, searchTerm, statusFilter),
    {
      enabled: !!user?.id,
      staleTime: 1 * 60 * 1000, // 1 minute
      cacheTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      onError: (error) => {
        console.error('Error searching projects:', error);
        toast.error('Failed to search projects');
      },
      ...options
    }
  );
};

// Mutation hooks for CRUD operations

// Create project mutation
export const useCreateProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation(
    (projectData) => projectService.createProject(user.id, projectData),
    {
      onSuccess: (newProject) => {
        // Invalidate and refetch projects list
        queryClient.invalidateQueries([QUERY_KEYS.PROJECTS, user.id]);
        
        // Add the new project to the cache
        queryClient.setQueryData([QUERY_KEYS.PROJECT, newProject.id, user.id], newProject);
      },
      onError: (error) => {
        console.error('Error creating project:', error);
        toast.error('Failed to create project');
      }
    }
  );
};

// Update project mutation
export const useUpdateProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ projectId, updates }) => projectService.updateProject(projectId, user.id, updates),
    {
      onSuccess: (updatedProject, { projectId }) => {
        // Update the specific project in cache
        queryClient.setQueryData([QUERY_KEYS.PROJECT, projectId, user.id], updatedProject);
        
        // Update projects list cache
        queryClient.setQueryData([QUERY_KEYS.PROJECTS, user.id], (oldData) => {
          if (!oldData) return oldData;
          return oldData.map(project => 
            project.id === projectId ? { ...project, ...updatedProject } : project
          );
        });
        
      },
      onError: (error) => {
        console.error('Error updating project:', error);
        toast.error('Failed to update project');
      }
    }
  );
};

// Delete project mutation
export const useDeleteProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation(
    (projectId) => projectService.deleteProject(projectId, user.id),
    {
      onSuccess: (_, projectId) => {
        // Remove project from cache
        queryClient.removeQueries([QUERY_KEYS.PROJECT, projectId, user.id]);
        
        // Update projects list cache
        queryClient.setQueryData([QUERY_KEYS.PROJECTS, user.id], (oldData) => {
          if (!oldData) return oldData;
          return oldData.filter(project => project.id !== projectId);
        });
        
      },
      onError: (error) => {
        console.error('Error deleting project:', error);
        toast.error('Failed to delete project');
      }
    }
  );
};

// Run analysis mutation
export const useRunAnalysis = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation(
    (projectId) => projectService.runProjectAnalysis(projectId, user.id),
    {
      onSuccess: (_, projectId) => {
        // Invalidate project data to refetch updated status
        queryClient.invalidateQueries([QUERY_KEYS.PROJECT, projectId, user.id]);
        queryClient.invalidateQueries([QUERY_KEYS.PROJECTS, user.id]);
        queryClient.invalidateQueries([QUERY_KEYS.DASHBOARD_ANALYTICS, user.id]);
      },
      onError: (error) => {
        console.error('Error running analysis:', error);
        toast.error('Failed to start analysis');
      }
    }
  );
};

// Add tool to project mutation
export const useAddToolToProject = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ projectId, toolConfig }) => projectService.addToolToProject(projectId, user.id, toolConfig),
    {
      onSuccess: (_, { projectId }) => {
        // Invalidate project data to refetch updated tools
        queryClient.invalidateQueries([QUERY_KEYS.PROJECT, projectId, user.id]);
        queryClient.invalidateQueries([QUERY_KEYS.PROJECTS, user.id]);
      },
      onError: (error) => {
        console.error('Error adding tool to project:', error);
        toast.error('Failed to add tool to project');
      }
    }
  );
};

// Helper hook to refresh all project data
export const useRefreshProjects = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.invalidateQueries([QUERY_KEYS.PROJECTS, user?.id]);
    toast.success('Projects refreshed!');
  };
};
