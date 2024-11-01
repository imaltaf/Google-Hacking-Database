import os
import requests
from flask import Flask, send_from_directory

# Telegram Bot settings
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Flask app setup
app = Flask(__name__)
DOWNLOAD_FOLDER = 'download'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Function to send Telegram notification
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=data)
        print("Notification sent.")
    except Exception as e:
        print(f"Failed to send notification: {e}")

# Flask route to serve files
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename)

# Main function
def main():
    # Your main script logic here
    print("Running main script...")

    # Simulate script completion
    # (In real use, your script's main logic would replace this line)
    print("Script complete!")

    # Notify via Telegram
    send_telegram_message("The script has completed successfully!")

# Run the main function, then start Flask server
if __name__ == "__main__":
    main()
    # Start Flask app for file download on port 5000
    app.run(host="0.0.0.0", port=5000)
