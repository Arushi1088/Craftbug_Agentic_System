import time
from playwright.sync_api import sync_playwright

def run_scenario():
    logs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        start_time = time.time()
        page.goto("http://localhost:3000/mock-word.html")
        logs.append({"step": "Visit homepage", "time_ms": int((time.time() - start_time) * 1000)})

        try:
            btn_start = page.locator("text=Start Editing")
            start_time = time.time()
            btn_start.click()
            logs.append({"step": "Click 'Start Editing'", "time_ms": int((time.time() - start_time) * 1000)})
        except Exception as e:
            logs.append({"step": "Click 'Start Editing'", "error": str(e)})

        try:
            text_box = page.locator("textarea")
            start_time = time.time()
            text_box.fill("This is a test sentence")
            logs.append({"step": "Type in text area", "time_ms": int((time.time() - start_time) * 1000)})
        except Exception as e:
            logs.append({"step": "Type in text area", "error": str(e)})

        browser.close()

    return logs

if __name__ == "__main__":
    import json
    result = run_scenario()
    with open("scenario_log.json", "w") as f:
        json.dump(result, f, indent=2)
    print("✅ Scenario executed and logged.")
