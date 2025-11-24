-- ============================================================================
-- Team Invitation System Revamp: Email-Based to Link-Based
-- Migration 005: Shareable Invitation Links System
-- ============================================================================
-- This migration transforms the team invitation system from email-based
-- to a modern shareable link system. All SMTP dependencies are removed.
-- ============================================================================

-- ============================================================================
-- STEP 1: Clean Up Existing Email-Based Invitations
-- ============================================================================

-- Mark all pending email-based invitations as expired
-- These were created for the old system and should not be used
UPDATE team_invitations 
SET 
    status = 'expired',
    updated_at = NOW()
WHERE status = 'pending';

COMMENT ON COLUMN team_invitations.invitation_token IS 'Secure cryptographic token for shareable invitation links (single-use, time-limited)';

-- ============================================================================
-- STEP 2: Add Indexes for Performance
-- ============================================================================

-- Ensure unique constraint exists on invitation_token
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'team_invitations' 
        AND indexname = 'team_invitations_invitation_token_key'
    ) THEN
        ALTER TABLE team_invitations ADD CONSTRAINT team_invitations_invitation_token_key UNIQUE (invitation_token);
    END IF;
END $$;

-- Add index for faster token lookups (critical for invitation acceptance)
CREATE INDEX IF NOT EXISTS idx_team_invitations_token_status 
ON team_invitations(invitation_token, status) 
WHERE status IN ('pending', 'accepted');

-- Add index for expiration cleanup queries
CREATE INDEX IF NOT EXISTS idx_team_invitations_expires_at 
ON team_invitations(expires_at) 
WHERE status = 'pending';

-- ============================================================================
-- STEP 3: Function to Generate Secure Invitation Link
-- ============================================================================

CREATE OR REPLACE FUNCTION generate_team_invitation_link(
    p_agency_id UUID,
    p_email TEXT,
    p_role_id TEXT,
    p_invited_by UUID,
    p_message TEXT DEFAULT NULL
) RETURNS TABLE(
    invitation_id UUID,
    invitation_token TEXT,
    invitation_url TEXT,
    expires_at TIMESTAMPTZ
) AS $$
DECLARE
    v_invitation_id UUID;
    v_token TEXT;
    v_expires_at TIMESTAMPTZ;
    v_agency_name TEXT;
BEGIN
    -- Validate that the agency exists
    SELECT name INTO v_agency_name
    FROM agencies
    WHERE id = p_agency_id AND status = 'active';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agency not found or inactive';
    END IF;
    
    -- Validate that the inviter is an admin of this agency
    IF NOT EXISTS (
        SELECT 1 
        FROM agency_team_members tm
        WHERE tm.agency_id = p_agency_id 
            AND tm.user_id = p_invited_by
            AND tm.role = 'admin'
            AND tm.status = 'active'
    ) THEN
        RAISE EXCEPTION 'Only agency admins can send invitations';
    END IF;
    
    -- Check if user already exists and is a team member
    IF EXISTS (
        SELECT 1 
        FROM agency_team_members tm
        JOIN user_profiles up ON tm.user_id = up.id
        WHERE tm.agency_id = p_agency_id 
            AND up.email = LOWER(p_email)
            AND tm.status IN ('active', 'pending')
    ) THEN
        RAISE EXCEPTION 'User is already a member of this agency';
    END IF;
    
    -- Check if there's already a pending invitation for this email
    IF EXISTS (
        SELECT 1 
        FROM team_invitations
        WHERE agency_id = p_agency_id 
            AND LOWER(email) = LOWER(p_email)
            AND status = 'pending'
            AND expires_at > NOW()
    ) THEN
        RAISE EXCEPTION 'An active invitation already exists for this email';
    END IF;
    
    -- Generate secure cryptographic token (64 characters)
    v_token := encode(gen_random_bytes(32), 'hex');
    
    -- Set expiration to 7 days from now
    v_expires_at := NOW() + INTERVAL '7 days';
    
    -- Create invitation record
    INSERT INTO team_invitations (
        agency_id,
        email,
        role_id,
        invited_by,
        invitation_token,
        message,
        status,
        expires_at
    ) VALUES (
        p_agency_id,
        LOWER(p_email),
        p_role_id,
        p_invited_by,
        v_token,
        p_message,
        'pending',
        v_expires_at
    )
    RETURNING id INTO v_invitation_id;
    
    -- Return invitation details
    RETURN QUERY SELECT 
        v_invitation_id,
        v_token,
        '/invite/accept/' || v_token AS invitation_url,
        v_expires_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION generate_team_invitation_link IS 'Generates a secure, shareable invitation link with cryptographic token (replaces email-based invitations)';

-- ============================================================================
-- STEP 4: Function to Get Invitation Details by Token
-- ============================================================================

CREATE OR REPLACE FUNCTION get_invitation_details(
    p_token TEXT
) RETURNS TABLE(
    invitation_id UUID,
    agency_id UUID,
    agency_name TEXT,
    email TEXT,
    role_id TEXT,
    role_name TEXT,
    role_description TEXT,
    invited_by_name TEXT,
    invited_by_email TEXT,
    message TEXT,
    status TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    is_valid BOOLEAN,
    validation_message TEXT
) AS $$
DECLARE
    v_invitation team_invitations%ROWTYPE;
    v_is_valid BOOLEAN := FALSE;
    v_message TEXT := '';
