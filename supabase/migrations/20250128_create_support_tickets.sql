-- Create support_tickets table
CREATE TABLE IF NOT EXISTS public.support_tickets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticket_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('normal', 'urgent')),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'closed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX idx_support_tickets_user_id ON public.support_tickets(user_id);

-- Create index on ticket_id for faster lookups
CREATE INDEX idx_support_tickets_ticket_id ON public.support_tickets(ticket_id);

-- Create index on status for filtering
CREATE INDEX idx_support_tickets_status ON public.support_tickets(status);

-- Create index on created_at for sorting
CREATE INDEX idx_support_tickets_created_at ON public.support_tickets(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own tickets
CREATE POLICY "Users can view own tickets"
    ON public.support_tickets
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own tickets
CREATE POLICY "Users can create tickets"
    ON public.support_tickets
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own tickets (for status changes)
CREATE POLICY "Users can update own tickets"
    ON public.support_tickets
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_support_ticket_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_support_tickets_updated_at
    BEFORE UPDATE ON public.support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION public.update_support_ticket_updated_at();

-- Function to generate ticket ID
CREATE OR REPLACE FUNCTION public.generate_ticket_id()
RETURNS TEXT AS $$
DECLARE
    new_ticket_id TEXT;
    counter INTEGER := 0;
BEGIN
    LOOP
        -- Generate random 5-digit number
        new_ticket_id := 'TICKET-' || LPAD(FLOOR(RANDOM() * 100000)::TEXT, 5, '0');
        
        -- Check if it exists
        IF NOT EXISTS (SELECT 1 FROM public.support_tickets WHERE ticket_id = new_ticket_id) THEN
            RETURN new_ticket_id;
        END IF;
        
        -- Prevent infinite loop
        counter := counter + 1;
        IF counter > 100 THEN
            RAISE EXCEPTION 'Could not generate unique ticket ID after 100 attempts';
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Add comment to table
COMMENT ON TABLE public.support_tickets IS 'Stores customer support tickets with email notifications';
