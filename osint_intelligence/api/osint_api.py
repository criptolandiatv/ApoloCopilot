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
        """
        Initialize the Supabase client using global settings and prepare default request headers.
        
        Sets the instance URL and API key from the application settings and constructs default HTTP headers:
        `apikey`, `Authorization` (Bearer token), `Content-Type: application/json`, and `Prefer: return=representation`.
        """
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def query(self, table: str, params: Dict = None) -> List[Dict]:
        """
        Fetch rows from a REST table using optional query parameters.
        
        Parameters:
            table (str): Name of the REST table to query.
            params (Dict, optional): Query parameters to apply to the request (e.g., filters, pagination).
        
        Returns:
            List[Dict]: A list of rows returned by the REST endpoint, each row represented as a dictionary.
        
        Raises:
            httpx.HTTPStatusError: If the HTTP request fails or returns a non-success status.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                params=params or {}
            )
            response.raise_for_status()
            return response.json()

    async def insert(self, table: str, data: Dict) -> Dict:
        """
        Insert a record into the given Supabase table.
        
        Parameters:
            table (str): Name of the Supabase table to insert into.
            data (Dict): The JSON-serializable payload representing the row to insert.
        
        Returns:
            Dict: The inserted row as returned by Supabase (parsed from the JSON response).
        
        Raises:
            httpx.HTTPStatusError: If the HTTP request fails or returns a non-2xx status.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def rpc(self, function: str, params: Dict = None) -> Any:
        """
        Call a Supabase/PostgREST RPC endpoint and return the parsed JSON result.
        
        Parameters:
        	function (str): Name of the remote procedure (RPC) to invoke.
        	params (Dict, optional): JSON-serializable parameters to send as the RPC payload; defaults to an empty object.
        
        Returns:
        	result (Any): The response body decoded from JSON.
        
        Raises:
        	httpx.HTTPStatusError: If the HTTP response has a non-success status code.
        """
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
    """
    Compute an input quality score for a research item based on its confidence, novelty, and signal strength.
    
    Returns:
        float: A numeric score where higher values indicate higher input quality.
    """
    return (0.4 * confidence) + (0.4 * signal_strength) + (0.2 * novelty)

def calculate_trust_score(
    followers: int,
    verified: bool,
    platform: str
) -> float:
    """
    Estimate an author's trustworthiness from follower count, verification status, and platform.
    
    The function combines contributions from follower count, verification, and platform-specific weighting and returns a normalized score.
    
    Parameters:
        platform (str): Platform identifier (e.g., "twitter", "linkedin", "reddit", "hackernews"); unknown values receive a default platform weighting.
    
    Returns:
        float: Trust score between 0.0 and 1.0, where higher values indicate greater trustworthiness.
    """
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
    """
    Compute a normalized engagement velocity for a post.
    
    Calculates engagement per hour and scales it into the range 0.0–1.0. If hours_old is less than or equal to zero, uses engagement divided by 100 as a heuristic before applying the 1.0 cap.
    
    Parameters:
        engagement (int): Total engagement count (likes, comments, shares, etc.).
        hours_old (float): Age of the post in hours.
    
    Returns:
        float: A value between 0.0 and 1.0 representing the normalized engagement velocity; higher values indicate faster engagement.
    """
    if hours_old <= 0:
        return min(1.0, engagement / 100)
    velocity = engagement / hours_old
    return min(1.0, velocity / 100)

def calculate_final_score(
    trust_score: float,
    velocity: float,
    engagement: int
) -> float:
    """
    Combine trust, velocity, and engagement into a single social signal score.
    
    Parameters:
        trust_score (float): Author/platform trust metric (typically 0.0–1.0).
        velocity (float): Engagement velocity metric (higher means faster recent engagement).
        engagement (int): Raw engagement count for the post.
    
    Returns:
        float: Final composite score where higher values indicate a stronger social signal. The engagement contribution is scaled by trust and capped before being combined with trust and velocity.
    """
    trust_weighted = engagement * trust_score
    normalized_twe = min(1.0, trust_weighted / 1000)

    return (0.4 * trust_score) + (0.3 * velocity) + (0.3 * normalized_twe)

