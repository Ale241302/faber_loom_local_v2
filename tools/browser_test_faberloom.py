#!/usr/bin/env python3
"""Headless browser test for FaberLoom local UI."""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

URL = "http://localhost:8000/static/index.html"
OUT_DIR = Path(__file__).resolve().parent
LOG_PATH = OUT_DIR / "browser_test_log.json"
SHOT_RENDERED = OUT_DIR / "browser_test_1_rendered.png"
SHOT_AFTER_ENTER = OUT_DIR / "browser_test_2_after_enter.png"
SHOT_AFTER_CLICK = OUT_DIR / "browser_test_3_after_click_send.png"

def main():
    logs = []
    errors = []
    network_errors = []
    requests = []

    def log_console(msg):
        entry = {"type": msg.type, "text": msg.text, "location": str(msg.location), "time": time.time()}
        logs.append(entry)
        if msg.type in ("error", "warning"):
            errors.append(entry)

    def log_pageerror(err):
        entry = {"type": "pageerror", "text": str(err), "time": time.time()}
        logs.append(entry)
        errors.append(entry)

    def log_request(req):
        requests.append({"method": req.method, "url": req.url, "time": time.time()})

    def log_response(resp):
        status = resp.status
        if status >= 400:
            network_errors.append({"status": status, "url": resp.url, "time": time.time()})

    def log_request_failed(req):
        try:
            failure = req.failure
            error_text = failure.get("errorText") if isinstance(failure, dict) else str(failure)
        except Exception as e:
            error_text = str(e)
        network_errors.append({"failed": True, "url": req.url, "error": error_text, "time": time.time()})

    report = {
        "url": URL,
        "start": time.time(),
        "console_errors": [],
        "console_warnings": [],
        "network_errors": [],
        "observed": {},
        "screenshots": {},
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.on("console", log_console)
        page.on("pageerror", log_pageerror)
        page.on("request", log_request)
        page.on("response", log_response)
        page.on("requestfailed", log_request_failed)

        try:
            page.goto(URL, wait_until="networkidle", timeout=15000)
        except PlaywrightTimeout:
            report["error"] = "Timeout waiting for page load"
            save(report, logs, errors, network_errors)
            browser.close()
            return

        # Wait for React/Babel render
        time.sleep(4)
        page.wait_for_load_state("networkidle")

        report["title"] = page.title()
        report["url_after"] = page.url
        page.screenshot(path=str(SHOT_RENDERED), full_page=True)
        report["screenshots"]["rendered"] = str(SHOT_RENDERED)

        # Locate composer
        textarea = page.locator('textarea[placeholder="Escribe para crear un chat nuevo…"]').first
        try:
            textarea.wait_for(state="visible", timeout=5000)
            composer_visible = True
        except PlaywrightTimeout:
            composer_visible = False

        report["observed"]["composer_visible"] = composer_visible
        if not composer_visible:
            report["error"] = "Composer textarea not visible"
            save(report, logs, errors, network_errors)
            browser.close()
            return

        # Type message
        textarea.fill("hola")
        report["observed"]["message_typed"] = "hola"

        # --- Try Enter ---
        textarea.press("Enter")
        report["observed"]["send_attempt_enter"] = True
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SHOT_AFTER_ENTER), full_page=True)
        report["screenshots"]["after_enter"] = str(SHOT_AFTER_ENTER)

        draft_after_enter = textarea.input_value()
        report["observed"]["draft_after_enter"] = draft_after_enter
        report["observed"]["enter_sent"] = draft_after_enter == ""

        # --- Fallback to clicking Send if Enter did not clear the draft ---
        if draft_after_enter != "":
            send_button = page.locator('button.send-button').first
            try:
                send_button.wait_for(state="visible", timeout=3000)
                send_button.click()
                report["observed"]["send_attempt_click"] = True
                time.sleep(6)  # wait for create + completion + UI updates
                page.wait_for_load_state("networkidle")
            except Exception as e:
                report["observed"]["send_attempt_click"] = False
                report["observed"]["send_click_error"] = str(e)

        page.screenshot(path=str(SHOT_AFTER_CLICK), full_page=True)
        report["screenshots"]["after_click_send"] = str(SHOT_AFTER_CLICK)

        # Re-locate textarea in case it remounted (placeholder changes after chat creation)
        final_textarea = page.locator('form[aria-label="Composer de chat"] textarea').first
        try:
            report["observed"]["draft_after_click_send"] = final_textarea.input_value(timeout=3000)
        except Exception as e:
            report["observed"]["draft_after_click_send_error"] = str(e)
            report["observed"]["draft_after_click_send"] = None

        try:
            report["observed"]["active_chat_title"] = page.locator(".stage-title h2").first.inner_text(timeout=3000) if page.locator(".stage-title h2").count() else None
        except Exception as e:
            report["observed"]["active_chat_title_error"] = str(e)
            report["observed"]["active_chat_title"] = None

        report["observed"]["body_text"] = page.locator("body").inner_text()[:2500]
        try:
            report["observed"]["thinking_steps_visible"] = page.locator(".thinking-steps").count() > 0 and page.locator(".thinking-steps").first.is_visible()
        except Exception:
            report["observed"]["thinking_steps_visible"] = False
        report["observed"]["message_bubbles_count"] = page.locator(".message-bubble, .message, [class*='message']").count()

        browser.close()

    report["end"] = time.time()
    report["console_errors"] = [e for e in errors if e["type"] == "error"]
    report["console_warnings"] = [e for e in errors if e["type"] == "warning"]
    report["network_errors"] = network_errors
    report["all_logs"] = logs
    report["requests_sample"] = requests[-20:]
    save(report, logs, errors, network_errors)
    print(json.dumps({
        "ok": True,
        "title": report.get("title"),
        "url": report.get("url_after"),
        "console_error_count": len(report["console_errors"]),
        "console_warning_count": len(report["console_warnings"]),
        "network_error_count": len(report["network_errors"]),
        "composer_visible": report["observed"].get("composer_visible"),
        "enter_sent": report["observed"].get("enter_sent"),
        "draft_after_click_send": report["observed"].get("draft_after_click_send"),
        "active_chat_title": report["observed"].get("active_chat_title"),
        "thinking_steps_visible": report["observed"].get("thinking_steps_visible"),
        "screenshots": report["screenshots"],
        "log_file": str(LOG_PATH),
    }, indent=2, ensure_ascii=False))

def save(report, logs, errors, network_errors):
    report["console_errors"] = [e for e in errors if e["type"] == "error"]
    report["console_warnings"] = [e for e in errors if e["type"] == "warning"]
    report["network_errors"] = network_errors
    report["all_logs"] = logs
    LOG_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

if __name__ == "__main__":
    main()
