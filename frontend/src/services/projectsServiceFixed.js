/**
 * FIXED Project Service - Direct Supabase connection
 * This bypasses any initialization issues with the main supabase client
 */

import { createClient } from '@supabase/supabase-js';
import toast from 'react-hot-toast';

// Get env vars directly
const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY;

console.log('🔧 ProjectsServiceFixed initializing...');
console.log('   URL:', SUPABASE_URL ? 'Present' : 'MISSING!');
console.log('   Key:', SUPABASE_ANON_KEY ? 'Present' : 'MISSING!');

// Create a fresh client instance
const supabaseFixed = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: false, // Don't interfere with main auth
  }
});

class ProjectsServiceFixed {
  
  /**
   * Create a new project - FIXED VERSION
   */
  async createProject(userId, projectData) {
    console.log('🚀 FIXED: Creating project...');
    console.log('📋 Data:', { userId, projectData });
    
    try {
      const insertData = {
        user_id: userId,
        name: projectData.name,
        description: projectData.description || null,
        client_name: projectData.client_name || null
      };
      
      console.log('📤 FIXED: Inserting with fresh client...');
      
      // Use the fresh client
      const { data, error } = await supabaseFixed
        .from('projects')
        .insert(insertData)
        .select()
        .single();
      
      if (error) {
        console.error('❌ FIXED: Insert failed:', error);
        toast.error(`Failed: ${error.message}`);
        throw error;
      }
      
      console.log('✅ FIXED: Project created:', data);
      toast.success('Project created successfully!');
      return data;
      
    } catch (error) {
      console.error('💥 FIXED: Exception:', error);
      throw error;
    }
  }
  
  /**
   * Get all projects for a user - FIXED VERSION
   */
  async getUserProjects(userId) {
    try {
      console.log('📁 FIXED: Fetching projects for user:', userId);
      
      const { data, error } = await supabaseFixed
        .from('projects')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('❌ FIXED: Fetch failed:', error);
        throw error;
      }

      console.log(`✅ FIXED: Fetched ${data?.length || 0} projects`);
      return data || [];
    } catch (error) {
      console.error('💥 FIXED: Exception:', error);
      throw error;
    }
  }
}

const projectsServiceFixed = new ProjectsServiceFixed();

// Make available globally for testing
if (typeof window !== 'undefined') {
  window.projectsServiceFixed = projectsServiceFixed;
  console.log('🧪 Fixed service available: window.projectsServiceFixed');
}

export default projectsServiceFixed;