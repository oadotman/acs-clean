import { supabase } from '../lib/supabaseClient';
import toast from 'react-hot-toast';

/**
 * Direct project creation - bypasses session checks for testing
 */
export async function createProjectDirect(userId, projectData) {
  console.log('🚀 DIRECT PROJECT CREATION TEST');
  console.log('📋 Input:', { userId, projectData });
  
  try {
    const insertData = {
      user_id: userId,
      name: projectData.name,
      description: projectData.description || null,
      client_name: projectData.client_name || null
    };
    
    console.log('📤 Direct insert, no session check...');
    
    // Direct insert without any session checks
    const { data, error } = await supabase
      .from('projects')
      .insert(insertData)
      .select()
      .single();
    
    if (error) {
      console.error('❌ Direct insert failed:', error);
      toast.error(`Failed: ${error.message}`);
      throw error;
    }
    
    console.log('✅ Direct insert successful:', data);
    toast.success('Project created (direct method)!');
    return data;
    
  } catch (error) {
    console.error('💥 Direct insert exception:', error);
    throw error;
  }
}

// Make it available globally for testing
if (typeof window !== 'undefined') {
  window.createProjectDirect = createProjectDirect;
  console.log('🧪 Test function available: window.createProjectDirect(userId, {name: "Test"})')
}

export default { createProjectDirect };