import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

stores = []
store = {}
page = 1
columns = ["Nom", "Details" ,"lien"]

def scrap_page(driver):
    global stores
    global store
    global page

    links = driver.find_elements(By.TAG_NAME, "a")
    links = links[7:]

    for link in links:
        if ("\n" in link.text):
            if (store != {}):
                stores.append(store)
                store = {}

            if ("\n" in link.text):

                data = link.text.split("\n")
                store["Nom"] = data[0]

                details = ""
                for i in range(1, len(data)):
                    details += data[i] + " "
                store["Details"] = details
                
                # data = link.text.split("\n")
                # for (i, d) in enumerate(data):
                #     if (i == 0):
                #         store["Nom"] = d
                #     elif (i == 2):
                #         try:
                #             store["Activité"] = d.split("·")[1]
                #         except:
                #             pass
                #     elif (i == 4):
                #         store["Open"] = d.split("·")[0]

        if (link.get_attribute("href") != None):
            if ("WEBSITE" in link.text):
                store["lien"] = link.get_attribute("href")
                stores.append(store)
                store = {}

        if ("Next" in link.text):
            print("Page: " + str(page) + " Scraped")
            link.click()
            time.sleep(5)
            page += 1
            scrap_page(driver)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 gmap.py ville")
        exit(84)
    url = sys.argv[1]

    driver = webdriver.Chrome()
    driver.get(url)

    time.sleep(2)

    buttons = driver.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.text == "Accept all":
            button.click()
            break

    time.sleep(3)

    divs = driver.find_elements(By.TAG_NAME, "div")
    for div in divs:
        if div.text == "More businesses":
            div.click()
            break

    time.sleep(3)

    scrap_page(driver)

    df = pd.DataFrame(stores, columns=columns)
    df.to_csv("gmap.csv", index=False)

if __name__ == "__main__":
    main()