BEGIN
    -- Fetch invitation
    SELECT * INTO v_invitation
    FROM team_invitations
    WHERE invitation_token = p_token;
    
    IF NOT FOUND THEN
        v_message := 'Invalid invitation link';
    ELSIF v_invitation.status = 'accepted' THEN
        v_message := 'This invitation has already been used';
    ELSIF v_invitation.status = 'cancelled' THEN
        v_message := 'This invitation has been cancelled by the administrator';
    ELSIF v_invitation.status = 'expired' OR v_invitation.expires_at < NOW() THEN
        v_message := 'This invitation has expired';
    ELSIF v_invitation.status = 'pending' THEN
        v_is_valid := TRUE;
        v_message := 'Valid invitation';
    ELSE
        v_message := 'Invalid invitation status';
    END IF;
    
    -- Return invitation details
    RETURN QUERY
    SELECT 
        v_invitation.id,
        v_invitation.agency_id,
        a.name AS agency_name,
        v_invitation.email,
        v_invitation.role_id,
        tr.name AS role_name,
        tr.description AS role_description,
        up.full_name AS invited_by_name,
        up.email AS invited_by_email,
        v_invitation.message,
        v_invitation.status,
        v_invitation.expires_at,
        v_invitation.created_at,
        v_is_valid,
        v_message
    FROM agencies a
    JOIN team_roles tr ON tr.id = v_invitation.role_id
    LEFT JOIN user_profiles up ON up.id = v_invitation.invited_by
    WHERE a.id = v_invitation.agency_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_invitation_details IS 'Retrieves invitation details by token for display on acceptance page (no authentication required)';

-- ============================================================================
-- STEP 5: Function to Accept Invitation
-- ============================================================================

CREATE OR REPLACE FUNCTION accept_team_invitation_link(
    p_invitation_token TEXT,
    p_user_id UUID
) RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    agency_id UUID,
    team_member_id UUID
) AS $$
DECLARE
    v_invitation team_invitations%ROWTYPE;
    v_user_email TEXT;
    v_team_member_id UUID;
BEGIN
    -- Get user email
    SELECT email INTO v_user_email
    FROM user_profiles
    WHERE id = p_user_id;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'User not found', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Fetch and lock invitation
    SELECT * INTO v_invitation
    FROM team_invitations
    WHERE invitation_token = p_invitation_token
    FOR UPDATE;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Invalid invitation link', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Validate invitation status
    IF v_invitation.status != 'pending' THEN
        RETURN QUERY SELECT FALSE, 'This invitation has already been used or cancelled', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Check expiration
    IF v_invitation.expires_at < NOW() THEN
        -- Mark as expired
        UPDATE team_invitations 
        SET status = 'expired', updated_at = NOW()
        WHERE id = v_invitation.id;
        
        RETURN QUERY SELECT FALSE, 'This invitation has expired', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Verify email matches (case-insensitive)
    IF LOWER(v_user_email) != LOWER(v_invitation.email) THEN
        RETURN QUERY SELECT FALSE, 'This invitation was sent to a different email address', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Check if user is already a team member
    IF EXISTS (
        SELECT 1 
        FROM agency_team_members
        WHERE agency_id = v_invitation.agency_id 
            AND user_id = p_user_id
            AND status IN ('active', 'pending')
    ) THEN
        RETURN QUERY SELECT FALSE, 'You are already a member of this team', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Add user to team
    INSERT INTO agency_team_members (
        agency_id,
        user_id,
        role,
        status,
        invited_by,
        created_at
    ) VALUES (
        v_invitation.agency_id,
        p_user_id,
        v_invitation.role_id,
        'active',
        v_invitation.invited_by,
        NOW()
    )
    RETURNING id INTO v_team_member_id;
    
    -- Mark invitation as accepted
    UPDATE team_invitations
    SET 
        status = 'accepted',
        accepted_at = NOW(),
        accepted_by = p_user_id,
        updated_at = NOW()
    WHERE id = v_invitation.id;
    
    -- Return success
    RETURN QUERY SELECT 
        TRUE, 
        'Successfully joined the team', 
        v_invitation.agency_id,
        v_team_member_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION accept_team_invitation_link IS 'Accepts a team invitation via shareable link, adds user to team, and marks invitation as used';

-- ============================================================================
-- STEP 6: Function to Revoke/Cancel Invitation
-- ============================================================================