def calculate_efficiency(ops: float, iqs: float) -> float:
    """
    Compute content efficiency as the ratio of output to input quality.
    
    Parameters:
        ops (float): Output value or score produced by the content (e.g., engagement, conversions).
        iqs (float): Input Quality Score representing the quality or effort invested.
    
    Returns:
        efficiency (float): The ratio `ops / iqs`; returns 0 if `iqs` is less than or equal to 0.
    """
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
    """
    Provide current service health status with a UTC timestamp.
    
    Returns:
        dict: A dictionary containing:
            - status (str): Health status, e.g., "healthy".
            - timestamp (str): UTC timestamp in ISO 8601 format.
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# -----------------------------------------------------------------------------
# KPI Dashboard
# -----------------------------------------------------------------------------

@app.get("/api/osint/kpis", response_model=List[KPIResponse])
async def get_kpis(days: int = Query(default=7, ge=1, le=90)):
    """
    Retrieve KPI summaries for the given rolling window and compare each metric to the previous period.
    
    Parameters:
        days (int): Window length in days for the KPI query (1–90).
    
    Returns:
        A list of KPI summary records each containing fields such as `metric_name`, `current_value`, `previous_value`, and `change_percent`.
    """
    try:
        kpis = await db.rpc("get_kpi_summary", {"p_days": days, "p_domain": settings.DOMAIN})
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/osint/dashboard/summary")
async def get_dashboard_summary():
    """
    Builds a 7-day dashboard summary aggregating social signals, research items, and content outputs for the service domain.
    
    Returns:
        A dict containing aggregated metrics for the past 7 days:
        - period (str): Fixed value "7_days".
        - signals (dict):
            - total (int): Number of social signals considered.
            - outliers (int): Number of signals marked as outliers.
            - outlier_rate (float): Fraction of signals that are outliers (rounded to 4 decimals).
            - avg_score (float): Mean final score across signals (rounded to 4 decimals).
            - avg_trust (float): Mean trust score across signals (rounded to 4 decimals).
            - by_platform (dict): Counts of signals grouped by platform.
        - research (dict):
            - total (int): Number of research items considered.
            - actionable (int): Number of research items marked actionable.
            - actionable_rate (float): Fraction of research items that are actionable (rounded to 4 decimals).
            - avg_quality (float): Mean input quality score across research items (rounded to 4 decimals).
        - content (dict):
            - total (int): Number of content outputs considered.
            - high_leverage (int): Number of content items with leverage level "high".
            - avg_efficiency (float): Mean efficiency across content items (rounded to 4 decimals).
        - generated_at (str): ISO8601 UTC timestamp when the summary was produced.
    """
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
    """
    Create and store a new research item and compute its input quality score (IQS).
    
    Parameters:
        research (ResearchInput): Research payload containing topic, source, insight text, confidence, novelty, signal strength, insight_type, category, and tags.
    
    Returns:
        dict: Result object with keys:
            - status (str): "success" on successful insert.
            - research_id (int | None): ID of the inserted research row, or None if not available.
            - scores (dict): Score breakdown containing:
                - input_quality_score (float): IQS rounded to 4 decimal places.
                - confidence (float)
                - novelty (float)
                - signal_strength (float)
            - actionable (bool): `true` if IQS > 0.6, `false` otherwise.
    
    Raises:
        HTTPException: Raised with status 500 and an error detail if insertion or processing fails.
    """
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
    """
    Retrieve research items for the HealthTech domain applying optional filters.
    
    Parameters:
        limit (int): Maximum number of items to return (1–200).
        insight_type (Optional[InsightType]): Filter by insight type.
        actionable_only (bool): If true, return only items marked actionable.
        min_quality (float): Minimum input quality score (0.0–1.0) to include.
    
    Returns:
        List[dict]: Matching research item records as returned by the backend.
    
    Raises:
        HTTPException: If an unexpected error occurs while fetching data.
    """
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
    """
    Submit a social signal, compute trust/velocity/final scores, persist the record, and return the created ID with computed metrics.
    
    Parameters:
    	signal (SocialSignalInput): Social post data used to compute scores and create a stored social signal record.
    
    Returns:
    	dict: A response object with keys:
    		- "status": operation status string ("success" on success).
    		- "signal_id": stored record ID or `None` if unavailable.
    		- "scores": mapping with computed metrics:
    			- "trust_score": trust score (rounded to 4 decimals).
    			- "velocity": velocity score (rounded to 4 decimals).
    			- "final_score": combined final score (rounded to 4 decimals).
    			- "engagement": raw engagement value (likes + shares*2 + comments*3).
    
    Raises:
    	HTTPException: If an unexpected error occurs while computing scores or persisting the record (resulting in a 500 response).
    """
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
    """
    Retrieve social signal records filtered by platform, score, and outlier status.
    
    Parameters:
        platform (Optional[Platform]): Platform enum to filter results by platform.
        limit (int): Maximum number of records to return (1–200).
        outliers_only (bool): If true, return only signals flagged as outliers.
        min_score (float): Minimum `final_score` threshold (0.0–1.0) to include.
    
    Returns:
        List[dict]: Rows from the `social_posts` table matching the domain and provided filters.
    
    Raises:
        HTTPException: If an unexpected error occurs while querying the database.
    """
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
    """
    Finds statistical outliers among recent social signals.
    
    Parameters:
        days (int): Number of past days to analyze (1–30).
    
    Returns:
        result (dict): A mapping with:
            - outliers (list): Signals with final_score above the outlier threshold; each entry includes original signal fields plus `z_score` (rounded to 2 decimals) and `percentile` (integer).
            - statistics (dict|None): Aggregate stats for the analyzed window or `None` if no signals were found. When present, contains:
                - mean (float): Mean final_score (rounded to 4 decimals).
                - std_dev (float): Standard deviation of final_score (rounded to 4 decimals).
                - threshold (float): Outlier threshold used (mean + 1.5 * std_dev, rounded to 4 decimals).
                - total_analyzed (int): Number of signals analyzed.
                - outlier_count (int): Number of detected outliers.
    
    Raises:
        HTTPException: If an unexpected error occurs while querying or processing signals.
    """
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
    """
    Compute weekly author rankings based on social signals from the past seven days.
    
    Fetches social posts within the last 7 days for the configured domain, aggregates metrics by author, and computes a composite ranking score that blends average post score, average trust, consistency, and outlier ratio. If no signals are found in the window, returns an empty list.
    
    Parameters:
        limit (int): Maximum number of ranking entries to return (1–100).
    
    Returns:
        List[dict]: Ordered list of ranking entries. Each entry contains:
            - author: author identifier
            - platform: primary platform observed for the author
            - rank: 1-based rank position
            - ranking_score: composite ranking score (rounded to 4 decimals)
            - avg_post_score: average final_score for the author's posts (rounded to 4 decimals)
            - avg_trust_score: average trust_score for the author's posts (rounded to 4 decimals)
            - total_posts: number of posts considered
            - total_engagement: sum of engagement across the author's posts
    """
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
    """
    Compile all-time author rankings based on historical social signal metrics.
    
    Parameters:
        limit (int): Maximum number of ranked authors to return (between 1 and 500).
    
    Returns:
        List[dict]: Ordered list of ranking records. Each record contains:
            - rank (int): 1-based rank position.
            - author (str): Author identifier.
            - platform (str): Primary platform for the author from the dataset.
            - lifetime_avg_score (float): Author's average final score across all posts.
            - total_posts (int): Number of posts considered for the author (authors with fewer than 3 posts are excluded).
            - total_engagement (int): Sum of engagement across the author's posts.
            - outlier_count (int): Number of posts marked as outliers for the author.
    """
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
    """
    Begin tracking a published content item and persist its output record.
    
    Looks up the associated research (by content.research_id) to estimate an input quality score, creates a content_outputs record with tracking metadata, and returns the stored-content summary.
    
    Parameters:
        content (ContentInput): Content metadata to track; must include content_id and research_id.
    
    Returns:
        dict: {
            "status": "success",
            "content_id": str,                 # the provided content_id
            "input_quality_score": float,      # estimated input quality score rounded to 4 decimals
            "tracking_started": bool           # true when tracking record was created
        }
    
    Raises:
        HTTPException: If any error occurs while fetching research context or inserting the content record.
    """
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
    """
    Provide content efficiency rankings filtered and ordered by efficiency.
    
    Parameters:
        limit (int): Maximum number of results to return (1–200). Defaults to 50.
        min_efficiency (float): Minimum efficiency threshold; only items with efficiency >= this value are returned. Defaults to 0.
    
    Returns:
        List[dict]: Ordered list of content efficiency records. Each dict contains:
            - content_id (str): The tracked content identifier.
            - platform (str): The platform where the content was published.
            - input_quality_score (float): Estimated input quality score (IQS).
            - output_performance_score (float): Measured output performance score.
            - efficiency (float): Ratio of output performance to input quality.
            - leverage_level (str): Categorized leverage level ("low", "medium", "high").
    
    Raises:
        HTTPException: With status 500 if an unexpected error occurs while querying or processing results.
    """
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
    """
    Fetches the most recent learning iteration record for the configured domain.
    
    Queries the learning_iterations table and returns the newest record for settings.DOMAIN. If no record exists, returns a dictionary with a `message` key indicating no data is available.
    
    Returns:
        dict: The latest learning iteration record, or `{"message": "No learning data available yet"}` when none exists.
    
    Raises:
        HTTPException: On unexpected failures during the query.
    """
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
    """
    Retrieve the current learned optimization weights for platform, timing, and topics.
    
    If no learning iteration exists for the configured domain, returns sensible default weights and marks the source as "default"; otherwise returns the latest iteration's weights and metadata with source "learned".
    
    Returns:
        dict: A mapping containing:
            - platform_weights (dict): Per-platform weight values (e.g., {"twitter": 1.0, ...}).
            - timing_weights (dict): Time-of-day weight values (e.g., {"morning": 1.0, ...}).
            - topic_weights (dict): Per-topic weight values (may be empty).
            - source (str): "learned" when returned from the latest iteration, "default" when defaults are used.
            - iteration (int, optional): Iteration number of the learned weights when source is "learned".
            - last_updated (str, optional): ISO timestamp of the learning iteration when source is "learned".
    
    Raises:
        HTTPException: If the backend query fails or an unexpected error occurs.
    """
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
    """
    Fetch recent learning iterations and indicate whether mean efficiency shows an improving trend.
    
    Parameters:
        limit (int): Maximum number of iterations to return (1–100). Defaults to 30.
    
    Returns:
        dict: {
            "iterations": List of learning iteration records (most recent first),
            "trend": "improving" if the most recent mean_efficiency is greater than the oldest returned mean_efficiency and more than one iteration is present, otherwise "stable"
        }
    
    Raises:
        HTTPException: Raised with status code 500 if the database query fails.
    """
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
    """
    Produce per-platform comparison metrics over a recent time window.
    
    Parameters:
        days (int): Number of days to include in the comparison (1–90).
    
    Returns:
        list[dict] | dict: A list of platform summary objects sorted by `avg_score`. Each object contains:
            - platform: platform identifier
            - signal_count: number of signals considered
            - avg_score: average final score (rounded to 4 decimals)
            - total_engagement: sum of engagement values
            - outlier_count: number of signals marked as outliers
            - outlier_rate: proportion of outliers (rounded to 4 decimals)
        Returns an empty dict if no signals are found for the given window.
    
    Raises:
        HTTPException: If an unexpected error occurs while querying or processing data.
    """
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
    """
    Produce daily aggregated trend metrics for social signals over the past `days`.
    
    Parameters:
        days (int): Number of past days to include in the trend (minimum 1, maximum 90).
    
    Returns:
        List[dict]: Chronologically ordered list of daily metrics where each dict contains:
            - date (str): ISO date (YYYY-MM-DD).
            - signal_count (int): Number of signals for that day.
            - avg_score (float): Average `final_score` for signals on that day (rounded to 4 decimals).
            - total_engagement (int): Sum of engagement values for that day.
            - outlier_count (int): Number of signals flagged as outliers that day.
    
    Raises:
        HTTPException: If an unexpected error occurs while fetching or processing signals.
    """
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