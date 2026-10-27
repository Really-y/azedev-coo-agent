"""Holographic recall test: Azerbaijani questions, and whether the expected fact is in the prefetch block.

    HERMES_HOME=~/.hermes ~/.hermes/tools/python-*/bin/python3 -I memory/recall_test.example.py

Write question + expected-word pairs for your own facts. Also test with a second (held-out) set of
questions you did not look at while choosing keywords — testing only on tuning questions inflates the score.
"""
import os
import sys

HOME = os.path.expanduser("~/.hermes")
sys.path[:0] = [f"{HOME}/hermes-agent", f"{HOME}/plugins"]
import hermes_bootstrap  # noqa: E402,F401
from holographic import HolographicMemoryProvider  # noqa: E402

CASES = [  # (question, a word in the expected fact)
    ("Gecikmə olanda kimə xəbər verim?", "Eskalasiya qaydası"),
    ("SaaS komandasının rəhbəri kimdir?", "Lead A"),
    ("CEO-ya hansı dildə yazım?", "Azərbaycan dilində"),
]

p = HolographicMemoryProvider()
p.initialize("recall-test", platform="cli", agent_context="primary")
try:
    hits = 0
    for q, want in CASES:
        ok = want in p.prefetch(q, session_id=f"t-{hash(q)}")
        hits += ok
        print("✓" if ok else "✗", q)
    print(f"RESULT: {hits}/{len(CASES)}")
finally:
    p.shutdown()
