"""Holographic yaddaşına ilkin sabit faktları yükləyir (bir dəfəlik).

İşə salma (Hermes-in öz Python-u ilə, asılılıqları hermes_bootstrap qoşur):
    HERMES_HOME=~/.hermes ~/.hermes/tools/python-*/bin/python3 -I memory/seed_facts.example.py

Qayda: hər fakt bir qısa cümlə + şəxs adı (entities) + 3-8 açar söz. Açar sözləri Azərbaycan
hərfləri ilə yazın (ə, ı, ş, ç, ğ): holographic "ə"-ni "e" kimi qatlamır, ASCII "gecikme" sözü
sualdakı "gecikmə" ilə uyğun gəlmir. Telefon nömrəsi, maliyyə və CEO-ya aid məxfi qeydlər bura
yazılmır — yaddaş istənilən söhbətə (WhatsApp daxil) düşə bilər.
"""
import os
import sys

HOME = os.path.expanduser("~/.hermes")
sys.path[:0] = [f"{HOME}/hermes-agent", f"{HOME}/plugins"]
import hermes_bootstrap  # noqa: E402,F401  (Hermes asılılıqlarını sys.path-a əlavə edir)
from holographic import HolographicMemoryProvider  # noqa: E402

FACTS = [  # (mətn, kateqoriya, entities, keywords, valid_from)
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
