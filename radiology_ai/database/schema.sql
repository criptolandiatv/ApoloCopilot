-- AI Radiology Report System - Database Schema
-- HIPAA-compliant schema with audit logging and encryption support

-- Enable WAL mode for performance
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Studies table - main radiology study records
CREATE TABLE IF NOT EXISTS studies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_uid TEXT UNIQUE NOT NULL,           -- DICOM StudyInstanceUID
    accession_number TEXT,                     -- Hospital accession
    patient_id_hash TEXT NOT NULL,            -- Hashed patient ID (de-identified)
    modality TEXT NOT NULL,                   -- CR, CT, MR, etc.
    body_part TEXT,
    study_date DATE NOT NULL,
    study_time TIME,
    referring_physician TEXT,
    clinical_indication TEXT,
    urgency TEXT DEFAULT 'routine',           -- routine, priority, urgent, stat
    status TEXT DEFAULT 'pending',            -- pending, in_progress, completed, signed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports table - AI-generated reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,           -- Unique report identifier
    study_id INTEGER NOT NULL REFERENCES studies(id),

    -- Report content
    technique TEXT,
    comparison TEXT,
    findings TEXT NOT NULL,
    impression TEXT NOT NULL,
    recommendations TEXT,                      -- JSON array

    -- AI metadata
    ai_confidence REAL NOT NULL,              -- 0.0 to 1.0
    error_collapse_data TEXT,                  -- JSON: collapse stages and log
    agent_outputs TEXT,                        -- JSON: all agent outputs
    hypothesis_timeline TEXT,                  -- JSON: hypothesis evolution
    processing_time_ms REAL,

    -- Workflow
    urgency TEXT NOT NULL,                    -- routine, priority, urgent, critical
    status TEXT DEFAULT 'draft',              -- draft, pending_review, reviewed, signed, amended
    radiologist_required BOOLEAN DEFAULT 1,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    signed_by TEXT,
    signed_at TIMESTAMP,

    FOREIGN KEY (study_id) REFERENCES studies(id)
);

-- Corrections table - radiologist corrections for learning
CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL REFERENCES reports(report_id),

    -- Original AI output
    original_diagnosis TEXT NOT NULL,
    original_confidence REAL,

    -- Correction
    corrected_diagnosis TEXT NOT NULL,
    correction_reason TEXT,
    severity TEXT,                             -- minor, moderate, major, critical

    -- Radiologist
    corrected_by TEXT NOT NULL,
    corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Learning status
    used_for_training BOOLEAN DEFAULT 0,
    training_batch_id TEXT,

    FOREIGN KEY (report_id) REFERENCES reports(report_id)
);

-- Findings library - standardized finding templates
CREATE TABLE IF NOT EXISTS findings_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_code TEXT UNIQUE NOT NULL,        -- Internal code
    finding_name TEXT NOT NULL,
    modality TEXT,                             -- CR, CT, MR, ALL
    body_part TEXT,
    icd10_code TEXT,
    snomed_code TEXT,
    urgency_default TEXT DEFAULT 'routine',
    description_template TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinical context templates
CREATE TABLE IF NOT EXISTS clinical_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_code TEXT UNIQUE NOT NULL,
    template_name TEXT NOT NULL,
    modality TEXT,
    body_part TEXT,
    indications TEXT,                          -- JSON array of common indications
    key_findings TEXT,                         -- JSON array of expected findings
    differential_diagnoses TEXT,               -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- AUDIT TABLES (HIPAA Compliance)
-- =============================================================================

-- Audit log - immutable audit trail
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,                 -- access, modify, sign, export, etc.
    table_name TEXT,
    record_id TEXT,
    user_id TEXT NOT NULL,
    user_role TEXT,
    action TEXT NOT NULL,
    details TEXT,                              -- JSON with additional context
    ip_address TEXT,
    user_agent TEXT,
    success BOOLEAN DEFAULT 1,
    error_message TEXT
);

-- Access log - PHI access tracking
CREATE TABLE IF NOT EXISTS phi_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,
    patient_id_hash TEXT NOT NULL,
    study_uid TEXT,
    report_id TEXT,
    access_type TEXT NOT NULL,                -- view, edit, export, print
    access_reason TEXT,
    duration_seconds INTEGER,
    data_exported BOOLEAN DEFAULT 0
);

-- =============================================================================
-- LEARNING/TRAINING TABLES
-- =============================================================================

-- Training batches - model improvement tracking
CREATE TABLE IF NOT EXISTS training_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correction_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',            -- pending, training, completed, failed
    model_version_before TEXT,
    model_version_after TEXT,
    metrics_before TEXT,                       -- JSON: accuracy, AUC, etc.
    metrics_after TEXT,
    completed_at TIMESTAMP
);

-- Model versions - version control for AI models
CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT UNIQUE NOT NULL,
    model_type TEXT NOT NULL,                 -- chest_xray, head_ct, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    training_dataset TEXT,                    -- JSON: dataset composition
    validation_metrics TEXT,                   -- JSON: performance metrics
    is_active BOOLEAN DEFAULT 0,
    checksum TEXT,                             -- SHA256 of model weights
    notes TEXT
);

-- =============================================================================
-- MARKETPLACE TABLES (Radiologist Collaboration)
-- =============================================================================

