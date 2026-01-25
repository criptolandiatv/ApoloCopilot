-- =============================================================================
-- OSINT Intelligence System - Essential Queries
-- HealthTech Domain - Dashboard & Analytics Queries
-- =============================================================================

-- =============================================================================
-- 1. KPI DASHBOARD QUERIES
-- =============================================================================

-- Weekly Summary Stats
SELECT
    COUNT(*) as total_signals,
    COUNT(*) FILTER (WHERE is_outlier = true) as outliers,
    ROUND(AVG(final_score)::numeric, 4) as avg_score,
    ROUND(AVG(trust_score)::numeric, 4) as avg_trust,
    COUNT(DISTINCT author) as unique_authors,
    SUM(engagement) as total_engagement
FROM social_posts
WHERE created_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech';

-- Research Quality Summary
SELECT
    COUNT(*) as total_research,
    ROUND(AVG(input_quality_score)::numeric, 4) as avg_iqs,
    ROUND(AVG(confidence)::numeric, 4) as avg_confidence,
    ROUND(AVG(novelty)::numeric, 4) as avg_novelty,
    COUNT(*) FILTER (WHERE actionable = true) as actionable_count,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority
FROM research_items
WHERE created_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech';

-- Content Efficiency Summary
SELECT
    COUNT(*) as total_content,
    ROUND(AVG(efficiency)::numeric, 4) as avg_efficiency,
    ROUND(AVG(output_performance_score)::numeric, 4) as avg_ops,
    COUNT(*) FILTER (WHERE leverage_level = 'high') as high_leverage,
    COUNT(*) FILTER (WHERE leverage_level = 'medium') as medium_leverage,
    COUNT(*) FILTER (WHERE leverage_level = 'low') as low_leverage
FROM content_outputs
WHERE published_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech'
  AND tracking_status = 'completed';

-- =============================================================================
-- 2. RANKING QUERIES
-- =============================================================================

-- Current Weekly Rankings with Movement
WITH current_week AS (
    SELECT
        author,
        platform,
        AVG(final_score) as avg_score,
        AVG(trust_score) as avg_trust,
        COUNT(*) as post_count,
        SUM(engagement) as total_engagement,
        COUNT(*) FILTER (WHERE is_outlier) as outlier_count
    FROM social_posts
    WHERE created_at > NOW() - INTERVAL '7 days'
      AND domain = 'healthtech'
    GROUP BY author, platform
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY avg_score DESC) as current_rank
    FROM current_week
),
previous_ranks AS (
    SELECT
        author,
        platform,
        rank as previous_rank
    FROM rankings
    WHERE period_type = 'weekly'
      AND period_end = (
          SELECT MAX(period_end)
          FROM rankings
          WHERE period_type = 'weekly'
            AND period_end < NOW() - INTERVAL '7 days'
      )
)
SELECT
    r.current_rank,
    r.author,
    r.platform,
    ROUND(r.avg_score::numeric, 4) as score,
    ROUND(r.avg_trust::numeric, 4) as trust,
    r.post_count,
    r.total_engagement,
    r.outlier_count,
    pr.previous_rank,
    COALESCE(pr.previous_rank - r.current_rank, 0) as movement,
    CASE
        WHEN pr.previous_rank IS NULL THEN 'NEW'
        WHEN pr.previous_rank > r.current_rank THEN 'UP'
        WHEN pr.previous_rank < r.current_rank THEN 'DOWN'
        ELSE 'STABLE'
    END as movement_type
FROM ranked r
LEFT JOIN previous_ranks pr ON r.author = pr.author AND r.platform = pr.platform
ORDER BY r.current_rank
LIMIT 50;

-- All-Time Top Performers
SELECT
    author,
    platform,
    COUNT(*) as total_posts,
    ROUND(AVG(final_score)::numeric, 4) as lifetime_avg_score,
    ROUND(AVG(trust_score)::numeric, 4) as lifetime_trust,
    SUM(engagement) as lifetime_engagement,
    COUNT(*) FILTER (WHERE is_outlier) as lifetime_outliers,
    MIN(created_at) as first_seen,
    MAX(created_at) as last_seen
