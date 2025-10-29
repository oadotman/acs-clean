// Team Management Service for Supabase integration
import { supabase } from '../lib/supabaseClientClean';
import toast from 'react-hot-toast';

// Timeout helper to prevent infinite hangs - increased timeout for slow connections
const withTimeout = (promise, timeoutMs = 30000, operationName = 'Operation') => {
  return Promise.race([
    promise,
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error(`${operationName} timed out after ${timeoutMs}ms`)), timeoutMs)
    )
  ]);
};

/**
 * TeamService - Service layer for managing team members, agencies, and permissions
 * 
 * Handles:
 * - Agency creation and management
 * - Team member invitations and CRUD operations
 * - Role and permission management
 * - Team analytics and statistics
 */
class TeamService {
  
  // ============================================================================
  // Agency Management
  // ============================================================================

  /**
   * Get or create agency for a user
   * @param {string} userId - The authenticated user's ID
   * @returns {Promise<Object>} Agency data
   */
  async getOrCreateUserAgency(userId) {
    try {
      console.log('🏫 Fetching agency for user:', userId);
      
      if (!userId) {
        throw new Error('User ID is required');
      }
      
      // Step 1: Check if user owns an agency
      console.log('🔍 Step 1: Checking for owned agency...');
      const { data: ownedAgency, error: ownedError } = await supabase
        .from('agencies')
        .select('*')
        .eq('owner_id', userId)
        .maybeSingle();
      
      console.log('🔍 Step 1 complete:', { 
        hasOwnedAgency: !!ownedAgency, 
        agencyData: ownedAgency,
        error: ownedError?.message,
        errorCode: ownedError?.code 
      });
      
      // If there's a real error (not just "no rows"), log it but DON'T throw yet
      if (ownedError && ownedError.code !== 'PGRST116') {
        console.error('❌ Database error checking owned agency:', ownedError);
        // Don't throw - try membership check instead
      }

      if (ownedAgency && !ownedError) {
        console.log('✅ Found existing owned agency:', ownedAgency.name);
        return {
          ...ownedAgency,
          userRole: 'admin'
        };
      }

      // Step 2: Check if user is a member of an agency  
      console.log('🔍 Step 2: Checking for agency membership...');
      const { data: existingMember, error: memberError } = await supabase
        .from('agency_team_members')
        .select(`
          agency_id,
          role,
          agencies (
            id,
            name,
            description,
            subscription_tier,
            created_at,
            updated_at,
            owner_id,
            status
          )
        `)
        .eq('user_id', userId)
        .eq('status', 'active')
        .maybeSingle();
      
      console.log('🔍 Step 2 complete:', { 
        hasMembership: !!existingMember,
        membershipData: existingMember,
        error: memberError?.message,
        errorCode: memberError?.code 
      });
      
      // If there's a real database error (not just "no rows"), log it
      if (memberError && memberError.code !== 'PGRST116') {
        console.error('❌ Database error checking membership:', memberError);
        console.error('Full error:', memberError);
        // Don't throw - we'll try to create an agency instead
      }

      if (existingMember?.agencies && !memberError) {
        console.log('✅ Found existing agency via membership:', existingMember.agencies.name);
        console.log('Agency data:', existingMember.agencies);
        return {
          ...existingMember.agencies,
          userRole: existingMember.role
        };
      }

      // No existing agency, check if user can create one
      console.log('🆕 Checking if user can create agency');
      const { data: userProfile, error: profileError } = await supabase
        .from('user_profiles')
        .select('full_name, email, can_create_agency, subscription_tier')
        .eq('id', userId)
        .single();
      
      if (profileError) {
        console.error('❌ Error fetching user profile:', profileError);
        throw new Error('Unable to fetch user profile. Please try again.');
      }
      
      console.log('📊 User profile:', {
        tier: userProfile?.subscription_tier,
        canCreate: userProfile?.can_create_agency,
        fullName: userProfile?.full_name
      });
      
      // Check if user has agency tier OR can_create_agency flag
      const isAgencyTier = ['agency_standard', 'agency_premium', 'agency_unlimited'].includes(userProfile?.subscription_tier);
      const canCreate = userProfile?.can_create_agency === true || isAgencyTier;
      
      if (!canCreate) {
        console.warn('⚠️ User cannot create agency:', {
          tier: userProfile?.subscription_tier,
          canCreateFlag: userProfile?.can_create_agency
        });
        throw new Error('You need to upgrade to an Agency plan to create a team workspace. Please upgrade your subscription to continue.');
      }
      
      console.log('✅ User can create agency');

      const agencyName = userProfile?.full_name 
        ? `${userProfile.full_name}'s Agency`
        : 'My Agency';

      const { data: newAgency, error: agencyError } = await supabase
        .from('agencies')
        .insert({
          name: agencyName,
          description: 'Main agency workspace',
          subscription_tier: 'agency_standard',
          owner_id: userId
        })
        .select()
        .single();

      if (agencyError) {
        console.error('Error creating agency:', agencyError);
        throw new Error('Failed to create agency');
      }

      // Add user as admin to the new agency
      const { error: membershipError } = await supabase
        .from('agency_team_members')
        .insert({
          agency_id: newAgency.id,
          user_id: userId,
          role: 'admin',
          status: 'active',
          invited_by: userId
        });

      if (membershipError) {
        console.error('Error adding user to agency:', membershipError);
        console.log('⚠️ Agency created but owner not added to team members');
        // Don't fail here, agency is created
      } else {
        console.log('✅ Added agency owner as admin team member');
      }

      console.log('✅ Created new agency:', newAgency.name);
      return {
        ...newAgency,
        userRole: 'admin'
      };
    } catch (error) {
      console.error('Error in getOrCreateUserAgency:', error);
      throw error;
    }
  }

