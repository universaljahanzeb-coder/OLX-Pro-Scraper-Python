import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION & USER INPUT ---
search_item = input("Enter the item to search (e.g., Corolla, iPhone): ")
ads_limit = int(input("Enter the number of ads to scrape (e.g., 50, 100): "))

# URL Generation Logic
query = search_item.replace(" ", "-")
target_url = f"https://www.olx.com.pk/items/q-{query}"

# --- 2. BROWSER INITIALIZATION ---
print("\n[SYSTEM] Launching Chrome Browser...")
options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Uncomment this to run without opening window
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(target_url)
time.sleep(5) 

# --- 3. INFINITE SCROLL ENGINE ---
print(f"[SYSTEM] Scraping {search_item} ads. Target: {ads_limit} records.")

scraped_data = []
last_page_height = driver.execute_script("return document.body.scrollHeight")

while len(scraped_data) < ads_limit:
    # Triggering Scroll to the bottom
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(3) # Wait for dynamic content to load
    
    # Locate ads using the primary class identified
    current_ads = driver.find_elements(By.CLASS_NAME, 'c2c78a22')
    print(f"[PROGRESS] Found {len(current_ads)} ads so far...")
    
    if len(current_ads) >= ads_limit:
        scraped_data = current_ads
        break
        
    # Check if the end of the page is reached
    new_page_height = driver.execute_script("return document.body.scrollHeight")
    if new_page_height == last_page_height:
        print("[INFO] Reached the end of the search results.")
        scraped_data = current_ads
        break
    last_page_height = new_page_height

# --- 4. DATA EXTRACTION LOGIC ---
print("\n[SYSTEM] Extracting detailed information...")
final_results = []

for ad in scraped_data[:ads_limit]:
    try:
        # Extracting Title using primary and backup selectors
        try:
            title = ad.find_element(By.TAG_NAME, 'h2').text
        except:
            title = ad.find_element(By.CLASS_NAME, '_14a70691').text
            
        # Extracting Price with text-based backup
        try:
            price = ad.find_element(By.CLASS_NAME, '_1ad5848d').text
        except:
            price = ad.find_element(By.XPATH, ".//span[contains(text(), 'Rs')]").text
            
        # Extracting Location
        try:
            location = ad.find_element(By.CLASS_NAME, '_2e28a695').text
        except:
            location = "Location Not Provided"

        # Validating and storing data
        if title and price:
            final_results.append({
                'Product Title': title,
                'Price': price,
                'Location': location
            })
            
    except Exception as e:
        continue # Skip corrupted or incomplete ad entries

# --- 5. DATA EXPORT (EXCEL) ---
if final_results:
    df = pd.DataFrame(final_results)
    file_name = f"Scraped_{search_item.replace(' ', '_')}.xlsx"
    df.to_excel(file_name, index=False)
    print(f"\n[SUCCESS] Data exported successfully to '{file_name}'")
    print(f"[SUMMARY] Total records captured: {len(final_results)}")
else:
    print("\n[ERROR] No data could be extracted.")

driver.quit()
print("[SYSTEM] Mission accomplished. Browser closed.") 