FROM social_posts
WHERE domain = 'healthtech'
GROUP BY author, platform
HAVING COUNT(*) >= 5
ORDER BY lifetime_avg_score DESC
LIMIT 100;

-- =============================================================================
-- 3. EFFICIENCY ANALYSIS QUERIES
-- =============================================================================

-- Top Efficiency Content (Best ROI)
SELECT
    co.id,
    co.platform,
    co.title,
    ri.topic as research_topic,
    ri.insight_type,
    ROUND(co.input_quality_score::numeric, 4) as iqs,
    ROUND(co.output_performance_score::numeric, 4) as ops,
    ROUND(co.efficiency::numeric, 4) as efficiency,
    co.leverage_level,
    co.impressions,
    co.likes,
    co.shares,
    co.published_at
FROM content_outputs co
LEFT JOIN research_items ri ON co.research_id = ri.id
WHERE co.tracking_status = 'completed'
  AND co.domain = 'healthtech'
  AND co.efficiency IS NOT NULL
ORDER BY co.efficiency DESC
LIMIT 20;

-- Efficiency by Platform
SELECT
    platform,
    COUNT(*) as content_count,
    ROUND(AVG(efficiency)::numeric, 4) as avg_efficiency,
    ROUND(AVG(input_quality_score)::numeric, 4) as avg_iqs,
    ROUND(AVG(output_performance_score)::numeric, 4) as avg_ops,
    COUNT(*) FILTER (WHERE leverage_level = 'high') as high_leverage_count,
    ROUND((COUNT(*) FILTER (WHERE leverage_level = 'high'))::numeric / COUNT(*)::numeric, 4) as high_leverage_rate
FROM content_outputs
WHERE tracking_status = 'completed'
  AND domain = 'healthtech'
GROUP BY platform
ORDER BY avg_efficiency DESC;

-- Research Topics that Produce Best Content
SELECT
    ri.topic,
    ri.insight_type,
    COUNT(co.id) as content_count,
    ROUND(AVG(ri.input_quality_score)::numeric, 4) as avg_input_quality,
    ROUND(AVG(co.efficiency)::numeric, 4) as avg_efficiency,
    ROUND(AVG(co.output_performance_score)::numeric, 4) as avg_ops,
    ROUND(SUM(co.impressions)::numeric / NULLIF(COUNT(co.id), 0), 0) as avg_impressions
FROM research_items ri
JOIN content_outputs co ON co.research_id = ri.id
WHERE co.tracking_status = 'completed'
  AND ri.domain = 'healthtech'
GROUP BY ri.topic, ri.insight_type
HAVING COUNT(co.id) >= 2
ORDER BY avg_efficiency DESC
LIMIT 20;

-- =============================================================================
-- 4. OUTLIER DETECTION QUERIES
-- =============================================================================

-- Find Statistical Outliers (Z-Score > 1.5)
WITH stats AS (
    SELECT
        AVG(final_score) as mean_score,
        STDDEV(final_score) as std_dev
    FROM social_posts
    WHERE created_at > NOW() - INTERVAL '7 days'
      AND domain = 'healthtech'
)
SELECT
    sp.id,
    sp.author,
    sp.platform,
    sp.content,
    sp.engagement,
    ROUND(sp.final_score::numeric, 4) as score,
    ROUND(sp.trust_score::numeric, 4) as trust,
    ROUND(((sp.final_score - stats.mean_score) / NULLIF(stats.std_dev, 0))::numeric, 2) as z_score,
    sp.post_created_at
FROM social_posts sp
CROSS JOIN stats
WHERE sp.created_at > NOW() - INTERVAL '7 days'
  AND sp.domain = 'healthtech'
  AND (sp.final_score - stats.mean_score) / NULLIF(stats.std_dev, 0) > 1.5
ORDER BY z_score DESC;

-- Engagement Velocity Leaders (Fast Rising Content)
SELECT
    id,
    author,
    platform,
    content,
    engagement,
    ROUND(velocity::numeric, 4) as velocity,
    ROUND(final_score::numeric, 4) as score,
    EXTRACT(EPOCH FROM (NOW() - post_created_at)) / 3600 as hours_old,
    ROUND((engagement::numeric / NULLIF(EXTRACT(EPOCH FROM (NOW() - post_created_at)) / 3600, 0))::numeric, 2) as engagement_per_hour
