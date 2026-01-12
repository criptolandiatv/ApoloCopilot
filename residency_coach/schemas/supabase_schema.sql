-- =============================================================================
-- RESIDENCY COACH - Complete Database Schema
-- Supabase/PostgreSQL - "Rumo ao Hexa R1"
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- =============================================================================
-- 1. CORE TABLES - Questions & Bullets System
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Tags (Taxonomia de Alta Especificidade)
-- -----------------------------------------------------------------------------
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL, -- 'specialty', 'topic', 'syndrome', 'procedure'
    parent_id UUID REFERENCES tags(id),
    description TEXT,

    -- Metadata for weighting algorithm
    global_weight FLOAT DEFAULT 1.0,  -- Base importance
    usp_weight FLOAT DEFAULT 1.0,     -- USP-specific weight
    unicamp_weight FLOAT DEFAULT 1.0, -- Unicamp-specific weight
    enare_weight FLOAT DEFAULT 1.0,   -- ENARE-specific weight

    -- Statistics
    total_questions INT DEFAULT 0,
    avg_error_rate FLOAT DEFAULT 0.0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tag relationships (correlações entre tags)
CREATE TABLE tag_correlations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tag_a_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    tag_b_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    correlation_strength FLOAT DEFAULT 0.5, -- 0-1, how related they are
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(tag_a_id, tag_b_id)
);

-- -----------------------------------------------------------------------------
-- Exams (Bancas e Provas)
-- -----------------------------------------------------------------------------
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    institution VARCHAR(100) NOT NULL, -- USP, Unicamp, ENARE, etc.
    year INT NOT NULL,
    edition VARCHAR(50), -- 'R1', 'R3', 'Acesso Direto'

    -- Exam profile (padrão de cobrança)
    difficulty_avg FLOAT DEFAULT 0.5,
    total_questions INT DEFAULT 0,

    -- Tag distribution (JSON com peso por tag nesta prova)
    tag_distribution JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(institution, year, edition)
);

-- -----------------------------------------------------------------------------
-- Questions (Questões Originais)
-- -----------------------------------------------------------------------------
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES exams(id),
    question_number INT,

    -- Original content
    original_text TEXT NOT NULL,
    options JSONB NOT NULL, -- {"a": "texto", "b": "texto", ...}
    correct_answer CHAR(1) NOT NULL,

    -- Bullet compression
    bullet_text TEXT NOT NULL, -- 1-2 lines compressed version
    debriefing TEXT NOT NULL,  -- Tactical explanation

    -- Classification
    difficulty FLOAT DEFAULT 0.5, -- 0-1 scale
    time_estimate_seconds INT DEFAULT 90,

    -- Media
    has_image BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    has_table BOOLEAN DEFAULT FALSE,
    table_data JSONB,

    -- Statistics (updated by triggers)
    times_answered INT DEFAULT 0,
    times_correct INT DEFAULT 0,
    global_error_rate FLOAT DEFAULT 0.0,
    avg_time_seconds FLOAT DEFAULT 0.0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    reviewed_by UUID,
    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Question-Tag relationship (many-to-many)
CREATE TABLE question_tags (
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    relevance FLOAT DEFAULT 1.0, -- How central this tag is to the question

    PRIMARY KEY (question_id, tag_id)
);

-- -----------------------------------------------------------------------------
-- Distractors Analysis (Por que cada alternativa está errada)
-- -----------------------------------------------------------------------------
CREATE TABLE distractors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    option_letter CHAR(1) NOT NULL,

    -- Why it's wrong (or right)
    is_correct BOOLEAN DEFAULT FALSE,
    explanation TEXT NOT NULL,
    common_trap TEXT, -- Why students fall for this

    -- What tags would lead someone to choose this wrongly
    misleading_tags UUID[] DEFAULT '{}',

    -- Statistics
    times_chosen INT DEFAULT 0,

    UNIQUE(question_id, option_letter)
);

