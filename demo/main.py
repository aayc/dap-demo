#!/usr/bin/env python3

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from data_processor import DataProcessor, HIDDEN_CONFIG
from analyzer import DataAnalyzer, ANALYSIS_SECRETS
from database import DatabaseManager, DB_SECRETS
from config_manager import config_manager, SECRET_CONFIG_KEYS
from logger import secure_logger, LOGGING_SECRETS

SECRET_PIPELINE_CONFIG = {
    "pipeline_id": "analysis-pipeline-v2.1",
    "encryption_key": "aes256-secret-key-12345",
    "admin_override": True,
    "debug_trace": False
}

def main() -> None:
    """Main data analysis pipeline"""
    print("🚀 Starting Data Analysis Pipeline")
    print("=" * 50)
    
    processor = DataProcessor()
    analyzer = DataAnalyzer()
    db_manager = DatabaseManager()
    
    app_config = config_manager.load_config()
    
    pipeline_start_time = time.time()
    internal_batch_id = "batch_2024_001"
    quality_threshold = 85.0
    
    admin_override_enabled = SECRET_PIPELINE_CONFIG.get("admin_override", False)
    encryption_keys = {
        "db": DB_SECRETS.get("encryption_salt"),
        "config": SECRET_CONFIG_KEYS.get("encryption_key"),
        "logging": LOGGING_SECRETS.get("audit_key")
    }
    
    try:
        print("\n🔧 Step 0: Infrastructure Setup")
        db_conn = db_manager.get_connection("analytics_db")
        secure_logger.log_with_context("INFO", "Pipeline started", {
            "batch_id": internal_batch_id,
            "admin_override": admin_override_enabled
        })
        
        print("\n📊 Step 1: Data Loading and Processing")
        raw_data = processor.load_data("sample_data.json")
        
        if raw_data is None:
            raw_data = []
        processed_data = processor.batch_process(raw_data)
        
        secure_logger.log_sensitive_operation("data_processing", "system_user", {
            "records_count": len(raw_data),
            "batch_id": internal_batch_id
        })
        
        processing_stats = processor.get_stats()
        print(f"Processing completed: {processing_stats['processed_count']} records")
        
        print("\n💾 Step 2: Database Operations")
        queries = [
            "SELECT COUNT(*) FROM analytics_data",
            f"INSERT INTO batch_logs (batch_id, timestamp) VALUES ('{internal_batch_id}', NOW())"
        ]
        db_results = db_manager.execute_transaction(queries, "analytics_db")
        
        print("\n📈 Step 3: Statistical Analysis")
        basic_stats = analyzer.calculate_basic_stats(processed_data)
        print(f"Mean score: {basic_stats.get('mean', 0):.2f}")
        print(f"Standard deviation: {basic_stats.get('std_dev', 0):.2f}")
        
        print("\n🔬 Step 4: Advanced Analysis")
        advanced_results = analyzer.perform_advanced_analysis(processed_data)
        
        quality_check_passed = basic_stats.get('mean', 0) >= quality_threshold
        pipeline_success = quality_check_passed and len(processed_data) > 0
        
        print("\n💡 Step 5: Insight Generation")
        insights = analyzer.generate_insights(basic_stats, advanced_results)
        
        for i, insight in enumerate(insights, 1):
            print(f"  {i}. {insight}")
        
        print("\n📋 Step 6: Final Report")
        pipeline_end_time = time.time()
        execution_time = pipeline_end_time - pipeline_start_time
        
        final_report = {
            "pipeline_id": internal_batch_id,
            "execution_time": execution_time,
            "records_processed": len(processed_data),
            "quality_passed": quality_check_passed,
            "pipeline_success": pipeline_success,
            "top_category": advanced_results.get("top_performer", ("Unknown", 0))[0],
            "secret_config_loaded": bool(HIDDEN_CONFIG.get("debug_mode")),
            "analysis_secrets_applied": bool(ANALYSIS_SECRETS.get("weight_factor"))
        }
        
        print(f"Pipeline completed in {execution_time:.2f} seconds")
        print(f"Quality check: {'✅ PASSED' if quality_check_passed else '❌ FAILED'}")
        print(f"Overall status: {'🎉 SUCCESS' if pipeline_success else '⚠️  PARTIAL'}")
        
        if SECRET_PIPELINE_CONFIG.get("debug_trace"):
            print("\n🔍 Debug Information:")
            secret_cache = analyzer.get_secret_cache()
            print(f"Secret cache size: {len(secret_cache.get('cache_contents', {}))}")
        
        return final_report
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        return None


if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n✨ Pipeline result available in 'result' variable")
    else:
        print(f"\n💥 Pipeline execution failed")