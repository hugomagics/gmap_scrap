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
cookies = False

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
                print("Page: " + str(page) + " Scraped" + " - " + city)
                link.click()
                time.sleep(2)
                page += 1
                scrap_page(driver, city)

        except Exception as e:
            store = {}
            pass

def launch_url(url, city):
    global cookies

    try:
        driver.get(url)
        time.sleep(1)

        if (cookies == False):
            cookies = True
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.text == "Accept all":
                    button.click()
                    time.sleep(1)
                    break

        divs = driver.find_elements(By.TAG_NAME, "div")
        divs = divs[370:]
        for div in divs:
            if div.text == "More businesses" or div.text == "More places":
                div.click()
                break
        time.sleep(1)
        scrap_page(driver, city)

    except Exception as e:
        print("Erreur sur la page: " + url)
        print(e)
        return

if __name__ == "__main__":
    start_time = time.time()

    if len(sys.argv) != 2:
        print("Usage: python3 gmap.py file")
        exit(84)
    file = sys.argv[1]

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)

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
        driver.close()
        print("scrapping effectué en %s secondes." % "{:.2f}".format(time.time() - start_time))