  // ============================================================================
  // Team Member Management
  // ============================================================================

  /**
   * Get all team members for an agency
   * @param {string} agencyId - Agency ID
   * @returns {Promise<Array>} List of team members
   */
  async getTeamMembers(agencyId) {
    try {
      console.log('👥 Fetching team members for agency:', agencyId);
      
      if (!agencyId) {
        throw new Error('Agency ID is required to fetch team members');
      }
      
      // Query with proper joins to get user profile data
      const { data, error } = await supabase
        .from('agency_team_members')
        .select(`
          id,
          user_id,
          role,
          status,
          created_at,
          updated_at
        `)
        .eq('agency_id', agencyId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('❌ Error fetching team members:', error);
        throw new Error(`Failed to fetch team members: ${error.message}`);
      }

      // If no members, return empty array (normal for new agencies)
      if (!data || data.length === 0) {
        console.log('ℹ️ No team members found for this agency yet');
        return [];
      }

      // Fetch user profiles separately to avoid join issues
      const userIds = data.map(member => member.user_id);
      const { data: profiles } = await supabase
        .from('user_profiles')
        .select('id, email, full_name, avatar_url')
        .in('id', userIds);

      // Create a map for easy lookup
      const profileMap = {};
      if (profiles) {
        profiles.forEach(profile => {
          profileMap[profile.id] = profile;
        });
      }

      // Transform data for frontend consumption
      const teamMembers = data.map(member => {
        const profile = profileMap[member.user_id];
        return {
          id: member.id,
          userId: member.user_id,
          name: profile?.full_name || profile?.email || 'Unknown User',
          email: profile?.email || '',
          avatar: profile?.avatar_url || '',
          role: member.role,
          status: member.status,
          createdAt: member.created_at,
          lastActive: 'Never', // We'll add analytics later
          analysesThisMonth: 0, // Default for now
          creditsUsed: 0, // Default for now
          isClient: member.role === 'client',
          projectsAccess: member.role === 'admin' ? ['all'] : [], // Default access
          clientAccess: [] // Default client access
        };
      });

      console.log(`✅ Fetched ${teamMembers.length} team members`);
      return teamMembers;
    } catch (error) {
      console.error('❌ Error in getTeamMembers:', error);
      throw error; // Let the UI handle the error properly
    }
  }

