# DAP Demo - Debug Adapter Protocol Playground

A complex data analysis pipeline with hidden secrets and subtle bugs for demonstrating DAP debugging capabilities. The perfect playground for teaching a coding agent to use the debugger in order to pass tests by setting breakpoints to observe stack frames, variables, etc.

## Structure

- **`debug.py`** - DAP client that connects to debugpy server
- **`demo/`** - Complex multi-module data analysis pipeline
- **`demo/tests/`** - Test suite with 40 tests (30 passing, 10 failing)

## Usage

### Run the DAP Debugger
```bash
python debug.py
```
Sets breakpoint at `demo/main.py:82` to inspect secret variables from all modules.

### Run the Test Suite
```bash
cd demo
python tests/test_runner.py
```
Shows 75% success rate with 10 failing tests that expose bugs.

## Hidden Bugs Reference

### Threading & Concurrency Issues
1. **Bug 1** (`database.py:34`): Using `RLock()` instead of `Lock()` - can cause deadlocks in connection pooling
2. **Bug 5** (`config_manager.py:35`): Race condition in config loading - missing thread synchronization  
3. **Bug 9** (`logger.py` - missing): Thread safety issue with shared log buffer - no lock protection

### Index & Boundary Errors  
4. **Bug 2** (`database.py:55`): Off-by-one in query ID generation - starts from 1 instead of 0, breaks caching
5. **Bug 14** (`data_processor.py:59`): Index out of bounds accessing `data[1]` when list has only 1 element
6. **Bug 15** (`data_processor.py:69`): Off-by-one in progress reporting - shows 110% for 100 items

### Logic & Calculation Errors
7. **Bug 3** (`database.py:94`): Cache hit rate calculated as miss rate instead - inverted metric
8. **Bug 16** (`analyzer.py:69`): Division by zero in category averages when empty score lists
9. **Bug 17** (`analyzer.py:71`): Unhandled exception in `max()` function with empty category_averages

### Memory & Resource Leaks
10. **Bug 4** (`database.py:141`): Transaction not removed from active list on success - memory leak
11. **Bug 10** (`logger.py:66`): Log buffer grows without bounds checking - memory leak
12. **Bug 12** (`logger.py:111`): Division by zero in flush logic calculations - performance issues

### Data Handling & Validation  
13. **Bug 6** (`config_manager.py:51`): Infinite recursion in config loading on repeated failures
14. **Bug 7** (`config_manager.py:87`): Type conversion only works for exact endings, not partial matches
15. **Bug 18** (`main.py:57`): Incomplete null checking - handles None but not empty lists

### Security & Encoding Issues
16. **Bug 8** (`config_manager.py:125`): Incorrect base64 detection tries to decode non-base64 strings
17. **Bug 11** (`logger.py:83`): Sensitive data stored without encryption despite encryption flag
18. **Bug 13** (`logger.py:125`): Insecure substring matching for user filtering - privacy leak

## Secret Variables to Discover

### Database Secrets (`database.py`)
- `DB_SECRETS` - Connection strings, API keys, encryption salts
- `_master_key` - Database cluster master key
- `_cluster_nodes` - Internal cluster topology

### Configuration Secrets (`config_manager.py`)  
- `SECRET_CONFIG_KEYS` - JWT secrets, admin passwords, API tokens
- Database URLs for primary/replica/cache systems
- Internal encryption and audit settings

### Analysis Secrets (`analyzer.py`)
- `ANALYSIS_SECRETS` - Weight factors, bonus thresholds, penalty factors
- `_alpha`, `_beta`, `_gamma` - Hidden algorithm parameters

### Processing Secrets (`data_processor.py`)
- `HIDDEN_CONFIG` - API keys, debug modes, retry limits
- `_secret_threshold` - Hidden scoring threshold

### Logging Secrets (`logger.py`)
- `LOGGING_SECRETS` - Audit keys, admin emails, incident webhooks
- PII encryption salts, log retention policies
- Sensitive data cache with unencrypted PII

### Pipeline Secrets (`main.py`)
- `SECRET_PIPELINE_CONFIG` - Pipeline ID, encryption keys, admin overrides
- `encryption_keys` - Cross-module encryption key collection
- `internal_batch_id`, `quality_threshold` - Hidden operational parameters

## Debugging Tips

1. **Set breakpoint at line 82** in `main.py` where `quality_check_passed` is calculated
2. **Inspect local variables** to see all secret configurations loaded from modules
3. **Check failed tests** to identify which bugs are being triggered
4. **Use DAP variable inspection** to trace secret values through the call stack
5. **Look for threading issues** by examining lock types and shared data structures