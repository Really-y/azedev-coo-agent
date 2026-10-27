"""Seeds the holographic memory with initial durable facts (run once).

Run it with Hermes' own Python (hermes_bootstrap puts its dependencies on sys.path):
    HERMES_HOME=~/.hermes ~/.hermes/tools/python-*/bin/python3 -I memory/seed_facts.example.py

Rule: each fact is one short sentence + the person's name (entities) + 3-8 keywords. Write the
keywords in Azerbaijani letters (ə, ı, ş, ç, ğ): holographic does not fold "ə" into "e", so the ASCII
keyword "gecikme" does not match "gecikmə" in a question. Phone numbers, finances and CEO-only notes
never go here — memory can surface in any chat, WhatsApp included. The facts below are in Azerbaijani
because the agent works in Azerbaijani.
"""
import os
import sys

HOME = os.path.expanduser("~/.hermes")
sys.path[:0] = [f"{HOME}/hermes-agent", f"{HOME}/plugins"]
import hermes_bootstrap  # noqa: E402,F401  (puts Hermes dependencies on sys.path)
from holographic import HolographicMemoryProvider  # noqa: E402

FACTS = [  # (text, category, entities, keywords, valid_from)
    ("Eskalasiya qaydası: üzv, sonra team lead, sonra COO, sonra CEO.", "project",
     [], ["eskalasiya", "gecikmə", "gecikib", "xəbər", "pillə", "kimə"], None),
    ("Lead A B2B Solutions / SaaS istiqamətinin team lead-idir.", "project",
     ["Lead A"], ["saas", "b2b", "rəhbər", "komanda", "sahə"], None),
    ("CEO cavabı Azərbaycan dilində, qısa və faktlara əsaslanan formada istəyir.", "user_pref",
     [], ["dil", "azərbaycanca", "üslub", "qısa", "hesabat", "format"], None),
]

p = HolographicMemoryProvider()
p.initialize("seed-facts", platform="cli", agent_context="primary")
try:
    for content, category, entities, keywords, valid_from in FACTS:
        args = {"action": "add", "content": content, "category": category, "origin": "confirmed",
                "entities": entities, "keywords": keywords}
        if valid_from:
            args["valid_from"] = valid_from
        print(p.handle_tool_call("fact_store", args)[:160])
    print(p.handle_tool_call("fact_store", {"action": "stats"})[:400])
finally:
    p.shutdown()
