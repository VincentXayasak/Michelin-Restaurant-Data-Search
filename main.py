"""
Before running main! Make sure to choose your location
and change where ever there are #Change comments in main.py,
backend.py, and frontend.py. 
"""
import os
import sys
import backend
import frontend
import sqlite3

JSON_FILE = "nyc.json"  # Change this to the path of your JSON file if needed
DB_FILE = "nyc.db"      # Change this to the path of your DB file if needed

def check_files_exist():
    """Check if the necessary .json and .db files exist."""
    return os.path.exists(JSON_FILE) and os.path.exists(DB_FILE)

def scrape_data():
    """Run the backend scraper to gather restaurant data."""
    try:
        print("Starting web scraper...")
        backend.scrape_restaurant_data(JSON_FILE)
        backend.create_database_from_json(JSON_FILE, DB_FILE)
        print("Scraping complete. Data saved to JSON and database.")
    except Exception as e:
        print(f"Error occurred during scraping: {e}")

def run_gui():
    """Run the frontend GUI to display restaurant data."""
    try:
        print("Starting GUI...")
        frontend.MainWin().mainloop()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error occurred while running GUI: {e}")

def main():
    """Main entry point to run the scraper or GUI based on user input."""
    print("Welcome to the Michelin Restaurant Data Search!")

    if check_files_exist():
        print("Data files already exist")
        run_gui()
    else:
        scrape_data()
        run_gui()

if __name__ == "__main__":
    main()