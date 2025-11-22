-- Add invitation_code column to agency_invitations table if it doesn't exist
-- This is for the code-based invitation system

-- Check if column exists and add if not
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='agency_invitations'
        AND column_name='invitation_code'
    ) THEN
        ALTER TABLE agency_invitations
        ADD COLUMN invitation_code VARCHAR(10);

        -- Create index for faster lookups
        CREATE INDEX idx_agency_invitations_code
        ON agency_invitations(invitation_code)
        WHERE status = 'pending';
    END IF;
END $$;

-- Update any existing pending invitations with a code if they don't have one
UPDATE agency_invitations
SET invitation_code = UPPER(SUBSTRING(invitation_token FROM 1 FOR 6))
WHERE invitation_code IS NULL
AND status = 'pending';