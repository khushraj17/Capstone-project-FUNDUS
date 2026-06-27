import json
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# -------------------------
# CONFIG
# -------------------------

CITY = "bhopal"
MAX_PAGES = 20

# -------------------------
# SELENIUM SETUP
# -------------------------

options = Options()

options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager().install()
    ),
    options=options
)

all_properties = []

# -------------------------
# PAGE LOOP
# -------------------------

for page in range(11, MAX_PAGES + 1):

    try:

        url = f"https://www.99acres.com/flats-in-{CITY}-ffid-page-{page}"

        print(f"\nScraping Page {page}")

        driver.get(url)

        time.sleep(8)

        html = driver.page_source

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Price Extraction
        price = ""

        try:
            price_tag = soup.select_one(
                "div.tupleNew__priceValWrap span"
            )

            if price_tag:
                price = price_tag.text.strip()

        except:
            pass

        # Nearby Locations
        nearby_locations = []

        try:

            nearby_locations = [

                x.text.strip()

                for x in soup.select(
                    "span.NearByLocation__infoText"
                )

            ]

        except:
            pass

        properties_found = 0

        # Extract JSON-LD data
        scripts = driver.find_elements(
            "xpath",
            '//script[@type="application/ld+json"]'
        )

        for script in scripts:

            try:

                data = json.loads(
                    script.get_attribute(
                        "innerHTML"
                    )
                )

                if (
                    isinstance(data, dict)
                    and data.get("@type") == "Apartment"
                ):

                    properties_found += 1

                    all_properties.append({

                            "name":
                                data.get("name"),

                            "url":
                                data.get("url"),

                            "price":
                                price,

                            "description":
                                data.get("description"),

                            "rooms":
                                data.get("numberOfRooms"),

                            "bathrooms":
                                data.get(
                                    "numberOfBathroomsTotal"
                                ),

                            "area":
                                data.get(
                                    "floorSize"
                                ),

                            "address":
                                data.get(
                                    "address",
                                    {}
                                ).get(
                                    "streetAddress"
                                ),

                            "locality":
                                data.get(
                                    "address",
                                    {}
                                ).get(
                                    "addressLocality"
                                ),

                            "nearby_locations":
                                nearby_locations,

                            "latitude":
                                data.get(
                                    "geo",
                                    {}
                                ).get(
                                    "latitude"
                                ),

                            "longitude":
                                data.get(
                                    "geo",
                                    {}
                                ).get(
                                    "longitude"
                                )

                        })

            except:
                pass

        print(
            f"Properties Found: {properties_found}"
        )

        if properties_found == 0:
            print(
                "No data found. Stopping."
            )
            break

    except Exception as e:

        print("Error:", e)

# -------------------------
# SAVE DATA
# -------------------------

driver.quit()

df = pd.DataFrame(
    all_properties
)

df.drop_duplicates(
    subset=["url"],
    inplace=True
)

file_name = f"{CITY}_properties1.csv"

df.to_csv(
    file_name,
    index=False
)

print("\nDone")
print("Total Records:", len(df))
print("Saved:", file_name)