-- =============================================================================
-- OSINT Intelligence System - Supabase Schema
-- HealthTech Domain - Complete Database Structure
-- =============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: research_items
-- Stores all research inputs and intelligence gathered
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS research_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Source tracking
    source TEXT NOT NULL,  -- 'pubmed', 'clinicaltrials', 'fda', 'manual', 'telegram'
    source_id TEXT,        -- Original ID from source
    source_url TEXT,

    -- Content
    topic TEXT NOT NULL,
    insight TEXT,
    raw_data JSONB,

    -- Quality scores (0-1 scale)
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    novelty FLOAT DEFAULT 0.5 CHECK (novelty >= 0 AND novelty <= 1),
    signal_strength FLOAT DEFAULT 0.5 CHECK (signal_strength >= 0 AND signal_strength <= 1),
    input_quality_score FLOAT GENERATED ALWAYS AS (
        (0.4 * confidence) + (0.4 * signal_strength) + (0.2 * novelty)
    ) STORED,

    -- Classification
    insight_type TEXT DEFAULT 'general',  -- 'trend', 'competitor', 'regulatory', 'opportunity', 'risk'
    actionable BOOLEAN DEFAULT false,
    priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'

    -- HealthTech specific
    domain TEXT DEFAULT 'healthtech',
    healthtech_category TEXT,  -- 'biotech', 'medtech', 'digital_health', 'pharma', etc.
    compliance_tags TEXT[],    -- ['HIPAA', 'FDA', 'GDPR']

    -- Metadata
    sources JSONB,
    tags TEXT[],
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Indexes for research_items
CREATE INDEX idx_research_source ON research_items(source);
CREATE INDEX idx_research_topic ON research_items USING gin(topic gin_trgm_ops);
CREATE INDEX idx_research_insight_type ON research_items(insight_type);
CREATE INDEX idx_research_domain ON research_items(domain);
CREATE INDEX idx_research_actionable ON research_items(actionable);
CREATE INDEX idx_research_created_at ON research_items(created_at DESC);
CREATE INDEX idx_research_iqs ON research_items(input_quality_score DESC);

-- -----------------------------------------------------------------------------
-- Table: social_posts
-- Stores all social media signals and engagement data
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Platform identification
    platform TEXT NOT NULL,  -- 'twitter', 'linkedin', 'reddit', 'hackernews'
    post_id TEXT NOT NULL,
    post_url TEXT,

    -- Author info
    author TEXT NOT NULL,
    author_id TEXT,
    followers INT DEFAULT 0,
    verified BOOLEAN DEFAULT false,
    author_bio TEXT,

    -- Content
    content TEXT,
    content_type TEXT DEFAULT 'post',  -- 'post', 'thread', 'comment', 'article'
    hashtags TEXT[],
    mentions TEXT[],
    urls TEXT[],

    -- Raw engagement metrics
    likes INT DEFAULT 0,
    shares INT DEFAULT 0,
    comments INT DEFAULT 0,
    views INT DEFAULT 0,
    engagement INT GENERATED ALWAYS AS (likes + (shares * 2) + (comments * 3)) STORED,

    -- Calculated scores (0-1 scale)
    velocity FLOAT DEFAULT 0 CHECK (velocity >= 0 AND velocity <= 1),
    trust_score FLOAT DEFAULT 0 CHECK (trust_score >= 0 AND trust_score <= 1),
    final_score FLOAT DEFAULT 0 CHECK (final_score >= 0 AND final_score <= 1),

    -- Outlier detection
    is_outlier BOOLEAN DEFAULT false,
    z_score FLOAT,
    percentile INT CHECK (percentile >= 0 AND percentile <= 100),

    -- Classification
    sentiment TEXT,  -- 'positive', 'negative', 'neutral'
    topic_relevance FLOAT,

    -- HealthTech specific
    domain TEXT DEFAULT 'healthtech',
    healthtech_keywords TEXT[],
    mentioned_companies TEXT[],
    mentioned_products TEXT[],

    -- Metadata
    metadata JSONB,

    -- Timestamps
    post_created_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(platform, post_id)
);

