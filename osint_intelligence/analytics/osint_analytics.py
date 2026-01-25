"""
OSINT Intelligence Analytics Engine
HealthTech Domain - Statistical Analysis & Metrics
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ScoreMetrics:
    """Input Quality Score (IQS) metrics"""
    confidence: float = 0.5
    novelty: float = 0.5
    signal_strength: float = 0.5

    @property
    def iqs(self) -> float:
        """Calculate Input Quality Score"""
        return (0.4 * self.confidence) + (0.4 * self.signal_strength) + (0.2 * self.novelty)


@dataclass
class PerformanceMetrics:
    """Output Performance Score (OPS) metrics"""
    engagement_rate: float = 0.0
    velocity: float = 0.0
    trust_engagement: float = 0.0

    @property
    def ops(self) -> float:
        """Calculate Output Performance Score"""
        return (0.5 * self.engagement_rate) + (0.3 * self.velocity) + (0.2 * self.trust_engagement)


@dataclass
class SocialSignal:
    """Social media signal data"""
    platform: str
    author: str
    post_id: str
    content: str
    followers: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    verified: bool = False
    created_at: Optional[datetime] = None

    @property
    def engagement(self) -> int:
        """Calculate total engagement"""
        return self.likes + (self.shares * 2) + (self.comments * 3)


@dataclass
class AnalysisResult:
    """Analysis result container"""
    metric_name: str
    value: float
    confidence_interval: Tuple[float, float] = None
    sample_size: int = 0
    metadata: Dict = field(default_factory=dict)


# =============================================================================
# CORE ANALYTICS ENGINE
# =============================================================================

class OSINTAnalytics:
    """Main analytics engine for OSINT intelligence"""

    # Platform trust weights
    PLATFORM_TRUST = {
        "twitter": 0.30,
        "linkedin": 0.40,
        "hackernews": 0.35,
        "reddit": 0.25
    }

    def __init__(self):
        self.cache = {}

    # -------------------------------------------------------------------------
    # SCORE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_input_quality_score(
        self,
        confidence: float,
        novelty: float,
        signal_strength: float
    ) -> float:
        """
        Calculate IQS (Input Quality Score)

        Formula: IQS = 0.4*confidence + 0.4*signal_strength + 0.2*novelty

        Args:
            confidence: Research confidence (0-1)
            novelty: Information novelty (0-1)
            signal_strength: Signal strength (0-1)

        Returns:
            IQS value between 0 and 1
        """
        confidence = np.clip(confidence, 0, 1)
        novelty = np.clip(novelty, 0, 1)
        signal_strength = np.clip(signal_strength, 0, 1)

        return (0.4 * confidence) + (0.4 * signal_strength) + (0.2 * novelty)

    def calculate_output_performance_score(
        self,
        engagement_rate: float,
        velocity: float,
        trust_engagement: float
    ) -> float:
        """
        Calculate OPS (Output Performance Score)

        Formula: OPS = 0.5*engagement_rate + 0.3*velocity + 0.2*trust_engagement

        Args:
            engagement_rate: Normalized engagement rate (0-1)
            velocity: Engagement velocity (0-1)
            trust_engagement: Trust-weighted engagement (0-1)

        Returns:
            OPS value between 0 and 1
        """
        engagement_rate = np.clip(engagement_rate, 0, 1)
        velocity = np.clip(velocity, 0, 1)
        trust_engagement = np.clip(trust_engagement, 0, 1)

        return (0.5 * engagement_rate) + (0.3 * velocity) + (0.2 * trust_engagement)

    def calculate_trust_score(
        self,
        followers: int,
        verified: bool,
        platform: str
    ) -> float:
        """
        Calculate trust score for social signal

        Components:
        - Follower score (log scale, max 0.4)
        - Verification bonus (0.2 if verified)
        - Platform trust (varies by platform)

        Args:
            followers: Number of followers
            verified: Whether account is verified
            platform: Social platform name

        Returns:
            Trust score between 0 and 1
        """
        # Follower trust (logarithmic scale)
        follower_score = min(0.4, np.log10(max(1, followers)) / 15)

        # Verification bonus
        verification_bonus = 0.2 if verified else 0

        # Platform trust
        platform_score = self.PLATFORM_TRUST.get(platform.lower(), 0.2)

        # Normalize to 0-1
        total = follower_score + verification_bonus + platform_score
        max_possible = 0.4 + 0.2 + 0.4

        return total / max_possible

    def calculate_velocity(
        self,
        engagement: int,
        hours_since_post: float
    ) -> float:
        """
        Calculate engagement velocity (engagement per hour)

        Args:
            engagement: Total engagement count
            hours_since_post: Hours since post was created

        Returns:
            Normalized velocity score (0-1)
        """
        if hours_since_post <= 0:
            return min(1.0, engagement / 100)

        velocity = engagement / hours_since_post
        return min(1.0, velocity / 100)  # Normalize assuming 100/hr is max

    def calculate_efficiency(
        self,
        ops: float,
        iqs: float
    ) -> float:
        """
        Calculate content efficiency (ROI)

        Formula: Efficiency = OPS / IQS

        High efficiency means low input produced high output (leverage)

        Args:
            ops: Output Performance Score
            iqs: Input Quality Score

        Returns:
            Efficiency ratio (can be > 1 for high performers)
        """
        if iqs <= 0:
            return 0.0
        return ops / iqs

    def calculate_final_score(
        self,
        trust_score: float,
        velocity: float,
        engagement: int
    ) -> float:
        """
        Calculate final social signal score

        Formula: 0.4*trust + 0.3*velocity + 0.3*normalized_trust_weighted_engagement

        Args:
            trust_score: Trust score (0-1)
            velocity: Velocity score (0-1)
            engagement: Raw engagement count

        Returns:
            Final score (0-1)
        """
        trust_weighted = engagement * trust_score
        normalized_twe = min(1.0, trust_weighted / 1000)

        return (0.4 * trust_score) + (0.3 * velocity) + (0.3 * normalized_twe)

    # -------------------------------------------------------------------------
    # STATISTICAL ANALYSIS
    # -------------------------------------------------------------------------

    def detect_outliers(
        self,
        values: List[float],
        threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Detect statistical outliers using z-score method

        Args:
            values: List of numeric values
            threshold: Z-score threshold for outlier detection (default 1.5)

        Returns:
            Dictionary with outlier analysis results
        """
        if not values or len(values) < 3:
            return {"outliers": [], "statistics": None}

        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return {
                "outliers": [],
                "statistics": {
                    "mean": float(mean),
                    "std_dev": 0,
                    "threshold": float(mean),
                    "count": len(values)
                }
            }

        z_scores = (arr - mean) / std
        outlier_threshold = mean + (threshold * std)

        outliers = []
        for i, (val, z) in enumerate(zip(values, z_scores)):
            if val > outlier_threshold:
                outliers.append({
                    "index": i,
                    "value": val,
                    "z_score": float(z),
                    "percentile": float(stats.percentileofscore(values, val))
                })

        return {
            "outliers": outliers,
            "statistics": {
                "mean": float(mean),
                "std_dev": float(std),
                "threshold": float(outlier_threshold),
                "count": len(values),
                "outlier_count": len(outliers),
                "outlier_rate": len(outliers) / len(values)
            }
        }

    def calculate_correlation(
        self,
        x: List[float],
        y: List[float]
    ) -> Dict[str, float]:
        """
        Calculate Pearson correlation between two variables

        Args:
            x: First variable values
            y: Second variable values

        Returns:
            Dictionary with correlation coefficient and p-value
        """
        if len(x) != len(y) or len(x) < 3:
            return {"correlation": None, "p_value": None, "r_squared": None}

        correlation, p_value = stats.pearsonr(x, y)

        return {
            "correlation": float(correlation),
            "p_value": float(p_value),
            "r_squared": float(correlation ** 2),
            "sample_size": len(x)
        }

    def calculate_ranking_score(
        self,
        avg_score: float,
        avg_trust: float,
        consistency: float,
        outlier_ratio: float
    ) -> float:
        """
        Calculate author ranking score

        Formula:
        - 40% average post score
        - 25% trust score
        - 20% consistency
        - 15% outlier ratio

        Args:
            avg_score: Average post score
            avg_trust: Average trust score
            consistency: Consistency score (1 - normalized std dev)
            outlier_ratio: Ratio of outlier posts

        Returns:
            Ranking score (0-1)
        """
        return (
            0.40 * avg_score +
            0.25 * avg_trust +
            0.20 * consistency +
            0.15 * outlier_ratio
        )

    def calculate_consistency(
        self,
        scores: List[float]
    ) -> float:
        """
        Calculate consistency score (lower variance = more consistent)

        Args:
            scores: List of scores

        Returns:
            Consistency score (0-1, higher is more consistent)
        """
        if not scores or len(scores) < 2:
            return 1.0

        mean = np.mean(scores)
        if mean == 0:
            return 1.0

        std = np.std(scores)
        coefficient_of_variation = std / mean

        # Convert to consistency (lower CV = higher consistency)
        return 1 - min(1, coefficient_of_variation)

    # -------------------------------------------------------------------------
    # TREND ANALYSIS
    # -------------------------------------------------------------------------

    def analyze_trend(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]] = None
    ) -> Dict[str, Any]:
        """
        Analyze trend in time series data

        Args:
            values: List of metric values
            timestamps: Optional list of timestamps

        Returns:
            Trend analysis results
        """
        if not values or len(values) < 3:
            return {"trend": "insufficient_data"}

        arr = np.array(values)
        x = np.arange(len(arr))

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, arr)

        # Moving averages
        window = min(7, len(arr) // 2)
        if window >= 2:
            ma = pd.Series(arr).rolling(window=window).mean().dropna().tolist()
        else:
            ma = values

        # Determine trend direction
        if p_value < 0.05:  # Statistically significant
            if slope > 0:
                trend_direction = "increasing"
            elif slope < 0:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        return {
            "trend": trend_direction,
            "slope": float(slope),
            "r_squared": float(r_value ** 2),
            "p_value": float(p_value),
            "moving_average": ma,
            "first_value": float(arr[0]),
            "last_value": float(arr[-1]),
            "change_percent": float((arr[-1] - arr[0]) / arr[0] * 100) if arr[0] != 0 else 0
        }

    # -------------------------------------------------------------------------
    # PLATFORM ANALYSIS
    # -------------------------------------------------------------------------

    def compare_platforms(
        self,
        signals: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Compare performance across platforms

        Args:
            signals: List of social signal dictionaries

        Returns:
            Platform comparison results
        """
        platforms = {}

        for signal in signals:
            platform = signal.get("platform", "unknown")
            if platform not in platforms:
                platforms[platform] = {
                    "count": 0,
                    "scores": [],
                    "engagement": 0,
                    "outliers": 0
                }

            platforms[platform]["count"] += 1
            platforms[platform]["scores"].append(signal.get("final_score", 0))
            platforms[platform]["engagement"] += signal.get("engagement", 0)
            if signal.get("is_outlier"):
                platforms[platform]["outliers"] += 1

        # Calculate metrics for each platform
        results = {}
        for platform, data in platforms.items():
            scores = data["scores"]
            results[platform] = {
                "signal_count": data["count"],
                "avg_score": float(np.mean(scores)) if scores else 0,
                "std_score": float(np.std(scores)) if len(scores) > 1 else 0,
                "total_engagement": data["engagement"],
                "outlier_count": data["outliers"],
                "outlier_rate": data["outliers"] / data["count"] if data["count"] > 0 else 0
            }

        return results

    # -------------------------------------------------------------------------
    # LEARNING LOOP
    # -------------------------------------------------------------------------

    def calculate_weight_adjustments(
        self,
        performance_data: Dict[str, Dict],
        current_weights: Dict[str, float],
        learning_rate: float = 0.1
    ) -> Dict[str, float]:
        """
        Calculate weight adjustments based on performance

        Implements cumulative advantage from Outliers theory

        Args:
            performance_data: Performance metrics by category
            current_weights: Current weight values
            learning_rate: How aggressively to adjust (0-1)

        Returns:
            Updated weights dictionary
        """
        updated_weights = current_weights.copy()

        # Calculate performance ratios
        total_outliers = sum(
            d.get("outlier_count", 0) for d in performance_data.values()
        )

        if total_outliers == 0:
            return updated_weights

        for category, data in performance_data.items():
            if category not in updated_weights:
                continue

            # Performance ratio vs expected equal distribution
            expected_ratio = 1 / len(performance_data)
            actual_ratio = data.get("outlier_count", 0) / total_outliers

            # Calculate adjustment
            # Higher performers get weight increase, lower get decrease
            adjustment = (actual_ratio - expected_ratio) * learning_rate

            # Apply bounded adjustment (prevent extreme swings)
            new_weight = current_weights.get(category, 1.0) * (1 + adjustment)
            updated_weights[category] = max(0.5, min(2.0, new_weight))

        return updated_weights

    def identify_success_patterns(
        self,
        high_performers: List[Dict],
        low_performers: List[Dict]
    ) -> Dict[str, Any]:
        """
        Identify patterns that distinguish high vs low performers

        Args:
            high_performers: List of high-performing items
            low_performers: List of low-performing items

        Returns:
            Pattern analysis results
        """
        patterns = {
            "high_performers": self._extract_patterns(high_performers),
            "low_performers": self._extract_patterns(low_performers),
            "differentiators": []
        }

        # Find differentiating factors
        hp = patterns["high_performers"]
        lp = patterns["low_performers"]

        # Platform differences
        for platform in set(hp.get("platforms", {}).keys()) | set(lp.get("platforms", {}).keys()):
            hp_rate = hp.get("platforms", {}).get(platform, 0)
            lp_rate = lp.get("platforms", {}).get(platform, 0)
            if abs(hp_rate - lp_rate) > 0.1:
                patterns["differentiators"].append({
                    "factor": f"platform_{platform}",
                    "high_performer_rate": hp_rate,
                    "low_performer_rate": lp_rate,
                    "recommendation": "focus" if hp_rate > lp_rate else "avoid"
                })

        return patterns

    def _extract_patterns(self, items: List[Dict]) -> Dict:
        """Extract patterns from a list of items"""
        if not items:
            return {}

        platforms = {}
        topics = {}
        timings = {}

        for item in items:
            # Platform distribution
            platform = item.get("platform", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1

            # Topic distribution
            topic = item.get("research_topic", item.get("topic", "unknown"))
            if topic:
                topics[topic] = topics.get(topic, 0) + 1

            # Timing distribution
            created = item.get("created_at") or item.get("published_at")
            if created:
                if isinstance(created, str):
                    try:
                        created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    except:
                        created = None
                if created:
                    hour = created.hour
                    timing = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
                    timings[timing] = timings.get(timing, 0) + 1

        # Normalize to rates
        total = len(items)
        return {
            "platforms": {k: v/total for k, v in platforms.items()},
            "topics": {k: v/total for k, v in topics.items()},
            "timings": {k: v/total for k, v in timings.items()},
            "count": total
        }

    # -------------------------------------------------------------------------
    # BATCH PROCESSING
    # -------------------------------------------------------------------------

    def process_signals_batch(
        self,
        signals: List[SocialSignal]
    ) -> pd.DataFrame:
        """
        Process a batch of social signals and return analyzed DataFrame

        Args:
            signals: List of SocialSignal objects

        Returns:
            DataFrame with all calculated metrics
        """
        records = []

        for signal in signals:
            trust_score = self.calculate_trust_score(
                signal.followers,
                signal.verified,
                signal.platform
            )

            hours_old = 0
            if signal.created_at:
                delta = datetime.utcnow() - signal.created_at
                hours_old = delta.total_seconds() / 3600

            velocity = self.calculate_velocity(signal.engagement, hours_old)
            final_score = self.calculate_final_score(
                trust_score,
                velocity,
                signal.engagement
            )

            records.append({
                "platform": signal.platform,
                "author": signal.author,
                "post_id": signal.post_id,
                "followers": signal.followers,
                "engagement": signal.engagement,
                "verified": signal.verified,
                "trust_score": trust_score,
                "velocity": velocity,
                "final_score": final_score,
                "hours_old": hours_old,
                "created_at": signal.created_at
            })

        df = pd.DataFrame(records)

        # Detect outliers
        if len(df) > 2:
            outlier_analysis = self.detect_outliers(df["final_score"].tolist())
            outlier_indices = {o["index"] for o in outlier_analysis["outliers"]}
            df["is_outlier"] = df.index.isin(outlier_indices)

            # Add z-scores
            mean = df["final_score"].mean()
            std = df["final_score"].std()
            df["z_score"] = (df["final_score"] - mean) / std if std > 0 else 0
            df["percentile"] = df["final_score"].rank(pct=True) * 100
        else:
            df["is_outlier"] = False
            df["z_score"] = 0
            df["percentile"] = 50

        return df

    def generate_rankings(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate author rankings from signal DataFrame

        Args:
            df: DataFrame with processed signals

        Returns:
            Rankings DataFrame
        """
        rankings = df.groupby(["author", "platform"]).agg({
            "final_score": ["mean", "std", "count"],
            "trust_score": "mean",
            "engagement": "sum",
            "is_outlier": "sum"
        }).reset_index()

        # Flatten column names
        rankings.columns = [
            "author", "platform", "avg_score", "score_std", "post_count",
            "avg_trust", "total_engagement", "outlier_count"
        ]

        # Calculate derived metrics
        rankings["consistency"] = rankings.apply(
            lambda r: 1 - min(1, r["score_std"] / r["avg_score"]) if r["avg_score"] > 0 else 1,
            axis=1
        )
        rankings["outlier_ratio"] = rankings["outlier_count"] / rankings["post_count"]

        # Calculate ranking score
        rankings["ranking_score"] = rankings.apply(
            lambda r: self.calculate_ranking_score(
                r["avg_score"],
                r["avg_trust"],
                r["consistency"],
                r["outlier_ratio"]
            ),
            axis=1
        )

        # Sort and rank
        rankings = rankings.sort_values("ranking_score", ascending=False)
        rankings["rank"] = range(1, len(rankings) + 1)

        return rankings


# =============================================================================
# VISUALIZATION HELPERS
# =============================================================================

class VisualizationHelper:
    """Helper class for generating visualization data"""

    @staticmethod
    def prepare_scatter_data(df: pd.DataFrame, x: str, y: str) -> List[Dict]:
        """Prepare data for scatter plot"""
        return df[[x, y]].dropna().to_dict("records")

    @staticmethod
    def prepare_time_series(df: pd.DataFrame, value_col: str, date_col: str) -> Dict:
        """Prepare data for time series chart"""
        grouped = df.groupby(pd.to_datetime(df[date_col]).dt.date)[value_col].mean()
        return {
            "dates": [d.isoformat() for d in grouped.index],
            "values": grouped.values.tolist()
        }

    @staticmethod
    def prepare_platform_distribution(df: pd.DataFrame) -> Dict:
        """Prepare data for platform distribution chart"""
        counts = df["platform"].value_counts()
        return {
            "labels": counts.index.tolist(),
            "values": counts.values.tolist()
        }


# =============================================================================
# MAIN EXPORTS
# =============================================================================

def create_analytics_engine() -> OSINTAnalytics:
    """Factory function to create analytics engine"""
    return OSINTAnalytics()


# Example usage
if __name__ == "__main__":
    # Initialize engine
    analytics = create_analytics_engine()

    # Example: Calculate scores
    iqs = analytics.calculate_input_quality_score(
        confidence=0.8,
        novelty=0.6,
        signal_strength=0.7
    )
    print(f"Input Quality Score: {iqs:.4f}")

    # Example: Process signals
    signals = [
        SocialSignal(
            platform="twitter",
            author="@example",
            post_id="123",
            content="Test post",
            followers=10000,
            likes=50,
            shares=10,
            comments=5,
            verified=True,
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        for _ in range(10)
    ]

    df = analytics.process_signals_batch(signals)
    print(f"\nProcessed {len(df)} signals")
    print(df[["author", "trust_score", "final_score", "is_outlier"]].head())

    # Example: Generate rankings
    rankings = analytics.generate_rankings(df)
    print(f"\nRankings:")
    print(rankings[["rank", "author", "ranking_score", "post_count"]].head())
