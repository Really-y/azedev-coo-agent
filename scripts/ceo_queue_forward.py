#!/usr/bin/env python3
"""Forward WhatsApp-session escalations to the CEO (cron no_agent, every 5m).
WhatsApp sessions have no send tool; they write one file per request into
~/.hermes/workspace/ceo-queue/inbox/. This prints new ones (delivered to CEO
Telegram by cron) and moves them to sent/. Empty stdout = nothing sent."""
import os, glob, shutil, datetime
B = os.path.expanduser("~/.hermes/workspace/ceo-queue")
files = sorted(glob.glob(f"{B}/inbox/*"))
out = []
for f in files:
    try:
        txt = open(f, encoding="utf-8", errors="replace").read().strip()[:1200]
    except Exception as e:
        txt = f"(oxunmadı: {e})"
    if txt:
        out.append(txt)
    shutil.move(f, f"{B}/sent/{datetime.datetime.now():%Y%m%d-%H%M%S}-{os.path.basename(f)}")
if out:
    print(f"📥 Təsdiq/eskalasiya sorğusu ({len(out)}):\n\n" + "\n\n———\n\n".join(out) +
          "\n\nCavabı bura yazın — icra edirəm.")
