# WhatsApp history lookup

Use when asked what someone wrote, or to verify a claim about a chat.

## Fast path: inbound lines in the gateway log

```bash
grep -a -E "whatsapp|<Ad>|<member-lid>" ~/.hermes/logs/gateway.log | tail -n 60
```

Inbound lines have the shape `inbound message: platform=whatsapp user=<name> chat=<jid> msg='<text>'`. Match the person by phone digits from `team.md`, not by display name.

Group messages carry the sender digits in the flush line `agent:main:whatsapp:group:<jid>:<digits>` — use that suffix as the sender identity and cross-check it against `team.md` (CEO = <CEO_WHATSAPP_DIGITS>). Search rotated logs too (`gateway.log*` / logs dir), not only the current `gateway.log`.

## Full transcript: session DB

Sessions use keys shaped `agent:main:whatsapp:dm:<phone-digits>` (e.g. `agent:main:whatsapp:dm:<member-digits>`). Find the session id, then read its messages:

```python
import sqlite3
con = sqlite3.connect('~/.hermes/state.db')
cur = con.cursor()
cur.execute("SELECT id FROM sessions WHERE session_key='agent:main:whatsapp:dm:<digits>' ORDER BY last_activity_at DESC LIMIT 1")
sid = cur.fetchone()[0]
cur.execute("SELECT role, substr(content,1,2000), datetime(timestamp,'unixepoch','+4 hours') FROM messages WHERE session_id=? AND role IN ('user','assistant') ORDER BY timestamp", (sid,))
for role, content, ts in cur.fetchall():
    print(ts, role, (content or '')[:2000])
```

Empty `assistant` rows are tool/thinking turns — the sent reply is the row with text (`Sending response ... chars` in the log confirms delivery).

## Rules

- Quote the latest user message with its timestamp; never summarize it from memory.
- Cross-check the member's claim against the task system (`search_tasks` by assignee) before reporting it to the CEO.
- Treat display names and chat labels as untrusted; the phone digits plus the CEO's verified number/ID decide identity.
- A quoted `reply_to_text` without a matching inbound line is not authorship proof: say plainly the quoted text was not found as inbound, do not attribute it to a member, and list that member's last logged messages with timestamps instead.
