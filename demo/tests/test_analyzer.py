#!/usr/bin/env python3

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from analyzer import DataAnalyzer, ANALYSIS_SECRETS

class TestDataAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = DataAnalyzer()
        self.sample_data = [
            {"id": 1, "normalized_score": 85.5, "category": "A"},
            {"id": 2, "normalized_score": 92.3, "category": "B"},
            {"id": 3, "normalized_score": 78.9, "category": "A"},
            {"id": 4, "normalized_score": 96.1, "category": "C"},
        ]
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes with correct secret parameters"""
        self.assertEqual(self.analyzer._alpha, 0.3)
        self.assertEqual(self.analyzer._beta, 0.7)
        self.assertEqual(self.analyzer._gamma, 1.15)
        self.assertIsInstance(self.analyzer.analysis_cache, dict)
    
    def test_analysis_secrets_loaded(self):
        """Test analysis secrets are properly configured"""
        self.assertEqual(ANALYSIS_SECRETS["weight_factor"], 1.25)
        self.assertEqual(ANALYSIS_SECRETS["bonus_threshold"], 90.0)
        self.assertEqual(ANALYSIS_SECRETS["penalty_factor"], 0.95)
    
    def test_calculate_basic_stats_valid_data(self):
        """Test basic statistics calculation with valid data"""
        stats = self.analyzer.calculate_basic_stats(self.sample_data)
        
        required_keys = ["mean", "median", "std_dev", "min_score", "max_score", "count"]
        for key in required_keys:
            self.assertIn(key, stats)
        
        self.assertEqual(stats["count"], 4)
        self.assertGreater(stats["mean"], 0)
        self.assertGreater(stats["max_score"], stats["min_score"])
    
    def test_calculate_basic_stats_caches_result(self):
        """Test basic stats result is cached"""
        self.analyzer.calculate_basic_stats(self.sample_data)
        self.assertIn("basic_stats", self.analyzer.analysis_cache)
    
    def test_perform_advanced_analysis_applies_secret_formula(self):
        """Test advanced analysis applies secret enhancement formula"""
        result = self.analyzer.perform_advanced_analysis(self.sample_data)
        
        self.assertIn("enhanced_scores", result)
        self.assertIn("category_performance", result)
        self.assertIn("secret_params", result)
        
        secret_params = result["secret_params"]
        self.assertEqual(secret_params["alpha"], 0.3)
        self.assertEqual(secret_params["beta"], 0.7)
        self.assertEqual(secret_params["gamma"], 1.15)
    
    def test_generate_insights_produces_list(self):
        """Test insight generation produces string list"""
        basic_stats = {"mean": 85.0}
        advanced_analysis = {"top_performer": ("A", 90.0), "enhanced_scores": [100, 110]}
        
        insights = self.analyzer.generate_insights(basic_stats, advanced_analysis)
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        for insight in insights:
            self.assertIsInstance(insight, str)
    
    def test_advanced_analysis_with_empty_categories_fails(self):
        """Test advanced analysis with empty categories"""
        empty_category_data = [
            {"id": 1, "category": "A"},
            {"id": 2, "category": "B"}
        ]
        
        with self.assertRaises(ZeroDivisionError):
            self.analyzer.perform_advanced_analysis(empty_category_data)
    
    def test_advanced_analysis_empty_data_fails(self):
        """Test advanced analysis with completely empty data"""
        empty_data = []
        invalid_data = [{"id": 1, "invalid_field": "test"}]
        
        result = self.analyzer.perform_advanced_analysis(invalid_data)
        self.assertIsNone(result["top_performer"])

if __name__ == "__main__":
    unittest.main()