FROM social_posts
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND domain = 'healthtech'
  AND post_created_at > NOW() - INTERVAL '24 hours'
ORDER BY engagement_per_hour DESC
LIMIT 20;

-- =============================================================================
-- 5. TREND ANALYSIS QUERIES
-- =============================================================================

-- Daily Signal Volume Trend
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_signals,
    COUNT(*) FILTER (WHERE is_outlier) as outliers,
    ROUND(AVG(final_score)::numeric, 4) as avg_score,
    SUM(engagement) as total_engagement
FROM social_posts
WHERE created_at > NOW() - INTERVAL '30 days'
  AND domain = 'healthtech'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Platform Distribution Over Time
SELECT
    DATE_TRUNC('week', created_at) as week,
    platform,
    COUNT(*) as signal_count,
    ROUND(AVG(final_score)::numeric, 4) as avg_score,
    SUM(engagement) as total_engagement
FROM social_posts
WHERE created_at > NOW() - INTERVAL '90 days'
  AND domain = 'healthtech'
GROUP BY DATE_TRUNC('week', created_at), platform
ORDER BY week DESC, signal_count DESC;

-- Topic Trend Analysis
SELECT
    DATE_TRUNC('week', created_at) as week,
    insight_type,
    COUNT(*) as research_count,
    ROUND(AVG(input_quality_score)::numeric, 4) as avg_quality,
    COUNT(*) FILTER (WHERE actionable = true) as actionable_count
FROM research_items
WHERE created_at > NOW() - INTERVAL '90 days'
  AND domain = 'healthtech'
GROUP BY DATE_TRUNC('week', created_at), insight_type
ORDER BY week DESC;

-- =============================================================================
-- 6. LEARNING LOOP QUERIES
-- =============================================================================

-- Get Latest Weights
SELECT
    id,
    iteration_number,
    iteration_date,
    platform_weights,
    topic_weights,
    timing_weights,
    mean_efficiency,
    improvement_rate
FROM learning_iterations
WHERE domain = 'healthtech'
ORDER BY iteration_date DESC
LIMIT 1;

-- Learning Progress Over Time
SELECT
    iteration_number,
    iteration_date,
    mean_efficiency,
    outlier_count,
    total_analyzed,
    improvement_rate,
    platform_weights->>'twitter' as twitter_weight,
    platform_weights->>'linkedin' as linkedin_weight
FROM learning_iterations
WHERE domain = 'healthtech'
ORDER BY iteration_date DESC
LIMIT 30;

-- Weight Evolution Analysis
WITH weight_changes AS (
    SELECT
        iteration_number,
        iteration_date,
        platform_weights,
        LAG(platform_weights) OVER (ORDER BY iteration_date) as prev_weights
    FROM learning_iterations
    WHERE domain = 'healthtech'
    ORDER BY iteration_date DESC
    LIMIT 10
)
SELECT
    iteration_number,
    iteration_date,
    (platform_weights->>'twitter')::float as twitter_current,
    (prev_weights->>'twitter')::float as twitter_previous,
    (platform_weights->>'linkedin')::float as linkedin_current,
    (prev_weights->>'linkedin')::float as linkedin_previous
FROM weight_changes
WHERE prev_weights IS NOT NULL;

-- =============================================================================
-- 7. ALERT QUERIES
-- =============================================================================

-- Pending Alerts by Severity
SELECT
    alert_type,
    severity,
    COUNT(*) as alert_count
FROM alerts
WHERE status = 'new'
  AND domain = 'healthtech'
GROUP BY alert_type, severity
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        ELSE 5
    END;

-- Recent Critical Alerts
SELECT
    id,
    alert_type,
    title,
    description,
    source_type,
    triggered_at,
    status
FROM alerts
WHERE severity IN ('critical', 'high')
  AND domain = 'healthtech'
  AND triggered_at > NOW() - INTERVAL '7 days'
ORDER BY triggered_at DESC;

-- =============================================================================
-- 8. KOL TRACKING QUERIES
-- =============================================================================