-- Indexes for social_posts
CREATE INDEX idx_social_platform ON social_posts(platform);
CREATE INDEX idx_social_author ON social_posts(author);
CREATE INDEX idx_social_created_at ON social_posts(created_at DESC);
CREATE INDEX idx_social_final_score ON social_posts(final_score DESC);
CREATE INDEX idx_social_is_outlier ON social_posts(is_outlier);
CREATE INDEX idx_social_domain ON social_posts(domain);
CREATE INDEX idx_social_post_created ON social_posts(post_created_at DESC);
CREATE INDEX idx_social_engagement ON social_posts(engagement DESC);
CREATE INDEX idx_social_trust ON social_posts(trust_score DESC);

-- Full-text search index
CREATE INDEX idx_social_content_search ON social_posts USING gin(to_tsvector('english', content));

-- -----------------------------------------------------------------------------
-- Table: content_outputs
-- Tracks content published and its performance
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS content_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identification
    content_id TEXT UNIQUE NOT NULL,
    research_id UUID REFERENCES research_items(id),

    -- Content details
    platform TEXT NOT NULL,
    content_type TEXT DEFAULT 'post',
    content_url TEXT,
    title TEXT,
    body TEXT,

    -- Input metrics (from research)
    input_quality_score FLOAT DEFAULT 0.5,
    research_confidence FLOAT,
    research_novelty FLOAT,

    -- Output metrics (engagement)
    engagement_rate FLOAT DEFAULT 0,
    velocity FLOAT DEFAULT 0,
    trust_engagement FLOAT DEFAULT 0,
    output_performance_score FLOAT GENERATED ALWAYS AS (
        (0.5 * engagement_rate) + (0.3 * velocity) + (0.2 * trust_engagement)
    ) STORED,

    -- Efficiency (ROI of content)
    efficiency FLOAT,  -- OPS / IQS
    leverage_level TEXT,  -- 'low', 'medium', 'high'

    -- Raw metrics
    impressions INT DEFAULT 0,
    clicks INT DEFAULT 0,
    likes INT DEFAULT 0,
    shares INT DEFAULT 0,
    comments INT DEFAULT 0,
    saves INT DEFAULT 0,

    -- Tracking
    tracking_status TEXT DEFAULT 'pending',  -- 'pending', 'active', 'completed', 'failed'
    tracking_schedule JSONB,
    tracking_history JSONB,

    -- HealthTech specific
    domain TEXT DEFAULT 'healthtech',
    research_topic TEXT,
    target_audience TEXT,

    -- Timestamps
    published_at TIMESTAMPTZ,
    tracking_started_at TIMESTAMPTZ,
    tracking_completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for content_outputs
CREATE INDEX idx_content_platform ON content_outputs(platform);
CREATE INDEX idx_content_research_id ON content_outputs(research_id);
CREATE INDEX idx_content_published ON content_outputs(published_at DESC);
CREATE INDEX idx_content_efficiency ON content_outputs(efficiency DESC);
CREATE INDEX idx_content_tracking ON content_outputs(tracking_status);
CREATE INDEX idx_content_ops ON content_outputs(output_performance_score DESC);

-- -----------------------------------------------------------------------------
-- Table: rankings
-- Stores historical ranking data for authors/influencers
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rankings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Author identification
    author TEXT NOT NULL,
    platform TEXT NOT NULL,

    -- Ranking data
    rank INT NOT NULL,
    previous_rank INT,
    movement INT,  -- positive = moved up
    movement_type TEXT,  -- 'up', 'down', 'stable', 'new'

    -- Scores
    ranking_score FLOAT NOT NULL,
    avg_post_score FLOAT,
    avg_trust_score FLOAT,
    avg_velocity FLOAT,
    consistency_score FLOAT,

    -- Activity metrics
    total_posts INT DEFAULT 0,
    total_engagement INT DEFAULT 0,
    outlier_count INT DEFAULT 0,
    outlier_ratio FLOAT,

    -- Period tracking
    period_type TEXT DEFAULT 'weekly',  -- 'daily', 'weekly', 'monthly', 'all_time'
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,

    -- Domain
    domain TEXT DEFAULT 'healthtech',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(author, platform, period_type, period_end)
);

-- Indexes for rankings
CREATE INDEX idx_rankings_author ON rankings(author);
CREATE INDEX idx_rankings_platform ON rankings(platform);
CREATE INDEX idx_rankings_rank ON rankings(rank);
CREATE INDEX idx_rankings_score ON rankings(ranking_score DESC);
CREATE INDEX idx_rankings_period ON rankings(period_type, period_end DESC);
CREATE INDEX idx_rankings_domain ON rankings(domain);

