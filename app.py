from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

def scrape_google_search(query):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Needed for container environments

    # 🔧 Explicitly point to Chrome binary installed by render-build.sh
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

    driver = webdriver.Chrome(options=options)

    try:
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

        return results

    except Exception as e:
        return [f"Error: {str(e)}"]

    finally:
        driver.quit()

@app.route("/")
def home():
    query = "miss wet t-shirt vienna"
    results = scrape_google_search(query)

    html = f"<h1>Search results for: {query}</h1><ul>"
    for link in results:
        html += f'<li><a href="{link}" target="_blank">{link}</a></li>'
    html += "</ul>"

    return html