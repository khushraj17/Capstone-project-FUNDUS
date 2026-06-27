# main.py

import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup


CITY = "mumbai"
MAX_PAGES = 5


driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager().install()
    )
)


all_properties = []


def get_text(soup, selector):

    tag = soup.select_one(selector)

    if tag:
        return tag.text.strip()

    return None


def scrape_property_details(link):

    try:

        driver.get(link)

        time.sleep(5)

        soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )

        data = {

            "areaWithType": get_text(
                soup,
                "#factArea"
            ),

            "bedRoom": get_text(
                soup,
                "#bedRoomNum"
            ),

            "bathroom": get_text(
                soup,
                "#bathroomNum"
            ),

            "balcony": get_text(
                soup,
                "#balconyNum"
            ),

            "additionalRoom": get_text(
                soup,
                "#additionalRooms"
            ),

            "address": get_text(
                soup,
                "#address"
            ),

            "floorNum": get_text(
                soup,
                "#floorNumLabel"
            ),

            "facing": get_text(
                soup,
                "#facingLabel"
            ),

            "agePossession": get_text(
                soup,
                "#agePossessionLbl"
            ),

            "description": get_text(
                soup,
                "#description"
            ),

            "property_id": get_text(
                soup,
                "#Prop_Id"
            )

        }

        return data

    except Exception as e:

        print(e)

        return {}


for page in range(1, MAX_PAGES + 1):

    print(f"\nPage {page}")

    url = (
        f"https://www.99acres.com/"
        f"flats-in-{CITY}-ffid-page-{page}"
    )

    driver.get(url)

    time.sleep(8)

    soup = BeautifulSoup(
        driver.page_source,
        "html.parser"
    )

    cards = soup.select(
        "a.tupleNew__propertyHeading"
    )

    print(
        "Listings Found:",
        len(cards)
    )

    for card in cards:

        try:

            property_name = card.get(
                "title"
            )

            link = card.get(
                "href"
            )

            details = scrape_property_details(
                link
            )

            row = {

                "property_name":
                    property_name,

                "link":
                    link,

                "society":
                    None,

                "price":
                    None,

                "area":
                    None,

                **details

            }

            all_properties.append(
                row
            )

        except Exception as e:

            print(e)


driver.quit()


df = pd.DataFrame(
    all_properties
)

df.to_csv(
    f"{CITY}_properties.csv",
    index=False
)

print(df.shape)
print("CSV Saved")