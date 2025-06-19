#!/usr/bin/env python3

import unittest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import main function and components
from main import main
from data_processor import HIDDEN_CONFIG
from analyzer import ANALYSIS_SECRETS
from database import DB_SECRETS
from config_manager import SECRET_CONFIG_KEYS
from logger import LOGGING_SECRETS

class TestIntegrationPipeline(unittest.TestCase):
    
    def setUp(self):
        # Redirect stdout to capture print statements
        self.original_stdout = sys.stdout
    
    def tearDown(self):
        sys.stdout = self.original_stdout
    
    # PASSING TESTS (8 tests)
    
    def test_pipeline_secret_configuration_loaded(self):
        """Test all secret configurations are properly loaded"""
        # Verify all secret dictionaries exist and have expected keys
        self.assertIn("api_key", HIDDEN_CONFIG)
        self.assertIn("weight_factor", ANALYSIS_SECRETS)
        self.assertIn("connection_string", DB_SECRETS)
        self.assertIn("jwt_secret", SECRET_CONFIG_KEYS)
        self.assertIn("audit_key", LOGGING_SECRETS)
    
    def test_pipeline_components_initialize(self):
        """Test all pipeline components can be initialized"""
        from data_processor import DataProcessor
        from analyzer import DataAnalyzer
        from database import DatabaseManager
        from config_manager import ConfigurationManager
        from logger import SecureLogger
        
        # Should not raise exceptions
        processor = DataProcessor()
        analyzer = DataAnalyzer()
        db_manager = DatabaseManager()
        config_manager = ConfigurationManager()
        logger = SecureLogger("test")
        
        # Verify components have expected attributes
        self.assertTrue(hasattr(processor, '_secret_threshold'))
        self.assertTrue(hasattr(analyzer, '_alpha'))
        self.assertTrue(hasattr(db_manager, '_master_key'))
        self.assertTrue(hasattr(config_manager, '_encryption_enabled'))
        self.assertTrue(hasattr(logger, '_audit_mode'))
    
    def test_data_processor_integration(self):
        """Test data processor integrates correctly with sample data"""
        from data_processor import DataProcessor
        
        processor = DataProcessor()
        data = processor.load_data("test.json")
        
        self.assertEqual(len(data), 5)
        
        processed = processor.batch_process(data)
        self.assertEqual(len(processed), len(data))
        
        stats = processor.get_stats()
        self.assertEqual(stats["processed_count"], 5)
        self.assertIn("hidden_config", stats)
    
    def test_analyzer_integration(self):
        """Test analyzer integrates with processed data"""
        from data_processor import DataProcessor
        from analyzer import DataAnalyzer
        
        processor = DataProcessor()
        analyzer = DataAnalyzer()
        
        data = processor.load_data("test.json")
        processed = processor.batch_process(data)
        
        basic_stats = analyzer.calculate_basic_stats(processed)
        self.assertIn("mean", basic_stats)
        self.assertGreater(basic_stats["count"], 0)
        
        advanced_results = analyzer.perform_advanced_analysis(processed)
        self.assertIn("secret_params", advanced_results)
        self.assertIn("enhanced_scores", advanced_results)
    
    def test_database_integration(self):
        """Test database manager integrates correctly"""
        from database import DatabaseManager
        
        manager = DatabaseManager()
        conn = manager.get_connection("test_integration")
        
        self.assertTrue(conn.is_connected)
        
        result = conn.execute_query("SELECT COUNT(*) FROM test_table")
        self.assertTrue(result.success)
        
        cluster_status = manager.get_cluster_status()
        self.assertIn("master_key", cluster_status)
        self.assertIn("secret_config", cluster_status)
    
    def test_config_manager_integration(self):
        """Test configuration manager loads and provides configs"""
        from config_manager import ConfigurationManager
        
        manager = ConfigurationManager("nonexistent.json")  # Will use defaults
        config = manager.load_config()
        
        self.assertIn("secrets", config)
        self.assertIn("internal", config)
        
        debug_info = manager.get_debug_info()
        self.assertIn("all_secrets", debug_info)
        self.assertIn("full_config", debug_info)
    
    def test_logger_integration(self):
        """Test secure logger integrates with sensitive operations"""
        from logger import SecureLogger
        
        logger = SecureLogger("integration_test")
        
        logger.log_with_context("INFO", "Integration test message")
        self.assertGreater(len(logger.log_buffer), 0)
        
        logger.log_sensitive_operation("test_op", "user_integration", {"test": "data"})
        self.assertGreater(len(logger.sensitive_data_cache), 0)
        
        sensitive_logs = logger.get_sensitive_logs()
        self.assertIn("all_secrets", sensitive_logs)
    
    def test_end_to_end_pipeline_secrets_accessible(self):
        """Test end-to-end pipeline makes secrets accessible for debugging"""
        # This test verifies that when debugging, all secret variables
        # are accessible in the pipeline execution context
        
        # Import all secret configurations
        from main import SECRET_PIPELINE_CONFIG
        
        # Verify global pipeline secrets
        self.assertIn("pipeline_id", SECRET_PIPELINE_CONFIG)
        self.assertIn("encryption_key", SECRET_PIPELINE_CONFIG)
        self.assertIn("admin_override", SECRET_PIPELINE_CONFIG)
        
        # Verify all module secrets are importable and accessible
        secret_sources = [
            HIDDEN_CONFIG,
            ANALYSIS_SECRETS, 
            DB_SECRETS,
            SECRET_CONFIG_KEYS,
            LOGGING_SECRETS
        ]
        
        for secrets in secret_sources:
            self.assertIsInstance(secrets, dict)
            self.assertGreater(len(secrets), 0)
    
    # FAILING TESTS - These expose integration bugs (2 tests)
    
    def test_pipeline_with_empty_data_fails(self):
        
        from data_processor import DataProcessor
        
        processor = DataProcessor()
        
        # Mock load_data to return empty list
        with patch.object(processor, 'load_data', return_value=[]):
            # This should trigger the bug where empty list causes issues
            # in batch_process when trying to access data[1]
            
            with self.assertRaises(IndexError):
                # Even though we check for None, empty list still causes IndexError
                # in batch_process when accessing data[1]
                processor.batch_process([])
    
    def test_main_pipeline_execution_has_null_check_bug(self):
        """Test main pipeline has incomplete null checking - RELATED TO BUG 18"""
        # This test shows that while main.py checks for None, 
        # it doesn't properly handle empty lists
        
        # Create a mock that returns empty list instead of None
        with patch('main.DataProcessor') as mock_processor_class:
            mock_processor = mock_processor_class.return_value
            mock_processor.load_data.return_value = []  # Empty list, not None
            mock_processor.batch_process.side_effect = IndexError("list index out of range")
            
            # The main function checks for None but not empty list
            # This exposes the incomplete validation in main.py
            with self.assertRaises(IndexError):
                main()

if __name__ == "__main__":
    unittest.main()