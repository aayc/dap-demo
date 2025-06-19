#!/usr/bin/env python3

import statistics
from typing import Any

ANALYSIS_SECRETS = {
    "weight_factor": 1.25,
    "bonus_threshold": 90.0,
    "penalty_factor": 0.95
}

class DataAnalyzer:
    def __init__(self) -> None:
        self.analysis_cache: dict[str, Any] = {}
        self._alpha: float = 0.3
        self._beta: float = 0.7
        self._gamma: float = 1.15
        
    def calculate_basic_stats(self, data: list[dict]) -> dict[str, float]:
        """Calculate basic statistics from processed data"""
        print("Calculating basic statistics...")
        
        scores = [record.get("normalized_score", 0) for record in data if "normalized_score" in record]
        
        if not scores:
            return {"error": "No scores found"}
        
        stats = {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
            "min_score": min(scores),
            "max_score": max(scores),
            "count": len(scores)
        }
        
        self.analysis_cache["basic_stats"] = stats
        return stats
    
    def perform_advanced_analysis(self, data: list[dict]) -> dict[str, Any]:
        """Perform advanced analysis with hidden algorithms"""
        print("Performing advanced analysis...")
        
        enhanced_scores = []
        category_performance = {}
        
        for record in data:
            if "normalized_score" in record and "category" in record:
                base_score = record["normalized_score"]
                category = record["category"]
                
                enhanced_score = (base_score * self._alpha + 
                                self._beta * ANALYSIS_SECRETS["weight_factor"] * base_score + 
                                self._gamma * 10)
                
                if base_score >= ANALYSIS_SECRETS["bonus_threshold"]:
                    enhanced_score *= 1.1
                elif base_score < 70:
                    enhanced_score *= ANALYSIS_SECRETS["penalty_factor"]
                
                enhanced_scores.append(enhanced_score)
                
                if category not in category_performance:
                    category_performance[category] = []
                category_performance[category].append(enhanced_score)
        
        category_averages = {}
        for cat, scores in category_performance.items():
            category_averages[cat] = sum(scores) / len(scores)
        
        top_performer = max(category_averages.items(), key=lambda x: x[1]) if category_averages else None
        
        analysis_result = {
            "enhanced_scores": enhanced_scores,
            "category_performance": category_averages,
            "top_performer": top_performer,
            "secret_params": {
                "alpha": self._alpha,
                "beta": self._beta,
                "gamma": self._gamma,
                "analysis_secrets": ANALYSIS_SECRETS
            }
        }
        
        self.analysis_cache["advanced_analysis"] = analysis_result
        return analysis_result
    
    def generate_insights(self, basic_stats: dict, advanced_analysis: dict) -> list[str]:
        """Generate insights from the analysis"""
        print("Generating insights...")
        
        insights = []
        
        if basic_stats.get("mean", 0) > 80:
            insights.append("Overall performance is above average")
        else:
            insights.append("Performance needs improvement")
        
        if advanced_analysis.get("top_performer"):
            top_cat, top_score = advanced_analysis["top_performer"]
            insights.append(f"Category '{top_cat}' shows highest performance ({top_score:.2f})")
        
        enhanced_scores = advanced_analysis.get("enhanced_scores", [])
        if enhanced_scores:
            high_performers = [s for s in enhanced_scores if s > 100]
            insights.append(f"Secret analysis reveals {len(high_performers)} high performers")
        
        return insights
    
    def get_secret_cache(self) -> dict[str, Any]:
        """Return the hidden analysis cache"""
        return {
            "cache_contents": self.analysis_cache,
            "secret_parameters": {
                "alpha": self._alpha,
                "beta": self._beta,
                "gamma": self._gamma
            },
            "analysis_secrets": ANALYSIS_SECRETS
        }