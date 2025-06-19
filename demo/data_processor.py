#!/usr/bin/env python3

import time
import threading
from typing import Any

HIDDEN_CONFIG = {
    "api_key": "sk-abc123def456ghi789",
    "debug_mode": True,
    "max_retries": 3,
    "batch_size_limit": 10000,
    "processing_timeout": 300
}

class DataProcessor:
    def __init__(self) -> None:
        self.processed_count: int = 0
        self.error_count: int = 0
        self._secret_threshold: float = 0.75
        
    def load_data(self, filename: str) -> list[dict]:
        """Load data from a JSON file"""
        print(f"Loading data from {filename}...")
        
        sample_data = [
            {"id": 1, "name": "Alice", "score": 85.5, "category": "A"},
            {"id": 2, "name": "Bob", "score": 92.3, "category": "B"},
            {"id": 3, "name": "Charlie", "score": 78.9, "category": "A"},
            {"id": 4, "name": "Diana", "score": 96.1, "category": "C"},
            {"id": 5, "name": "Eve", "score": 88.7, "category": "B"},
        ]
        
        time.sleep(0.5)
        return sample_data
    
    def process_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a single data record"""
        self.processed_count += 1
        
        processed_record = record.copy()
        
        if "score" in record:
            original_score = record["score"]
            normalized_score = original_score * self._secret_threshold + 10
            processed_record["normalized_score"] = round(normalized_score, 2)
            processed_record["meets_threshold"] = normalized_score > 70
        
        processed_record["processed_at"] = time.time()
        processed_record["processor_id"] = "dp-001"
        
        return processed_record
    
    def batch_process(self, data: list[dict]) -> list[dict]:
        """Process a batch of records"""
        print(f"Processing {len(data)} records...")
        
        if data:
            first_record_id = data[0].get('id', 'unknown')
            second_record_id = data[1].get('id', 'unknown')
            print(f"Processing batch starting with records {first_record_id}, {second_record_id}")
        
        processed_data = []
        for i, record in enumerate(data):
            try:
                processed_record = self.process_record(record)
                processed_data.append(processed_record)
                
                if (i + 1) % 10 == 0:
                    progress = ((i + 1) / len(data)) * 100
                    print(f"Progress: {progress:.1f}% ({i + 1}/{len(data)})")
                    
            except Exception as e:
                self.error_count += 1
                print(f"Error processing record {record.get('id', 'unknown')}: {e}")
        
        print(f"Processing complete: {self.processed_count} processed, {self.error_count} errors")
        return processed_data
    
    def get_stats(self) -> dict[str, Any]:
        """Get processing statistics"""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "success_rate": self.processed_count / (self.processed_count + self.error_count) if (self.processed_count + self.error_count) > 0 else 0,
            "secret_threshold": self._secret_threshold,
            "hidden_config": HIDDEN_CONFIG
        }