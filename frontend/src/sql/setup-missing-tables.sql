-- This SQL should be run in your Supabase SQL Editor to ensure all required tables exist
-- Run this if you're getting 401/404 errors when trying to access projects

-- Check if the new tables exist, if not, create them
-- (Based on shared-workflow-schema.sql)

-- Ad Copy Projects - Main projects table
CREATE TABLE IF NOT EXISTS ad_copy_projects (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL DEFAULT 'Untitled Project',
    description TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'analyzing', 'completed', 'archived')),
    
    -- Core ad copy data (centralized)
    headline TEXT NOT NULL,
    body_text TEXT NOT NULL,
    cta TEXT NOT NULL,
    platform TEXT NOT NULL,
    industry TEXT,
    target_audience TEXT,
    
    -- Project metadata
    tags TEXT[], -- For organization/search
    is_template BOOLEAN DEFAULT false,
    parent_project_id UUID REFERENCES ad_copy_projects(id), -- For versioning/variations
    
    -- Pipeline configuration
    enabled_tools TEXT[] DEFAULT ARRAY['compliance', 'legal', 'brand_voice', 'psychology'], -- Tools to run
    pipeline_order TEXT[] DEFAULT ARRAY['compliance', 'legal', 'brand_voice', 'psychology'],
    auto_chain_analysis BOOLEAN DEFAULT true, -- Whether to run tools sequentially
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    
    PRIMARY KEY (id)
);

-- Tool Analysis Results - Store results from each tool
CREATE TABLE IF NOT EXISTS tool_analysis_results (
    id UUID DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES ad_copy_projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Tool identification
    tool_name TEXT NOT NULL CHECK (tool_name IN (
        'compliance', 'legal', 'brand_voice', 'psychology', 
        'roi_generator', 'ab_test', 'industry_optimizer', 'performance_forensics'
    )),
    tool_version TEXT DEFAULT '1.0',
    
    -- Analysis metadata
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,
    
    -- Results data (flexible JSON storage)
    result_data JSONB NOT NULL DEFAULT '{}',
    error_message TEXT,
    
    -- Chain analysis metadata
    chain_position INTEGER, -- Order in the pipeline
    depends_on_tool TEXT, -- Which tool should complete first
    
    -- Scores and metrics (for quick querying without JSON parsing)
    overall_score DECIMAL(5,2),
    risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high')),
    confidence_score DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id),
    UNIQUE(project_id, tool_name) -- One result per tool per project (latest)
);

-- Analysis Pipeline Runs - Track execution of tool chains
CREATE TABLE IF NOT EXISTS analysis_pipeline_runs (
    id UUID DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES ad_copy_projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Pipeline execution metadata
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    tools_requested TEXT[] NOT NULL, -- Which tools were requested
    tools_completed TEXT[] DEFAULT ARRAY[]::TEXT[], -- Which tools have completed
    current_tool TEXT, -- Currently executing tool
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_runtime_ms INTEGER,
    
    -- Results summary
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    overall_status TEXT,
    summary_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- Project Collaborators (for team features)
CREATE TABLE IF NOT EXISTS project_collaborators (
    id UUID DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES ad_copy_projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    invited_by UUID NOT NULL REFERENCES user_profiles(id),
    
    role TEXT DEFAULT 'viewer' CHECK (role IN ('owner', 'editor', 'viewer')),
    permissions TEXT[] DEFAULT ARRAY['read'], -- granular permissions
    
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accepted_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
    
    PRIMARY KEY (id),
    UNIQUE(project_id, user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ad_copy_projects_user_id ON ad_copy_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_copy_projects_status ON ad_copy_projects(status);
CREATE INDEX IF NOT EXISTS idx_ad_copy_projects_created_at ON ad_copy_projects(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ad_copy_projects_tags ON ad_copy_projects USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_tool_results_project_id ON tool_analysis_results(project_id);
CREATE INDEX IF NOT EXISTS idx_tool_results_tool_name ON tool_analysis_results(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_results_status ON tool_analysis_results(status);
CREATE INDEX IF NOT EXISTS idx_tool_results_user_tool ON tool_analysis_results(user_id, tool_name);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_project_id ON analysis_pipeline_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_user_id ON analysis_pipeline_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON analysis_pipeline_runs(status);

CREATE INDEX IF NOT EXISTS idx_collaborators_project_id ON project_collaborators(project_id);
CREATE INDEX IF NOT EXISTS idx_collaborators_user_id ON project_collaborators(user_id);

-- Enable RLS on new tables
ALTER TABLE ad_copy_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_collaborators ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Ad Copy Projects
DROP POLICY IF EXISTS "Users can view own projects and shared projects" ON ad_copy_projects;
CREATE POLICY "Users can view own projects and shared projects" ON ad_copy_projects
    FOR SELECT USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM project_collaborators 
            WHERE project_id = ad_copy_projects.id 
            AND user_id = auth.uid() 
            AND status = 'accepted'
        )
    );

DROP POLICY IF EXISTS "Users can create own projects" ON ad_copy_projects;
CREATE POLICY "Users can create own projects" ON ad_copy_projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own projects or shared projects with edit permission" ON ad_copy_projects;
CREATE POLICY "Users can update own projects or shared projects with edit permission" ON ad_copy_projects
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM project_collaborators 
            WHERE project_id = ad_copy_projects.id 
            AND user_id = auth.uid() 
            AND status = 'accepted'
            AND role IN ('owner', 'editor')
        )
    );

DROP POLICY IF EXISTS "Users can delete own projects" ON ad_copy_projects;
CREATE POLICY "Users can delete own projects" ON ad_copy_projects
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for Tool Results
DROP POLICY IF EXISTS "Users can view results for accessible projects" ON tool_analysis_results;
CREATE POLICY "Users can view results for accessible projects" ON tool_analysis_results
    FOR SELECT USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM ad_copy_projects acp
            JOIN project_collaborators pc ON acp.id = pc.project_id
            WHERE acp.id = tool_analysis_results.project_id 
            AND pc.user_id = auth.uid() 
            AND pc.status = 'accepted'
        )
    );

