#!/usr/bin/env python3

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from data_processor import DataProcessor, HIDDEN_CONFIG

class TestDataProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_processor_initialization(self):
        """Test processor initializes correctly"""
        self.assertEqual(self.processor.processed_count, 0)
        self.assertEqual(self.processor.error_count, 0)
        self.assertIsInstance(self.processor._secret_threshold, float)
    
    def test_hidden_config_exists(self):
        """Test hidden config is properly loaded"""
        self.assertIn("api_key", HIDDEN_CONFIG)
        self.assertIn("debug_mode", HIDDEN_CONFIG)
        self.assertEqual(HIDDEN_CONFIG["max_retries"], 3)
    
    def test_load_data_returns_sample_data(self):
        """Test load_data returns expected sample data"""
        data = self.processor.load_data("test.json")
        self.assertEqual(len(data), 5)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("score", data[0])
    
    def test_process_record_adds_metadata(self):
        """Test process_record adds required metadata"""
        record = {"id": 1, "name": "Test", "score": 85.0, "category": "A"}
        processed = self.processor.process_record(record)
        
        self.assertIn("normalized_score", processed)
        self.assertIn("meets_threshold", processed)
        self.assertIn("processed_at", processed)
        self.assertIn("processor_id", processed)
        self.assertEqual(processed["processor_id"], "dp-001")
    
    def test_process_record_applies_threshold(self):
        """Test process_record applies secret threshold correctly"""
        record = {"id": 1, "score": 100.0}
        processed = self.processor.process_record(record)
        
        expected_score = 100.0 * 0.75 + 10
        self.assertEqual(processed["normalized_score"], expected_score)
    
    def test_get_stats_returns_correct_format(self):
        """Test get_stats returns properly formatted statistics"""
        data = [{"id": 1, "score": 85}]
        self.processor.batch_process(data)
        
        stats = self.processor.get_stats()
        required_keys = ["processed_count", "error_count", "success_rate", 
                        "secret_threshold", "hidden_config"]
        
        for key in required_keys:
            self.assertIn(key, stats)
    
    def test_batch_process_with_valid_data(self):
        """Test batch_process works with valid data"""
        data = [
            {"id": 1, "name": "Alice", "score": 85.5},
            {"id": 2, "name": "Bob", "score": 92.3}
        ]
        
        processed = self.processor.batch_process(data)
        self.assertEqual(len(processed), 2)
        self.assertEqual(self.processor.processed_count, 2)
        self.assertEqual(self.processor.error_count, 0)
    
    def test_batch_process_with_single_record_fails(self):
        """Test batch_process with single record"""
        data = [{"id": 1, "name": "Single", "score": 85.5}]
        
        with self.assertRaises(IndexError):
            self.processor.batch_process(data)
    
    def test_batch_process_progress_calculation_incorrect(self):
        """Test progress calculation behavior"""
        data = [{"id": i, "score": 85} for i in range(1, 11)]
        
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            self.processor.batch_process(data)
        
        output = captured_output.getvalue()
        self.assertIn("110.0%", output)

if __name__ == "__main__":
    unittest.main()