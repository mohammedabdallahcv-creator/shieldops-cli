import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from shieldops_cli.formatters.table import _first_present, to_table
from shieldops_cli.formatters.summary import to_summary

r1 = {'security_score': 0, 'security_score_grade': 'F'}
print("=== Direct _first_present test ===")
print("_first_present(0):", repr(_first_present(0)))
print("_first_present(None, 0):", repr(_first_present(None, 0)))
print()

# Check what to_summary produces
s = to_summary("analyze", r1)
print("Summary raw repr:", repr(s))
print()

# Check what to_table produces - raw bytes
t = to_table("analyze", r1)
print("Table raw repr first 500 chars:", repr(t[:500]))
print()

# Check what result.get returns
print("result.get('security_score'):", repr(r1.get("security_score")))
print()
