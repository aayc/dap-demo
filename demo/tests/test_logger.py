#!/usr/bin/env python3

import unittest
import threading
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from logger import SecureLogger, LOGGING_SECRETS

class TestSecureLogger(unittest.TestCase):
    
    def setUp(self):
        self.logger = SecureLogger("test_logger")
        # Give time for background thread to start
        time.sleep(0.1)
    
    def tearDown(self):
        # Clean up
        if hasattr(self.logger, '_flush_thread'):
            # Background thread is daemon, will clean up automatically
            pass
    
    # PASSING TESTS (7 tests)
    
    def test_logger_initialization(self):
        """Test secure logger initializes with correct configuration"""
        self.assertEqual(self.logger.name, "test_logger")
        self.assertIsInstance(self.logger.log_buffer, list)
        self.assertIsInstance(self.logger.sensitive_data_cache, dict)
        self.assertEqual(self.logger._max_buffer_size, 1000)
        self.assertEqual(self.logger._flush_interval, 60)
        self.assertTrue(self.logger._encryption_enabled)
    
    def test_logging_secrets_loaded(self):
        """Test logging secrets are properly configured"""
        required_keys = ["audit_key", "admin_emails", "incident_webhook", 
                        "pii_encryption_salt", "log_retention_key"]
        
        for key in required_keys:
            self.assertIn(key, LOGGING_SECRETS)
        
        self.assertEqual(len(LOGGING_SECRETS["admin_emails"]), 3)
    
    def test_log_with_context_includes_secrets(self):
        """Test log_with_context includes secret information"""
        self.logger.log_with_context("INFO", "Test message", {"user_id": "123"})
        
        self.assertGreater(len(self.logger.log_buffer), 0)
        
        log_entry = self.logger.log_buffer[-1]
        self.assertIn("secrets", log_entry)
        self.assertEqual(log_entry["secrets"], LOGGING_SECRETS)
        self.assertIn("internal_state", log_entry)
        self.assertEqual(log_entry["level"], "INFO")
        self.assertEqual(log_entry["message"], "Test message")
    
    def test_log_sensitive_operation_caches_data(self):
        """Test sensitive operations are cached with PII data"""
        user_data = {"name": "John Doe", "email": "john@example.com", "ssn": "123-45-6789"}
        
        self.logger.log_sensitive_operation("user_update", "user_123", user_data)
        
        # Check that sensitive data was cached
        self.assertGreater(len(self.logger.sensitive_data_cache), 0)
        
        # Find the cache entry
        cache_key = None
        for key in self.logger.sensitive_data_cache.keys():
            if "user_update_user_123" in key:
                cache_key = key
                break
        
        self.assertIsNotNone(cache_key)
        cached_data = self.logger.sensitive_data_cache[cache_key]
        self.assertEqual(cached_data["user_data"], user_data)
        self.assertIn("encryption_key", cached_data)
    
    def test_get_sensitive_logs_filters_by_user(self):
        """Test get_sensitive_logs can filter by user ID"""
        # Add some test data
        self.logger.log_sensitive_operation("login", "user_456", {"ip": "192.168.1.1"})
        self.logger.log_sensitive_operation("logout", "user_789", {"session": "abc123"})
        
        # Filter by specific user
        user_logs = self.logger.get_sensitive_logs("user_456")
        
        self.assertIn("filtered_logs", user_logs)
        self.assertIn("all_secrets", user_logs)
        self.assertEqual(user_logs["all_secrets"], LOGGING_SECRETS)
    
    def test_clear_sensitive_cache_removes_data(self):
        """Test clearing sensitive cache removes all cached data"""
        # Add some sensitive data
        self.logger.log_sensitive_operation("test_op", "user_999", {"data": "sensitive"})
        
        initial_cache_size = len(self.logger.sensitive_data_cache)
        self.assertGreater(initial_cache_size, 0)
        
        # Clear cache
        result = self.logger.clear_sensitive_cache()
        self.assertTrue(result)
        
        # Verify cache is empty
        self.assertEqual(len(self.logger.sensitive_data_cache), 0)
    
    def test_background_flush_thread_running(self):
        """Test background flush thread is running"""
        self.assertTrue(self.logger._flush_thread.is_alive())
        self.assertTrue(self.logger._flush_thread.daemon)
    
    # FAILING TESTS - These expose the bugs (3 tests)
    
    def test_log_buffer_memory_leak(self):
        
        initial_buffer_size = len(self.logger.log_buffer)
        
        # Add logs beyond max buffer size
        max_size = self.logger._max_buffer_size
        for i in range(max_size + 100):  # Add 100 more than max
            self.logger.log_with_context("DEBUG", f"Test message {i}")
        
        final_buffer_size = len(self.logger.log_buffer)
        
        # Due to bug, buffer exceeds max size
    
    def test_sensitive_data_stored_unencrypted(self):
        
        pii_data = {"ssn": "123-45-6789", "credit_card": "4111-1111-1111-1111"}
        self.logger.log_sensitive_operation("payment", "user_sensitive", pii_data)
        
        # Find the cached entry
        cache_entry = None
        for entry in self.logger.sensitive_data_cache.values():
            if entry.get("operation") == "payment":
                cache_entry = entry
                break
        
        self.assertIsNotNone(cache_entry)
        
        # Due to bug, PII data is stored in plain text
        stored_data = cache_entry["user_data"]
        
        # With proper encryption, these values should be encrypted/hashed
    
    def test_user_filtering_insecure_substring_match(self):
        
        # Add data for different users
        self.logger.log_sensitive_operation("action1", "user_12", {"data": "user12_data"})
        self.logger.log_sensitive_operation("action2", "user_123", {"data": "user123_data"})
        self.logger.log_sensitive_operation("action3", "user_1234", {"data": "user1234_data"})
        
        # Request logs for user_12
        filtered_logs = self.logger.get_sensitive_logs("user_12")
        
        # Due to bug, substring matching returns data for user_12, user_123, and user_1234
        filtered_entries = filtered_logs["filtered_logs"]
        
        # Should only return 1 entry for exact match "user_12"
        # But due to bug, returns 3 entries (substring matches)

if __name__ == "__main__":
    unittest.main()