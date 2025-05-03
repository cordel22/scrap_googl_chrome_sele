from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
import random
from user_agents import USER_AGENTS  # List of user agents

app = Flask(__name__)

CHROME_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

working_agents = []  # Will be filled on startup

def configure_driver(user_agent):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent}")
    options.binary_location = CHROME_PATH
    return webdriver.Chrome(options=options)

def test_user_agent(agent):
    try:
        driver = configure_driver(agent)
        driver.get("https://www.bing.com")
        time.sleep(1.5)
        search_box = driver.find_elements(By.NAME, "q")
        if search_box:
            print(f"[PASS] Agent working: {agent[:50]}...")
            return True
        else:
            print(f"[FAIL] Agent loaded Bing but no search box: {agent[:50]}...")
            return False
    except Exception as e:
        print(f"[ERROR] Agent failed completely: {agent[:50]}... Error: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

def find_working_user_agents():
    print("[INFO] Starting user-agent health check...")
    for agent in USER_AGENTS:
        if test_user_agent(agent):
            working_agents.append(agent)
        time.sleep(random.uniform(1.5, 3))  # Polite delay to avoid suspicion
    print(f"[INFO] ✅ Found {len(working_agents)} working user agent(s).")

def scrape_bing_search(query):
    if not os.path.exists(CHROME_PATH):
        return "❌ Chrome binary NOT found!", []

    if not working_agents:
        return "❌ No working user agents available!", []

    # Try up to 3 different agents randomly
    for _ in range(3):
        user_agent = random.choice(working_agents)
        print(f"[INFO] Using user agent: {user_agent[:80]}")

        try:
            driver = configure_driver(user_agent)
            print("[INFO] ✅ Chrome WebDriver launched.")

            search_url = f"https://www.bing.com/search?q={query}"
            print(f"[INFO] Navigating to: {search_url}")
            driver.get(search_url)
            time.sleep(2.5)

            elements = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')
            results = []

            for el in elements:
                href = el.get_attribute("href")
                if href and "bing.com" not in href:
                    results.append(href)
                if len(results) >= 5:
                    break

            print(f"[INFO] ✅ Got {len(results)} results.")
            return "✅ Search successful!", results

        except Exception as e:
            print(f"[WARN] ❗ Agent failed: {e}")
            time.sleep(2)

        finally:
            try:
                driver.quit()
            except:
                pass

    return "❌ All attempts failed!", []

@app.route("/")
def home():
    query = "bertrand russell"
    chrome_message, results = scrape_bing_search(query)

    if results:
        html = f"<h1>{chrome_message}</h1><h2>Search results for: {query}</h2><ul>"
        for link in results:
            html += f'<li><a href="{link}" target="_blank">{link}</a></li>'
        html += "</ul>"
    else:
        html = f"<h1>{chrome_message}</h1><h2>No results found for: {query}.</h2>"

    return html

if __name__ == "__main__":
    if os.path.exists(CHROME_PATH):
        find_working_user_agents()
    else:
        print("[ERROR] ❌ Chrome binary NOT found.")
    app.run(host="0.0.0.0", port=5000)