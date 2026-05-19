import argparse
import csv
import logging
import random
import subprocess
import re
import sys
import time
import traceback
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

pyperclip = None
Application = None
Desktop = None
send_keys = None
LOG_PATH = Path(__file__).with_name("zalo_sender.log")


def setup_logging():
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_zalo_dependencies():
    global pyperclip, Application, Desktop, send_keys

    try:
        import pyperclip as pyperclip_module
        from pywinauto import Application as ApplicationClass
        from pywinauto import Desktop as DesktopClass
        from pywinauto.keyboard import send_keys as send_keys_func
    except ImportError as exc:
        missing = str(exc).split("'")[1] if "'" in str(exc) else str(exc)
        print(f"Missing dependency: {missing}")
        print("Install dependencies with:")
        print("  python -m pip install -r requirements.txt")
        raise SystemExit(1) from exc

    pyperclip = pyperclip_module
    Application = ApplicationClass
    Desktop = DesktopClass
    send_keys = send_keys_func


def read_rows(csv_path: Path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"phone", "message"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"CSV is missing required column(s): {', '.join(sorted(missing))}"
            )

        rows = []
        for line_number, row in enumerate(reader, start=2):
            phone = normalize_phone(row.get("phone") or "")
            message = (row.get("message") or "").strip()
            if not phone or not message:
                print(f"Skipping line {line_number}: phone/message is empty")
                continue
            if not looks_like_phone(phone):
                print(f"Skipping line {line_number}: invalid phone number: {phone}")
                continue
            rows.append({"phone": phone, "message": message, "line": line_number})
        return rows


def normalize_phone(value: str) -> str:
    value = value.strip()
    if value.startswith("+"):
        return "+" + re.sub(r"\D", "", value[1:])
    return re.sub(r"\D", "", value)


def looks_like_phone(value: str) -> bool:
    if value.startswith("+"):
        digits = value[1:]
    else:
        digits = value
    return digits.isdigit() and 8 <= len(digits) <= 15


def connect_zalo(title_re: str):
    try:
        windows = Desktop(backend="uia").windows(title_re=title_re, visible_only=True)
        logging.info("Found %s visible window(s) matching %s", len(windows), title_re)
        for window in windows:
            logging.info(
                "Window candidate: title=%r handle=%s",
                window.window_text(),
                window.handle,
            )
        exact_windows = [w for w in windows if w.window_text().strip() == "Zalo"]
        if exact_windows:
            win = exact_windows[0]
        elif windows:
            win = windows[0]
        else:
            handle = find_zalo_window_handle_from_powershell()
            logging.info("PowerShell fallback Zalo handle=%s", handle)
            if not handle:
                raise RuntimeError("No Zalo window handle found")
            win = Desktop(backend="uia").window(handle=handle)

        app = Application(backend="uia").connect(handle=win.handle)
    except Exception as exc:
        logging.exception("Cannot connect to Zalo")
        raise RuntimeError(
            "Cannot connect to Zalo PC. Open Zalo PC, log in, and keep its window visible."
        ) from exc

    win = app.window(handle=win.handle)
    win.set_focus()
    time.sleep(0.5)
    return win


def find_zalo_window_handle_from_powershell():
    command = (
        "Get-Process | "
        "Where-Object { $_.ProcessName -eq 'Zalo' -and $_.MainWindowTitle -eq 'Zalo' -and $_.MainWindowHandle -ne 0 } | "
        "Select-Object -First 1 -ExpandProperty MainWindowHandle"
    )
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if completed.returncode != 0:
        logging.info("PowerShell handle lookup failed: %s", completed.stderr.strip())
        return None
    output = completed.stdout.strip()
    return int(output) if output.isdigit() else None


def paste_text(text: str):
    pyperclip.copy(text)
    time.sleep(0.1)
    send_keys("^v")


def open_phone(phone: str, search_hotkey: str, after_search_delay: float):
    logging.info("Opening phone %s", phone)
    send_keys(search_hotkey)
    time.sleep(0.3)
    paste_text(phone)
    time.sleep(after_search_delay)
    send_keys("{ENTER}")
    time.sleep(0.8)


def clear_message_box():
    send_keys("^a")
    time.sleep(0.1)
    send_keys("{BACKSPACE}")


def focus_or_reconnect(win, title_re: str):
    try:
        win.set_focus()
        return win
    except Exception:
        return connect_zalo(title_re)


def send_current_message(win, title_re: str):
    win = focus_or_reconnect(win, title_re)
    time.sleep(0.2)
    try:
        send_keys("{ENTER}")
    except Exception as exc:
        logging.exception("Could not send Enter")
        print(f"Could not send Enter to Zalo automatically: {exc}")
        print("The message is still drafted in Zalo. Click the chat box and press Enter manually.")
        raise
    return win


def sleep_random(min_seconds: float, max_seconds: float, reason: str):
    if max_seconds < min_seconds:
        max_seconds = min_seconds
    delay = random.uniform(min_seconds, max_seconds)
    logging.info("Sleeping %.2fs: %s", delay, reason)
    time.sleep(delay)


def prompt_action(index: int, total: int, phone: str) -> str:
    print()
    print(f"[{index}/{total}] Drafted message for phone: {phone}")
    print("Inspect Zalo PC now.")
    while True:
        answer = input("Send this message? [s]end / s[k]ip / [q]uit: ").strip().lower()
        if answer in {"s", "send"}:
            return "send"
        if answer in {"k", "skip"}:
            return "skip"
        if answer in {"q", "quit"}:
            return "quit"
        print("Please type s, k, or q.")


