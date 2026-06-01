"""Quick verification: score=0 should display as 0, not fall through to N/A."""
import sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from shieldops_cli.formatters.summary import to_summary
from shieldops_cli.formatters.table import to_table


def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


print("=== SCENARIO 1: score=0, grade=F ===")
r1 = {'security_score': 0, 'security_score_grade': 'F'}
s1 = to_summary('analyze', r1)
t1 = strip_ansi(to_table('analyze', r1))
print(f"  Summary: {s1}")
print(f"  Table:\n{t1}")
assert '0' in t1, f"FAIL: table should contain 0, got:\n{t1}"
assert 'F' in t1, f"FAIL: table should contain F, got:\n{t1}"
assert 'N/A' not in t1, f"FAIL: table should NOT contain N/A, got:\n{t1}"
print("  PASS: 0 preserved as valid score, grade F shown\n")

print("=== SCENARIO 2: score=72, grade=B ===")
r2 = {
    'security_score': 72,
    'security_score_grade': 'B',
    'report_contract': {
        'critical_count': 1, 'high_count': 1, 'medium_count': 1, 'low_count': 0,
        'detailed_issues': [{'severity': 'critical', 'category': 'Security',
                             'message': 'test', 'fix': 'fix', 'rule_id': 'X', 'line': 1}]
    }
}
s2 = to_summary('analyze', r2)
t2 = strip_ansi(to_table('analyze', r2))
print(f"  Summary: {s2}")
print(f"  Table:\n{t2}")
assert '72' in t2, f"FAIL"
print("  PASS\n")

print("=== SCENARIO 3: legacy only (no top-level) ===")
r3 = {
    'report_contract': {
        'security_score_percent': 65, 'security_score_grade': 'C',
        'critical_count': 0, 'high_count': 0, 'medium_count': 0, 'low_count': 0,
        'detailed_issues': []
    }
}
t3 = strip_ansi(to_table('analyze', r3))
print(f"  Summary: {to_summary('analyze', r3)}")
print(f"  Table:\n{t3}")
assert '65' in t3, f"FAIL"
assert 'C' in t3, f"FAIL"
print("  PASS: legacy fallback works\n")

print("=== SCENARIO 4: canonical 0/F wins over legacy 50/D ===")
r4 = {
    'security_score': 0, 'security_score_grade': 'F',
    'report_contract': {'security_score_percent': 50, 'security_score_grade': 'D'}
}
t4 = strip_ansi(to_table('analyze', r4))
print(f"  Summary: {to_summary('analyze', r4)}")
print(f"  Table:\n{t4}")
assert '0' in t4, f"FAIL: 0 should be shown, got:\n{t4}"
assert 'F' in t4, f"FAIL: F should be shown, got:\n{t4}"
print("  PASS: canonical 0/F wins over legacy 50/D\n")

print("=== SCENARIO 5: empty result ===")
r5 = {'findings': []}
t5 = strip_ansi(to_table('analyze', r5))
print(f"  Summary: {to_summary('analyze', r5)}")
print(f"  Table:\n{t5}")
assert 'N/A' in t5, f"FAIL: N/A should be shown for empty"
print("  PASS: N/A shown when no scores at all\n")

print("ALL SCENARIOS PASSED")
