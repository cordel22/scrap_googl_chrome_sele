from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
import random
from user_agents import USER_AGENTS  # Your user agent pool

app = Flask(__name__)

CHROME_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

def scrape_bing_search(query):
    # Step 1: Verify Chrome binary
    if os.path.exists(CHROME_PATH):
        chrome_status = "✅ Chrome binary found."
        print("[INFO] Chrome binary exists at expected path.")
    else:
        chrome_status = "❌ Chrome binary NOT found!"
        print("[ERROR] Chrome binary is missing at:", CHROME_PATH)
        return chrome_status + " Chrome not found.", []

    # Step 2: Configure options
    user_agent = random.choice(USER_AGENTS)
    print(f"[INFO] Selected User Agent: {user_agent}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent}")
    options.binary_location = CHROME_PATH

    try:
        # Step 3: Start driver
        driver = webdriver.Chrome(options=options)
        print("[INFO] ✅ Chrome WebDriver launched.")

        # Step 4: Fetch Bing search results
        search_url = f"https://www.bing.com/search?q={query}"
        print(f"[INFO] Navigating to: {search_url}")
        driver.get(search_url)
        time.sleep(2)

        # Step 5: Extract results from Bing
        results = []
        elements = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')
        print(f"[INFO] Found {len(elements)} result candidates.")

        for el in elements:
            href = el.get_attribute("href")
            if href and "bing.com" not in href:
                results.append(href)
            if len(results) >= 3:
                break

        print(f"[INFO] ✅ Scraped {len(results)} result(s) for query '{query}'")
        return chrome_status, results

    except Exception as e:
        error_msg = f"{chrome_status} ❗ Error during scraping: {str(e)}"
        print("[ERROR]", error_msg)
        return error_msg, []

    finally:
        try:
            driver.quit()
            print("[INFO] WebDriver closed.")
        except:
            print("[WARN] WebDriver cleanup failed or not needed.")

@app.route("/")
def home():
    query = "donald trump"
    chrome_message, results = scrape_bing_search(query)

    if results:
        html = f"<h1>{chrome_message}</h1><h2>Search results for: {query}</h2><ul>"
        for link in results:
            html += f'<li><a href="{link}" target="_blank">{link}</a></li>'
        html += "</ul>"
        print("[INFO] ✅ Results rendered successfully.")
    else:
        html = f"<h1>{chrome_message}</h1><h2>No results found for: {query}.</h2>"
        print("[ERROR] ❌ No valid results or scraping failed.")

    return html