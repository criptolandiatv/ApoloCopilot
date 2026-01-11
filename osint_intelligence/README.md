# OSINT Intelligence System - HealthTech

> Enterprise-grade Open Source Intelligence system for HealthTech brand monitoring, competitive analysis, and content optimization.

## Overview

This system provides a complete OSINT (Open Source Intelligence) pipeline specifically designed for HealthTech companies. It combines automated data collection, AI-powered analysis, and a learning loop based on the "Outliers" principle of cumulative advantage.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OSINT Intelligence System                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Research   │───>│    Social    │───>│   Content    │───>│  Learning │ │
│  │   Pipeline   │    │   Signals    │    │  Efficiency  │    │    Loop   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│         │                   │                   │                   │       │
│         v                   v                   v                   v       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Supabase (PostgreSQL)                        │  │
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐  │  │
│  │  │  research_  │  social_    │  content_   │  learning_          │  │  │
│  │  │  items      │  posts      │  outputs    │  iterations         │  │  │
│  │  └─────────────┴─────────────┴─────────────┴─────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│         │                   │                   │                   │       │
│         v                   v                   v                   v       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Dashboard (React/D3.js)                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Research Intelligence Pipeline
- PubMed medical research integration
- ClinicalTrials.gov monitoring
- FDA drug/device alerts
- AI-powered insight extraction (Claude)

### 2. Social Signal Tracking
- Multi-platform monitoring (Twitter, LinkedIn, Reddit, HackerNews)
- Trust-weighted scoring
- Outlier detection (statistical)
- KOL (Key Opinion Leader) identification

### 3. Content Efficiency Engine
- Input Quality Score (IQS) calculation
- Output Performance Score (OPS) tracking
- Efficiency = OPS/IQS ratio
- Leverage level classification

### 4. Ranking System
- Weekly and all-time rankings
- Movement tracking
- Consistency scoring
- Trust-weighted metrics

### 5. Learning Loop (Outliers)
- Automatic weight optimization
- Pattern recognition
- Cumulative advantage implementation
- Continuous improvement

## Metrics Framework

### Input Quality Score (IQS)
```
IQS = 0.4 × Confidence + 0.4 × Signal_Strength + 0.2 × Novelty
```

### Output Performance Score (OPS)
```
OPS = 0.5 × Engagement_Rate + 0.3 × Velocity + 0.2 × Trust_Engagement
```

### Trust Score
```
Trust = (Follower_Score + Verification_Bonus + Platform_Trust) / Max_Possible
```
- Follower Score: `min(0.4, log10(followers) / 15)`
- Verification Bonus: `0.2 if verified else 0`
- Platform Trust: Twitter=0.3, LinkedIn=0.4, HackerNews=0.35, Reddit=0.25

### Efficiency (ROI)
```
Efficiency = OPS / IQS
```
- High: > 1.5x
- Medium: 0.75x - 1.5x
- Low: < 0.75x

### Ranking Score
```
Ranking = 0.40 × Avg_Score + 0.25 × Trust + 0.20 × Consistency + 0.15 × Outlier_Ratio
```

## Directory Structure

```
osint_intelligence/
├── workflows/                    # n8n workflow JSON files
│   ├── 01_research_intelligence_pipeline.json
│   ├── 02_social_signal_tracker.json
│   ├── 03_content_efficiency_engine.json
│   ├── 04_ranking_system.json
│   └── 05_outliers_learning_loop.json
│
├── schemas/                      # Database schemas
│   ├── supabase_schema.sql      # Complete Supabase schema
│   └── supabase_queries.sql     # Essential dashboard queries
│
├── api/                         # FastAPI backend
│   └── osint_api.py            # REST API endpoints
│
├── dashboard/                   # Frontend
│   └── index.html              # Dashboard UI
│
├── analytics/                   # Python analytics
│   ├── osint_analytics.py      # Analytics engine
│   └── requirements.txt        # Python dependencies
│
└── templates/                   # Notion/Airtable templates
    └── notion_template.json
```

## Installation

### 1. Supabase Setup
```sql
-- Run the schema file
\i schemas/supabase_schema.sql
```

### 2. n8n Workflows
Import each workflow JSON file into n8n:
1. Go to n8n > Settings > Import from File
2. Select workflow JSON files
3. Configure credentials

### 3. API Server
```bash
cd api
pip install -r ../analytics/requirements.txt
uvicorn osint_api:app --host 0.0.0.0 --port 8001
```

### 4. Dashboard
Serve the dashboard HTML or integrate into your frontend framework.

## Configuration

### Environment Variables
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
ANTHROPIC_API_KEY=your-claude-api-key
```

### n8n Credentials Required
- Telegram Bot Token
- Twitter API v2 (OAuth 2.0)
- LinkedIn API
- Supabase API
- Anthropic API (Claude)
- Slack Webhook (optional)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/osint/dashboard/summary` | GET | Dashboard KPIs |
| `/api/osint/research` | GET/POST | Research items |
| `/api/osint/social/signals` | GET | Social signals |
| `/api/osint/social/outliers` | GET | Statistical outliers |
| `/api/osint/rankings/weekly` | GET | Weekly rankings |
| `/api/osint/rankings/all-time` | GET | All-time rankings |
| `/api/osint/content/efficiency` | GET | Efficiency data |
| `/api/osint/learning/weights` | GET | Current weights |
| `/api/osint/analytics/trend` | GET | Trend analysis |

## Dashboard Views

1. **Overview** - KPIs, trends, insights
2. **Rankings** - Author leaderboard
3. **Efficiency** - IQS vs OPS analysis
4. **Pipeline** - Data flow visualization
5. **Trends** - Historical analysis
6. **Learning** - Weight optimization

## HealthTech Focus

### Data Sources
- **PubMed** - Medical research
- **ClinicalTrials.gov** - Trial data
- **FDA** - Regulatory signals
- **Social Media** - KOL activity

### Categories Tracked
- Digital Health
- Biotech
- MedTech
- Pharma
- Telemedicine
- Wearables
- Diagnostics
- Genomics

### Compliance Considerations
- HIPAA awareness
- FDA regulatory tracking
- GDPR compliance
- Data anonymization

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.