CREATE OR REPLACE FUNCTION revoke_team_invitation(
    p_invitation_id UUID,
    p_revoker_user_id UUID
) RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_invitation team_invitations%ROWTYPE;
BEGIN
    -- Fetch invitation
    SELECT * INTO v_invitation
    FROM team_invitations
    WHERE id = p_invitation_id;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Invitation not found';
        RETURN;
    END IF;
    
    -- Verify revoker is an admin of the agency
    IF NOT EXISTS (
        SELECT 1 
        FROM agency_team_members tm
        WHERE tm.agency_id = v_invitation.agency_id 
            AND tm.user_id = p_revoker_user_id
            AND tm.role = 'admin'
            AND tm.status = 'active'
    ) THEN
        RETURN QUERY SELECT FALSE, 'Only agency admins can revoke invitations';
        RETURN;
    END IF;
    
    -- Check if invitation can be revoked
    IF v_invitation.status = 'accepted' THEN
        RETURN QUERY SELECT FALSE, 'Cannot revoke an invitation that has already been accepted';
        RETURN;
    END IF;
    
    IF v_invitation.status = 'cancelled' THEN
        RETURN QUERY SELECT FALSE, 'This invitation has already been cancelled';
        RETURN;
    END IF;
    
    -- Cancel the invitation
    UPDATE team_invitations
    SET 
        status = 'cancelled',
        updated_at = NOW()
    WHERE id = p_invitation_id;
    
    RETURN QUERY SELECT TRUE, 'Invitation successfully revoked';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION revoke_team_invitation IS 'Cancels a pending invitation, preventing it from being accepted (admin only)';

-- ============================================================================
-- STEP 7: Function to Get All Invitations for an Agency
-- ============================================================================

CREATE OR REPLACE FUNCTION get_agency_invitations(
    p_agency_id UUID,
    p_user_id UUID
) RETURNS TABLE(
    invitation_id UUID,
    email TEXT,
    role_id TEXT,
    role_name TEXT,
    status TEXT,
    invitation_token TEXT,
    invitation_url TEXT,
    message TEXT,
    invited_by_name TEXT,
    invited_by_email TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    is_expired BOOLEAN,
    days_until_expiry INTEGER
) AS $$
BEGIN
    -- Verify user has access to this agency
    IF NOT EXISTS (
        SELECT 1 
        FROM agency_team_members tm
        WHERE tm.agency_id = p_agency_id 
            AND tm.user_id = p_user_id
            AND tm.role IN ('admin', 'editor')
            AND tm.status = 'active'
    ) THEN
        RAISE EXCEPTION 'Access denied: You do not have permission to view invitations';
    END IF;
    
    RETURN QUERY
    SELECT 
        ti.id,
        ti.email,
        ti.role_id,
        tr.name AS role_name,
        ti.status,
        ti.invitation_token,
        '/invite/accept/' || ti.invitation_token AS invitation_url,
        ti.message,
        up.full_name AS invited_by_name,
        up.email AS invited_by_email,
        ti.expires_at,
        ti.created_at,
        ti.accepted_at,
        (ti.expires_at < NOW()) AS is_expired,
        GREATEST(0, EXTRACT(DAYS FROM (ti.expires_at - NOW()))::INTEGER) AS days_until_expiry
    FROM team_invitations ti
    JOIN team_roles tr ON ti.role_id = tr.id
    LEFT JOIN user_profiles up ON ti.invited_by = up.id
    WHERE ti.agency_id = p_agency_id
    ORDER BY 
        CASE ti.status 
            WHEN 'pending' THEN 1 
            WHEN 'accepted' THEN 2 
            WHEN 'expired' THEN 3 
            WHEN 'cancelled' THEN 4 
        END,
        ti.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_agency_invitations IS 'Retrieves all invitations for an agency (admin/editor only)';

-- ============================================================================
-- STEP 8: Scheduled Job to Auto-Expire Old Invitations
-- ============================================================================

CREATE OR REPLACE FUNCTION expire_old_invitations()
RETURNS INTEGER AS $$
DECLARE
    v_expired_count INTEGER;
BEGIN
    UPDATE team_invitations
    SET 
        status = 'expired',
        updated_at = NOW()
    WHERE status = 'pending' 
        AND expires_at < NOW();
    
    GET DIAGNOSTICS v_expired_count = ROW_COUNT;
    
    RETURN v_expired_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION expire_old_invitations IS 'Maintenance function to automatically expire old pending invitations (run via cron or scheduled job)';

-- ============================================================================
-- STEP 9: Grant Permissions
-- ============================================================================

GRANT EXECUTE ON FUNCTION generate_team_invitation_link(UUID, TEXT, TEXT, UUID, TEXT) TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION get_invitation_details(TEXT) TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION accept_team_invitation_link(TEXT, UUID) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION revoke_team_invitation(UUID, UUID) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_agency_invitations(UUID, UUID) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION expire_old_invitations() TO service_role;

-- ============================================================================
-- STEP 10: Verification Queries
-- ============================================================================

-- Verify indexes were created
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'team_invitations'
    AND indexname LIKE '%token%'
ORDER BY indexname;

-- Count invitations by status
SELECT 
    status,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE expires_at < NOW()) as expired_count
FROM team_invitations
GROUP BY status
ORDER BY status;

-- Summary
SELECT 
    '✅ Team Invitation Link System Migration Complete!' as status,
    'All email dependencies removed. Use generate_team_invitation_link() to create shareable links.' as details;
