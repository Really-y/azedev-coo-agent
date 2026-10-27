#!/usr/bin/env python3
"""Archives Hermes memory and workspace files and sends them to a Telegram backup group (cron no_agent).

The group's chat id is in ~/.local/share/hermes-backup/telegram_chat. The bot token is read from
~/.hermes/.env (TELEGRAM_BOT_TOKEN). .env, auth.json, state.db (chat history) and other secrets never
go into the archive. Empty stdout = success, no message; on failure the text goes to the CEO's Telegram.
"""
import datetime, io, json, os, re, sqlite3, tarfile, tempfile, urllib.request, uuid

H = os.path.expanduser("~/.hermes")
CHAT_FILE = os.path.expanduser("~/.local/share/hermes-backup/telegram_chat")
ITEMS = ["SOUL.md", "memories", "workspace", "dreaming.json", "cron/jobs.json", "cron-prompts", "scripts",
         "skills/coo-operations", "config.yaml"]
SECRET = re.compile(r"kmcp_[A-Za-z0-9_.\-]{20,}|\bsk-[A-Za-z0-9_\-]{20,}|\bghp_[A-Za-z0-9]{20,}|"
                    r"\b\d{8,10}:AA[A-Za-z0-9_\-]{30,}")  # Kanba, OpenAI, GitHub, Telegram bot


def env_value(name):
    for line in open(f"{H}/.env", encoding="utf-8"):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError(f"{name} is not in .env")


def skip(info):
    name = os.path.basename(info.name)
    return None if name.endswith(".lock") or name == "__pycache__" else info


def build_archive(path):
    leaks = []
    with tarfile.open(path, "w:gz") as tar:
        for item in ITEMS:
            src = f"{H}/{item}"
            if not os.path.exists(src):
                continue
            for root, _, files in os.walk(src) if os.path.isdir(src) else [(os.path.dirname(src), [], [item])]:
                for f in files:
                    p = os.path.join(root, os.path.basename(f))
                    if p.endswith((".md", ".json", ".yaml", ".py", ".txt")) and \
                            SECRET.search(open(p, encoding="utf-8", errors="ignore").read()):
                        leaks.append(os.path.relpath(p, H))
            tar.add(src, arcname=item, filter=skip)
        # the SQLite memory may be open: use the backup API for a consistent copy
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            with sqlite3.connect(f"file:{H}/memory_store.db?mode=ro", uri=True) as s, sqlite3.connect(tmp.name) as d:
                s.backup(d)
                facts = d.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            tar.add(tmp.name, arcname="memory_store.db")
    if leaks:
        raise RuntimeError("text that looks like a secret was found, backup not sent: " + ", ".join(leaks))
    return facts


def send_document(token, chat_id, path, caption):
    boundary = uuid.uuid4().hex
    body = io.BytesIO()
    for key, value in (("chat_id", chat_id), ("caption", caption)):
        body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="document"; '
               f'filename="{os.path.basename(path)}"\r\nContent-Type: application/gzip\r\n\r\n'.encode())
    body.write(open(path, "rb").read())
    body.write(f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendDocument", data=body.getvalue(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        if not json.load(r).get("ok"):
            raise RuntimeError("Telegram sendDocument ok=false")


def main():
    chat_id = open(CHAT_FILE).read().strip()
    now = datetime.datetime.now()
    with tempfile.TemporaryDirectory() as tmp:
        path = f"{tmp}/hermes-backup-{now:%Y-%m-%d_%H%M}.tar.gz"
        facts = build_archive(path)
        size_kb = os.path.getsize(path) // 1024
        send_document(env_value("TELEGRAM_BOT_TOKEN"), chat_id, path,
                      f"🗄 Hermes backup — {now:%d.%m.%Y %H:%M}\nMemory: {facts} facts · {size_kb} KB")


try:
    main()
except Exception as exc:
    msg = str(exc)
    try:
        msg = msg.replace(env_value("TELEGRAM_BOT_TOKEN"), "***")  # keep the token out of URL errors
    except Exception:
        pass
    print(f"⚠️ Hermes Telegram backup failed: {msg}")
