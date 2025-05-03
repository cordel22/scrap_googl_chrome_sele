from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
from user_agents import USER_AGENTS  # Your custom list of user agents

app = Flask(__name__)

CHROME_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

def scrape_google_search(query):
    # Step 1: Check Chrome binary
    if os.path.exists(CHROME_PATH):
        chrome_status = "✅ Chrome binary found at expected path."
        print("[INFO]", chrome_status)
    else:
        chrome_status = "❌ Chrome binary NOT found at expected path!"
        print("[ERROR]", chrome_status)

    # Step 2: Setup WebDriver options with stealth
    user_agent = random.choice(USER_AGENTS)
    print(f"[INFO] Using User-Agent: {user_agent}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.binary_location = CHROME_PATH

    try:
        driver = webdriver.Chrome(options=options)
        print("[INFO] ✅ Chrome WebDriver launched successfully.")
        
        # Step 3: Inject JS to mask automation
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

        driver.get(f"https://www.google.com/search?q={query}")
        print(f"[INFO] Navigating to Google Search for: {query}")

        # Step 4: Wait for search results to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="yuRUbf"]/a'))
            )
            print("[INFO] ✅ Primary results detected with main XPath.")
        except:
            print("[WARN] Primary XPath did not return results. Trying alternate XPath...")

        results = []
        
        # Step 5: Try primary XPath
        elements = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a')

        # If empty, try backup XPath
        if not elements:
            elements = driver.find_elements(By.XPATH, '//a/h3/../../a')
            if elements:
                print("[INFO] ✅ Results found using backup XPath.")
            else:
                print("[ERROR] ❌ No results found using either XPath.")

        for el in elements:
            href = el.get_attribute("href")
            if href and "google.com" not in href:
                results.append(href)
            if len(results) >= 3:
                break

        # Step 6: Print diagnostic info
        print(f"[INFO] Final page title: {driver.title}")
        print(f"[INFO] Final URL: {driver.current_url}")
        print("[DEBUG] Page source preview:\n", driver.page_source[:1000])

        print(f"[INFO] ✅ Scraped {len(results)} valid result(s) for query: '{query}'")
        return chrome_status, results

    except Exception as e:
        error_msg = f"{chrome_status} ❗ Error during scraping: {str(e)}"
        print("[ERROR]", error_msg)
        return error_msg, []

    finally:
        try:
            driver.quit()
            print("[INFO] ✅ WebDriver closed successfully.")
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
        print("[INFO] ✅ Results successfully displayed.")
    else:
        html = f"<h1>{chrome_message}</h1><h2>No results found for: {query}. Please try again later.</h2>"
        print("[ERROR] ❌ No results found or there was an error during scraping.")

    return html