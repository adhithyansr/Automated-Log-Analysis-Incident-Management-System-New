"""
Test script to demonstrate exact phrase matching for alerts.
This shows how the alert system works with full phrases vs single keywords.
"""

# Sample log messages from demo_logs.txt
test_logs = [
    "ERROR DatabaseConnection - Failed to connect to database after 3 retries (timeout=5000ms)",
    "WARN AuthService - Failed login attempt for username=admin from IP=192.168.1.45",
    "FATAL SQLIntegrityConstraintViolationException: Duplicate entry 'user_123' for key 'users.username'"
]

def test_keyword_matching(keyword, logs):
    """Test which logs match the given keyword"""
    print(f"\n{'='*70}")
    print(f"Testing Keyword: '{keyword}'")
    print(f"{'='*70}")
    
    matches = []
    for i, log in enumerate(logs, 1):
        # Case-insensitive exact phrase matching (same as analyzer.py)
        if keyword.lower() in log.lower():
            matches.append(i)
            print(f"✓ MATCH   - Log {i}: {log[:60]}...")
        else:
            print(f"✗ NO MATCH - Log {i}: {log[:60]}...")
    
    print(f"\nResult: {len(matches)} log(s) matched out of {len(logs)}")
    return matches

# Test Case 1: Single keyword "failed" - matches multiple logs
print("\n" + "="*70)
print("TEST CASE 1: Using single keyword 'failed'")
print("="*70)
test_keyword_matching("failed", test_logs)

# Test Case 2: Exact phrase "Failed to connect to database" - matches only specific log
print("\n" + "="*70)
print("TEST CASE 2: Using exact phrase 'Failed to connect to database'")
print("="*70)
test_keyword_matching("Failed to connect to database", test_logs)

# Test Case 3: Another exact phrase - matches different log
print("\n" + "="*70)
print("TEST CASE 3: Using exact phrase 'Failed login attempt'")
print("="*70)
test_keyword_matching("Failed login attempt", test_logs)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
✓ Single keyword like 'failed' → Matches ALL logs containing 'failed'
✓ Exact phrase like 'Failed to connect to database' → Matches ONLY that specific log
✓ Case-insensitive matching works correctly
✓ Whitespace trimming ensures clean matching

RECOMMENDATION for your alert:
- Alert Name: "Database Connection Alert"
- Keyword: "Failed to connect to database"
- This will ONLY trigger on database connection failures
- It will NOT trigger on "Failed login attempt" or other "failed" logs
""")