-- =============================================================================
-- 2. USER SYSTEM
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Users (Estudantes)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Auth (synced with Supabase Auth)
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE, -- WhatsApp

    -- Profile
    full_name VARCHAR(200),
    avatar_url TEXT,
    medical_school VARCHAR(200),
    graduation_year INT,

    -- Target exam
    target_institution VARCHAR(100) DEFAULT 'USP',
    target_year INT DEFAULT 2026,
    target_specialty VARCHAR(100),

    -- Subscription
    subscription_tier VARCHAR(20) DEFAULT 'free', -- free, basic, elite
    subscription_expires_at TIMESTAMPTZ,

    -- Gamification
    total_betcoins INT DEFAULT 100, -- Starting balance
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    total_xp INT DEFAULT 0,
    level INT DEFAULT 1,

    -- Statistics
    total_questions_answered INT DEFAULT 0,
    total_correct INT DEFAULT 0,
    total_study_time_minutes INT DEFAULT 0,

    -- Preferences
    preferred_study_mode VARCHAR(50) DEFAULT 'balanced',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    dark_mode BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- User Tag Weights (Pesos Personalizados por Tag)
-- This is the CORE of the Outliers algorithm
-- -----------------------------------------------------------------------------
CREATE TABLE user_tag_weights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,

    -- Performance metrics
    times_seen INT DEFAULT 0,
    times_correct INT DEFAULT 0,
    times_wrong INT DEFAULT 0,
    times_skipped INT DEFAULT 0,
    times_marked_doubt INT DEFAULT 0,

    -- Calculated weights (updated by algorithm)
    error_rate FLOAT DEFAULT 0.0,
    confidence_score FLOAT DEFAULT 0.5, -- User's self-assessed confidence
    mastery_level FLOAT DEFAULT 0.0,    -- 0-1, calculated from performance

    -- Algorithm weights
    priority_weight FLOAT DEFAULT 1.0,  -- Higher = more questions from this tag
    last_decay_at TIMESTAMPTZ DEFAULT NOW(),

    -- Spaced repetition
    next_review_at TIMESTAMPTZ,
    review_interval_days INT DEFAULT 1,
    ease_factor FLOAT DEFAULT 2.5, -- SM-2 algorithm

    -- Timestamps
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, tag_id)
);

-- =============================================================================
-- 3. ANSWER TRACKING
-- =============================================================================

-- -----------------------------------------------------------------------------
-- User Answers (Histórico de Respostas)
-- -----------------------------------------------------------------------------
CREATE TABLE user_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,

    -- Answer details
    selected_answer CHAR(1),
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds INT,

    -- Context
    study_mode VARCHAR(50), -- 'show_milhao', 'outlier', 'simulado', 'revisao'
    session_id UUID,

    -- User feedback
    marked_as_doubt BOOLEAN DEFAULT FALSE,
    marked_as_favorite BOOLEAN DEFAULT FALSE,
    user_notes TEXT,
    difficulty_feedback VARCHAR(20), -- 'easy', 'medium', 'hard'

    -- Gamification context
    betcoins_wagered INT DEFAULT 0,
    betcoins_won INT DEFAULT 0,
    xp_earned INT DEFAULT 0,

    answered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user history queries
CREATE INDEX idx_user_answers_user_time ON user_answers(user_id, answered_at DESC);
CREATE INDEX idx_user_answers_question ON user_answers(question_id);

-- =============================================================================
-- 4. GAMIFICATION SYSTEM
-- =============================================================================

-- -----------------------------------------------------------------------------
-- BetCoins Transactions
-- -----------------------------------------------------------------------------
CREATE TABLE betcoin_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    amount INT NOT NULL, -- Positive = gain, Negative = loss
    balance_after INT NOT NULL,

    transaction_type VARCHAR(50) NOT NULL,
    -- Types: 'daily_bonus', 'streak_bonus', 'question_bet', 'show_milhao',
    --        'challenge_win', 'purchase', 'referral', 'achievement'

    description TEXT,
    reference_id UUID, -- Link to answer, challenge, etc.

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Achievements (Conquistas)
-- -----------------------------------------------------------------------------
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    icon_url TEXT,

    -- Requirements
    requirement_type VARCHAR(50) NOT NULL,
    -- Types: 'streak', 'total_correct', 'tag_mastery', 'speed', 'show_milhao_win'
    requirement_value INT NOT NULL,
    requirement_tag_id UUID REFERENCES tags(id),

    -- Rewards
    betcoin_reward INT DEFAULT 0,
    xp_reward INT DEFAULT 0,

    -- Rarity
    rarity VARCHAR(20) DEFAULT 'common', -- common, rare, epic, legendary

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User achievements
CREATE TABLE user_achievements (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (user_id, achievement_id)
);