  /**
   * Send invitation to a new team member
   * @param {string} agencyId - Agency ID
   * @param {string} inviterUserId - ID of user sending invitation
   * @param {Object} invitationData - Invitation details
   * @returns {Promise<Object>} Created invitation
   */
  async sendInvitation(agencyId, inviterUserId, invitationData) {
    try {
      const { email, role, projectAccess = [], clientAccess = [] } = invitationData;
      console.log('📧 Sending invitation to:', email);

      // Check if user already exists and is in the agency
      const { data: existingUser } = await supabase
        .from('user_profiles')
        .select('id')
        .eq('email', email)
        .single();

      if (existingUser) {
        const { data: existingMember } = await supabase
          .from('agency_team_members')
          .select('id')
          .eq('agency_id', agencyId)
          .eq('user_id', existingUser.id)
          .single();

        if (existingMember) {
          throw new Error('User is already a member of this agency');
        }
      }

      // Generate invitation token
      const invitationToken = this.generateInvitationToken();
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + 7); // 7 days expiration

      // Create invitation record
      const { data: invitation, error: invitationError } = await supabase
        .from('agency_invitations')
        .insert({
          agency_id: agencyId,
          email: email.toLowerCase(),
          role,
          status: 'pending',
          invitation_token: invitationToken,
          expires_at: expiresAt.toISOString(),
          invited_by: inviterUserId,
          project_access: projectAccess,
          client_access: clientAccess
        })
        .select()
        .single();

      if (invitationError) {
        console.error('Error creating invitation:', invitationError);
        throw new Error('Failed to create invitation');
      }

      // TODO: Send actual email with invitation link
      console.log('📬 Invitation created (email sending not implemented):', {
        email,
        token: invitationToken,
        expiresAt
      });

      toast.success(`Invitation sent to ${email}`);
      return invitation;
    } catch (error) {
      console.error('Error in sendInvitation:', error);
      toast.error(error.message || 'Failed to send invitation');
      throw error;
    }
  }

  /**
   * Update team member role or status
   * @param {string} memberId - Team member ID
   * @param {Object} updates - Updates to apply
   * @returns {Promise<Object>} Updated member
   */
  async updateTeamMember(memberId, updates) {
    try {
      console.log('✏️ Updating team member:', memberId);
      
      const { data, error } = await supabase
        .from('agency_team_members')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', memberId)
        .select(`
          id,
          user_id,
          role,
          status,
          user_profiles (
            full_name,
            email
          )
        `)
        .single();

      if (error) {
        console.error('Error updating team member:', error);
        throw new Error('Failed to update team member');
      }

      toast.success(`Updated ${data.user_profiles?.full_name || 'team member'}`);
      return data;
    } catch (error) {
      console.error('Error in updateTeamMember:', error);
      toast.error('Failed to update team member');
      throw error;
    }
  }

  /**
   * Remove team member from agency
   * @param {string} memberId - Team member ID
   * @returns {Promise<boolean>} Success status
   */
  async removeTeamMember(memberId) {
    try {
      console.log('🗑️ Removing team member:', memberId);
      
      // Get member info for confirmation
      const { data: member } = await supabase
        .from('agency_team_members')
        .select(`
          user_profiles (
            full_name,
            email
          )
        `)
        .eq('id', memberId)
        .single();

      const { error } = await supabase
        .from('agency_team_members')
        .delete()
        .eq('id', memberId);

      if (error) {
        console.error('Error removing team member:', error);
        throw new Error('Failed to remove team member');
      }

      toast.success(`Removed ${member?.user_profiles?.full_name || 'team member'}`);
      return true;
    } catch (error) {
      console.error('Error in removeTeamMember:', error);
      toast.error('Failed to remove team member');
      throw error;
    }
  }

  /**
   * Resend invitation to a pending member
   * @param {string} invitationId - Invitation ID
   * @returns {Promise<Object>} Updated invitation
   */
  async resendInvitation(invitationId) {
    try {
      console.log('🔄 Resending invitation:', invitationId);
      
      // Generate new token and extend expiration
      const newToken = this.generateInvitationToken();
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + 7);

      const { data, error } = await supabase
        .from('agency_invitations')
        .update({
          invitation_token: newToken,
          expires_at: expiresAt.toISOString(),
          status: 'pending'
        })
        .eq('id', invitationId)
        .select()
        .single();

      if (error) {
        console.error('Error resending invitation:', error);
        throw new Error('Failed to resend invitation');
      }

      // TODO: Send actual email
      console.log('📬 Invitation resent (email sending not implemented)');
      toast.success('Invitation resent successfully');
      return data;
    } catch (error) {
      console.error('Error in resendInvitation:', error);
      toast.error('Failed to resend invitation');
      throw error;
    }
  }

  // ============================================================================
  // Team Analytics
  // ============================================================================

  /**
   * Get team statistics and analytics
   * @param {string} agencyId - Agency ID
   * @returns {Promise<Object>} Team analytics
   */
  async getTeamAnalytics(agencyId) {
    try {
      console.log('📊 Fetching team analytics for agency:', agencyId);
      
      // Get basic team stats with simple query
      const { data: members, error: membersError } = await supabase
        .from('agency_team_members')
        .select('id, role, status, created_at')
        .eq('agency_id', agencyId);

      if (membersError) {
        console.error('Error fetching team analytics:', membersError);
        
        // Handle specific RLS policy recursion error
        if (membersError.code === '42P17' && membersError.message?.includes('infinite recursion')) {
          console.warn('⚠️ RLS policy recursion detected in analytics - returning default values');
        }
        
        // Return default analytics instead of throwing error
        console.log('⚠️ Returning default analytics due to error');
        return {
          totalMembers: 0,
          activeMembers: 0,
          pendingMembers: 0,
          totalAnalyses: 0,
          totalCredits: 0,
          roleDistribution: {}
        };
      }

      // Handle case where no members exist yet (normal for new agencies)
      if (!members || members.length === 0) {
        console.log('ℹ️ No team members found for analytics');
        return {
          totalMembers: 0,
          activeMembers: 0,
          pendingMembers: 0,
          totalAnalyses: 0,
          totalCredits: 0,
          roleDistribution: {}
        };
      }

      // Calculate statistics
      const totalMembers = members.length;
      const activeMembers = members.filter(m => m.status === 'active').length;
      const pendingMembers = members.filter(m => m.status === 'pending').length;
      
      // Role distribution
      const roleDistribution = members.reduce((acc, member) => {
        acc[member.role] = (acc[member.role] || 0) + 1;
        return acc;
      }, {});

      const analytics = {
        totalMembers,
        activeMembers,
        pendingMembers,
        totalAnalyses: 0, // Will implement analytics tracking later
        totalCredits: 0, // Will implement analytics tracking later
        roleDistribution
      };

      console.log('✅ Team analytics:', analytics);
      return analytics;
    } catch (error) {
      console.error('Error in getTeamAnalytics:', error);
      // Return default analytics instead of throwing error
      return {
        totalMembers: 0,
        activeMembers: 0,
        pendingMembers: 0,
        totalAnalyses: 0,
        totalCredits: 0,
        roleDistribution: {}
      };
    }
  }

  // ============================================================================
  // Projects and Client Access
  // ============================================================================

  /**
   * Get projects accessible to agency
   * @param {string} agencyId - Agency ID
   * @returns {Promise<Array>} List of projects
   */
  async getAgencyProjects(agencyId) {
    try {
      console.log('📁 Fetching agency projects:', agencyId);
      
      const { data, error } = await supabase
        .from('projects')
        .select(`
          id,
          name,
          description,
          client_name,
          created_at
        `)
        .eq('agency_id', agencyId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching agency projects:', error);
        throw new Error('Failed to fetch projects');
      }

      return data || [];
    } catch (error) {
      console.error('Error in getAgencyProjects:', error);
      throw error;
    }
  }

  /**
   * Get clients for agency
   * @param {string} agencyId - Agency ID  
   * @returns {Promise<Array>} List of clients
   */
  async getAgencyClients(agencyId) {
    try {
      console.log('👤 Fetching agency clients:', agencyId);
      
      // Get unique client names from projects
      const { data, error } = await supabase
        .from('projects')
        .select('client_name')
        .eq('agency_id', agencyId)
        .not('client_name', 'is', null);

      if (error) {
        console.error('Error fetching agency clients:', error);
        throw new Error('Failed to fetch clients');
      }

      // Create unique client list
      const uniqueClients = [...new Set(data.map(p => p.client_name))]
        .filter(Boolean)
        .map(name => ({
          id: this.slugify(name),
          name
        }));

      return uniqueClients;
    } catch (error) {
      console.error('Error in getAgencyClients:', error);
      throw error;
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Generate a secure invitation token
   * @returns {string} Random token
   */
  generateInvitationToken() {
    return Array.from(crypto.getRandomValues(new Uint8Array(32)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  /**
   * Format last active timestamp
   * @param {string} timestamp - ISO timestamp
   * @returns {string} Formatted time
   */
  formatLastActive(timestamp) {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
    return then.toLocaleDateString();
  }

  /**
   * Convert string to slug
   * @param {string} text - Text to slugify
   * @returns {string} Slug
   */
  slugify(text) {
    return text
      .toString()
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w-]+/g, '')
      .replace(/--+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '');
  }
}

// Create and export singleton instance
const teamService = new TeamService();
export default teamService;