-- Radiologists - registered radiologists
CREATE TABLE IF NOT EXISTS radiologists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email_hash TEXT NOT NULL,                 -- Hashed for privacy
    specialty TEXT,
    certification_verified BOOLEAN DEFAULT 0,
    certification_date DATE,
    tier TEXT DEFAULT 'standard',             -- freemium, standard, premium, equity
    equity_stake REAL DEFAULT 0,              -- Ownership percentage
    reports_reviewed INTEGER DEFAULT 0,
    corrections_made INTEGER DEFAULT 0,
    accuracy_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
);

-- Radiologist earnings
CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    radiologist_id INTEGER NOT NULL REFERENCES radiologists(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    reports_signed INTEGER DEFAULT 0,
    corrections_contributed INTEGER DEFAULT 0,
    base_earnings REAL DEFAULT 0,
    bonus_earnings REAL DEFAULT 0,
    total_earnings REAL DEFAULT 0,
    paid BOOLEAN DEFAULT 0,
    paid_at TIMESTAMP,
    FOREIGN KEY (radiologist_id) REFERENCES radiologists(id)
);

-- Prompt marketplace
CREATE TABLE IF NOT EXISTS prompt_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT UNIQUE NOT NULL,
    creator_id INTEGER REFERENCES radiologists(id),
    name TEXT NOT NULL,
    description TEXT,
    modality TEXT,
    body_part TEXT,
    prompt_text TEXT NOT NULL,
    price REAL DEFAULT 0,                     -- 0 for free templates
    downloads INTEGER DEFAULT 0,
    rating REAL,
    is_public BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_studies_patient ON studies(patient_id_hash);
CREATE INDEX IF NOT EXISTS idx_studies_date ON studies(study_date);
CREATE INDEX IF NOT EXISTS idx_studies_modality ON studies(modality);
CREATE INDEX IF NOT EXISTS idx_studies_status ON studies(status);

CREATE INDEX IF NOT EXISTS idx_reports_study ON reports(study_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_urgency ON reports(urgency);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);

CREATE INDEX IF NOT EXISTS idx_corrections_report ON corrections(report_id);
CREATE INDEX IF NOT EXISTS idx_corrections_diagnosis ON corrections(corrected_diagnosis);
CREATE INDEX IF NOT EXISTS idx_corrections_training ON corrections(used_for_training);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_log(event_type);

CREATE INDEX IF NOT EXISTS idx_phi_access_user ON phi_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_phi_access_patient ON phi_access_log(patient_id_hash);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS studies_updated
    AFTER UPDATE ON studies
    BEGIN
        UPDATE studies SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Audit trigger for reports
CREATE TRIGGER IF NOT EXISTS audit_reports_insert
    AFTER INSERT ON reports
    BEGIN
        INSERT INTO audit_log (event_type, table_name, record_id, user_id, action)
        VALUES ('create', 'reports', NEW.report_id, 'system', 'AI report generated');
    END;

-- Audit trigger for corrections
CREATE TRIGGER IF NOT EXISTS audit_corrections_insert
    AFTER INSERT ON corrections
    BEGIN
        INSERT INTO audit_log (event_type, table_name, record_id, user_id, action, details)
        VALUES ('correction', 'corrections', NEW.id, NEW.corrected_by, 'Report corrected',
                json_object('original', NEW.original_diagnosis, 'corrected', NEW.corrected_diagnosis));
    END;

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Standard findings for chest X-ray trauma
INSERT OR IGNORE INTO findings_library (finding_code, finding_name, modality, body_part, icd10_code, urgency_default)
VALUES
    ('PTX_L', 'Left pneumothorax', 'CR', 'CHEST', 'J93.9', 'urgent'),
    ('PTX_R', 'Right pneumothorax', 'CR', 'CHEST', 'J93.9', 'urgent'),
    ('PTX_TENSION', 'Tension pneumothorax', 'CR', 'CHEST', 'J93.0', 'critical'),
    ('HTX_L', 'Left hemothorax', 'CR', 'CHEST', 'J94.2', 'urgent'),
    ('HTX_R', 'Right hemothorax', 'CR', 'CHEST', 'J94.2', 'urgent'),
    ('CONTUSION', 'Pulmonary contusion', 'CR', 'CHEST', 'S27.329A', 'priority'),
    ('RIB_FX', 'Rib fracture', 'CR', 'CHEST', 'S22.39XA', 'routine'),
    ('FLAIL', 'Flail chest', 'CR', 'CHEST', 'S22.5XXA', 'urgent'),
    ('CVC_POSITION', 'CVC position', 'CR', 'CHEST', NULL, 'routine'),
    ('NGT_POSITION', 'NGT position', 'CR', 'CHEST', NULL, 'routine'),
    ('ETT_POSITION', 'ETT position', 'CR', 'CHEST', NULL, 'routine');

-- Clinical templates for trauma
INSERT OR IGNORE INTO clinical_templates (template_code, template_name, modality, body_part, indications, key_findings)
VALUES
    ('TRAUMA_CHEST', 'Chest Trauma Protocol', 'CR', 'CHEST',
     '["MVA", "Fall", "Penetrating trauma", "Blunt trauma"]',
     '["Pneumothorax", "Hemothorax", "Rib fractures", "Pulmonary contusion", "Aortic injury"]'),
    ('ICU_LINE', 'ICU Line Check', 'CR', 'CHEST',
     '["Post-CVC placement", "Post-intubation", "NGT placement verification"]',
     '["CVC position", "ETT position", "NGT position", "Iatrogenic pneumothorax"]');
