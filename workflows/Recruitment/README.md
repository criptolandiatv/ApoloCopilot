# Automated Recruitment System Workflows

## 🎯 Overview

This directory contains n8n workflows for automated talent discovery and recruitment.

## 📁 Workflows

### 2100_Recruitment_Automated_Talent_Discovery_Scheduled.json

**Complete end-to-end recruitment automation system**

**Trigger:** Daily at 09:00 + Manual

**What it does:**
1. **Scouts** multiple platforms (GitHub, Twitter, Dev.to, LinkedIn)
2. **Validates** candidates (portfolio, activity, employment status, location)
3. **Scores** using AI (technical, communication, cultural fit)
4. **Reaches out** with personalized messages
5. **Reports** weekly summaries to hiring team

**Key Features:**
- Discovers 100-200 candidates/day
- Filters to 20-30 qualified candidates
- AI-powered analysis with Claude
- Selects top 10 weekly for outreach
- Multi-platform messaging (GitHub, Twitter, LinkedIn)
- PostgreSQL database integration
- Comprehensive weekly reports

**Scoring System (100 points):**
- Technical Skills: 0-40 points
- Communication: 0-30 points
- Cultural Fit (AI): 0-30 points

**Prerequisites:**
- GitHub API credentials
- Twitter/X API v2 credentials
- LinkedIn OAuth credentials
- Anthropic Claude API key
- Apify API token
- PostgreSQL database
- SMTP email credentials

**Target Candidates:**
- Technical skills but low public reach
- No formal employment currently
- Active on public platforms
- Located in Brazil (or configurable)

## 📖 Documentation

See `/Documentation/RECRUITMENT_SYSTEM.md` for:
- Complete architecture details
- How the algorithm discovers candidates
- Scoring methodology
- Setup instructions
- Database schema
- Optimization tips
- Privacy & ethics guidelines

## 🚀 Quick Start

1. Import workflow into n8n
2. Configure all API credentials
3. Set up PostgreSQL database
4. Test with manual trigger
5. Activate daily schedule

## 💡 The Concept

This implements the "treasure hunt" recruitment approach:

**Challenge:** Create a system that finds YOU as the ideal candidate.

**Success criteria:**
- Can articulate how the algorithm would discover you
- Understands signals that indicate fit
- Can differentiate yourself from false positives

If you can explain this well, you've demonstrated the metacognitive ability we're looking for.

## 📊 Example Results

**Weekly Output:**
- 156 candidates scanned
- 42 passed validation
- 12 high priority
- 10 contacted with personalized messages

**Top candidate scores:** 75-90/100

**Response rate:** ~30% (industry average: 10-15%)

## 🔧 Customization

Key areas to customize:
- Search keywords and tech stacks
- Location filters
- Scoring thresholds
- Message templates
- Validation criteria

## 📈 Success Metrics

Track:
- Candidates discovered
- Validation pass rate
- Average scores by category
- Outreach response rate
- Interview conversion rate
- Quality of hire

## 🤝 Contributing

To improve this workflow:
1. Test with different search parameters
2. Optimize scoring algorithms
3. Enhance AI prompts for better analysis
4. Add new talent platforms
5. Share results and metrics

## 📝 Notes

- Workflow is designed for daily execution
- Claude AI provides cultural fit analysis
- All outreach is personalized via AI
- Respects privacy and GDPR compliance
- Database stores all candidate interactions

## 🏆 Awards Program

**Top 5 candidates who best articulate how they'd be discovered: Interview + R$ 300**

This rewards metacognitive ability and systems thinking.

---

*Version: 1.0.0*
*Created: 2025-11-05*
*Category: Recruitment Automation*