-- -----------------------------------------------------------------------------
-- Table: learning_iterations
-- Stores the learning loop data and weight adjustments
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_iterations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Iteration tracking
    iteration_number SERIAL,
    iteration_date TIMESTAMPTZ DEFAULT NOW(),

    -- Updated weights (JSON for flexibility)
    platform_weights JSONB DEFAULT '{}',
    topic_weights JSONB DEFAULT '{}',
    timing_weights JSONB DEFAULT '{}',

    -- Statistics from this iteration
    statistics JSONB DEFAULT '{}',

    -- Generated insights
    insights TEXT[],
    recommendations JSONB,

    -- Performance metrics
    mean_efficiency FLOAT,
    outlier_count INT,
    total_analyzed INT,
    improvement_rate FLOAT,  -- compared to previous iteration

    -- Domain
    domain TEXT DEFAULT 'healthtech',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for learning_iterations
CREATE INDEX idx_learning_date ON learning_iterations(iteration_date DESC);
CREATE INDEX idx_learning_domain ON learning_iterations(domain);

-- -----------------------------------------------------------------------------
-- Table: kol_profiles
-- Detailed profiles of Key Opinion Leaders
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kol_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identification
    username TEXT NOT NULL,
    platform TEXT NOT NULL,
    profile_url TEXT,

    -- Profile data
    display_name TEXT,
    bio TEXT,
    location TEXT,
    verified BOOLEAN DEFAULT false,

    -- Metrics
    followers INT DEFAULT 0,
    following INT DEFAULT 0,
    total_posts INT DEFAULT 0,

    -- Calculated scores
    influence_score FLOAT,
    engagement_rate FLOAT,
    trust_score FLOAT,
    consistency_score FLOAT,

    -- Classification
    expertise_areas TEXT[],
    healthtech_focus TEXT[],  -- ['biotech', 'digital_health', 'FDA_policy']

    -- Tracking
    first_seen_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ,
    tracking_enabled BOOLEAN DEFAULT true,

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(username, platform)
);

-- Indexes for kol_profiles
CREATE INDEX idx_kol_platform ON kol_profiles(platform);
CREATE INDEX idx_kol_influence ON kol_profiles(influence_score DESC);
CREATE INDEX idx_kol_tracking ON kol_profiles(tracking_enabled);

-- -----------------------------------------------------------------------------
-- Table: alerts
-- Stores generated alerts from OSINT monitoring
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Alert identification
    alert_type TEXT NOT NULL,  -- 'competitor', 'regulatory', 'trend', 'mention', 'opportunity'
    severity TEXT DEFAULT 'info',  -- 'info', 'low', 'medium', 'high', 'critical'

    -- Content
    title TEXT NOT NULL,
    description TEXT,
    source_type TEXT,  -- 'social', 'research', 'news'
    source_id UUID,
    source_url TEXT,

    -- Classification
    keywords TEXT[],
    entities TEXT[],  -- Companies, products, people mentioned

    -- Status
    status TEXT DEFAULT 'new',  -- 'new', 'acknowledged', 'investigating', 'resolved', 'dismissed'
    assigned_to TEXT,

    -- Domain
    domain TEXT DEFAULT 'healthtech',

    -- Timestamps
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for alerts
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_triggered ON alerts(triggered_at DESC);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- View: Weekly dashboard summary
CREATE OR REPLACE VIEW v_weekly_dashboard AS
SELECT
    COUNT(DISTINCT sp.id) as total_signals,
    COUNT(DISTINCT sp.id) FILTER (WHERE sp.is_outlier = true) as outlier_signals,
    COUNT(DISTINCT sp.author) as unique_authors,
    AVG(sp.final_score) as avg_signal_score,
    AVG(sp.trust_score) as avg_trust_score,
    COUNT(DISTINCT ri.id) as research_items,
    AVG(ri.input_quality_score) as avg_research_quality,
    COUNT(DISTINCT co.id) as content_published,
    AVG(co.efficiency) as avg_efficiency
FROM social_posts sp
CROSS JOIN LATERAL (
    SELECT * FROM research_items ri
    WHERE ri.created_at > NOW() - INTERVAL '7 days'
) ri
CROSS JOIN LATERAL (
    SELECT * FROM content_outputs co
    WHERE co.published_at > NOW() - INTERVAL '7 days'
) co
WHERE sp.created_at > NOW() - INTERVAL '7 days';

