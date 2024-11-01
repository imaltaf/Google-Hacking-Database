# scraper.py
import os
import csv
import time
from datetime import datetime
import telegram
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

load_dotenv()

class GHDBScraper:
    def __init__(self):
        self.base_url = "https://www.exploit-db.com/google-hacking-database"
        self.telegram_bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.output_dir = 'data'
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        return webdriver.Chrome(options=chrome_options)

    def wait_for_table_load(self, driver):
        """Wait for the table to load completely"""
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.dt-table"))
            )
            time.sleep(2)  # Allow for any dynamic content to load
        except TimeoutException:
            self.send_telegram_notification("Timeout waiting for table to load")
            raise

    def get_total_pages(self, driver):
        """Get the total number of pages"""
        try:
            pagination_info = driver.find_element(By.CSS_SELECTOR, "#exploits-table_info").text
            total_entries = int(pagination_info.split()[-2].replace(',', ''))
            entries_per_page = int(pagination_info.split()[1])
            return (total_entries + entries_per_page - 1) // entries_per_page
        except Exception as e:
            self.send_telegram_notification(f"Error getting total pages: {str(e)}")
            raise

    def parse_table_data(self, driver):
        """Parse the current page's table data"""
        data = []
        rows = driver.find_elements(By.CSS_SELECTOR, "table.dt-table tbody tr")
        
        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:
                    data.append({
                        'date_added': cols[0].text.strip(),
                        'dork': cols[1].text.strip(),
                        'category': cols[2].text.strip(),
                        'author': cols[3].text.strip()
                    })
            except Exception as e:
                print(f"Error parsing row: {str(e)}")
                continue
                
        return data

    def scrape_all_pages(self):
        """Scrape data from all pages"""
        driver = self.setup_driver()
        all_data = []
        
        try:
            driver.get(self.base_url)
            self.wait_for_table_load(driver)
            total_pages = self.get_total_pages(driver)
            
            self.send_telegram_notification(f"Starting scrape of {total_pages} pages...")
            
            for page in range(1, total_pages + 1):
                try:
                    if page > 1:
                        next_button = driver.find_element(By.CSS_SELECTOR, "#exploits-table_next")
                        if "disabled" not in next_button.get_attribute("class"):
                            next_button.click()
                            self.wait_for_table_load(driver)
                    
                    page_data = self.parse_table_data(driver)
                    all_data.extend(page_data)
                    
                    if page % 10 == 0:
                        self.send_telegram_notification(f"Scraped {page}/{total_pages} pages...")
                
                except Exception as e:
                    self.send_telegram_notification(f"Error on page {page}: {str(e)}")
                    continue
            
            return all_data
            
        finally:
            driver.quit()

    def save_to_csv(self, data):
        """Save all data to a single CSV file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.output_dir}/complete_ghdb_data_{timestamp}.csv'
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date_added', 'dork', 'category', 'author']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return filename
        except Exception as e:
            self.send_telegram_notification(f"Error saving to CSV: {str(e)}")
            raise

    def send_telegram_notification(self, message):
        """Send notification via Telegram"""
        try:
            self.telegram_bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Error sending Telegram notification: {str(e)}")

    def run(self):
        """Main execution method"""
        try:
            print("Starting complete GHDB data extraction...")
            data = self.scrape_all_pages()
            
            csv_file = self.save_to_csv(data)
            
            success_message = (
                f"GHDB data extraction completed successfully!\n"
                f"Total entries: {len(data)}\n"
                f"CSV file: {csv_file}"
            )
            print(success_message)
            self.send_telegram_notification(success_message)
            
        except Exception as e:
            error_message = f"Error in GHDB scraper: {str(e)}"
            print(error_message)
            self.send_telegram_notification(error_message)

if __name__ == "__main__":
    scraper = GHDBScraper()
    scraper.run()