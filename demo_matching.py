"""
ALERT KEYWORD MATCHING - DEMONSTRATION
How the updated analyzer.py works with your logs
"""

# Your demo_logs.txt content
log1 = "ERROR DatabaseConnection - Failed to connect to database after 3 retries (timeout=5000ms)"
log2 = "WARN AuthService - Failed login attempt for username=admin from IP=192.168.1.45"
log3 = "FATAL SQLIntegrityConstraintViolationException: Duplicate entry 'user_123' for key 'users.username'"

print("="*80)
print("SCENARIO 1: Alert keyword = 'failed' (single word)")
print("="*80)
keyword1 = "failed"
print(f"\nKeyword: '{keyword1}'\n")
print(f"Log 1: {keyword1.lower() in log1.lower()} - {log1[:70]}...")
print(f"Log 2: {keyword1.lower() in log2.lower()} - {log2[:70]}...")
print(f"Log 3: {keyword1.lower() in log3.lower()} - {log3[:70]}...")
print(f"\n-> Result: Matches 2 logs (any log with 'failed')\n")

print("="*80)
print("SCENARIO 2: Alert keyword = 'Failed to connect to database' (exact phrase)")
print("="*80)
keyword2 = "Failed to connect to database"
print(f"\nKeyword: '{keyword2}'\n")
match1 = keyword2.lower() in log1.lower()
match2 = keyword2.lower() in log2.lower()
match3 = keyword2.lower() in log3.lower()
print(f"Log 1: {match1} - {log1[:70]}...")
print(f"Log 2: {match2} - {log2[:70]}...")
print(f"Log 3: {match3} - {log3[:70]}...")
print(f"\n-> Result: Matches 1 log (ONLY the database connection failure)")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("""
The alert system now works correctly with EXACT PHRASES:

1. Create an alert with keyword: "Failed to connect to database"
   -> Triggers ONLY on: Database connection failures
   -> Does NOT trigger on: Failed login attempts or other 'failed' logs

2. The matching is:
   - Case-insensitive (FAILED = failed = Failed)
   - Exact phrase matching (the entire phrase must be present)
   - Whitespace trimmed automatically

3. Your original request is COMPLETE:
   - Alert will trigger on "Failed to connect to database" logs only
   - Will NOT trigger on other logs with just "failed" in them
""")