-- View: Top performers this week
CREATE OR REPLACE VIEW v_top_performers_weekly AS
SELECT
    author,
    platform,
    COUNT(*) as post_count,
    SUM(engagement) as total_engagement,
    AVG(final_score) as avg_score,
    AVG(trust_score) as avg_trust,
    COUNT(*) FILTER (WHERE is_outlier = true) as outlier_count,
    MAX(followers) as max_followers
FROM social_posts
WHERE created_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech'
GROUP BY author, platform
ORDER BY avg_score DESC
LIMIT 50;

-- View: Content efficiency leaderboard
CREATE OR REPLACE VIEW v_content_efficiency AS
SELECT
    co.id,
    co.platform,
    co.title,
    co.input_quality_score,
    co.output_performance_score,
    co.efficiency,
    co.leverage_level,
    ri.topic as research_topic,
    ri.insight_type,
    co.published_at
FROM content_outputs co
LEFT JOIN research_items ri ON co.research_id = ri.id
WHERE co.tracking_status = 'completed'
ORDER BY co.efficiency DESC;

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function: Calculate and update efficiency score
CREATE OR REPLACE FUNCTION update_content_efficiency()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.input_quality_score > 0 THEN
        NEW.efficiency := NEW.output_performance_score / NEW.input_quality_score;
        NEW.leverage_level := CASE
            WHEN NEW.efficiency > 1.5 THEN 'high'
            WHEN NEW.efficiency > 0.75 THEN 'medium'
            ELSE 'low'
        END;
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for efficiency calculation
CREATE TRIGGER tr_update_content_efficiency
    BEFORE INSERT OR UPDATE OF output_performance_score, input_quality_score
    ON content_outputs
    FOR EACH ROW
    EXECUTE FUNCTION update_content_efficiency();

-- Function: Auto-detect outliers in social posts
CREATE OR REPLACE FUNCTION detect_social_outliers(threshold_multiplier FLOAT DEFAULT 1.5)
RETURNS TABLE (
    post_id UUID,
    z_score FLOAT,
    is_outlier BOOLEAN
) AS $$
DECLARE
    mean_score FLOAT;
    std_dev FLOAT;
BEGIN
    -- Calculate statistics for recent posts (7 days)
    SELECT
        AVG(final_score),
        STDDEV(final_score)
    INTO mean_score, std_dev
    FROM social_posts
    WHERE created_at > NOW() - INTERVAL '7 days';

    -- Return outlier classification
    RETURN QUERY
    SELECT
        sp.id,
        CASE WHEN std_dev > 0 THEN (sp.final_score - mean_score) / std_dev ELSE 0 END,
        CASE WHEN std_dev > 0 THEN sp.final_score > (mean_score + (threshold_multiplier * std_dev)) ELSE false END
    FROM social_posts sp
    WHERE sp.created_at > NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Function: Get ranking movement