-- -----------------------------------------------------------------------------
-- Show do Milhão Sessions
-- -----------------------------------------------------------------------------
CREATE TABLE show_milhao_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session config
    total_questions INT DEFAULT 15,
    difficulty_progression VARCHAR(20) DEFAULT 'classic',
    -- 'classic': 5 easy, 5 medium, 5 hard
    -- 'random': mixed
    -- 'nightmare': all hard

    -- Progress
    current_question INT DEFAULT 0,
    questions_answered JSONB DEFAULT '[]', -- [{question_id, correct, betcoins}]

    -- Stakes
    initial_betcoins INT DEFAULT 0,
    current_pot INT DEFAULT 0,
    checkpoints JSONB DEFAULT '[]', -- [5, 10] = safe points

    -- Lifelines
    lifelines_available JSONB DEFAULT '{"50_50": true, "pular": true, "universitarios": true}',
    lifelines_used JSONB DEFAULT '[]',

    -- Status
    status VARCHAR(20) DEFAULT 'in_progress', -- in_progress, won, lost, abandoned
    final_prize INT DEFAULT 0,

    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

-- -----------------------------------------------------------------------------
-- Daily Challenges
-- -----------------------------------------------------------------------------
CREATE TABLE daily_challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challenge_date DATE NOT NULL UNIQUE,

    -- Challenge definition
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,

    -- Requirements
    challenge_type VARCHAR(50) NOT NULL,
    -- Types: 'answer_count', 'correct_streak', 'tag_focus', 'time_challenge'
    target_value INT NOT NULL,
    target_tag_id UUID REFERENCES tags(id),
    time_limit_minutes INT,

    -- Rewards
    betcoin_reward INT DEFAULT 50,
    xp_reward INT DEFAULT 100,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User daily challenge progress
CREATE TABLE user_daily_challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES daily_challenges(id) ON DELETE CASCADE,

    current_progress INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,

    UNIQUE(user_id, challenge_id)
);

-- =============================================================================
-- 5. STUDY SESSIONS & ANALYTICS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Study Sessions
-- -----------------------------------------------------------------------------
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session info
    session_type VARCHAR(50) NOT NULL,
    -- Types: 'free_practice', 'show_milhao', 'simulado', 'revisao', 'outlier_mode'

    -- Configuration
    tag_focus UUID[], -- Specific tags for this session
    question_count_target INT,
    time_limit_minutes INT,

    -- Results
    questions_answered INT DEFAULT 0,
    questions_correct INT DEFAULT 0,
    total_time_seconds INT DEFAULT 0,

    -- Gamification
    betcoins_earned INT DEFAULT 0,
    xp_earned INT DEFAULT 0,

    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- Device/context
    device_type VARCHAR(50),
    app_version VARCHAR(20)
);

-- -----------------------------------------------------------------------------
-- Performance Snapshots (Weekly/Monthly aggregates)
-- -----------------------------------------------------------------------------
CREATE TABLE performance_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    snapshot_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Metrics
    total_questions INT DEFAULT 0,
    total_correct INT DEFAULT 0,
    accuracy_rate FLOAT DEFAULT 0.0,

    study_time_minutes INT DEFAULT 0,
    sessions_count INT DEFAULT 0,

    -- Tag performance (top 10 weakest)
    weakest_tags JSONB DEFAULT '[]',
    -- Strongest tags
    strongest_tags JSONB DEFAULT '[]',

    -- Comparison
    rank_percentile FLOAT, -- Compared to other users
    improvement_vs_previous FLOAT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, snapshot_type, period_start)
);

-- =============================================================================
-- 6. AI COACH INTERACTION
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Coach Conversations
-- -----------------------------------------------------------------------------
CREATE TABLE coach_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Context
    context_type VARCHAR(50) NOT NULL,
    -- Types: 'question_doubt', 'topic_explanation', 'study_plan', 'motivation', 'free_chat'

    related_question_id UUID REFERENCES questions(id),
    related_tag_id UUID REFERENCES tags(id),

    -- Conversation
    messages JSONB DEFAULT '[]',
    -- [{role: 'user'|'assistant', content: '...', timestamp: '...'}]

    -- AI metadata
    model_used VARCHAR(50),
    total_tokens INT DEFAULT 0,

    -- Feedback
    user_rating INT, -- 1-5
    was_helpful BOOLEAN,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- 7. FUNCTIONS & TRIGGERS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: Calculate user tag weight (Outliers Algorithm)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_tag_priority_weight(
    p_error_rate FLOAT,
    p_times_seen INT,
    p_mastery_level FLOAT,
    p_days_since_last_review INT,
    p_exam_weight FLOAT DEFAULT 1.0
) RETURNS FLOAT AS $$
DECLARE
    base_weight FLOAT;
    recency_factor FLOAT;
    exposure_factor FLOAT;
    final_weight FLOAT;
