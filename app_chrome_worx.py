from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)

CHROME_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

def scrape_google_search(query):
    # Check if Chrome binary exists
    if os.path.exists(CHROME_PATH):
        chrome_status = "✅ Chrome binary found at expected path."
        print("[INFO] Chrome binary located.")
    else:
        chrome_status = "❌ Chrome binary NOT found at expected path!"
        print("[ERROR] Chrome binary missing! Expected at:", CHROME_PATH)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = CHROME_PATH

    try:
        driver = webdriver.Chrome(options=options)
        print("[INFO] Chrome WebDriver launched successfully.")
        driver.get(f"https://www.google.com/search?q={query}")
        time.sleep(2)

        results = []
        elements = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a')
        for el in elements:
            href = el.get_attribute("href")
            if href and "google.com" not in href:
                results.append(href)
            if len(results) >= 3:
                break

        print(f"[INFO] Scraped {len(results)} results for query: '{query}'")
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
            print("[WARN] WebDriver cleanup failed or was never started.")

@app.route("/")
def home():
    query = "donald trump"
    chrome_message, results = scrape_google_search(query)

    html = f"<h1>{chrome_message}</h1><h2>Search results for: {query}</h2><ul>"
    for link in results:
        html += f'<li><a href="{link}" target="_blank">{link}</a></li>'
    html += "</ul>"

    return html