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
        """
        Compute the input quality score as a weighted aggregate of confidence, signal strength, and novelty.
        
        Returns:
            float: Input Quality Score between 0.0 and 1.0 representing the combined quality of the input.
        """
        return (0.4 * self.confidence) + (0.4 * self.signal_strength) + (0.2 * self.novelty)


@dataclass
class PerformanceMetrics:
    """Output Performance Score (OPS) metrics"""
    engagement_rate: float = 0.0
    velocity: float = 0.0
    trust_engagement: float = 0.0

    @property
    def ops(self) -> float:
        """
        Compute the Output Performance Score as a weighted combination of engagement rate, velocity, and trust engagement.
        
        Returns:
            float: Output Performance Score computed as 0.5 * engagement_rate + 0.3 * velocity + 0.2 * trust_engagement.
        """
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
        """
        Compute an aggregated engagement score from likes, shares, and comments.
        
        Returns:
            aggregated_engagement (int): Total engagement as a single integer value.
        """
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
        """
        Initialize the OSINTAnalytics instance.
        
        Creates an empty in-memory cache stored on the instance as `self.cache` for short-term storage of computed results.
        """
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
        Compute the Input Quality Score (IQS) from confidence, novelty, and signal strength.
        
        Input values outside the 0–1 range are clamped to that range before scoring.
        
        Parameters:
            confidence (float): Research or signal confidence, expected 0–1.
            novelty (float): Information novelty or uniqueness, expected 0–1.
            signal_strength (float): Measured strength of the signal, expected 0–1.
        
        Returns:
            float: IQS value between 0 and 1 computed as 0.4*confidence + 0.4*signal_strength + 0.2*novelty.
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
        Compute the Output Performance Score (OPS) from engagement rate, velocity, and trust-weighted engagement.
        
        Each input is treated as a normalized value between 0 and 1 and clipped to that range before scoring.
        
        Parameters:
            engagement_rate (float): Normalized engagement rate (0 to 1).
            velocity (float): Engagement velocity normalized to 0 to 1.
            trust_engagement (float): Trust-weighted engagement normalized to 0 to 1.
        
        Returns:
            float: OPS value between 0 and 1.
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
        Estimate a normalized trust score for a social signal.
        
        Parameters:
        	followers (int): Number of followers for the account.
        	verified (bool): Whether the account is verified.
        	platform (str): Social platform name; lookup is case-insensitive and unknown platforms use a default platform weight.
        
        Returns:
        	float: Trust score in the range 0.0 to 1.0, where higher values indicate greater trust.
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
        Compute a normalized engagement velocity score from total engagement and post age.
        
        Parameters:
            engagement (int): Total engagement count for the post.
            hours_since_post (float): Hours elapsed since the post was created; if zero or negative, the function treats the age as instantaneous for normalization.
        
        Returns:
            float: Normalized velocity score between 0.0 and 1.0 where higher values indicate faster engagement.
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
        Compute efficiency as the ratio of output performance to input quality.
        
        Represents leverage where values greater than 1 indicate outputs exceed inputs.
        
        Parameters:
            ops (float): Output Performance Score.
            iqs (float): Input Quality Score.
        
        Returns:
            float: Efficiency ratio (ops / iqs). Returns 0.0 if iqs is less than or equal to 0.
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
        Compute a combined final score for a social signal.
        
        The score mixes trust, velocity, and a trust-weighted engagement component (engagement multiplied by trust_score, scaled and capped to the [0,1] range) into a single value in [0,1].
        
        Parameters:
            trust_score (float): Trust weight between 0 and 1.
            velocity (float): Velocity score between 0 and 1.
            engagement (int): Raw engagement count (e.g., likes + shares + comments).
        
        Returns:
            float: Final score between 0 and 1.
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
        Identify high-value statistical outliers in a numeric sequence using a z-score cutoff.
        
        Requires at least three values; if fewer are provided the function returns {"outliers": [], "statistics": None}. If all values have zero standard deviation the function returns no outliers and a statistics dict with std_dev 0 and threshold equal to the mean.
        
        Parameters:
            values (List[float]): Sequence of numeric values to analyze.
            threshold (float): Multiplier of the standard deviation to define the outlier cutoff (default 1.5).
        
        Returns:
            Dict[str, Any]: Dictionary with two keys:
                - "outliers": list of outlier records, each containing:
                    - "index": index of the outlier in the input list
                    - "value": the outlier value
                    - "z_score": z-score of the value
                    - "percentile": percentile of the value within the input list
                - "statistics": summary statistics or None. When present includes:
                    - "mean": mean of the input values
                    - "std_dev": standard deviation
                    - "threshold": numeric cutoff used to classify outliers
                    - "count": total number of input values
                    - "outlier_count": number of detected outliers
                    - "outlier_rate": outlier_count / count
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
        Compute the Pearson correlation between two numeric vectors.
        
        Parameters:
            x (List[float]): Values of the first variable; must have the same length as `y` and at least 3 elements.
            y (List[float]): Values of the second variable; must have the same length as `x` and at least 3 elements.
        
        Returns:
            dict: {
                "correlation": Pearson correlation coefficient as a float, or `None` if inputs are invalid;
                "p_value": two-tailed p-value for the test of non-correlation as a float, or `None` if inputs are invalid;
                "r_squared": coefficient of determination (correlation squared) as a float, or `None` if inputs are invalid;
                "sample_size": number of paired observations (int) when valid
            }
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
        Compute a composite ranking score for an author using averaged metrics.
        
        Parameters:
            avg_score (float): Average post score for the author.
            avg_trust (float): Average trust score for the author.
            consistency (float): Consistency metric (higher means more consistent).
            outlier_ratio (float): Proportion of the author's posts classified as outliers.
        
        Returns:
            float: Ranking score between 0 and 1.
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
        Compute a consistency score for a series of numeric scores where lower relative variance indicates higher consistency.
        
        Returns:
            consistency (float): Value between 0 and 1; `1.0` indicates perfect or undefined variability (used when fewer than two scores or mean equals zero), values closer to 0 indicate greater relative variability.
        
        Parameters:
            scores (List[float]): Sequence of numeric scores to evaluate.
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
        Determine trend direction and compute basic trend statistics for a numeric series.
        
        Parameters:
            values (List[float]): Ordered sequence of numeric observations (length must be >= 3).
            timestamps (Optional[List[datetime]]): Optional timestamps corresponding to values; provided for context but not required.
        
        Returns:
            dict: Analysis results containing:
                - trend (str): One of "increasing", "decreasing", or "stable" indicating the trend direction.
                - slope (float): Estimated slope of the fitted linear trend.
                - r_squared (float): Coefficient of determination for the fitted trend.
                - p_value (float): Two-sided p-value for the slope (trend) estimate.
                - moving_average (List[float]): Short-window moving average series (may be the original values if window is too small).
                - first_value (float): First value of the input series.
                - last_value (float): Last value of the input series.
                - change_percent (float): Percentage change from first to last value (0 if first value is 0).
        
        If fewer than three values are provided, returns {"trend": "insufficient_data"}.
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
        Compute per-platform aggregate metrics from a list of social signal records.
        
        Parameters:
            signals (List[Dict]): Iterable of signal dictionaries. Each dictionary is expected to contain at least the keys:
                - "platform": platform name (str)
                - "final_score": numeric score for the signal
                - "engagement": numeric engagement value for the signal
                - "is_outlier": boolean flag indicating whether the signal is an outlier
        
        Returns:
            Dict[str, Dict]: Mapping from platform name to a metrics dictionary containing:
                - "signal_count" (int): number of signals for the platform
                - "avg_score" (float): mean of `final_score` values (0 if none)
                - "std_score" (float): standard deviation of `final_score` values (0 if fewer than 2)
                - "total_engagement" (int/float): sum of `engagement` values
                - "outlier_count" (int): number of signals marked as outliers
                - "outlier_rate" (float): outlier_count divided by signal_count (0 if signal_count is 0)
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
        Adjusts category weights based on observed outlier counts to emphasize categories with higher outlier rates.
        
        Parameters:
        	performance_data (Dict[str, Dict]): Mapping of category to metrics dictionary; expects an integer "outlier_count" key for each category.
        	current_weights (Dict[str, float]): Existing weights keyed by category; categories not present are ignored.
        	learning_rate (float): Fractional scaling of adjustments (0 to 1) that controls how aggressively weights are changed.
        
        Returns:
        	Dict[str, float]: New weights keyed by category. Each weight is scaled relative to the original and clamped to the range [0.5, 2.0].
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
        Extracts characteristic patterns from high- and low-performing items and identifies platform-level differentiators.
        
        Parameters:
            high_performers (List[Dict]): List of records representing high-performing items (each record should include at least a "platform" key; other keys like topics or timestamps may be used by pattern extraction).
            low_performers (List[Dict]): List of records representing low-performing items (same structure as high_performers).
        
        Returns:
            Dict[str, Any]: A mapping with keys:
                - "high_performers": normalized pattern distributions for the high-performing set (platforms, topics, timings, count).
                - "low_performers": normalized pattern distributions for the low-performing set (platforms, topics, timings, count).
                - "differentiators": list of factors that differ between the two sets; each entry contains:
                    - "factor": identifier for the differentiator (e.g., "platform_<name>"),
                    - "high_performer_rate": rate for the high-performing group,
                    - "low_performer_rate": rate for the low-performing group,
                    - "recommendation": "focus" when the factor is more prevalent among high performers, otherwise "avoid".
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
        """
        Aggregate categorical distributions for platform, topic, and posting time from a list of item records.
        
        Parameters:
            items (List[Dict]): Sequence of item records. Each item may include:
                - 'platform' (str): platform name.
                - 'research_topic' or 'topic' (str): topic label.
                - 'created_at' or 'published_at' (datetime or ISO-8601 str): timestamp of the item.
              Missing fields are treated as "unknown"; unparsable timestamp strings are ignored for timing.
        
        Returns:
            Dict: A dictionary with:
                - 'platforms': mapping of platform -> relative frequency (0.0-1.0).
                - 'topics': mapping of topic -> relative frequency (0.0-1.0).
                - 'timings': mapping of timing bucket -> relative frequency (0.0-1.0). Timing buckets are:
                    'morning' (hour < 12), 'afternoon' (12 <= hour < 17), 'evening' (hour >= 17).
                  Items without valid timestamps are excluded from timing counts.
                - 'count': total number of input items.
        """
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
        Aggregate a list of SocialSignal objects into a DataFrame with computed trust, velocity, final score, and outlier annotations.
        
        Parameters:
            signals (List[SocialSignal]): SocialSignal instances to process.
        
        Returns:
            pd.DataFrame: DataFrame containing one row per signal with columns:
                - platform: source platform name
                - author: author identifier
                - post_id: post identifier
                - followers: follower count
                - engagement: computed engagement value from the signal
                - verified: verification status (bool)
                - trust_score: computed trust score for the author/platform
                - velocity: engagement per hour metric
                - final_score: aggregated final score combining trust, velocity, and engagement
                - hours_old: age of the post in hours (0 if created_at missing or in future)
                - created_at: original timestamp from the signal
                - is_outlier: boolean flag set when the final_score is detected as an outlier (z-score based)
                - z_score: standardized final_score (0 when variance is zero or insufficient rows)
                - percentile: percentile rank of final_score in the batch (0-100)
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
        Generate a per-author-and-platform ranking table from processed signal records.
        
        Parameters:
            df (pd.DataFrame): Processed signals with columns: 'author', 'platform', 'final_score', 'trust_score', 'engagement', and 'is_outlier'.
        
        Returns:
            pd.DataFrame: Rankings table with columns:
                - author: author identifier
                - platform: platform name
                - avg_score: mean of final_score for the group
                - score_std: standard deviation of final_score for the group
                - post_count: number of posts for the group
                - avg_trust: mean trust_score for the group
                - total_engagement: sum of engagement for the group
                - outlier_count: count of posts marked as outliers
                - consistency: consistency metric in [0,1], higher is more consistent
                - outlier_ratio: fraction of posts that are outliers
                - ranking_score: composite ranking score used for ordering
                - rank: integer rank (1 = highest ranking_score)
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
        """
        Prepare a list of point records for a scatter plot using two DataFrame columns.
        
        Parameters:
            df (pd.DataFrame): Source DataFrame containing the columns.
            x (str): Column name for the x-axis values.
            y (str): Column name for the y-axis values.
        
        Returns:
            records (List[Dict]): List of dictionaries with keys `x` and `y` (column names) for rows where both values are present.
        """
        return df[[x, y]].dropna().to_dict("records")

    @staticmethod
    def prepare_time_series(df: pd.DataFrame, value_col: str, date_col: str) -> Dict:
        """
        Aggregate a numeric column by calendar date and return aligned date and mean-value series.
        
        Parameters:
            df (pd.DataFrame): Input DataFrame containing the date and value columns.
            value_col (str): Name of the numeric column to aggregate (mean).
            date_col (str): Name of the column containing datetimes or date-like values; values are converted to calendar dates.
        
        Returns:
            Dict: A dictionary with:
                - "dates" (List[str]): ISO-formatted calendar date strings in ascending order.
                - "values" (List[float]): Mean of `value_col` for each corresponding date.
        """
        grouped = df.groupby(pd.to_datetime(df[date_col]).dt.date)[value_col].mean()
        return {
            "dates": [d.isoformat() for d in grouped.index],
            "values": grouped.values.tolist()
        }

    @staticmethod
    def prepare_platform_distribution(df: pd.DataFrame) -> Dict:
        """
        Prepare labels and values for a platform distribution chart from a DataFrame.
        
        Parameters:
            df (pd.DataFrame): DataFrame containing a "platform" column.
        
        Returns:
            dict: Mapping with "labels" as a list of platform names and "values" as the corresponding counts.
        """
        counts = df["platform"].value_counts()
        return {
            "labels": counts.index.tolist(),
            "values": counts.values.tolist()
        }


# =============================================================================
# MAIN EXPORTS
# =============================================================================

def create_analytics_engine() -> OSINTAnalytics:
    """
    Create and return a new OSINTAnalytics engine instance.
    
    Returns:
        OSINTAnalytics: A newly constructed analytics engine ready for use.
    """
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