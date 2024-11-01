# scraper.py
import os
import csv
from datetime import datetime
import telegram
from dotenv import load_dotenv

load_dotenv()

class GHDBScraper:
    def __init__(self):
        self.telegram_bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.output_dir = 'data'
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def parse_ghdb_data(self):
        """Parse the sample GHDB data"""
        # Sample data provided
        sample_data = """Show 15 Quick Search Date Added Dork Category Author
2003-06-24 "Index of /backup" Sensitive Directories anonymous
2003-06-24 "powered by openbsd" +"powered by apache" Web Server Detection anonymous
2003-06-24 "# Dumping data for table" Files Containing Juicy Info anonymous
2003-06-24 intitle:index.of intext:"secring.skr"|"secring.pgp"|"secring.bak" Files Containing Passwords anonymous
2003-06-24 intitle:index.of passwd passwd.bak Files Containing Passwords anonymous
2003-06-24 intitle:index.of master.passwd Files Containing Passwords anonymous
2003-06-24 intitle:"Index of" pwd.db Files Containing Passwords anonymous
2003-06-24 intitle:"Index of" dbconvert.exe chats Files Containing Juicy Info anonymous
2003-06-24 "cacheserverreport for" "This analysis was produced by calamaris" Files Containing Juicy Info anonymous
2003-06-24 intitle:"Index of" ".htpasswd" htpasswd.bak Files Containing Passwords anonymous"""

        data = []
        for line in sample_data.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.strip().split('" ')
                if len(parts) > 1:
                    # Handle quoted dorks
                    date = parts[0].split()[0]
                    dork = parts[0].split('"')[1]
                    remaining = ' '.join(parts[1:]).strip()
                else:
                    # Handle unquoted dorks
                    parts = line.strip().split()
                    date = parts[0]
                    # Find where the category starts (it's usually 2-3 words)
                    for i in range(len(parts)-3, 1, -1):
                        if ' '.join(parts[i:i+2]) in ["Containing Passwords", "Containing Juicy", "Server Detection", "Directories anonymous"]:
                            dork = ' '.join(parts[1:i])
                            remaining = ' '.join(parts[i:])
                            break

                # Split remaining into category and author
                category_parts = remaining.split()
                author = category_parts[-1]
                category = ' '.join(category_parts[:-1])

                data.append({
                    'date_added': date,
                    'dork': dork,
                    'category': category,
                    'author': author
                })
        
        return data

    def save_to_csv(self, data):
        """Save the data to a CSV file with timestamp in filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.output_dir}/ghdb_data_{timestamp}.csv'
        
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
            print("Starting GHDB data extraction...")
            data = self.parse_ghdb_data()
            
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