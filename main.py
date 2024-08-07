from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, \
    ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
import os
import time

driver_path = "/home/user/chrome-linux64/chrome"
# Set the path to the ChromeDriver executable in the PATH environment variable
os.environ["PATH"] += ":/home/user/chrome-linux64/chrome"
driver = webdriver.Chrome()
JUMIA_URL = "https://www.jumia.co.ke"
driver.get(JUMIA_URL)
with open(file="visited_pages.txt", mode="w") as file:
    file.close()

# find the news banner cncel
banner_cancel = driver.find_element(by=By.XPATH, value="//button[@aria-label='newsletter_popup_close-cta']")
banner_cancel.click()


def has_loaded(driver):
    cats = driver.find_elements(by=By.XPATH, value="//div[contains(@class,'cat')]/a")
    return len(cats) > 5


# implement a function to check for already visited pages
scrapped_pages = []

# find the categories
try:
    time.sleep(3)
    menu_items = driver.find_elements(by=By.XPATH, value="//div[contains(@class,'cat')]/a[@class='tit']")
except NoSuchElementException:

    WebDriverWait(driver, 10).until(has_loaded)
    menu_items = driver.find_elements(by=By.XPATH, value="//div[contains(@class,'cat')]/a[@class='tit']")

# save the links to a list
list_of_menu_links = [item.get_attribute('href') for item in menu_items]
for link in list_of_menu_links:
    try:
        driver.get(url=link)
        print(f"page name {link}")
        with open(file="visited_pages.txt", mode="a") as file:
            file.write(f"{link}\n")
    except InvalidArgumentException:
        continue

    # get the categories in that page
    time.sleep(2.2)
    categories = driver.find_elements(by=By.XPATH, value="//div[contains(@class,'-fh')]/article/a")
    print(f"{len(categories)} links found")

    # add the category links to a list
    category_links_list = [category.get_attribute('href') for category in categories]
    # start navigating to each of the links
    for category in category_links_list:
        driver.get(url=category)
        time.sleep(1.5)
        # find the submenus in this page
        submenus = driver.find_elements(by=By.XPATH, value="//div[contains(@class,'-fh')]/article/a")
        # add the submenu links to a list
        submenus_list = [x.get_attribute("href") for x in submenus]
        # navigate to each submenu and start fetching
        for menu in submenus_list[2:]:
            if menu in scrapped_pages:
                continue
            else:
                driver.get(url=menu)
                time.sleep(1.5)
                # todo keep these in a loop until it breaks
                next_present = True
                # todo fetch the products ,
                i = 0
                while next_present:
                    i += 1
                    if i > 2:
                        break
                    # todo print page number

                    # name
                    name_path = "//div[contains(@data-catalog,'true')]/article/a/div/h3"
                    item_names = driver.find_elements(by=By.XPATH, value=name_path)
                    names_list = [name.text for name in item_names]

                    # price
                    price_path = "//div[contains(@data-catalog,'true')]/article/a/div/div[@class='prc']"
                    prices = driver.find_elements(by=By.XPATH, value=price_path)
                    current_prices_list = [price.text for price in prices]

                    # discount

                    discount_path = "//div[contains(@data-catalog,'true')]/article/a/div/div[@class='old']"
                    old_prices = []

                    # todo final step before clicking next
                    for i in range(len(prices)):
                        # print(f"i = {i}")
                        # todo align discounts to the products ,find elements using the products as root
                        # discount_path = '..//div[@class="s-prc-w"]/div[@class="old"]'
                        discount_path = '//div[@class="info"]/div/div[@class="old"]'
                        old_price = driver.find_elements(by=By.XPATH, value=discount_path)
                        # print(f"no of elements : {len(old_price)}")
                        try:
                            # x = prices[i].find_element(by=By.XPATH, value=discount_path)
                            # print(f"class {x.get_attribute('class')}")
                            # old_price = prices[i].find_element(by=By.XPATH, value=discount_path).text
                            try:
                                old_price = driver.find_elements(by=By.XPATH, value=discount_path)[i].text

                                print(f"old price : {old_price}")
                                old_prices.append(old_price)
                            except IndexError:
                                # todo save the page with index errors
                                print(f"i value : {i}")
                                old_price = driver.find_elements(by=By.XPATH, value=discount_path)
                                print(f"no of elements : {len(old_price)}")
                                break
                                time.sleep(4000)

                        except NoSuchElementException:
                            print("error")
                            # use the current price as the original price
                            old_prices.append(current_prices_list[i])

                        # todo implement write here
                        print(f"{names_list[i]} -> {current_prices_list[i]} old price : {old_prices[i]}")

                    time.sleep(1.7)

                    # loacte the next page button and click
                    try:
                        next_button = driver.find_element(by=By.XPATH, value="//a[@aria-label='Next Page']")
                    except NoSuchElementException:
                        break


                    # scroll to the next button
                    # Scroll the element into view

                    # Scroll the element to the top of the page
                    def scroller():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", next_button)
                        time.sleep(1)
                        driver.execute_script("window.scrollBy(0,-250)")
                        time.sleep(0.8)


                    try:
                        scroller()
                        next_button.click()
                        time.sleep(4)
                    except ElementClickInterceptedException:
                        scroller()
                        time.sleep(3)
                        # todo implement a wait for element to be clickable
                        next_button.click()

            # add the url to list of scrapped pages
            scrapped_pages += menu
            time.sleep(2)

    time.sleep(0.8)

time.sleep(100)