def get_action(index: int, total: int, phone: str, auto_send: bool) -> str:
    if auto_send:
        print()
        print(f"[{index}/{total}] Auto-sending message for phone: {phone}")
        return "send"
    return prompt_action(index, total, phone)


def main():
    setup_logging()
    logging.info("Starting zalo_csv_sender")
    parser = argparse.ArgumentParser(
        description="Draft Zalo PC messages from a CSV and require confirmation before each send."
    )
    parser.add_argument("csv", type=Path, help="CSV path with columns: phone,message")
    parser.add_argument(
        "--title-re",
        default=".*Zalo.*",
        help="Window title regex for Zalo PC. Default: .*Zalo.*",
    )
    parser.add_argument(
        "--search-hotkey",
        default="^f",
        help="Zalo search hotkey for pywinauto. Default: ^f",
    )
    parser.add_argument(
        "--after-search-delay",
        type=float,
        default=1.0,
        help="Seconds to wait after pasting contact in search. Increase on slow PCs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate and print CSV rows; do not control Zalo.",
    )
    parser.add_argument(
        "--start-now",
        action="store_true",
        help="Connect to Zalo immediately without waiting for the initial Enter prompt.",
    )
    parser.add_argument(
        "--auto-send",
        action="store_true",
        help="Send each drafted message immediately without asking for s/k/q confirmation.",
    )
    parser.add_argument(
        "--between-send-delay",
        type=float,
        default=None,
        help="Fixed seconds to wait after each sent message. Overrides random delay.",
    )
    parser.add_argument(
        "--min-send-delay",
        type=float,
        default=8.0,
        help="Minimum random seconds to wait after each sent message in auto-send mode. Default: 8",
    )
    parser.add_argument(
        "--max-send-delay",
        type=float,
        default=20.0,
        help="Maximum random seconds to wait after each sent message in auto-send mode. Default: 20",
    )
    parser.add_argument(
        "--min-before-send-delay",
        type=float,
        default=1.5,
        help="Minimum random seconds to pause after drafting and before pressing Enter in auto-send mode. Default: 1.5",
    )
    parser.add_argument(
        "--max-before-send-delay",
        type=float,
        default=4.0,
        help="Maximum random seconds to pause after drafting and before pressing Enter in auto-send mode. Default: 4",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"CSV not found: {args.csv}")
        sys.exit(1)

    try:
        rows = read_rows(args.csv)
    except Exception as exc:
        print(f"Cannot read CSV: {exc}")
        sys.exit(1)

    if not rows:
        print("No valid rows found.")
        return

    print(f"Loaded {len(rows)} message(s) from {args.csv}")
    logging.info("Loaded %s valid row(s) from %s", len(rows), args.csv)
    if args.dry_run:
        for row in rows:
            print(f"Line {row['line']}: {row['phone']} -> {row['message']}")
        return

    load_zalo_dependencies()

    print("Make sure Zalo PC is open, logged in, and not minimized.")
    if not args.start_now:
        input("Press Enter to connect to Zalo PC...")

    win = connect_zalo(args.title_re)

    sent = 0
    skipped = 0
    for index, row in enumerate(rows, start=1):
        phone = row["phone"]
        message = row["message"]
        logging.info("Processing row %s/%s phone=%s", index, len(rows), phone)

        win = focus_or_reconnect(win, args.title_re)
        open_phone(phone, args.search_hotkey, args.after_search_delay)
        paste_text(message)
        logging.info("Drafted message for phone=%s", phone)

        action = get_action(index, len(rows), phone, args.auto_send)
        logging.info("User action for phone=%s: %s", phone, action)

        if action == "send":
            try:
                if args.auto_send:
                    sleep_random(
                        args.min_before_send_delay,
                        args.max_before_send_delay,
                        "before auto-send",
                    )
                win = send_current_message(win, args.title_re)
                sent += 1
                logging.info("Sent phone=%s", phone)
                if args.between_send_delay is not None:
                    time.sleep(args.between_send_delay)
                elif args.auto_send:
                    sleep_random(args.min_send_delay, args.max_send_delay, "after auto-send")
                else:
                    time.sleep(0.8)
            except Exception:
                retry = input("Press Enter manually in Zalo, then type [c]ontinue or [q]uit: ").strip().lower()
                if retry in {"q", "quit"}:
                    print("Stopped by user.")
                    logging.info("Stopped by user after send failure")
                    break
        elif action == "skip":
            win = focus_or_reconnect(win, args.title_re)
            clear_message_box()
            skipped += 1
            logging.info("Skipped phone=%s", phone)
            time.sleep(0.3)
        else:
            win = focus_or_reconnect(win, args.title_re)
            clear_message_box()
            print("Stopped by user.")
            logging.info("Stopped by user")
            break

    print()
    print(f"Done. Sent: {sent}. Skipped: {skipped}.")
    logging.info("Done. Sent=%s Skipped=%s", sent, skipped)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        setup_logging()
        logging.error("Fatal error:\n%s", traceback.format_exc())
        print()
        print(f"Fatal error. Details were written to: {LOG_PATH}")
        raise
