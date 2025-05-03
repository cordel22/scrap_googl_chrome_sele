from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
from user_agents import USER_AGENTS

app = Flask(__name__)

CHROME_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

def scrape_google_search(query):
    print("▶️ Starting scrape for query:", query)

    # Step 1: Verify Chrome binary
    if os.path.exists(CHROME_PATH):
        chrome_status = "✅ Chrome binary found at expected path."
        print("[CHECK] Chrome binary: FOUND ✅")
    else:
        chrome_status = "❌ Chrome binary NOT found at expected path!"
        print("[CHECK] Chrome binary: MISSING ❌ Expected at:", CHROME_PATH)

    # Step 2: Prepare options with stealth
    user_agent = random.choice(USER_AGENTS)
    print("[INFO] Using user-agent:", user_agent)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-agent={user_agent}")
    options.binary_location = CHROME_PATH

    try:
        driver = webdriver.Chrome(options=options)
        print("[OK] Chrome WebDriver launched.")

        # Step 3: Bypass headless detection via CDP
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        print("[OK] WebDriver stealth setup complete.")

        driver.get(f"https://www.google.com/search?q={query}")
        print("[OK] Navigated to Google search.")

        # Step 4: Wait dynamically for results
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="yuRUbf"]/a'))
            )
            print("[OK] Search results detected.")
        except:
            print("[FAIL] Timeout: Search results not found.")
            print("[DEBUG] Page title:", driver.title)
            print("[DEBUG] Current URL:", driver.current_url)
            print("[DEBUG] Page source snippet:\n", driver.page_source[:1000])
            return f"{chrome_status} ❗ Timeout waiting for search results", []

        # Step 5: Extract links
        results = []
        elements = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a')
        print(f"[INFO] Found {len(elements)} result elements.")

        for el in elements:
            href = el.get_attribute("href")
            if href and "google.com" not in href:
                results.append(href)
            if len(results) >= 3:
                break

        if results:
            print(f"[SUCCESS] Scraped {len(results)} results for '{query}'")
        else:
            print("[WARN] No valid external links found in results.")

        return chrome_status, results

    except Exception as e:
        error_msg = f"{chrome_status} ❗ Error during scraping: {str(e)}"
        print("[ERROR]", error_msg)
        return error_msg, []

    finally:
        try:
            driver.quit()
            print("[CLEANUP] WebDriver closed successfully.")
        except:
            print("[WARN] WebDriver cleanup failed or was never started.")

@app.route("/")
def home():
    query = "donald trump"
    chrome_message, results = scrape_google_search(query)

    if results:
        html = f"<h1>{chrome_message}</h1><h2>Search results for: {query}</h2><ul>"
        for link in results:
            html += f'<li><a href="{link}" target="_blank">{link}</a></li>'
        html += "</ul>"
        print("[INFO] Results successfully returned to browser.")
    else:
        html = f"<h1>{chrome_message}</h1><h2>No results found for: {query}. Please try again later.</h2>"
        print("[FAILURE] No results returned.")

    return html