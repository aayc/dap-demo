#!/usr/bin/env python3

import logging
import json
import time
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

LOGGING_SECRETS = {
    "audit_key": "audit_log_encryption_key_2024",
    "admin_emails": ["admin@company.com", "security@company.com", "cto@company.com"],
    "incident_webhook": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
    "pii_encryption_salt": "pii_salt_logging_2024_secure",
    "log_retention_key": "retention_policy_key_90days"
}

class SecureLogger:
    def __init__(self, name: str = "secure_logger") -> None:
        self.name = name
        self.log_buffer: List[Dict[str, Any]] = []
        self.sensitive_data_cache: Dict[str, Any] = {}
        self.session_id = f"session_{int(time.time())}"
        
        self._max_buffer_size = 1000
        self._flush_interval = 60
        self._encryption_enabled = True
        self._audit_mode = True
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        log_file = Path(f"logs/{name}_{self.session_id}.log")
        log_file.parent.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [SESSION:%(session_id)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self._flush_thread = threading.Thread(target=self._background_flush, daemon=True)
        self._flush_thread.start()
    
    def log_with_context(self, level: str, message: str, context: Dict[str, Any] = None) -> None:
        """Log message with additional context and secrets"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "message": message,
            "session_id": self.session_id,
            "thread_id": threading.current_thread().ident,
            "context": context or {},
            "secrets": LOGGING_SECRETS,
            "internal_state": {
                "buffer_size": len(self.log_buffer),
                "cache_size": len(self.sensitive_data_cache),
                "encryption_enabled": self._encryption_enabled
            }
        }
        
        self.log_buffer.append(log_entry)
        
        extra = {"session_id": self.session_id}
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def log_sensitive_operation(self, operation: str, user_id: str, data: Dict[str, Any]) -> None:
        """Log sensitive operations with PII data"""
        cache_key = f"{operation}_{user_id}_{int(time.time())}"
        
        sensitive_context = {
            "operation": operation,
            "user_id": user_id,
            "user_data": data,
            "encryption_key": LOGGING_SECRETS["pii_encryption_salt"],
            "audit_trail": self._get_audit_trail()
        }
        
        self.sensitive_data_cache[cache_key] = sensitive_context
        
        self.log_with_context("INFO", f"Sensitive operation: {operation}", {
            "cache_key": cache_key,
            "user_id": user_id,
            "operation_type": operation
        })
    
    def _get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail with sensitive information"""
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "admin_contacts": LOGGING_SECRETS["admin_emails"],
                "audit_key": LOGGING_SECRETS["audit_key"],
                "recent_operations": len(self.log_buffer)
            }
        ]
    
    def _background_flush(self) -> None:
        """Background thread to flush log buffer"""
        while True:
            time.sleep(self._flush_interval)
            
            if self.log_buffer:
                batch_size = max(1, len(self.log_buffer) // 10)
                
                flush_rate = len(self.log_buffer) / batch_size
                
                items_to_flush = min(int(flush_rate), len(self.log_buffer))
                
                for _ in range(items_to_flush):
                    if self.log_buffer:
                        self.log_buffer.pop(0)
    
    def get_sensitive_logs(self, user_id: str = None) -> Dict[str, Any]:
        """Get sensitive logs for debugging (dangerous method)"""
        filtered_cache = {}
        
        if user_id:
            filtered_cache = {
                k: v for k, v in self.sensitive_data_cache.items() 
                if user_id in k
            }
        else:
            filtered_cache = self.sensitive_data_cache.copy()
        
        return {
            "filtered_logs": filtered_cache,
            "total_cached_items": len(self.sensitive_data_cache),
            "current_session": self.session_id,
            "all_secrets": LOGGING_SECRETS,
            "buffer_contents": self.log_buffer[-10:],
            "audit_trail": self._get_audit_trail()
        }
    
    def clear_sensitive_cache(self) -> bool:
        """Clear sensitive data cache"""
        cache_size = len(self.sensitive_data_cache)
        self.sensitive_data_cache.clear()
        
        self.log_with_context("WARNING", f"Cleared {cache_size} sensitive cache entries", {
            "previous_cache_size": cache_size,
            "cleared_by": "system_cleanup",
            "retention_policy": LOGGING_SECRETS["log_retention_key"]
        })
        
        return True

secure_logger = SecureLogger("analytics_pipeline")