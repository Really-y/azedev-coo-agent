#!/usr/bin/env python3
"""Team stats from kanba search_tasks dumps.

Usage: team_stats.py OPEN_JSON DONE_JSON [YYYY-MM-DD]
  OPEN_JSON = search_tasks(status=open, limit=200) spillover file
  DONE_JSON = search_tasks(status=done, limit=200) spillover file
Writes ~/.hermes/workspace/kpi/<date>.json and prints a compact table.
Single source of truth for counts - never count by hand.
Note: done date = updated_at (approx; later edits shift it).
"""
import json, sys, collections, datetime as dt, os

PROJ = {  # kanban project_id prefix -> short name (replace with your own boards)
    "aaaaaaaa": "game-studio", "bbbbbbbb": "saas", "cccccccc": "marketing"}
TEAM = {  # lead -> members (same names as team.md; replace with your own team)
    "Lead A": ["Lead A", "Member 1", "Member 2"],
    "Lead B": ["Lead B", "Member 3"],
    "Lead C": ["Lead C", "Member 4"],
}

def load(p):
    return json.load(open(p))["tasks"]

def main():
    o, d = load(sys.argv[1]), load(sys.argv[2])
    today = sys.argv[3] if len(sys.argv) > 3 else str(dt.date.today())
    since = str(dt.date.fromisoformat(today) - dt.timedelta(days=30))
    nm = lambda t: ((t.get("assignee") or {}).get("full_name") or "UNASSIGNED").strip()
    per = collections.defaultdict(lambda: dict(open=0, overdue=0, nodue=0, weakdesc=0,
                                               done30=0, ontime=0, late=0, overdue_titles=[]))
    for t in o:
        p = per[nm(t)]; p["open"] += 1
        due = (t["due_date"] or "")[:10]
        if not due: p["nodue"] += 1
        elif due < today:
            p["overdue"] += 1; p["overdue_titles"].append(f'{t["title"][:40]} ({due})')
        if len((t["description"] or "").strip()) < 20: p["weakdesc"] += 1
    for t in d:
        if t["updated_at"][:10] < since: continue
        p = per[nm(t)]; p["done30"] += 1
        if t["due_date"]:
            p["ontime" if t["updated_at"][:10] <= t["due_date"][:10] else "late"] += 1
    leads = {}
    for lead, mem in TEAM.items():
        idle = [m for m in mem if per[m]["open"] == 0]
        leads[lead] = dict(open=sum(per[m]["open"] for m in mem),
                           overdue=sum(per[m]["overdue"] for m in mem),
                           nodue=sum(per[m]["nodue"] for m in mem),
                           weakdesc=sum(per[m]["weakdesc"] for m in mem), idle=idle)
    out = dict(date=today, open_total=len(o), per=per, leads=leads)
    path = os.path.expanduser(f"~/.hermes/workspace/kpi/{today}.json")
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(f"open={len(o)} overdue={sum(v['overdue'] for v in per.values())} -> {path}")
    for k, v in sorted(per.items(), key=lambda x: -x[1]["open"]):
        r = v["ontime"] / (v["ontime"] + v["late"]) * 100 if v["ontime"] + v["late"] else None
        print(f'{k:22} open={v["open"]} over={v["overdue"]} done30={v["done30"]} '
              f'ontime={"-" if r is None else f"{r:.0f}%"} nodue={v["nodue"]} weakdesc={v["weakdesc"]}')
    for l, v in leads.items(): print("LEAD", l, v)

if __name__ == "__main__":
    main()