BEGIN
    -- Higher error rate = higher priority
    base_weight := 1.0 + (p_error_rate * 2.0);

    -- Less exposure = higher priority (minimum 5 exposures for stability)
    IF p_times_seen < 5 THEN
        exposure_factor := 1.5;
    ELSIF p_times_seen < 20 THEN
        exposure_factor := 1.2;
    ELSE
        exposure_factor := 1.0;
    END IF;

    -- Spaced repetition: older = needs review
    recency_factor := 1.0 + (LEAST(p_days_since_last_review, 30) * 0.03);

    -- Low mastery = high priority
    final_weight := base_weight * exposure_factor * recency_factor * (2.0 - p_mastery_level) * p_exam_weight;

    -- Clamp between 0.1 and 10.0
    RETURN GREATEST(0.1, LEAST(10.0, final_weight));
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- Function: Update user tag weights after answer
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_user_tag_weights()
RETURNS TRIGGER AS $$
DECLARE
    tag_record RECORD;
    new_error_rate FLOAT;
    new_mastery FLOAT;
    days_since FLOAT;
BEGIN
    -- Get all tags for this question
    FOR tag_record IN
        SELECT tag_id FROM question_tags WHERE question_id = NEW.question_id
    LOOP
        -- Upsert user_tag_weights
        INSERT INTO user_tag_weights (user_id, tag_id, times_seen, times_correct, times_wrong)
        VALUES (NEW.user_id, tag_record.tag_id, 1,
                CASE WHEN NEW.is_correct THEN 1 ELSE 0 END,
                CASE WHEN NEW.is_correct THEN 0 ELSE 1 END)
        ON CONFLICT (user_id, tag_id) DO UPDATE SET
            times_seen = user_tag_weights.times_seen + 1,
            times_correct = user_tag_weights.times_correct + CASE WHEN NEW.is_correct THEN 1 ELSE 0 END,
            times_wrong = user_tag_weights.times_wrong + CASE WHEN NEW.is_correct THEN 0 ELSE 1 END,
            times_marked_doubt = user_tag_weights.times_marked_doubt + CASE WHEN NEW.marked_as_doubt THEN 1 ELSE 0 END,
            last_seen_at = NOW();

        -- Recalculate metrics
        UPDATE user_tag_weights
        SET
            error_rate = CASE
                WHEN times_seen > 0 THEN times_wrong::FLOAT / times_seen::FLOAT
                ELSE 0
            END,
            mastery_level = CASE
                WHEN times_seen >= 10 THEN
                    LEAST(1.0, (times_correct::FLOAT / times_seen::FLOAT) *
                    (1.0 - (times_marked_doubt::FLOAT / GREATEST(1, times_seen)::FLOAT) * 0.2))
                ELSE
                    (times_correct::FLOAT / GREATEST(1, times_seen)::FLOAT) * 0.5
            END,
            priority_weight = calculate_tag_priority_weight(
                CASE WHEN times_seen > 0 THEN times_wrong::FLOAT / times_seen::FLOAT ELSE 0.5 END,
                times_seen,
                CASE WHEN times_seen >= 10 THEN times_correct::FLOAT / times_seen::FLOAT ELSE 0.5 END,
                EXTRACT(DAY FROM NOW() - last_seen_at)::INT,
                1.0
            )
        WHERE user_id = NEW.user_id AND tag_id = tag_record.tag_id;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tag_weights
AFTER INSERT ON user_answers
FOR EACH ROW EXECUTE FUNCTION update_user_tag_weights();