DROP POLICY IF EXISTS "Users can create results for accessible projects" ON tool_analysis_results;
CREATE POLICY "Users can create results for accessible projects" ON tool_analysis_results
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND
        EXISTS (
            SELECT 1 FROM ad_copy_projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can update results for accessible projects" ON tool_analysis_results;
CREATE POLICY "Users can update results for accessible projects" ON tool_analysis_results
    FOR UPDATE USING (
        auth.uid() = user_id AND
        EXISTS (
            SELECT 1 FROM ad_copy_projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

-- RLS Policies for Pipeline Runs
DROP POLICY IF EXISTS "Users can view pipeline runs for accessible projects" ON analysis_pipeline_runs;
CREATE POLICY "Users can view pipeline runs for accessible projects" ON analysis_pipeline_runs
    FOR SELECT USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM ad_copy_projects acp
            JOIN project_collaborators pc ON acp.id = pc.project_id
            WHERE acp.id = analysis_pipeline_runs.project_id 
            AND pc.user_id = auth.uid() 
            AND pc.status = 'accepted'
        )
    );

DROP POLICY IF EXISTS "Users can create pipeline runs for accessible projects" ON analysis_pipeline_runs;
CREATE POLICY "Users can create pipeline runs for accessible projects" ON analysis_pipeline_runs
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND
        EXISTS (
            SELECT 1 FROM ad_copy_projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can update pipeline runs for accessible projects" ON analysis_pipeline_runs;
CREATE POLICY "Users can update pipeline runs for accessible projects" ON analysis_pipeline_runs
    FOR UPDATE USING (
        auth.uid() = user_id AND
        EXISTS (
            SELECT 1 FROM ad_copy_projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

-- RLS Policies for Collaborators
DROP POLICY IF EXISTS "Users can view collaborations" ON project_collaborators;
CREATE POLICY "Users can view collaborations" ON project_collaborators
    FOR SELECT USING (
        auth.uid() = user_id OR 
        auth.uid() = invited_by OR
        EXISTS (
            SELECT 1 FROM ad_copy_projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can invite collaborators to own projects" ON project_collaborators;
CREATE POLICY "Users can invite collaborators to own projects" ON project_collaborators
    FOR INSERT WITH CHECK (
        auth.uid() = invited_by AND
        EXISTS (
            SELECT 1 FROM ad_copy_projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

-- Insert some sample data for testing (optional)
-- You can uncomment this if you want some test projects

/*
INSERT INTO ad_copy_projects (
    user_id, 
    project_name, 
    description, 
    headline, 
    body_text, 
    cta, 
    platform, 
    industry, 
    target_audience,
    status
) 
SELECT 
    id as user_id,
    'Sample Holiday Campaign' as project_name,
    'Test project for holiday promotions' as description,
    'Get 50% Off This Holiday Season!' as headline,
    'Limited time offer on all our premium products. Don''t miss out!' as body_text,
    'Shop Now' as cta,
    'Facebook' as platform,
    'E-commerce' as industry,
    'Holiday shoppers aged 25-45' as target_audience,
    'draft' as status
FROM user_profiles 
WHERE NOT EXISTS (
    SELECT 1 FROM ad_copy_projects 
    WHERE user_id = user_profiles.id
)
LIMIT 1;
*/

-- Success message
SELECT 'Tables and policies created successfully!' as message;
