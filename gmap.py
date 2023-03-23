import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup

stores = []
store = {}
page = 1
columns = ["Nom", "Enseigne", "Contact", "Ouvert", "lien", "Ville"]

def scrap_page(driver, city):
    global stores
    global store
    global page

    links = driver.find_elements(By.TAG_NAME, "a")
    links = links[7:]

    for link in links:
        try:
            if ("\n" in link.text):
                if (store != {}):
                    store["Ville"] = city
                    stores.append(store)
                    store = {}

                if ("\n" in link.text):
                    html = link.get_attribute("innerHTML")
                    soup = BeautifulSoup(html, "html.parser")
                    spans = soup.find_all("span")
                    divs = soup.find_all("div")

                    store["Nom"] = spans[0].text

                    if (len(divs) > 3):
                        store["Enseigne"] = divs[3].text.split("·")[-1]

                    state = divs[-1].text.split("·")[0]
                    if ("⋅" in state):
                        store["Ouvert"] = state.split("⋅")[0]

                    last = divs[-1].text.split("·")[-1]
                    if (last.replace(' ', '').isdigit()):
                        store["Contact"] = last

            if (link.get_attribute("href") != None):
                if ("WEBSITE" in link.text):
                    store["lien"] = link.get_attribute("href")
                    store["Ville"] = city
                    stores.append(store)
                    store = {}

            if ("Next" in link.text):
                print("Page: " + str(page) + " Scraped")
                link.click()
                time.sleep(2)
                page += 1
                scrap_page(driver, city)

        except:
            print("Error")
            store = {}
            pass

def launch_url(url, city):

    driver.get(url)

    time.sleep(1)

    buttons = driver.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.text == "Accept all":
            button.click()
            break

    time.sleep(1)

    divs = driver.find_elements(By.TAG_NAME, "div")
    for div in divs:
        if div.text == "More businesses" or div.text == "More places":
            div.click()
            break

    time.sleep(1)

    scrap_page(driver, city)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gmap.py file")
        exit(84)
    file = sys.argv[1]

    driver = webdriver.Chrome()
    with open(file, "r") as f:
        content = f.read()
        lines = content.split('\n')
        job = lines[0]
        for line in lines[1:]:
            if (line == ""):
                continue
            launch_url("https://www.google.com/search?q=" + job + "+" + line, line)
            page = 1
        df = pd.DataFrame(stores, columns=columns)
        df.to_csv("gmap-" + job + ".csv", index=False)