-- -----------------------------------------------------------------------------
-- Function: Update question statistics
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_question_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE questions
    SET
        times_answered = times_answered + 1,
        times_correct = times_correct + CASE WHEN NEW.is_correct THEN 1 ELSE 0 END,
        global_error_rate = CASE
            WHEN times_answered > 0 THEN
                (times_answered - times_correct)::FLOAT / times_answered::FLOAT
            ELSE 0
        END,
        avg_time_seconds = CASE
            WHEN times_answered > 0 THEN
                (avg_time_seconds * (times_answered - 1) + COALESCE(NEW.time_taken_seconds, 0)) / times_answered
            ELSE COALESCE(NEW.time_taken_seconds, 0)
        END,
        updated_at = NOW()
    WHERE id = NEW.question_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_question_stats
AFTER INSERT ON user_answers
FOR EACH ROW EXECUTE FUNCTION update_question_stats();

-- -----------------------------------------------------------------------------
-- Function: Award XP and check level up
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION award_xp(
    p_user_id UUID,
    p_xp_amount INT
) RETURNS TABLE(new_total_xp INT, new_level INT, leveled_up BOOLEAN) AS $$
DECLARE
    current_xp INT;
    current_level INT;
    xp_for_next_level INT;
    did_level_up BOOLEAN := FALSE;
BEGIN
    SELECT total_xp, level INTO current_xp, current_level
    FROM users WHERE id = p_user_id;

    current_xp := current_xp + p_xp_amount;

    -- Level formula: XP needed = level * 100 * 1.5^(level-1)
    xp_for_next_level := (current_level * 100 * POWER(1.5, current_level - 1))::INT;

    WHILE current_xp >= xp_for_next_level LOOP
        current_level := current_level + 1;
        did_level_up := TRUE;
        xp_for_next_level := (current_level * 100 * POWER(1.5, current_level - 1))::INT;
    END LOOP;

    UPDATE users
    SET total_xp = current_xp, level = current_level, updated_at = NOW()
    WHERE id = p_user_id;

    RETURN QUERY SELECT current_xp, current_level, did_level_up;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 8. VIEWS FOR DASHBOARD
-- =============================================================================

-- User performance overview
CREATE OR REPLACE VIEW v_user_performance AS
SELECT
    u.id as user_id,
    u.full_name,
    u.target_institution,
    u.level,
    u.total_xp,
    u.total_betcoins,
    u.current_streak,
    u.total_questions_answered,
    CASE WHEN u.total_questions_answered > 0
        THEN ROUND((u.total_correct::NUMERIC / u.total_questions_answered) * 100, 1)
        ELSE 0
    END as accuracy_percentage,
    u.total_study_time_minutes,
    (SELECT COUNT(*) FROM user_achievements WHERE user_id = u.id) as achievements_count
FROM users u;

-- User weakest tags (for Outliers mode)
CREATE OR REPLACE VIEW v_user_weak_tags AS
SELECT
    utw.user_id,
    t.name as tag_name,
    t.slug as tag_slug,
    t.category,
    utw.times_seen,
    utw.error_rate,
    utw.mastery_level,
    utw.priority_weight,
    utw.last_seen_at
FROM user_tag_weights utw
JOIN tags t ON t.id = utw.tag_id
WHERE utw.times_seen >= 3
ORDER BY utw.priority_weight DESC;

-- Leaderboard
CREATE OR REPLACE VIEW v_leaderboard AS
SELECT
    u.id,
    u.full_name,
    u.avatar_url,
    u.medical_school,
    u.level,
    u.total_xp,
    u.total_betcoins,
    u.current_streak,
    CASE WHEN u.total_questions_answered > 0
        THEN ROUND((u.total_correct::NUMERIC / u.total_questions_answered) * 100, 1)
        ELSE 0
    END as accuracy,
    RANK() OVER (ORDER BY u.total_xp DESC) as rank_xp,
    RANK() OVER (ORDER BY u.current_streak DESC) as rank_streak
FROM users u
WHERE u.total_questions_answered >= 10;