-- KOL Performance Summary
SELECT
    kp.username,
    kp.platform,
    kp.followers,
    ROUND(kp.influence_score::numeric, 4) as influence,
    ROUND(kp.engagement_rate::numeric, 4) as engagement_rate,
    kp.expertise_areas,
    COUNT(sp.id) as recent_posts,
    ROUND(AVG(sp.final_score)::numeric, 4) as recent_avg_score
FROM kol_profiles kp
LEFT JOIN social_posts sp ON sp.author = kp.username
    AND sp.platform = kp.platform
    AND sp.created_at > NOW() - INTERVAL '7 days'
WHERE kp.tracking_enabled = true
GROUP BY kp.id, kp.username, kp.platform, kp.followers,
         kp.influence_score, kp.engagement_rate, kp.expertise_areas
ORDER BY influence DESC;

-- KOL Activity Analysis
SELECT
    author,
    platform,
    COUNT(*) as post_count,
    ROUND(AVG(final_score)::numeric, 4) as avg_score,
    ROUND(AVG(engagement)::numeric, 0) as avg_engagement,
    MAX(post_created_at) as last_active,
    array_agg(DISTINCT unnest(healthtech_keywords)) as topics
FROM social_posts
WHERE created_at > NOW() - INTERVAL '30 days'
  AND domain = 'healthtech'
  AND author IN (SELECT username FROM kol_profiles WHERE tracking_enabled = true)
GROUP BY author, platform
ORDER BY avg_score DESC;

-- =============================================================================
-- 9. CORRELATION QUERIES
-- =============================================================================

-- Input Quality vs Output Performance Correlation
SELECT
    ROUND(input_quality_score * 10, 0) / 10 as iqs_bucket,
    COUNT(*) as sample_count,
    ROUND(AVG(output_performance_score)::numeric, 4) as avg_ops,
    ROUND(AVG(efficiency)::numeric, 4) as avg_efficiency,
    ROUND(STDDEV(output_performance_score)::numeric, 4) as ops_stddev
FROM content_outputs
WHERE tracking_status = 'completed'
  AND input_quality_score IS NOT NULL
  AND domain = 'healthtech'
GROUP BY ROUND(input_quality_score * 10, 0) / 10
HAVING COUNT(*) >= 3
ORDER BY iqs_bucket;

-- Trust Score vs Engagement Correlation
SELECT
    ROUND(trust_score * 10, 0) / 10 as trust_bucket,
    COUNT(*) as sample_count,
    ROUND(AVG(engagement)::numeric, 0) as avg_engagement,
    ROUND(AVG(final_score)::numeric, 4) as avg_score,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY engagement)::numeric, 0) as median_engagement
FROM social_posts
WHERE created_at > NOW() - INTERVAL '30 days'
  AND trust_score IS NOT NULL
  AND domain = 'healthtech'
GROUP BY ROUND(trust_score * 10, 0) / 10
ORDER BY trust_bucket;

-- =============================================================================
-- 10. EXPORT QUERIES
-- =============================================================================

-- Export Weekly Report Data
SELECT
    'signals' as data_type,
    json_build_object(
        'total', COUNT(*),
        'outliers', COUNT(*) FILTER (WHERE is_outlier),
        'avg_score', ROUND(AVG(final_score)::numeric, 4),
        'by_platform', json_agg(DISTINCT platform)
    ) as data
FROM social_posts
WHERE created_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech'
UNION ALL
SELECT
    'research',
    json_build_object(
        'total', COUNT(*),
        'actionable', COUNT(*) FILTER (WHERE actionable),
        'avg_quality', ROUND(AVG(input_quality_score)::numeric, 4)
    )
FROM research_items
WHERE created_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech'
UNION ALL
SELECT
    'content',
    json_build_object(
        'total', COUNT(*),
        'avg_efficiency', ROUND(AVG(efficiency)::numeric, 4),
        'high_leverage', COUNT(*) FILTER (WHERE leverage_level = 'high')
    )
FROM content_outputs
WHERE published_at > NOW() - INTERVAL '7 days'
  AND domain = 'healthtech'
  AND tracking_status = 'completed';
