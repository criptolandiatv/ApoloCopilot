"""
OSINT Intelligence API - HealthTech
FastAPI extension for OSINT intelligence system
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import httpx
import json
import os
from functools import lru_cache
import asyncio

# =============================================================================
# CONFIGURATION
# =============================================================================

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DOMAIN: str = "healthtech"

settings = Settings()

# =============================================================================
# MODELS
# =============================================================================

class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"

class InsightType(str, Enum):
    TREND = "trend"
    COMPETITOR = "competitor"
    REGULATORY = "regulatory"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    GENERAL = "general"

class LeverageLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class MovementType(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    NEW = "new"

# Request Models
class ResearchInput(BaseModel):
    topic: str
    source: str = "manual"
    insight: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    novelty: float = Field(default=0.5, ge=0, le=1)
    signal_strength: float = Field(default=0.5, ge=0, le=1)
    insight_type: InsightType = InsightType.GENERAL
    healthtech_category: Optional[str] = None
    tags: Optional[List[str]] = []

class SocialSignalInput(BaseModel):
    platform: Platform
    post_id: str
    author: str
    content: str
    followers: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    verified: bool = False
    post_created_at: Optional[datetime] = None

class ContentInput(BaseModel):
    content_id: str
    research_id: str
    platform: Platform
    content_url: Optional[str] = None
    title: Optional[str] = None
    published_at: Optional[datetime] = None

# Response Models
class ScoreResponse(BaseModel):
    input_quality_score: float
    confidence: float
    novelty: float
    signal_strength: float

class RankingResponse(BaseModel):
    rank: int
    author: str
    platform: str
    ranking_score: float
    avg_post_score: float
    avg_trust_score: float
    total_posts: int
    movement: Optional[int] = None
    movement_type: Optional[str] = None

class KPIResponse(BaseModel):
    metric_name: str
    current_value: float
    previous_value: Optional[float]
    change_percent: Optional[float]

class EfficiencyResponse(BaseModel):
    content_id: str
    platform: str
    input_quality_score: float
    output_performance_score: float
    efficiency: float
    leverage_level: str

# =============================================================================
# API INITIALIZATION
# =============================================================================

app = FastAPI(
    title="OSINT Intelligence API",
    description="HealthTech OSINT Intelligence System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# SUPABASE CLIENT
# =============================================================================

class SupabaseClient:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def query(self, table: str, params: Dict = None) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                params=params or {}
            )
            response.raise_for_status()
            return response.json()

    async def insert(self, table: str, data: Dict) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def rpc(self, function: str, params: Dict = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/rest/v1/rpc/{function}",
                headers=self.headers,
                json=params or {}
            )
            response.raise_for_status()
            return response.json()

db = SupabaseClient()

# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

def calculate_input_quality_score(
    confidence: float,
    novelty: float,
    signal_strength: float
) -> float:
    """Calculate IQS (Input Quality Score)"""
    return (0.4 * confidence) + (0.4 * signal_strength) + (0.2 * novelty)

def calculate_trust_score(
    followers: int,
    verified: bool,
    platform: str
) -> float:
    """Calculate trust score based on social signals"""
    import math

    # Follower trust (log scale, max 0.4)
    follower_score = min(0.4, math.log10(max(1, followers)) / 15)

    # Verification bonus
    verification_bonus = 0.2 if verified else 0

    # Platform trust
    platform_trust = {
        "twitter": 0.3,
        "linkedin": 0.4,
        "hackernews": 0.35,
        "reddit": 0.25
    }
    platform_score = platform_trust.get(platform, 0.2)

    total = follower_score + verification_bonus + platform_score
    max_possible = 0.4 + 0.2 + 0.4

    return total / max_possible

def calculate_velocity(engagement: int, hours_old: float) -> float:
    """Calculate engagement velocity"""
    if hours_old <= 0:
        return min(1.0, engagement / 100)
    velocity = engagement / hours_old
    return min(1.0, velocity / 100)

def calculate_final_score(
    trust_score: float,
    velocity: float,
    engagement: int
) -> float:
    """Calculate final social signal score"""
    trust_weighted = engagement * trust_score
    normalized_twe = min(1.0, trust_weighted / 1000)

    return (0.4 * trust_score) + (0.3 * velocity) + (0.3 * normalized_twe)

def calculate_efficiency(ops: float, iqs: float) -> float:
    """Calculate content efficiency (ROI)"""
    if iqs <= 0:
        return 0
    return ops / iqs

# =============================================================================
# API ENDPOINTS
# =============================================================================

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# -----------------------------------------------------------------------------
# KPI Dashboard
# -----------------------------------------------------------------------------

@app.get("/api/osint/kpis", response_model=List[KPIResponse])
async def get_kpis(days: int = Query(default=7, ge=1, le=90)):
    """Get KPI summary with period comparison"""
    try:
        kpis = await db.rpc("get_kpi_summary", {"p_days": days, "p_domain": settings.DOMAIN})
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/dashboard/summary")
async def get_dashboard_summary():
    """Get comprehensive dashboard summary"""
    try:
        # Parallel fetch of all dashboard data
        signals_task = db.query("social_posts", {
            "created_at": f"gte.{(datetime.utcnow() - timedelta(days=7)).isoformat()}",
            "domain": f"eq.{settings.DOMAIN}",
            "select": "id,final_score,trust_score,is_outlier,engagement,platform"
        })

        research_task = db.query("research_items", {
            "created_at": f"gte.{(datetime.utcnow() - timedelta(days=7)).isoformat()}",
            "domain": f"eq.{settings.DOMAIN}",
            "select": "id,input_quality_score,actionable,insight_type"
        })

        content_task = db.query("content_outputs", {
            "published_at": f"gte.{(datetime.utcnow() - timedelta(days=7)).isoformat()}",
            "domain": f"eq.{settings.DOMAIN}",
            "tracking_status": "eq.completed",
            "select": "id,efficiency,leverage_level,platform"
        })

        signals, research, content = await asyncio.gather(
            signals_task, research_task, content_task
        )

        # Calculate summaries
        total_signals = len(signals)
        outliers = sum(1 for s in signals if s.get("is_outlier"))
        avg_score = sum(s.get("final_score", 0) for s in signals) / max(1, total_signals)
        avg_trust = sum(s.get("trust_score", 0) for s in signals) / max(1, total_signals)

        total_research = len(research)
        actionable_research = sum(1 for r in research if r.get("actionable"))
        avg_iqs = sum(r.get("input_quality_score", 0) for r in research) / max(1, total_research)

        total_content = len(content)
        high_leverage = sum(1 for c in content if c.get("leverage_level") == "high")
        avg_efficiency = sum(c.get("efficiency", 0) for c in content) / max(1, total_content)

        # Platform breakdown
        platform_counts = {}
        for s in signals:
            p = s.get("platform", "unknown")
            platform_counts[p] = platform_counts.get(p, 0) + 1

        return {
            "period": "7_days",
            "signals": {
                "total": total_signals,
                "outliers": outliers,
                "outlier_rate": round(outliers / max(1, total_signals), 4),
                "avg_score": round(avg_score, 4),
                "avg_trust": round(avg_trust, 4),
                "by_platform": platform_counts
            },
            "research": {
                "total": total_research,
                "actionable": actionable_research,
                "actionable_rate": round(actionable_research / max(1, total_research), 4),
                "avg_quality": round(avg_iqs, 4)
            },
            "content": {
                "total": total_content,
                "high_leverage": high_leverage,
                "avg_efficiency": round(avg_efficiency, 4)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Research Intelligence
# -----------------------------------------------------------------------------

@app.post("/api/osint/research")
async def create_research(research: ResearchInput):
    """Submit new research item"""
    try:
        # Calculate IQS
        iqs = calculate_input_quality_score(
            research.confidence,
            research.novelty,
            research.signal_strength
        )

        data = {
            "topic": research.topic,
            "source": research.source,
            "insight": research.insight,
            "confidence": research.confidence,
            "novelty": research.novelty,
            "signal_strength": research.signal_strength,
            "insight_type": research.insight_type.value,
            "healthtech_category": research.healthtech_category,
            "tags": research.tags,
            "actionable": iqs > 0.6,
            "domain": settings.DOMAIN
        }

        result = await db.insert("research_items", data)

        return {
            "status": "success",
            "research_id": result[0]["id"] if result else None,
            "scores": {
                "input_quality_score": round(iqs, 4),
                "confidence": research.confidence,
                "novelty": research.novelty,
                "signal_strength": research.signal_strength
            },
            "actionable": iqs > 0.6
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/research")
async def get_research(
    limit: int = Query(default=50, ge=1, le=200),
    insight_type: Optional[InsightType] = None,
    actionable_only: bool = False,
    min_quality: float = Query(default=0, ge=0, le=1)
):
    """Get research items with filters"""
    try:
        params = {
            "domain": f"eq.{settings.DOMAIN}",
            "order": "created_at.desc",
            "limit": str(limit)
        }

        if insight_type:
            params["insight_type"] = f"eq.{insight_type.value}"
        if actionable_only:
            params["actionable"] = "eq.true"
        if min_quality > 0:
            params["input_quality_score"] = f"gte.{min_quality}"

        results = await db.query("research_items", params)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Social Signals
# -----------------------------------------------------------------------------

@app.post("/api/osint/social/signal")
async def submit_social_signal(signal: SocialSignalInput):
    """Submit a social signal for analysis"""
    try:
        # Calculate scores
        trust_score = calculate_trust_score(
            signal.followers,
            signal.verified,
            signal.platform.value
        )

        engagement = signal.likes + (signal.shares * 2) + (signal.comments * 3)

        hours_old = 0
        if signal.post_created_at:
            delta = datetime.utcnow() - signal.post_created_at.replace(tzinfo=None)
            hours_old = delta.total_seconds() / 3600

        velocity = calculate_velocity(engagement, hours_old)
        final_score = calculate_final_score(trust_score, velocity, engagement)

        data = {
            "platform": signal.platform.value,
            "post_id": signal.post_id,
            "author": signal.author,
            "content": signal.content,
            "followers": signal.followers,
            "verified": signal.verified,
            "likes": signal.likes,
            "shares": signal.shares,
            "comments": signal.comments,
            "trust_score": trust_score,
            "velocity": velocity,
            "final_score": final_score,
            "post_created_at": signal.post_created_at.isoformat() if signal.post_created_at else None,
            "domain": settings.DOMAIN
        }

        result = await db.insert("social_posts", data)

        return {
            "status": "success",
            "signal_id": result[0]["id"] if result else None,
            "scores": {
                "trust_score": round(trust_score, 4),
                "velocity": round(velocity, 4),
                "final_score": round(final_score, 4),
                "engagement": engagement
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/social/signals")
async def get_social_signals(
    platform: Optional[Platform] = None,
    limit: int = Query(default=50, ge=1, le=200),
    outliers_only: bool = False,
    min_score: float = Query(default=0, ge=0, le=1)
):
    """Get social signals with filters"""
    try:
        params = {
            "domain": f"eq.{settings.DOMAIN}",
            "order": "final_score.desc",
            "limit": str(limit)
        }

        if platform:
            params["platform"] = f"eq.{platform.value}"
        if outliers_only:
            params["is_outlier"] = "eq.true"
        if min_score > 0:
            params["final_score"] = f"gte.{min_score}"

        results = await db.query("social_posts", params)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/social/outliers")
async def get_outliers(days: int = Query(default=7, ge=1, le=30)):
    """Get statistical outliers from social signals"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        signals = await db.query("social_posts", {
            "created_at": f"gte.{cutoff}",
            "domain": f"eq.{settings.DOMAIN}",
            "order": "final_score.desc"
        })

        if not signals:
            return {"outliers": [], "statistics": None}

        # Calculate statistics
        scores = [s.get("final_score", 0) for s in signals]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        threshold = mean + (1.5 * std_dev)

        # Identify outliers
        outliers = []
        for s in signals:
            score = s.get("final_score", 0)
            if score > threshold:
                z_score = (score - mean) / std_dev if std_dev > 0 else 0
                outliers.append({
                    **s,
                    "z_score": round(z_score, 2),
                    "percentile": round(
                        sum(1 for x in scores if x <= score) / len(scores) * 100
                    )
                })

        return {
            "outliers": outliers,
            "statistics": {
                "mean": round(mean, 4),
                "std_dev": round(std_dev, 4),
                "threshold": round(threshold, 4),
                "total_analyzed": len(signals),
                "outlier_count": len(outliers)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Rankings
# -----------------------------------------------------------------------------

@app.get("/api/osint/rankings/weekly", response_model=List[RankingResponse])
async def get_weekly_rankings(limit: int = Query(default=50, ge=1, le=100)):
    """Get weekly author rankings"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()

        signals = await db.query("social_posts", {
            "created_at": f"gte.{cutoff}",
            "domain": f"eq.{settings.DOMAIN}",
            "select": "author,platform,final_score,trust_score,engagement,is_outlier"
        })

        if not signals:
            return []

        # Aggregate by author
        author_stats = {}
        for s in signals:
            author = s["author"]
            if author not in author_stats:
                author_stats[author] = {
                    "author": author,
                    "platform": s["platform"],
                    "scores": [],
                    "trust_scores": [],
                    "total_engagement": 0,
                    "outlier_count": 0
                }

            author_stats[author]["scores"].append(s.get("final_score", 0))
            author_stats[author]["trust_scores"].append(s.get("trust_score", 0))
            author_stats[author]["total_engagement"] += s.get("engagement", 0)
            if s.get("is_outlier"):
                author_stats[author]["outlier_count"] += 1

        # Calculate rankings
        rankings = []
        for author, stats in author_stats.items():
            avg_score = sum(stats["scores"]) / len(stats["scores"])
            avg_trust = sum(stats["trust_scores"]) / len(stats["trust_scores"])
            post_count = len(stats["scores"])

            # Consistency score
            mean = avg_score
            variance = sum((s - mean) ** 2 for s in stats["scores"]) / len(stats["scores"])
            std_dev = variance ** 0.5
            consistency = 1 - min(1, std_dev / mean if mean > 0 else 0)

            # Outlier ratio
            outlier_ratio = stats["outlier_count"] / post_count

            # Final ranking score
            ranking_score = (
                0.40 * avg_score +
                0.25 * avg_trust +
                0.20 * consistency +
                0.15 * outlier_ratio
            )

            rankings.append({
                "author": author,
                "platform": stats["platform"],
                "ranking_score": round(ranking_score, 4),
                "avg_post_score": round(avg_score, 4),
                "avg_trust_score": round(avg_trust, 4),
                "total_posts": post_count,
                "total_engagement": stats["total_engagement"]
            })

        # Sort and add rank
        rankings.sort(key=lambda x: x["ranking_score"], reverse=True)
        for i, r in enumerate(rankings[:limit]):
            r["rank"] = i + 1

        return rankings[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/rankings/all-time")
async def get_alltime_rankings(limit: int = Query(default=100, ge=1, le=500)):
    """Get all-time author rankings"""
    try:
        signals = await db.query("social_posts", {
            "domain": f"eq.{settings.DOMAIN}",
            "select": "author,platform,final_score,trust_score,engagement,is_outlier,created_at"
        })

        if not signals:
            return []

        # Similar aggregation as weekly but with all data
        author_stats = {}
        for s in signals:
            author = s["author"]
            if author not in author_stats:
                author_stats[author] = {
                    "author": author,
                    "platform": s["platform"],
                    "scores": [],
                    "total_engagement": 0,
                    "outlier_count": 0,
                    "first_seen": s.get("created_at"),
                    "last_seen": s.get("created_at")
                }

            author_stats[author]["scores"].append(s.get("final_score", 0))
            author_stats[author]["total_engagement"] += s.get("engagement", 0)
            if s.get("is_outlier"):
                author_stats[author]["outlier_count"] += 1

        # Build rankings
        rankings = []
        for author, stats in author_stats.items():
            if len(stats["scores"]) < 3:  # Minimum activity threshold
                continue

            avg_score = sum(stats["scores"]) / len(stats["scores"])

            rankings.append({
                "rank": 0,
                "author": author,
                "platform": stats["platform"],
                "lifetime_avg_score": round(avg_score, 4),
                "total_posts": len(stats["scores"]),
                "total_engagement": stats["total_engagement"],
                "outlier_count": stats["outlier_count"]
            })

        rankings.sort(key=lambda x: x["lifetime_avg_score"], reverse=True)
        for i, r in enumerate(rankings[:limit]):
            r["rank"] = i + 1

        return rankings[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Content Efficiency
# -----------------------------------------------------------------------------

@app.post("/api/osint/content")
async def track_content(content: ContentInput):
    """Start tracking published content"""
    try:
        # Fetch research context
        research = await db.query("research_items", {
            "id": f"eq.{content.research_id}",
            "select": "*"
        })

        iqs = 0.5
        if research:
            r = research[0]
            iqs = calculate_input_quality_score(
                r.get("confidence", 0.5),
                r.get("novelty", 0.5),
                r.get("signal_strength", 0.5)
            )

        data = {
            "content_id": content.content_id,
            "research_id": content.research_id,
            "platform": content.platform.value,
            "content_url": content.content_url,
            "title": content.title,
            "published_at": content.published_at.isoformat() if content.published_at else datetime.utcnow().isoformat(),
            "input_quality_score": iqs,
            "tracking_status": "active",
            "domain": settings.DOMAIN
        }

        result = await db.insert("content_outputs", data)

        return {
            "status": "success",
            "content_id": content.content_id,
            "input_quality_score": round(iqs, 4),
            "tracking_started": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/content/efficiency", response_model=List[EfficiencyResponse])
async def get_content_efficiency(
    limit: int = Query(default=50, ge=1, le=200),
    min_efficiency: float = Query(default=0, ge=0)
):
    """Get content efficiency rankings"""
    try:
        params = {
            "domain": f"eq.{settings.DOMAIN}",
            "tracking_status": "eq.completed",
            "order": "efficiency.desc",
            "limit": str(limit)
        }

        if min_efficiency > 0:
            params["efficiency"] = f"gte.{min_efficiency}"

        results = await db.query("content_outputs", params)

        return [
            {
                "content_id": r["content_id"],
                "platform": r["platform"],
                "input_quality_score": r.get("input_quality_score", 0),
                "output_performance_score": r.get("output_performance_score", 0),
                "efficiency": r.get("efficiency", 0),
                "leverage_level": r.get("leverage_level", "low")
            }
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Learning Loop
# -----------------------------------------------------------------------------

@app.get("/api/osint/learning/latest")
async def get_latest_learning():
    """Get latest learning iteration data"""
    try:
        results = await db.query("learning_iterations", {
            "domain": f"eq.{settings.DOMAIN}",
            "order": "iteration_date.desc",
            "limit": "1"
        })

        if not results:
            return {"message": "No learning data available yet"}

        return results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/learning/weights")
async def get_current_weights():
    """Get current optimized weights"""
    try:
        results = await db.query("learning_iterations", {
            "domain": f"eq.{settings.DOMAIN}",
            "order": "iteration_date.desc",
            "limit": "1"
        })

        if not results:
            # Return default weights
            return {
                "platform_weights": {
                    "twitter": 1.0,
                    "linkedin": 1.0,
                    "reddit": 1.0,
                    "hackernews": 1.0
                },
                "timing_weights": {
                    "morning": 1.0,
                    "afternoon": 1.0,
                    "evening": 1.0
                },
                "topic_weights": {},
                "source": "default"
            }

        learning = results[0]
        return {
            "platform_weights": learning.get("platform_weights", {}),
            "timing_weights": learning.get("timing_weights", {}),
            "topic_weights": learning.get("topic_weights", {}),
            "source": "learned",
            "iteration": learning.get("iteration_number"),
            "last_updated": learning.get("iteration_date")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/learning/progress")
async def get_learning_progress(limit: int = Query(default=30, ge=1, le=100)):
    """Get learning progress over time"""
    try:
        results = await db.query("learning_iterations", {
            "domain": f"eq.{settings.DOMAIN}",
            "order": "iteration_date.desc",
            "limit": str(limit)
        })

        return {
            "iterations": results,
            "trend": "improving" if len(results) > 1 and
                results[0].get("mean_efficiency", 0) > results[-1].get("mean_efficiency", 0)
                else "stable"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# Analytics
# -----------------------------------------------------------------------------

@app.get("/api/osint/analytics/platform-comparison")
async def get_platform_comparison(days: int = Query(default=30, ge=1, le=90)):
    """Compare platform performance"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        signals = await db.query("social_posts", {
            "created_at": f"gte.{cutoff}",
            "domain": f"eq.{settings.DOMAIN}",
            "select": "platform,final_score,trust_score,engagement,is_outlier"
        })

        if not signals:
            return {}

        # Aggregate by platform
        platforms = {}
        for s in signals:
            p = s["platform"]
            if p not in platforms:
                platforms[p] = {
                    "platform": p,
                    "count": 0,
                    "scores": [],
                    "engagement": 0,
                    "outliers": 0
                }

            platforms[p]["count"] += 1
            platforms[p]["scores"].append(s.get("final_score", 0))
            platforms[p]["engagement"] += s.get("engagement", 0)
            if s.get("is_outlier"):
                platforms[p]["outliers"] += 1

        # Calculate metrics
        results = []
        for p, data in platforms.items():
            avg_score = sum(data["scores"]) / len(data["scores"])
            results.append({
                "platform": p,
                "signal_count": data["count"],
                "avg_score": round(avg_score, 4),
                "total_engagement": data["engagement"],
                "outlier_count": data["outliers"],
                "outlier_rate": round(data["outliers"] / data["count"], 4)
            })

        results.sort(key=lambda x: x["avg_score"], reverse=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/analytics/trend")
async def get_trend_analysis(days: int = Query(default=30, ge=1, le=90)):
    """Get daily trend analysis"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        signals = await db.query("social_posts", {
            "created_at": f"gte.{cutoff}",
            "domain": f"eq.{settings.DOMAIN}",
            "select": "created_at,final_score,engagement,is_outlier",
            "order": "created_at.asc"
        })

        if not signals:
            return []

        # Group by day
        daily = {}
        for s in signals:
            date = s["created_at"][:10]  # Extract date
            if date not in daily:
                daily[date] = {
                    "date": date,
                    "count": 0,
                    "scores": [],
                    "engagement": 0,
                    "outliers": 0
                }

            daily[date]["count"] += 1
            daily[date]["scores"].append(s.get("final_score", 0))
            daily[date]["engagement"] += s.get("engagement", 0)
            if s.get("is_outlier"):
                daily[date]["outliers"] += 1

        # Build trend data
        trend = []
        for date, data in sorted(daily.items()):
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            trend.append({
                "date": date,
                "signal_count": data["count"],
                "avg_score": round(avg_score, 4),
                "total_engagement": data["engagement"],
                "outlier_count": data["outliers"]
            })

        return trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