CREATE OR REPLACE FUNCTION get_ranking_movement(
    p_author TEXT,
    p_platform TEXT,
    p_period_type TEXT DEFAULT 'weekly'
)
RETURNS TABLE (
    current_rank INT,
    previous_rank INT,
    movement INT,
    movement_type TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH recent_rankings AS (
        SELECT
            r.rank,
            r.period_end,
            ROW_NUMBER() OVER (ORDER BY r.period_end DESC) as rn
        FROM rankings r
        WHERE r.author = p_author
          AND r.platform = p_platform
          AND r.period_type = p_period_type
        ORDER BY r.period_end DESC
        LIMIT 2
    )
    SELECT
        (SELECT rank FROM recent_rankings WHERE rn = 1)::INT,
        (SELECT rank FROM recent_rankings WHERE rn = 2)::INT,
        ((SELECT rank FROM recent_rankings WHERE rn = 2) - (SELECT rank FROM recent_rankings WHERE rn = 1))::INT,
        CASE
            WHEN (SELECT rank FROM recent_rankings WHERE rn = 2) IS NULL THEN 'new'
            WHEN (SELECT rank FROM recent_rankings WHERE rn = 2) > (SELECT rank FROM recent_rankings WHERE rn = 1) THEN 'up'
            WHEN (SELECT rank FROM recent_rankings WHERE rn = 2) < (SELECT rank FROM recent_rankings WHERE rn = 1) THEN 'down'
            ELSE 'stable'
        END::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Function: Generate KPI summary
CREATE OR REPLACE FUNCTION get_kpi_summary(
    p_days INT DEFAULT 7,
    p_domain TEXT DEFAULT 'healthtech'
)
RETURNS TABLE (
    metric_name TEXT,
    current_value FLOAT,
    previous_value FLOAT,
    change_percent FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT
            'total_signals' as metric,
            COUNT(*)::FLOAT as value
        FROM social_posts
        WHERE created_at > NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
        UNION ALL
        SELECT
            'avg_trust_score',
            AVG(trust_score)
        FROM social_posts
        WHERE created_at > NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
        UNION ALL
        SELECT
            'outlier_rate',
            (COUNT(*) FILTER (WHERE is_outlier))::FLOAT / NULLIF(COUNT(*), 0)
        FROM social_posts
        WHERE created_at > NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
        UNION ALL
        SELECT
            'avg_efficiency',
            AVG(efficiency)
        FROM content_outputs
        WHERE published_at > NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
    ),
    previous_period AS (
        SELECT
            'total_signals' as metric,
            COUNT(*)::FLOAT as value
        FROM social_posts
        WHERE created_at BETWEEN NOW() - (p_days * 2 || ' days')::INTERVAL
          AND NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
        UNION ALL
        SELECT
            'avg_trust_score',
            AVG(trust_score)
        FROM social_posts
        WHERE created_at BETWEEN NOW() - (p_days * 2 || ' days')::INTERVAL
          AND NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
        UNION ALL
        SELECT
            'outlier_rate',
            (COUNT(*) FILTER (WHERE is_outlier))::FLOAT / NULLIF(COUNT(*), 0)
        FROM social_posts
        WHERE created_at BETWEEN NOW() - (p_days * 2 || ' days')::INTERVAL
          AND NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
        UNION ALL
        SELECT
            'avg_efficiency',
            AVG(efficiency)
        FROM content_outputs
        WHERE published_at BETWEEN NOW() - (p_days * 2 || ' days')::INTERVAL
          AND NOW() - (p_days || ' days')::INTERVAL
          AND domain = p_domain
    )
    SELECT
        c.metric,
        c.value,
        p.value,
        CASE WHEN p.value > 0 THEN ((c.value - p.value) / p.value) * 100 ELSE NULL END
    FROM current_period c
    LEFT JOIN previous_period p ON c.metric = p.metric;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE research_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_iterations ENABLE ROW LEVEL SECURITY;
ALTER TABLE kol_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users (adjust based on your auth setup)
CREATE POLICY "Allow all for authenticated users" ON research_items
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON social_posts
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON content_outputs
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON rankings
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON learning_iterations
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON kol_profiles
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON alerts
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =============================================================================
-- SAMPLE QUERIES FOR DASHBOARDS
-- =============================================================================

-- Query: Weekly KPI Cards
-- SELECT * FROM get_kpi_summary(7, 'healthtech');

-- Query: Top 10 Influencers
-- SELECT * FROM v_top_performers_weekly LIMIT 10;

-- Query: High-efficiency content
-- SELECT * FROM v_content_efficiency WHERE efficiency > 1.0 LIMIT 20;

-- Query: Recent alerts by severity
-- SELECT * FROM alerts WHERE status = 'new' ORDER BY severity DESC, triggered_at DESC;

-- Query: Platform performance comparison
-- SELECT
--     platform,
--     COUNT(*) as post_count,
--     AVG(final_score) as avg_score,
--     AVG(trust_score) as avg_trust,
--     SUM(engagement) as total_engagement
-- FROM social_posts
-- WHERE created_at > NOW() - INTERVAL '30 days'
-- GROUP BY platform
-- ORDER BY avg_score DESC;

-- Query: Research topics that produce best content
-- SELECT
--     ri.topic,
--     ri.insight_type,
--     AVG(co.efficiency) as avg_efficiency,
--     COUNT(co.id) as content_count
-- FROM research_items ri
-- JOIN content_outputs co ON co.research_id = ri.id
-- WHERE co.tracking_status = 'completed'
-- GROUP BY ri.topic, ri.insight_type
-- HAVING COUNT(co.id) > 2
-- ORDER BY avg_efficiency DESC;
