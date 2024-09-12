import requests
from bs4 import BeautifulSoup 
import re
import json
import sqlite3

def scrape_restaurant_data(JSON_FILE):
    """Scrape data from the Michelin website and save it to a JSON file."""
    website = "https://guide.michelin.com/us/en/new-york-state/new-york/restaurants?sort=distance"  # Change this to the appropriate URL
    data = {}

    while True:
        # Request the page content
        page = requests.get(website)
        soup = BeautifulSoup(page.content, "lxml")
        
        # Find the restaurant card divs
        div = soup.find_all("div", class_="card__menu selection-card box-placeholder js-restaurant__list_item js-match-height js-map")
        base_url = re.search(r".*\.com", page.url).group()

        # Process each restaurant card
        for elem in div:
            restaurantData = elem.find("div", {"class": "love-icon pl-icon js-favorite-restaurant"}).attrs
            restaurant_url = base_url + elem.select_one("a")["href"] 
            restaurant_name = restaurantData["data-restaurant-name"]
            city = restaurantData["data-dtm-city"]
            cuisine = restaurantData["data-cooking-type"]
            cost = re.search(r"\$+", elem.find(string=re.compile("\$+"))).group()

            # Get restaurant-specific details by visiting its page
            restaurantPage = requests.get(restaurant_url)
            restaurantSoup = BeautifulSoup(restaurantPage.content, "lxml")
            address = restaurantSoup.find("li", class_="restaurant-details__heading--address").text

            # Store restaurant data
            data[restaurant_name] = {
                "url": restaurant_url,
                "city": city,
                "cost": cost,
                "cuisine": cuisine,
                "address": address
            }

        # Check if there are more pages of restaurants
        extraPages = soup.find("div", class_="js-restaurant__bottom-pagination")
        if extraPages and extraPages.find("i", class_="fa fa-angle-right"):
            website = base_url + extraPages.find_all("a")[-1]["href"]
        else:
            break

    # Save the data to the JSON file
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=3)

    print(f"Data successfully saved to {JSON_FILE}")

def create_database_from_json(JSON_FILE, DB_FILE):
    """Create a database from the JSON file with restaurant data."""
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    # Prepare the data for insertion
    dataLists = []
    for key, value in data.items():
        dataLists.append([key] + [v for v in value.values()])

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Create the CityTable, CostTable, CuisineTable, and MainTable
    cur.execute("DROP TABLE IF EXISTS CityTable")
    cur.execute('''CREATE TABLE CityTable(
                id INTEGER PRIMARY KEY,
                city TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS CostTable")
    cur.execute('''CREATE TABLE CostTable(
                id INTEGER PRIMARY KEY,
                cost TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS CuisineTable")
    cur.execute('''CREATE TABLE CuisineTable(
                id INTEGER PRIMARY KEY,
                cuisine TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS MainTable")
    cur.execute('''CREATE TABLE IF NOT EXISTS MainTable (
                name TEXT NOT NULL PRIMARY KEY,
                url TEXT,
                city INTEGER,
                cost INTEGER,
                cuisine INTEGER,
                address TEXT,
                FOREIGN KEY (city) REFERENCES CityTable(id),
                FOREIGN KEY (cost) REFERENCES CostTable(id),
                FOREIGN KEY (cuisine) REFERENCES CuisineTable(id)
                )''')

    # Insert data into the tables
    for data in dataLists:
        city = data[2]
        query = "INSERT OR IGNORE INTO CityTable (city) VALUES (?)"
        cur.execute(query, (city,))
        cur.execute("SELECT id FROM CityTable WHERE city = ?", (city,))
        city_id = cur.fetchone()[0]

        cost = data[3]
        query = "INSERT OR IGNORE INTO CostTable (cost) VALUES (?)"
        cur.execute(query, (cost,))
        cur.execute("SELECT id FROM CostTable WHERE cost = ?", (cost,))
        cost_id = cur.fetchone()[0]

        cuisine = data[4]
        query = "INSERT OR IGNORE INTO CuisineTable (cuisine) VALUES (?)"
        cur.execute(query, (cuisine,))
        cur.execute("SELECT id FROM CuisineTable WHERE cuisine = ?", (cuisine,))
        cuisine_id = cur.fetchone()[0]

        name = data[0]
        url = data[1]
        address = data[5]
        query = "INSERT INTO MainTable (name, url, city, cost, cuisine, address) VALUES (?, ?, ?, ?, ?, ?)"
        values = (name, url, city_id, cost_id, cuisine_id, address)
        cur.execute(query, values)

    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} created successfully.")

if __name__ == "__main__":
    scrape_restaurant_data()
    create_database_from_json()
    