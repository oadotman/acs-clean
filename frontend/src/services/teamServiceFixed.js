// Team Management Service - Fixed Version with Direct Supabase Implementation
// This version doesn't rely on backend API for invitations
import { supabase } from '../lib/supabaseClientClean';
import toast from 'react-hot-toast';

/**
 * TeamServiceFixed - Direct Supabase implementation for team invitations
 * No backend API calls for invitations - works entirely in frontend
 */
class TeamServiceFixed {

  /**
   * Generate a 6-character invitation code
   */
  generateInvitationCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // No O,0,I,1
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  }

  /**
   * Create invitation directly in Supabase (no backend API)
   */
  async createInvitation(agencyId, inviterUserId, invitationData) {
    try {
      const { email, role = 'viewer', projectAccess = [], clientAccess = [] } = invitationData;

      console.log('📝 Creating invitation directly in Supabase...');

      // Generate 6-character code
      const invitationCode = this.generateInvitationCode();

      // Calculate expiration (7 days from now)
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + 7);

      // Check if user is already a member
      const { data: existingMember } = await supabase
        .from('agency_team_members')
        .select('id')
        .eq('agency_id', agencyId)
        .eq('user_id', inviterUserId)
        .single();

      if (!existingMember) {
        throw new Error('You are not a member of this agency');
      }

      // Check for existing invitation
      const { data: existingInvite } = await supabase
        .from('agency_invitations')
        .select('id')
        .eq('agency_id', agencyId)
        .eq('email', email.toLowerCase())
        .eq('status', 'pending')
        .single();

      if (existingInvite) {
        // Delete existing invitation
        await supabase
          .from('agency_invitations')
          .delete()
          .eq('id', existingInvite.id);
      }

      // Create new invitation
      const invitationRecord = {
        agency_id: agencyId,
        email: email.toLowerCase(),
        role: role,
        invitation_token: invitationCode, // Store code in token field for compatibility
        status: 'pending',
        expires_at: expiresAt.toISOString(),
        invited_by: inviterUserId,
        project_access: projectAccess,
        client_access: clientAccess
      };

      // Try to add invitation_code field if column exists
      if (this.supportsInvitationCodeField) {
        invitationRecord.invitation_code = invitationCode;
      }

      const { data: newInvitation, error } = await supabase
        .from('agency_invitations')
        .insert(invitationRecord)
        .select()
        .single();

      if (error) {
        console.error('Supabase error:', error);

        // If invitation_code column doesn't exist, retry without it
        if (error.message?.includes('invitation_code')) {
          this.supportsInvitationCodeField = false;
          delete invitationRecord.invitation_code;

          const { data: retryInvitation, error: retryError } = await supabase
            .from('agency_invitations')
            .insert(invitationRecord)
            .select()
            .single();

          if (retryError) {
            throw new Error('Failed to create invitation: ' + retryError.message);
          }

          return {
            success: true,
            invitation_code: invitationCode,
            invitation_id: retryInvitation.id,
            message: `Invitation code generated: ${invitationCode}`
          };
        }

        throw new Error('Failed to create invitation: ' + error.message);
      }

      console.log('✅ Invitation created successfully:', invitationCode);

      return {
        success: true,
        invitation_code: invitationCode,
        invitation_id: newInvitation.id,
        message: `Invitation code generated: ${invitationCode}`
      };

    } catch (error) {
      console.error('Error creating invitation:', error);
      throw error;
    }
  }

  /**
   * Accept invitation by code directly through Supabase
   */
  async acceptInvitationByCode(code, userId) {
    try {
      console.log('🎯 Accepting invitation with code:', code);

      const normalizedCode = code.toUpperCase().trim();

      // Find invitation by code (try both fields for compatibility)
      let { data: invitation, error } = await supabase
        .from('agency_invitations')
        .select('*')
        .eq('invitation_code', normalizedCode)
        .eq('status', 'pending')
        .single();

      if (!invitation || error) {
        // Try invitation_token field as fallback
        const tokenResult = await supabase
          .from('agency_invitations')
          .select('*')
          .eq('invitation_token', normalizedCode)
          .eq('status', 'pending')
          .single();

        if (tokenResult.data) {
          invitation = tokenResult.data;
        } else {
          throw new Error('Invalid or expired invitation code');
        }
      }

      // Check expiration
      const expiresAt = new Date(invitation.expires_at);
      if (expiresAt < new Date()) {
        throw new Error('This invitation has expired');
      }

      // Check if user is already a member
      const { data: existingMember } = await supabase
        .from('agency_team_members')
        .select('id')
        .eq('agency_id', invitation.agency_id)
        .eq('user_id', userId)
        .single();

      if (existingMember) {
        throw new Error('You are already a member of this team');
      }

      // Add user to team
      const { data: newMember, error: memberError } = await supabase
        .from('agency_team_members')
        .insert({
          agency_id: invitation.agency_id,
          user_id: userId,
          role: invitation.role,
          status: 'active',
          invited_by: invitation.invited_by,
          project_access: invitation.project_access || [],
          client_access: invitation.client_access || []
        })
        .select()
        .single();

      if (memberError) {
        throw new Error('Failed to add you to the team: ' + memberError.message);
      }

      // Mark invitation as accepted
      await supabase
        .from('agency_invitations')
        .update({
          status: 'accepted',
          accepted_at: new Date().toISOString(),
          accepted_by: userId
        })
        .eq('id', invitation.id);

      console.log('✅ Successfully joined team!');

      return {
        success: true,
        agency_id: invitation.agency_id,
        role: invitation.role,
        message: 'Successfully joined the team!'
      };

    } catch (error) {
      console.error('Error accepting invitation:', error);
      throw error;
    }
  }

  /**
   * Get or create agency (existing functionality)
   */
  async getOrCreateUserAgency(userId) {
    try {
      console.log('🏫 Fetching agency for user:', userId);

      // Check if user owns an agency
      const { data: ownedAgency, error: ownedError } = await supabase
        .from('agencies')
        .select('*')
        .eq('owner_id', userId)
        .maybeSingle();

      if (ownedAgency && !ownedError) {
        return {
          ...ownedAgency,
          userRole: 'admin'
        };
      }

      // Check if user is a member of an agency
      const { data: membership } = await supabase
        .from('agency_team_members')
        .select(`
          agency_id,
          role,
          agencies (*)
        `)
        .eq('user_id', userId)
        .eq('status', 'active')
        .maybeSingle();

      if (membership?.agencies) {
        return {
          ...membership.agencies,
          userRole: membership.role
        };
      }

      // Create new agency if user has permission
      const { data: userProfile } = await supabase
        .from('user_profiles')
        .select('full_name, subscription_tier')
        .eq('id', userId)
        .single();

      const isAgencyTier = ['agency_standard', 'agency_premium', 'agency_unlimited']
        .includes(userProfile?.subscription_tier);

      if (!isAgencyTier) {
        throw new Error('Upgrade to an Agency plan to create a team');
      }

      const agencyName = userProfile?.full_name
        ? `${userProfile.full_name}'s Agency`
        : 'My Agency';

      const { data: newAgency, error: createError } = await supabase
        .from('agencies')
        .insert({
          name: agencyName,
          description: 'Main agency workspace',
          owner_id: userId
        })
        .select()
        .single();

      if (createError) {
        throw new Error('Failed to create agency: ' + createError.message);
      }

      // Add owner as admin member
      await supabase
        .from('agency_team_members')
        .insert({
          agency_id: newAgency.id,
          user_id: userId,
          role: 'admin',
          status: 'active',
          invited_by: userId
        });

      return {
        ...newAgency,
        userRole: 'admin'
      };

    } catch (error) {
      console.error('Error in getOrCreateUserAgency:', error);
      throw error;
    }
  }

  /**
   * Get team members (fixed to avoid relationship ambiguity)
   */
  async getTeamMembers(agencyId) {
    try {
      // First get team members
      const { data: members, error } = await supabase
        .from('agency_team_members')
        .select('*')
        .eq('agency_id', agencyId)
        .order('created_at', { ascending: false });

      if (error) {
        throw new Error('Failed to fetch team members: ' + error.message);
      }

      if (!members || members.length === 0) {
        return [];
      }

      // Get unique user IDs
      const userIds = [...new Set(members.map(m => m.user_id).filter(Boolean))];

      // Fetch user profiles separately to avoid relationship ambiguity
      const { data: profiles, error: profileError } = await supabase
        .from('user_profiles')
        .select('id, email, full_name, avatar_url')
        .in('id', userIds);

      if (profileError) {
        console.warn('Could not fetch user profiles:', profileError);
      }

      // Create a map for easy lookup
      const profileMap = {};
      if (profiles) {
        profiles.forEach(profile => {
          profileMap[profile.id] = profile;
        });
      }

      // Transform for frontend
      return members.map(member => {
        const profile = profileMap[member.user_id] || {};
        return {
          id: member.id,
          userId: member.user_id,
          name: profile.full_name || profile.email || 'Unknown',
          email: profile.email || '',
          avatar: profile.avatar_url || '',
          role: member.role,
          status: member.status,
          createdAt: member.created_at,
          lastActive: 'N/A',
          analysesThisMonth: 0,
          creditsUsed: 0,
          isClient: member.role === 'client',
          projectsAccess: member.project_access || [],
          clientAccess: member.client_access || []
        };
      });

    } catch (error) {
      console.error('Error fetching team members:', error);
      throw error;
    }
  }

  /**
   * Get team analytics
   */
  async getTeamAnalytics(agencyId) {
    try {
      // Get pending invitations separately to avoid confusion
      const { data: invitations } = await supabase
        .from('agency_invitations')
        .select('id')
        .eq('agency_id', agencyId)
        .eq('status', 'pending');

      const { data: members } = await supabase
        .from('agency_team_members')
        .select('id, role, status')
        .eq('agency_id', agencyId);

      const totalMembers = members?.length || 0;
      const activeMembers = members?.filter(m => m.status === 'active').length || 0;
      const pendingInvitations = invitations?.length || 0;

      return {
        totalMembers,
        activeMembers,
        pendingMembers: pendingInvitations,
        totalAnalyses: 0,
        totalCredits: 0,
        roleDistribution: {}
      };

    } catch (error) {
      console.error('Error fetching analytics:', error);
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

  /**
   * Remove team member
   */
  async removeTeamMember(memberId) {
    try {
      const { error } = await supabase
        .from('agency_team_members')
        .delete()
        .eq('id', memberId);

      if (error) {
        throw new Error('Failed to remove team member: ' + error.message);
      }

      toast.success('Team member removed');
      return true;

    } catch (error) {
      console.error('Error removing team member:', error);
      toast.error(error.message);
      throw error;
    }
  }

  /**
   * Update team member
   */
  async updateTeamMember(memberId, updates) {
    try {
      const { data, error } = await supabase
        .from('agency_team_members')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', memberId)
        .select()
        .single();

      if (error) {
        throw new Error('Failed to update team member: ' + error.message);
      }

      toast.success('Team member updated');
      return data;

    } catch (error) {
      console.error('Error updating team member:', error);
      toast.error(error.message);
      throw error;
    }
  }

  /**
   * Get agency projects - fetch projects from all agency members
   */
  async getAgencyProjects(agencyId) {
    try {
      console.log('📁 Fetching projects for agency:', agencyId);

      // First, get all team member user IDs
      const { data: members, error: membersError } = await supabase
        .from('agency_team_members')
        .select('user_id')
        .eq('agency_id', agencyId)
        .eq('status', 'active');

      if (membersError) {
        console.error('Error fetching team members:', membersError);
        return [];
      }

      if (!members || members.length === 0) {
        return [];
      }

      const userIds = members.map(m => m.user_id).filter(Boolean);

      if (userIds.length === 0) {
        return [];
      }

      // Fetch all projects from team members
      const { data: projects, error: projectsError } = await supabase
        .from('projects')
        .select('id, name, description, client_name, created_at, updated_at, user_id')
        .in('user_id', userIds)
        .order('updated_at', { ascending: false });

      if (projectsError) {
        console.error('Error fetching projects:', projectsError);
        return [];
      }

      console.log(`✅ Fetched ${projects?.length || 0} projects for agency`);
      return projects || [];

    } catch (error) {
      console.error('Error in getAgencyProjects:', error);
      return [];
    }
  }

  /**
   * Get agency clients - fetch unique client names from projects and client-role team members
   */
  async getAgencyClients(agencyId) {
    try {
      console.log('👥 Fetching clients for agency:', agencyId);

      // Get client-role team members
      const { data: clientMembers, error: clientError } = await supabase
        .from('agency_team_members')
        .select(`
          id,
          user_id,
          role
        `)
        .eq('agency_id', agencyId)
        .eq('role', 'client')
        .eq('status', 'active');

      if (clientError) {
        console.error('Error fetching client members:', clientError);
        return [];
      }

      // Get user profiles for clients
      const clients = [];

      if (clientMembers && clientMembers.length > 0) {
        const userIds = clientMembers.map(c => c.user_id).filter(Boolean);

        if (userIds.length > 0) {
          const { data: profiles } = await supabase
            .from('user_profiles')
            .select('id, email, full_name')
            .in('id', userIds);

          if (profiles) {
            profiles.forEach(profile => {
              clients.push({
                id: profile.id,
                name: profile.full_name || profile.email,
                email: profile.email,
                type: 'team_member'
              });
            });
          }
        }
      }

      // Also get unique client names from projects
      const { data: members } = await supabase
        .from('agency_team_members')
        .select('user_id')
        .eq('agency_id', agencyId)
        .eq('status', 'active');

      if (members && members.length > 0) {
        const userIds = members.map(m => m.user_id).filter(Boolean);

        if (userIds.length > 0) {
          const { data: projects } = await supabase
            .from('projects')
            .select('client_name')
            .in('user_id', userIds)
            .not('client_name', 'is', null);

          if (projects) {
            const uniqueClientNames = [...new Set(projects.map(p => p.client_name).filter(Boolean))];
            uniqueClientNames.forEach(clientName => {
              // Don't add duplicates
              if (!clients.find(c => c.name === clientName)) {
                clients.push({
                  id: `client_${clientName.toLowerCase().replace(/\s+/g, '_')}`,
                  name: clientName,
                  type: 'project_client'
                });
              }
            });
          }
        }
      }

      console.log(`✅ Fetched ${clients.length} clients for agency`);
      return clients;

    } catch (error) {
      console.error('Error in getAgencyClients:', error);
      return [];
    }
  }
}

// Flag to track if invitation_code column exists
TeamServiceFixed.prototype.supportsInvitationCodeField = true;

// Create and export singleton
const teamServiceFixed = new TeamServiceFixed();
export default teamServiceFixed;