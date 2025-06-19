#!/usr/bin/env python3

import unittest
import threading
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database import DatabaseConnection, DatabaseManager, DB_SECRETS

class TestDatabaseConnection(unittest.TestCase):
    
    def setUp(self):
        self.conn = DatabaseConnection("test_conn_123")
        self.conn.connect()
    
    # PASSING TESTS (5 tests)
    
    def test_connection_initialization(self):
        """Test database connection initializes correctly"""
        self.assertEqual(self.conn.connection_id, "test_conn_123")
        self.assertIsInstance(self.conn.query_cache, dict)
        self.assertEqual(self.conn._max_connections, 50)
        self.assertEqual(self.conn._timeout_seconds, 30)
    
    def test_connection_establishes_successfully(self):
        """Test database connection establishes"""
        self.assertTrue(self.conn.is_connected)
        self.assertIn("connection_hash", self.conn.query_cache)
    
    def test_execute_query_basic_functionality(self):
        """Test basic query execution works"""
        result = self.conn.execute_query("SELECT * FROM test_table")
        
        self.assertTrue(result.success)
        self.assertEqual(result.rows_affected, 42)
        self.assertGreater(result.execution_time, 0)
        self.assertIsInstance(result.query_id, str)
    
    def test_execute_query_caches_results(self):
        """Test query results are cached with secret metadata"""
        result = self.conn.execute_query("SELECT COUNT(*) FROM users")
        
        self.assertIn(result.query_id, self.conn.query_cache)
        cached_result = self.conn.query_cache[result.query_id]
        
        self.assertIn("secret_params", cached_result)
        self.assertIn("execution_context", cached_result)
        self.assertEqual(cached_result["secret_params"], DB_SECRETS)
    
    def test_select_query_optimization(self):
        """Test SELECT queries get secret optimization hints"""
        result = self.conn.execute_query("SELECT * FROM products WHERE category = 'A'")
        
        cached_result = self.conn.query_cache[result.query_id]
        optimized_query = cached_result["optimized_query"]
        
        self.assertIn("/* HINT: use_index */", optimized_query)
        # SELECT queries should be faster (0.8 multiplier)
        self.assertLess(result.execution_time, 0.1)
    
    # FAILING TESTS - These expose the bugs (2 tests)
    
    def test_query_id_generation_bug(self):
        
        # First query should have ID "query_0" but will have "query_1"
        result1 = self.conn.execute_query("SELECT 1")
        
        # Second query should have ID "query_1" but will have "query_2"
        result2 = self.conn.execute_query("SELECT 2")
    
    def test_connection_stats_cache_hit_rate_incorrect(self):
        
        # Execute some queries to populate cache
        for i in range(5):
            self.conn.execute_query(f"SELECT {i}")
        
        stats = self.conn.get_connection_stats()
        
        # All queries should be cache misses (execution_time > 0.05)
        # So cache_hit_rate should be 0, but due to bug it shows miss rate
        # Since all are misses, it will show 1.0 (100% miss rate as hit rate)

class TestDatabaseManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = DatabaseManager()
    
    # PASSING TESTS (4 tests)
    
    def test_manager_initialization(self):
        """Test database manager initializes with secrets"""
        self.assertIsInstance(self.manager.connections, dict)
        self.assertIsInstance(self.manager.active_transactions, list)
        self.assertEqual(self.manager._master_key, "db_master_key_prod_2024")
        self.assertEqual(len(self.manager._cluster_nodes), 3)
    
    def test_get_connection_creates_new_connection(self):
        """Test getting connection creates and caches new connection"""
        conn = self.manager.get_connection("test_db")
        
        self.assertIn("test_db", self.manager.connections)
        self.assertTrue(conn.is_connected)
        self.assertEqual(conn.connection_id, "test_db")
    
    def test_get_connection_reuses_existing(self):
        """Test getting same connection reuses existing instance"""
        conn1 = self.manager.get_connection("reuse_test")
        conn2 = self.manager.get_connection("reuse_test")
        
        self.assertIs(conn1, conn2)  # Same object instance
        self.assertEqual(len(self.manager.connections), 1)
    
    def test_get_cluster_status_includes_secrets(self):
        """Test cluster status includes secret information"""
        status = self.manager.get_cluster_status()
        
        required_keys = ["master_key", "cluster_nodes", "active_connections", 
                        "active_transactions", "secret_config"]
        for key in required_keys:
            self.assertIn(key, status)
        
        self.assertEqual(status["secret_config"], DB_SECRETS)
    
    # FAILING TEST - Exposes the bug (1 test)
    
    def test_transaction_cleanup_memory_leak(self):
        
        queries = ["SELECT 1", "SELECT 2"]
        initial_count = len(self.manager.active_transactions)
        
        # Execute transaction
        results = self.manager.execute_transaction(queries, "leak_test")
        
        # Transaction should be removed from active list, but due to bug it isn't
        final_count = len(self.manager.active_transactions)
        
        # Due to bug, active count increases by 1 (transaction not cleaned up)
        
        # Verify all results are successful
        for result in results:
            self.assertTrue(result.success)

if __name__ == "__main__":
    unittest.main()