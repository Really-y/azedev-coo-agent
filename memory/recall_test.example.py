"""Holographic recall testi: Azərbaycan dilində suallar, gözlənilən faktın prefetch blokunda olub-olmadığı.

    HERMES_HOME=~/.hermes ~/.hermes/tools/python-*/bin/python3 -I memory/recall_test.example.py

Öz faktlarınıza uyğun sual + gözlənilən söz cütləri yazın. Açar sözləri seçərkən istifadə etmədiyiniz
ikinci (holdout) sual dəsti ilə də yoxlayın — yalnız tənzimlədiyiniz suallarla test nəticəni şişirdir.
"""
import os
import sys

HOME = os.path.expanduser("~/.hermes")
sys.path[:0] = [f"{HOME}/hermes-agent", f"{HOME}/plugins"]
import hermes_bootstrap  # noqa: E402,F401
from holographic import HolographicMemoryProvider  # noqa: E402

CASES = [  # (sual, gözlənilən faktda olan söz)
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
    print(f"NƏTİCƏ: {hits}/{len(CASES)}")
finally:
    p.shutdown()