-- =============================================================================
-- 9. INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX idx_questions_exam ON questions(exam_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_question_tags_tag ON question_tags(tag_id);
CREATE INDEX idx_user_tag_weights_user ON user_tag_weights(user_id);
CREATE INDEX idx_user_tag_weights_priority ON user_tag_weights(user_id, priority_weight DESC);
CREATE INDEX idx_betcoin_transactions_user ON betcoin_transactions(user_id, created_at DESC);
CREATE INDEX idx_study_sessions_user ON study_sessions(user_id, started_at DESC);
CREATE INDEX idx_tags_slug ON tags(slug);
CREATE INDEX idx_tags_category ON tags(category);

-- Full text search on questions
CREATE INDEX idx_questions_fts ON questions
USING gin(to_tsvector('portuguese', original_text || ' ' || bullet_text));

-- =============================================================================
-- 10. SEED DATA - Initial Tags (Especialidades Core)
-- =============================================================================

INSERT INTO tags (name, slug, category, global_weight) VALUES
-- Grandes Áreas
('Clínica Médica', 'clinica_medica', 'specialty', 1.2),
('Cirurgia Geral', 'cirurgia_geral', 'specialty', 1.2),
('Pediatria', 'pediatria', 'specialty', 1.1),
('Ginecologia e Obstetrícia', 'gineco_obstetricia', 'specialty', 1.1),
('Medicina Preventiva', 'preventiva', 'specialty', 1.0),

-- Cirurgia - Síndromes
('Abdome Agudo Inflamatório', 'abdome_agudo_inflamatorio', 'syndrome', 1.3),
('Abdome Agudo Obstrutivo', 'abdome_agudo_obstrutivo', 'syndrome', 1.2),
('Abdome Agudo Perfurativo', 'abdome_agudo_perfurativo', 'syndrome', 1.2),
('Trauma Abdominal', 'trauma_abdominal', 'syndrome', 1.4),

-- Tópicos específicos
('Apendicite', 'apendicite', 'topic', 1.5),
('Colecistite', 'colecistite', 'topic', 1.3),
('Pancreatite', 'pancreatite', 'topic', 1.3),
('Obstrução Intestinal', 'obstrucao_intestinal', 'topic', 1.2),
('Hérnia Inguinal', 'hernia_inguinal', 'topic', 1.1),
('Câncer Colorretal', 'ca_colorretal', 'topic', 1.4),

-- Clínica Médica
('Insuficiência Cardíaca', 'icc', 'topic', 1.3),
('Infarto Agudo do Miocárdio', 'iam', 'topic', 1.5),
('Diabetes Mellitus', 'diabetes', 'topic', 1.2),
('Hipertensão Arterial', 'has', 'topic', 1.2),
('Pneumonia', 'pneumonia', 'topic', 1.3),
('DPOC', 'dpoc', 'topic', 1.2),
('Asma', 'asma', 'topic', 1.1),
('Insuficiência Renal', 'irc', 'topic', 1.2),

-- Pediatria
('Bronquiolite', 'bronquiolite', 'topic', 1.2),
('Diarreia Aguda Pediátrica', 'diarreia_pediatrica', 'topic', 1.2),
('Icterícia Neonatal', 'ictericia_neonatal', 'topic', 1.3),

-- GO
('Pré-Eclâmpsia', 'pre_eclampsia', 'topic', 1.4),
('Trabalho de Parto', 'trabalho_parto', 'topic', 1.3),
('Sangramento 1º Trimestre', 'sangramento_1tri', 'topic', 1.2)

ON CONFLICT (slug) DO NOTHING;

-- =============================================================================
-- 11. INITIAL ACHIEVEMENTS
-- =============================================================================

INSERT INTO achievements (slug, name, description, requirement_type, requirement_value, betcoin_reward, xp_reward, rarity) VALUES
('first_blood', 'First Blood', 'Responda sua primeira questão', 'total_correct', 1, 10, 50, 'common'),
('streak_3', 'Hat-Trick', '3 dias seguidos de estudo', 'streak', 3, 30, 100, 'common'),
('streak_7', 'Semana Perfeita', '7 dias seguidos de estudo', 'streak', 7, 100, 300, 'rare'),
('streak_30', 'Mês de Ferro', '30 dias seguidos de estudo', 'streak', 30, 500, 1000, 'epic'),
('centurion', 'Centurião', '100 questões corretas', 'total_correct', 100, 200, 500, 'rare'),
('millennial', 'Milênio', '1000 questões corretas', 'total_correct', 1000, 1000, 3000, 'legendary'),
('show_milhao_win', 'Milionário', 'Vença o Show do Milhão', 'show_milhao_win', 1, 500, 1000, 'epic'),
('speed_demon', 'Speed Demon', 'Responda 10 questões em menos de 5 minutos', 'speed', 10, 100, 200, 'rare')
ON CONFLICT (slug) DO NOTHING;
